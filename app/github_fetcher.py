
import json
import logging
import math
import requests

from backoff import on_exception, expo
from ratelimit import limits, RateLimitException


CALLS_PER_MINUTE = 10
SECONDS_PER_MINUTE = 60
MAX_TRIES = 8


def page_url(url, page):
    return url + str(page)


def page_num_to_github_page_num(page_num, page_size, github_page_size):
    return math.ceil(page_num / (github_page_size / page_size))


def github_page_num_to_page_num(github_page_num, page_size):
    return (github_page_num - 1) * page_size + 1


# pre-fetch pages and cache them for faster response times
def init_cache(connection, max_items, url, page_size, github_page_size, cache_exp):
    # fetch the first PRE_FETCH_PAGES as they are likely to be accessed
    page_num = 1
    items_pages, starting_fetched_page_num = \
        fetch_page_items(url, page_num, page_size, github_page_size)
    store_pages(connection, items_pages, starting_fetched_page_num, cache_exp)

    # fetch the last PRE_FETCH_PAGES as they are likely to be accessed
    page_num = math.ceil(((max_items - github_page_size) / page_size)) + 1
    items_pages, starting_fetched_page_num = \
        fetch_page_items(url, page_num, page_size, github_page_size)
    store_pages(connection, items_pages, starting_fetched_page_num, cache_exp)


# in this sample project only one worker is run so limits will not be exceeded, but
# with several workers more coordination would need to be done
@on_exception(expo, RateLimitException, max_tries=MAX_TRIES)
@limits(calls=CALLS_PER_MINUTE, period=SECONDS_PER_MINUTE)
def make_request(url):
    return requests.get(url)


def simplify_item(item):
    return {
        'name': item['full_name'],
        'url': item['html_url'],
        'language': item['language'],
        'description': item['description']
    }


def fetch_page_items(url, page_num, page_size, github_page_size):
    github_page_num = page_num_to_github_page_num(page_num, page_size, github_page_size)

    # align page with github page boundaries of GITHUB_PAGE_SIZE
    # aligned_page =

    response = make_request(page_url(url, github_page_num))

    if response.status_code == 200:
        response_json = response.json()

        if 'items' in response_json:
            items = list(map(lambda item: simplify_item(item), response_json['items']))

            # break list up into pages of page_size items
            items_pages = [items[i * page_size:(i + 1) * page_size]
                           for i in range((len(items) + page_size - 1) // page_size)]

            return items_pages, github_page_num_to_page_num(github_page_num, page_size)

        else:
            logging.warning('Received unexpected response from GitHub for request:' + response.url)

    else:
        logging.warning('Request \'' + response.url + '\' returned with status code: '
                        + str(response.status_code))

    return None


def store_pages(connection, items_pages, page_num, cache_exp):
    if items_pages is not None and len(items_pages) > 0:
        for item_page in items_pages:
            # it's possible for page data to go stale because we cache it. this is a trade off
            # between performance and being up-to-date. the cache expire time can be played with
            # to find the most suitable expiration time
            connection.set(page_num, json.dumps(item_page), cache_exp)

            logging.info('Cached page ' + str(page_num))

            page_num = page_num + 1


# this function is executed by a worker in a background process
def pre_fetch_pages(config, page_num, last_page):
    import redis
    from rq import Connection

    redis_url = config.get('REDIS_URL')
    github_url = config.get('GITHUB_BASE_QUERY')
    page_size = config.get('PAGE_SIZE')
    github_page_size = config.get('GITHUB_PAGE_SIZE')
    cache_exp_time = config.get('CACHE_EXPIRE_TIME')

    connection = redis.from_url(redis_url)

    # fetching 1 github page (100 items / page) at a time is equivalent to 10 pages in this
    # app (10 items / page)
    pages_to_fetch = get_pages_to_fetch(page_num, 1, last_page)

    with Connection(connection):
        for page in pages_to_fetch:
            # page will not be in cache if it hasn't previously been fetched or if the
            # cache time expired on it
            if not connection.exists(page):
                logging.info('page ' + str(page) + ' is not in the cache so fetching it')

                items_pages, starting_fetched_page_num = \
                    fetch_page_items(github_url, page, page_size, github_page_size)

                store_pages(connection, items_pages, starting_fetched_page_num, cache_exp_time)
            else:
                logging.info('page ' + str(page) + ' is in the cache so not fetching it')


# rudimentary, but it serves its purpose for this example project
def get_pages_to_fetch(page_num, num_pages_pre_fetch, last_page):
    r = range(page_num - num_pages_pre_fetch, page_num + num_pages_pre_fetch + 1)

    return list(filter(lambda page: 1 <= page <= last_page, r))
