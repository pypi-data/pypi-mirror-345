from typing import List, Dict, Any, Union

def convert_paths_to_glom_spec(paths: List[str]) -> Dict:
    """
    Convert dot notation paths to glom specification.
    
    Args:
        paths: List of dot notation paths (e.g., ['users.name', 'users.profile.age'])
        
    Returns:
        Dict: Glom specification
    """
    def is_array_path(path_parts: List[str], all_paths: List[List[str]]) -> bool:
        """
        Determine if a path is an array path by checking if any other paths
        extend from this path.
        """
        current_path = '.'.join(path_parts)
        for other_parts in all_paths:
            other_path = '.'.join(other_parts)
            if other_path != current_path and other_path.startswith(current_path + '.'):
                return True
        return False

    def group_paths_by_root(paths: List[str]) -> Dict[str, List[List[str]]]:
        """Group paths by their root key."""
        grouped = {}
        for path in paths:
            parts = path.split('.')
            root = parts[0]
            if root not in grouped:
                grouped[root] = []
            grouped[root].append(parts)
        return grouped

    def build_nested_spec(paths: List[List[str]], all_paths: List[List[str]]) -> Dict:
        """Build nested spec structure from paths."""
        spec = {}
        
        for parts in paths:
            current = spec
            path_length = len(parts)
            
            # Build the path incrementally
            for i, part in enumerate(parts[1:], 1):
                subpath = parts[:i+1]
                
                if i == path_length - 1:  # Last part
                    if is_array_path(parts[:-1], all_paths):
                        # Parent is an array
                        parent_path = '.'.join(parts[1:-1])
                        if parts[-2] not in current:
                            current[parts[-2]] = (parent_path, [{part: part}])
                    else:
                        # Regular field
                        current[part] = '.'.join(parts[1:])
                else:
                    if is_array_path(subpath, all_paths):
                        # Current part is an array
                        if part not in current:
                            current[part] = ('.'.join(parts[1:i+1]), [{}])
                        current = current[part][1][0]
                    else:
                        # Regular nested object
                        if part not in current:
                            current[part] = {}
                        current = current[part]
        
        return spec

    # Get all path parts for analysis
    all_path_parts = [path.split('.') for path in paths]
    
    # Group paths by root
    grouped_paths = group_paths_by_root(paths)
    
    # Build the final spec
    result = {}
    for root, paths_list in grouped_paths.items():
        nested_spec = build_nested_spec(paths_list, all_path_parts)
        result[root] = (root, [nested_spec])
        
    return result
data = {
    'users': [
        {
            'id': 1,
            'name': 'John',
            'profile': {
                'age': 30,
                'contacts': [
                    {'type': 'email', 'value': 'john@example.com'},
                    {'type': 'phone', 'value': '123-456-7890'}
                ]
            }
        },
        {
            'id': 2,
            'name': 'Jane',
            'profile': {
                'age': 25,
                'contacts': [
                    {'type': 'email', 'value': 'jane@example.com'},
                    {'type': 'phone', 'value': '098-765-4321'}
                ]
            }
        }
    ]
}

def pick(obj: Any, paths: Union[List[str], str]) -> Any:
    """
    Pick specific fields from nested dictionaries/lists using dot notation.
    Only shows specified fields in nested arrays and objects.
    
    Args:
        obj: Source object (dict or list)
        paths: Single path string or list of paths using dot notation
               e.g., 'users.name' or ['users.name', 'users.profile.age']
    
    Returns:
        Dict/List with only the specified fields
    """
    # Handle single path string
    if isinstance(paths, str):
        paths = [paths]
        
    # Handle lists
    if isinstance(obj, list):
        return [pick(item, paths) for item in obj]
        
    # Handle non-dict values
    if not isinstance(obj, dict):
        return obj
        
    # Group paths by their first part and track array paths
    grouped_paths = {}
    array_paths = set()
    
    for path in paths:
        parts = path.split('.')
        if not parts:
            continue
            
        root = parts[0]
        if root not in grouped_paths:
            grouped_paths[root] = []
            
        if len(parts) > 1:
            subpath = '.'.join(parts[1:])
            grouped_paths[root].append(subpath)
            
            # Track array paths
            if isinstance(obj.get(root), list):
                array_paths.add(root)
            elif len(parts) > 2 and isinstance(obj.get(parts[0], {}).get(parts[1]), list):
                array_paths.add(f"{parts[0]}.{parts[1]}")
            
    # Build result
    result = {}
    for key, subpaths in grouped_paths.items():
        value = obj.get(key)
        if value is not None:
            if subpaths:
                picked = pick(value, subpaths)
                # Only include non-empty results
                if picked not in (None, {}, []):
                    result[key] = picked
            else:
                result[key] = value
                
    return result
r = pick(data, ['users.name', 'users.profile.contacts'])
print(r)

# # Pick names only
# result1 = glom(data, convert_paths_to_glom_spec(['users.name', 'users.profile.contacts.type']))
# print("Names only:", result1)
