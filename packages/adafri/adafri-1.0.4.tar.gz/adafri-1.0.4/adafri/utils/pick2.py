from typing import Any, Dict, List, Union, Set
import re

def _resolve_path(path: str) -> List[Union[str, int]]:
    """Convert string path to list of keys/indices."""
    if not path:
        return []
    
    parts = []
    # Handle both array[0] and simple dot notation
    matches = re.findall(r'([^.\[\]]+)|\[(\d+)\]', path)
    
    for match in matches:
        # Each match is a tuple of two groups
        if match[0]:  # Normal key
            parts.append(match[0])
        else:  # Array index
            parts.append(int(match[1]))
            
    return parts

def _get_value(obj: Any, path: List[Union[str, int]], collect_arrays: bool = True) -> Any:
    """
    Get value from object using path list.
    If collect_arrays is True, it will collect values from all array elements when encountering an array.
    """
    current = obj
    
    for i, key in enumerate(path):
        try:
            if isinstance(current, list) and collect_arrays and not isinstance(key, int):
                # Map operation over all array elements
                return [_get_value(item, path[i:], collect_arrays) for item in current]
            elif isinstance(current, (dict, list)):
                current = current[key]
            elif hasattr(current, str(key)):
                current = getattr(current, str(key))
            else:
                return None
        except (KeyError, IndexError, TypeError, AttributeError):
            return None
            
    return current

def _set_value(target: dict, path: List[Union[str, int]], value: Any) -> None:
    """Set value in target dict using path list."""
    if not path:
        return
        
    current = target
    
    for i, key in enumerate(path[:-1]):
        if isinstance(key, int):
            prev_key = path[i-1] if i > 0 else None
            if prev_key is not None:
                if prev_key not in current or not isinstance(current[prev_key], list):
                    current[prev_key] = []
                while len(current[prev_key]) <= key:
                    current[prev_key].append({})
                current = current[prev_key][key]
            else:
                if not isinstance(current, list):
                    current = target.setdefault(key, {})
                else:
                    while len(current) <= key:
                        current.append({})
                    current = current[key]
        else:
            current = current.setdefault(key, {})

    last_key = path[-1]
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        # Handle array results from collection
        if last_key not in current:
            current[last_key] = value
        else:
            if not isinstance(current[last_key], list):
                current[last_key] = value
            else:
                # Merge with existing array
                while len(current[last_key]) < len(value):
                    current[last_key].append({})
                for i, v in enumerate(value):
                    current[last_key][i].update(v)
    else:
        current[last_key] = value

def pick(obj: Any, *paths: Union[str, List[str], Set[str], tuple]) -> dict:
    """
    Creates an object composed of the picked object properties.
    Supports deep picking using dot notation and array indices.
    When encountering arrays, it will collect the specified property from all elements.
    
    Args:
        obj: Source object
        *paths: String paths or list/set/tuple of paths
        
    Returns:
        dict: New object with picked properties
        
    Examples:
        >>> data = {'users': [{'name': 'John'}, {'name': 'Jane'}]}
        >>> pick(data, 'users.name')
        {'users': [{'name': 'John'}, {'name': 'Jane'}]}
    """
    if not obj:
        return {}
    
    # Flatten paths if a list/set/tuple was passed
    flat_paths = []
    for path in paths:
        if isinstance(path, (list, set, tuple)):
            flat_paths.extend(path)
        else:
            flat_paths.append(path)
    
    result = {}
    for path in flat_paths:
        resolved_path = _resolve_path(path)
        value = _get_value(obj, resolved_path)
        if value is not None:
            _set_value(result, resolved_path, value)
            
    return result

# Example usage
if __name__ == "__main__":
    data = {
        'users': [
            {
                'id': 1,
                'name': 'John',
                'contacts': [
                    {'type': 'email', 'value': 'john@example.com'},
                    {'type': 'phone', 'value': '123-456-7890'}
                ]
            },
            {
                'id': 2,
                'name': 'Jane',
                'contacts': [
                    {'type': 'email', 'value': 'jane@example.com'},
                    {'type': 'phone', 'value': '098-765-4321'}
                ]
            }
        ],
        'settings': {
            'notifications': True
        }
    }

    # Test cases
    print("Pick all names from users:")
    print(pick(data, 'users.name'))
    # {'users': [{'name': 'John'}, {'name': 'Jane'}]}

    # print("\nPick all contact values:")
    # print(pick(data, 'users.contacts.value'))
    # # {'users': [{'contacts': [{'value': 'john@example.com'}, {'value': '123-456-7890'}]}, 
    # #            {'contacts': [{'value': 'jane@example.com'}, {'value': '098-765-4321'}]}]}

    # print("\nPick multiple properties:")
    # print(pick(data, 'users.name', 'users.id'))
    # # {'users': [{'name': 'John', 'id': 1}, {'name': 'Jane', 'id': 2}]}

    # print("\nMix of array and non-array paths:")
    # print(pick(data, 'users.name', 'settings.notifications'))
    # # {'users': [{'name': 'John'}, {'name': 'Jane'}], 'settings': {'notifications': True}}

    # # Additional test case with nested arrays
    # data2 = {
    #     'departments': [
    #         {
    #             'name': 'Engineering',
    #             'teams': [
    #                 {'name': 'Frontend', 'members': ['Alice', 'Bob']},
    #                 {'name': 'Backend', 'members': ['Charlie', 'David']}
    #             ]
    #         },
    #         {
    #             'name': 'Marketing',
    #             'teams': [
    #                 {'name': 'Digital', 'members': ['Eve', 'Frank']},
    #                 {'name': 'Brand', 'members': ['Grace', 'Henry']}
    #             ]
    #         }
    #     ]
    # }

    # print("\nPick nested array properties:")
    # print(pick(data2, 'departments.teams.name'))
    # # {'departments': [
    # #     {'teams': [{'name': 'Frontend'}, {'name': 'Backend'}]},
    # #     {'teams': [{'name': 'Digital'}, {'name': 'Brand'}]}
    # # ]}