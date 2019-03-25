
import json
import logging
import math

from flask import (
    abort, Flask, jsonify, redirect, render_template, request, url_for
)

from flask_redis import FlaskRedis

from rq import Queue

from app.github_fetcher import init_cache, fetch_page_items, store_pages, pre_fetch_pages, \
    page_num_to_github_page_num
from app.json_transformer import InvalidRequestError, transform


redis_store = FlaskRedis()


def create_app(test_config=None):
    logging.basicConfig(filename='server.log', level=logging.INFO)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    redis_store.init_app(app)
    redis_store.flushall()

    task_queue = Queue('default', connection=redis_store)

    init_cache(redis_store, app.config.get('GITHUB_MAX_ITEMS'), app.config.get('GITHUB_BASE_QUERY'),
               app.config.get('PAGE_SIZE'), app.config.get('GITHUB_PAGE_SIZE'),
               app.config.get('CACHE_EXPIRE_TIME'))

    #
    # routes
    #
    # with larger applications these routes would be put into logical groups
    # and broken into separate files and/or modules
    #
    @app.route('/', methods=('GET', ))
    def index():
        return redirect(url_for('json_transformer'))

    # we use POST here as data is coming in from an HTML form with no JS. if this were a REST
    # API, this would likely be a PUT because the operation is idempotent of JSON transformation
    # is idempotent
    @app.route('/json-transformer', methods=('GET', 'POST'))
    def json_transformer():
        if request.method == 'GET':
            return render_template('json-transformer.html')

        try:
            json_out = transform(json.loads(request.form['json_input']))

            # process the POST
            return jsonify(json_out)
        except json.JSONDecodeError as e:
            abort(400, e)
        except InvalidRequestError as e:
            abort(400, e)

    @app.route('/github-elixir-search', methods=('GET',))
    def github_elixir_search():
        page_size = app.config.get('PAGE_SIZE')
        github_max_items = app.config.get('GITHUB_MAX_ITEMS')
        github_page_size = app.config.get('GITHUB_PAGE_SIZE')
        github_url = app.config.get('GITHUB_BASE_QUERY')
        cache_exp_time = app.config.get('CACHE_EXPIRE_TIME')

        # GitHub caps search results at 1000. Since we have 10 items / per page, this means
        # our last page is 100.

        # last page for this app is 1000 / 10 = 100 (note: this is different from the last page for
        # github which would be 1000 / 100 = 10)
        last_page = math.ceil(github_max_items / page_size)

        try:
            page_num = int(request.args.get('page', 1))

            assert 0 < page_num <= last_page, \
                'Page number invalid. Page must be between 1 and ' + str(last_page) + '. 100 is ' \
                + 'the last page of data. The GitHub Search API limits results to the first 1000 ' \
                + 'items for unauthenticated requests. Since the project\'s page size is 10, ' \
                + 'we have a maximum of 100 pages. See https://developer.github.com/v3/search/ ' \
                + 'for more info.'

        except Exception as e:
            abort(400, e)

        items = redis_store.get(page_num)

        if items is None:
            try:
                items_pages, starting_fetched_page_num = \
                    fetch_page_items(github_url, page_num, page_size, github_page_size)
                store_pages(redis_store, items_pages, starting_fetched_page_num, cache_exp_time)

                items = items_pages[(page_num - 1) % page_size]
            except InvalidRequestError as e:
                abort(400, e)

        else:
            # pre-fetch pages via a background worker
            task_queue.enqueue(pre_fetch_pages, app.config, page_num, last_page)

            items = json.loads(items)

        return render_template('github-elixir-search.html', items=items, first_page=1,
                               last_page=last_page, previous_page=max(page_num - 1, 1),
                               next_page=min(page_num + 1, last_page))

    @app.errorhandler(404)
    def bad_request(error):
        return render_template('error.html', error=error), 400

    return app







