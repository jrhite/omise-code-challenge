
# HOST
The system is running at hosted at `128.199.99.164` on port `80`

# URLs
## JSON transformer
The JSON transformer can be found [here](http://128.199.99.164/json-transformer). Enter your JSON
here and it will return the transformed JSON.

## GitHub Elixir Search
GitHub Elixir Search can be found [here](http://128.199.99.164/github-elixir-search). Visit this
URL and use the First Page, Previous Page, Next Page and Last Page buttons to navigate the results.

# General Notes
As there are no database requirements and other system requirements are quite light, I chose to use
Flask (instead of Django for example), as it is lighter weight yet fulfills the requirements the
system has.

The system also uses a Redis queue for caching GitHub results with a 1 hour expiration. Also,
pre-fetching of GitHub pages is done when a user navigates pages to make sure the system has
already cached what the user will likely look for (eg: previous and next pages)

Pre-fetching puts tasks on a redis task queue so not to block the main web request thread. A single
worker process (more could be started) handles grabbing and exeucting tasks from the queue.

# Source code
## GitHub
`$ git clone https://github.com/jrhite/omise-code-challenge.git`

## Tests
```
$ cd omise-code-challenge
$ python3.7 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ export FLASK_APP=app
$ export FLASK_ENV=development
$ pytest
```

Note: the testing of this system is much lighter than a real system would have. I'm a big believer
in TDD concepts and I like to apply and adapt them as needed for the environment.

# Deployment
## Unix
```
<remote> $ sudo apt update
<remote> $ sudo apt install unzip redis-server python3.7 python3.7-venv python-pip
<remote> $ sudo systemctl restart redis.service

<local>  $ git archive --prefix=omise-code-challenge/ -o latest.zip HEAD
<local>  $ scp latest.zip root@128.199.99.164:/app/latest.zip

<remote> $ cd /app/omise-code-challenge
<remote> $ unzip latest.zip
<remote> $ python3.7 -m venv venv
<remote> $ source venv/bin/activate
<remote> $ pip install wheel
<remote> $ python setup.py bdist_wheel
<remote> $ pip install -r requirements.txt
<remote> $ export FLASK_APP=app
<remote> $ export FLASK_ENV=development

# in production nginx would be used as a reverse proxy and the actual flask app would
# be run using gunicorn, uwsgi or waitress. 'flask run' should not be used in production
<remote> $ flask run --host=0.0.0.0 --port=80 & disown

# start a worker
<remote> $ python worker.py & disown
```


