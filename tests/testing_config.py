
TEST_CONFIG = {
    'DEBUG': False,
    'TESTING': True,

    'REDIS_URL': 'redis://localhost:6379/0',

    'CACHE_EXPIRE_TIME': 3600,
    'PAGE_SIZE': 10,

    'GITHUB_BASE_QUERY': 'https://api.github.com/search/repositories?q=elixir&per_page=100&page=',
    'GITHUB_MAX_ITEMS': 1000,
    'GITHUB_PAGE_SIZE': 100
}
