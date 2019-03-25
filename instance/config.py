

DEBUG = False
TESTING = False

REDIS_URL = 'redis://localhost:6379/0'

CACHE_EXPIRE_TIME = 3600   # in seconds, 1 hour
PAGE_SIZE = 10

# defined by Github
GITHUB_BASE_QUERY = 'https://api.github.com/search/repositories?q=elixir&per_page=100&page='
# github gives a hard limit: only the first 1000 search results are available
# https://developer.github.com/v3/search/
GITHUB_MAX_ITEMS = 1000
GITHUB_PAGE_SIZE = 100



