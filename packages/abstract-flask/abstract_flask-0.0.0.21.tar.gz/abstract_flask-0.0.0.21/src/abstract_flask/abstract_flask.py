import os,sys,unicodedata,hashlib,json
from abstract_utilities import make_list,get_media_types,get_logFile
from multiprocessing import Process
from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app
)
from flask_cors import CORS
from abstract_flask import get_request_data
from werkzeug.utils import secure_filename
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

def get_desired_key_values(obj,keys=None):
    if keys == None:
        return obj
    new_dict={}
    if obj and isinstance(obj,dict):
        for key in keys:
            new_dict[key] = obj.get(key)
    return new_dict
   
def jsonify_it(obj):
    if isinstance(obj,dict):
        status_code = obj.get("status_code")
        return jsonify(obj),status_code
      
def required_keys(keys,req):
    datas = get_request_data(req)
    for key in keys:
        value = datas.get(key)
        if not value:
            return {"error": f"could not find {key} in values","status_code":400}
    return datas
   
def excecute_request(keys,req,func=None,desired_keys=None):
    try:
        datas = required_keys(keys,req)
        if datas and isinstance(datas,dict) and datas.get('error'):
            return datas
        desired_key_values = get_desired_key_values(obj=datas,keys=desired_keys)
        result = func(**desired_key_values)
        return {"result": result,"status_code":200}
    except Exception as e:
        return {"error": f"{e}","status_code":500}
def get_bp(name, static_folder=None, static_url_path=None):
    # if they passed a filename, strip it down to the module name
    if os.path.isfile(name):
        name = os.path.splitext(os.path.basename(name))[0]

    bp_name = f"{name}_bp"
    logger  = get_logFile(bp_name)
    logger.info(f"Python path: {sys.path!r}")

    # build up only the kwargs they actually gave us
    bp_kwargs = {}
    if static_folder is not None:
        bp_kwargs['static_folder']    = static_folder
    if static_url_path is not None:
        bp_kwargs['static_url_path']  = static_url_path

    bp = Blueprint(
        bp_name,
        __name__,
        **bp_kwargs,
    )
    return bp, logger
