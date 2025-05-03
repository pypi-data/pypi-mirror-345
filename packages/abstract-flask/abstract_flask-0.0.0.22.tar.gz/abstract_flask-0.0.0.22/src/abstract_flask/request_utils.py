from abstract_utilities import make_list
import json
async def makeParams(*arg,**kwargs):
   arg=make_list(arg)
   arg.append({k: v for k, v in kwargs.items() if v is not None})
   return arg
def dump_if_json(obj):
    """Convert a dictionary to a JSON string if the object is a dictionary."""
    if isinstance(obj, dict):
        return json.dumps(obj)
    return obj
def parse_request(flask_request):
    """Parse incoming Flask request and return args and kwargs."""
    args = []
    kwargs = {}

    if flask_request.method == 'POST' and flask_request.is_json:
        # Parse from JSON body
        data = flask_request.get_json()
        args = data.get('args', [])
        kwargs = {key: value for key, value in data.items() if key != 'args'}
    else:
        # Parse from query parameters
        args = flask_request.args.getlist('args')
        kwargs = {key: value for key, value in flask_request.args.items() if key != 'args'}

    return args,kwargs
def parse_and_return_json(flask_request):
    args,kwargs = parse_request(flask_request)
    return {
        'args': args,
        'kwargs': kwargs
    }
def parse_and_spec_vars(flask_request,varList):
    if isinstance(varList,dict):
      varList = list(varList.keys())
    args,kwargs = parse_request(flask_request)
    kwargs = get_only_kwargs(varList,*args,**kwargs)
    return kwargs
   
def get_only_kwargs(varList,*args,**kwargs):
    new_kwargs={}
    for i,arg in enumerate(args):
        key_variable = varList[i]
        kwargs[key_variable]=arg
    for key,value in kwargs.items():
        if key in varList:
            new_kwargs[key] = value
    return new_kwargs
def get_proper_kwargs(strings, **kwargs):
    # Convert the provided strings to lowercase for case-insensitive matching
    strings_lower = [string.lower() for string in strings]
    matched_keys = {}  # This will store matched keys and their corresponding values
    
    remaining_kwargs = kwargs.copy()  # Copy the kwargs so we can remove matched keys

    # Exact matching: Find exact lowercase matches first and remove them
    for string in strings_lower:
        for key in list(remaining_kwargs):  # Iterate over a copy of the keys
            if key.lower() == string:
                matched_keys[key] = remaining_kwargs.pop(key)  # Remove matched key from remaining_kwargs
                break

    # Partial matching: Check for keys that contain the string and remove them
    for string in strings_lower:
        for key in list(remaining_kwargs):  # Iterate over a copy of the keys
            if string in key.lower():
                matched_keys[key] = remaining_kwargs.pop(key)  # Remove matched key from remaining_kwargs
                break

    # Return the first matched value or None if no match
    if matched_keys:
        return list(matched_keys.values())[0]
    
    # Log or raise an error if no key was found for debugging
    print(f"No matching key found for: {strings} in {kwargs.keys()}")
    return None
def get_request_data(req):
    """Retrieve JSON data (for POST) or query parameters (for GET)."""
    if req.method == 'POST':
        return req.json
    else:
        return req.args.to_dict()
def get_user_ip(req):
   user_ip = req.remote_addr
   return user_ip
