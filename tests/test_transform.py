
import json
import os

from app.error import InvalidRequestError
from app.json_transformer import transform

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


def test_json_transform_empty_json():
    assert '[]' == dumps(transform(json.loads('{}')))


def test_json_transform_one_element_root():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 0,
      "parent_id": null,
      "title": "Title"
    }
  ]
}
'''.strip()

    elements_output = '''
[
  {
    "children": [],
    "id": 1,
    "level": 0,
    "parent_id": null,
    "title": "Title"
  }
]
'''.strip()

    assert elements_output == dumps(transform(json.loads(elements_input)))


def test_json_transform_valid_data():
    assert test_data_json_output_str == dumps(transform(json.loads(test_data_json_input_str)))


def test_json_transform_root_element_has_parent_throws():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 0,
      "parent_id": 10,
      "title": "Title"
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for root element with a parent'
    except InvalidRequestError as e:
        assert e.args == ('Element 1 is a root element and cannot have a parent',)


def test_json_transform_non_root_element_has_null_parent():
    elements_input = '''
    {
      "0": [
        {
          "children": [],
          "id": 1,
          "level": 0,
          "parent_id": null,
          "title": "Title"
        }
      ],
      "1": [
        {
          "children": [],
          "id": 2,
          "level": 1,
          "parent_id": null,
          "title": "Child Title"
        }
      ]
    }
    '''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for non root element with null ' \
                      + 'parent'
    except InvalidRequestError as e:
        assert e.args == ('Element 2 is not a root element and must have a parent',)


def test_json_transform_non_root_element_has_invalid_parent_throws():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 0,
      "parent_id": null,
      "title": "Title"
    }
  ],
  "1": [
    {
      "children": [],
      "id": 2,
      "level": 1,
      "parent_id": 10,
      "title": "Child Title"
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for non root element with invalid ' \
                      + 'parent'
    except InvalidRequestError as e:
        assert e.args == ('Element 2 has an invalid parent',)


def test_json_transform_duplicate_id():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 0,
      "parent_id": null,
      "title": "Title"
    }
  ],
  "1": [
    {
      "children": [],
      "id": 2,
      "level": 1,
      "parent_id": 1,
      "title": "Child Title 1"
    },
    {
      "children": [],
      "id": 2,
      "level": 1,
      "parent_id": 1,
      "title": "Child Title 2"
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for request with duplicate ids'
    except InvalidRequestError as e:
        assert e.args == ('Duplicate id \'2\' detected',)


def test_json_transform_element_missing_required_key():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 0,
      "parent_id": null
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for request containing an element ' \
                      + 'with a missing required key'
    except InvalidRequestError as e:
        assert e.args == ('Element 1 is missing the required keys: title',)


def test_json_transform_element_has_non_empty_children_array():
    elements_input = '''
{
  "0": [
    {
      "children": [
        {
          "children": [],
          "id": 2,
          "level": 1,
          "parent_id": 1,
          "title": "Child Title 1"
        }
      ],
      "id": 1,
      "level": 0,
      "parent_id": null,
      "title": "Title"
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for request containing an element ' \
                      + 'with a a non-empty children array'
    except InvalidRequestError as e:
        assert e.args == ('Element 1 has a non-empty children array',)


def test_json_transform_element_level_does_not_match_input():
    elements_input = '''
{
  "0": [
    {
      "children": [],
      "id": 1,
      "level": 1,
      "parent_id": null,
      "title": "Title"
    }
  ]
}
'''.strip()

    try:
        transform(json.loads(elements_input))

        assert False, 'Invalid request error should be thrown for request containing an element ' \
                      + 'with a level that does not match the input'
    except InvalidRequestError as e:
        assert e.args == ('Element 1\'s level does not match its level in the input',)
