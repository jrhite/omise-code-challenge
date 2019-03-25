

from app.error import InvalidRequestError


#
# in this example project, given the sample input/output JSON I assume and validate that:
#
#   1. the following keys are required for each element: id, children, level, parent_id, title
#   2. for non-empty JSON input, there must be at least one 'root' element with parent_id == null
#   3. also because the sample output JSON is an array, I assume there can be multiple 'root'
#      elements with parent_id == null
#   4. each element's id is unique
#   5. other than 'root' elements, every element must have a parent_id that references another
#      element's id in the given JSON input
#   6. the children array of all elements in the JSON input is an empty array
#   7. there are no circular references between the elements, both directly and indirectly
#   8. all elements in the input JSON under key = 'x' where x is a number (in string form),
#      element.level == x. this is assumed, but it is not explicitly validated in this example
#      project
#
# for the purposes of this project a fail-fast approach is taken to validation
#

required_keys = {'id', 'children', 'level', 'parent_id', 'title'}


#
# runtime complexity: O(n)
#
#   flatten_elements() => O(n)
#   build_element_trees() => O(n)
#
#   transform = 2 * O(n) => O(n)
#
# space complexity: O(n)
#
#   a JSON object is created from the JSON string containing n elements => O(n)
#
#   an intermediate hashtable is created containing n elements for fast lookup. this requires
#   k * n of memory where k is a constant amount of extra memory used for each element in the
#   hashtable. the hashtable holds references to each element. n => O(kn) => O(n)
#
#   a final array of element trees is created containing n elements, combined (array and trees).
#   the array and trees hold references to each element => O(n)

#
# Note: I considered using a JSON schema validation library (eg: marshmallow) for this project, but
# in the end, it seemed like overkill, so I just do the simple validations in the code below
#
def transform(json_input):
    # create an intermediate structure for fast element lookup
    elements = flatten_elements(json_input)

    # create the actual array of element trees
    element_trees = build_element_trees(elements)

    return element_trees


# runs in O(n) time, as it processes each of n elements one time
def flatten_elements(json_input):
    element_tree = {}

    has_root_element = False

    if not isinstance(json_input, dict):
        raise InvalidRequestError('Top-level element must be a dictionary')

    # the keys in this object are level numbers (in string form) so we sort them to ensure they are,
    # in order
    for key in sorted(json_input.keys()):
        try:
            int(key)
        except ValueError:
            raise InvalidRequestError('Top-level element keys must be numbers')

        if not isinstance(json_input[key], list):
            raise InvalidRequestError('Top-level element values must be lists')

        for element in json_input[key]:
            missing_keys = list(required_keys - set(element.keys()))

            if len(missing_keys) > 0:
                raise InvalidRequestError('Element ' + str(element['id']) + ' is missing the '
                                          'required keys: ' + ','.join(missing_keys))

            # validate a root element
            if key == '0':
                if element['parent_id'] is not None:
                    raise InvalidRequestError('Element ' + str(element['id']) + ' is a root '
                                              + 'element and cannot have a parent')
                else:
                    has_root_element = True

            # validate non-root element
            elif key != '0' and element['parent_id'] is None:
                raise InvalidRequestError('Element ' + str(element['id']) + ' is not a root '
                                          + 'element and must have a parent')

            if len(element['children']) > 0:
                raise InvalidRequestError('Element ' + str(element['id']) + ' has a non-empty '
                                          + 'children array')

            if str(element['level']) != key:
                raise InvalidRequestError('Element ' + str(element['id']) + '\'s level does not '
                                          + 'match its level in the input')

            if element['id'] in element_tree:
                raise InvalidRequestError('Duplicate id \'' + str(element['id']) + '\' detected')

            element_tree[element['id']] = element

    if not has_root_element and len(element_tree) > 0:
        raise InvalidRequestError('There are no root elements')

    return element_tree


# runs in O(n) time, as it processes each of n elements one time, with a constant
# hash-based lookup of constant time
def build_element_trees(elements):
    element_trees = []

    for element_id in elements:
        element = elements[element_id]
        parent_id = element['parent_id']

        if parent_id is None:
            element_trees.append(element)
        else:
            # elements must have valid parent_elements
            if parent_id not in elements:
                raise InvalidRequestError('Element ' + str(element['id']) + ' has an invalid '
                                          + 'parent')

            parent_element = elements[parent_id]
            parent_element['children'].append(element)

    return element_trees
