
import json
import os


#
# for more elaborate testing import and use the unittest module. here we keep it very
# lightweight and simple
#

with open(os.path.join(os.path.dirname(__file__),
                       'test_data/test_data_transform_json_in.json'), 'rb') as f:
    test_data_json_input_str = f.read().decode('utf8').rstrip()

with open(os.path.join(os.path.dirname(__file__),
                       'test_data/test_data_transform_json_out.json'), 'rb') as f:
    test_data_json_output_str = f.read().decode('utf8').rstrip()


def dumps(json_obj):
    return json.dumps(json_obj, sort_keys=True, indent=2)



def test_index_redirect(client):
    response = client.get('/')

    assert response.headers['Location'].endswith('json-transformer')
    assert response.status_code == 302


def test_json_transformer_get(client):
    response = client.get('/json-transformer')

    assert response.status_code == 200


def test_json_transformer_post(client):
    response = client.post('/json-transformer', data=dict(
        json_input=test_data_json_input_str
    ))

    assert response.status_code == 200
    assert test_data_json_output_str == dumps(response.json)


def test_github_elixir_search_get(client):
    response = client.get('/github-elixir-search')

    assert response.status_code == 200


def test_github_elixir_search_get_first_page(client):
    response = client.get('/github-elixir-search?page=1')

    assert response.status_code == 200
    assert 'elixir-lang/elixir' in str(response.data)


def test_github_elixir_search_get_last_page(client):
    response = client.get('/github-elixir-search?page=100')

    assert response.status_code == 200
    assert 'andreapavoni/nova' in str(response.data)
