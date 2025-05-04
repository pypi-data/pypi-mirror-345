"""

ct_utils.py

Numeric/geometry/array utility functions.

"""

#%% Imports and constants

import inspect
import json
import math
import os
import builtins

import jsonpickle
import numpy as np

from operator import itemgetter

# List of file extensions we'll consider images; comparisons will be case-insensitive
# (i.e., no need to include both .jpg and .JPG on this list).
image_extensions = ['.jpg', '.jpeg', '.gif', '.png']


#%% Functions

def truncate_float_array(xs, precision=3):
    """
    Truncates the fractional portion of each floating-point value in the array [xs] 
    to a specific number of floating-point digits.

    Args:
        xs (list): list of floats to truncate
        precision (int, optional): the number of significant digits to preserve, should be >= 1            
            
    Returns:
        list: list of truncated floats
    """

    return [truncate_float(x, precision=precision) for x in xs]


def round_float_array(xs, precision=3):
    """
    Truncates the fractional portion of each floating-point value in the array [xs] 
    to a specific number of floating-point digits.

    Args:
        xs (list): list of floats to round
        precision (int, optional): the number of significant digits to preserve, should be >= 1            
            
    Returns:
        list: list of rounded floats    
    """
    
    return [round_float(x,precision) for x in xs]


def round_float(x, precision=3):
    """
    Convenience wrapper for the native Python round()
    
    Args:
        x (float): number to truncate
        precision (int, optional): the number of significant digits to preserve, should be >= 1
    
    Returns:
        float: rounded value
    """
    
    return round(x,precision)
    
    
def truncate_float(x, precision=3):
    """
    Truncates the fractional portion of a floating-point value to a specific number of 
    floating-point digits.
    
    For example: 
        
        truncate_float(0.0003214884) --> 0.000321
        truncate_float(1.0003214884) --> 1.000321
    
    This function is primarily used to achieve a certain float representation
    before exporting to JSON.

    Args:
        x (float): scalar to truncate
        precision (int, optional): the number of significant digits to preserve, should be >= 1
        
    Returns:
        float: truncated version of [x]
    """

    return math.floor(x * (10 ** precision)) / (10 ** precision)


def args_to_object(args, obj):
    """
    Copies all fields from a Namespace (typically the output from parse_args) to an
    object. Skips fields starting with _. Does not check existence in the target
    object.

    Args:
        args (argparse.Namespace): the namespace to convert to an object
        obj (object): object whose whose attributes will be updated
        
    Returns:
        object: the modified object (modified in place, but also returned)
    """
    
    for n, v in inspect.getmembers(args):
        if not n.startswith('_'):
            setattr(obj, n, v)

    return obj


def dict_to_object(d, obj):
    """
    Copies all fields from a dict to an object. Skips fields starting with _. 
    Does not check existence in the target object.

    Args:
        d (dict): the dict to convert to an object
        obj (object): object whose whose attributes will be updated
        
    Returns:
        object: the modified object (modified in place, but also returned)
    """
    
    for k in d.keys():
        if not k.startswith('_'):
            setattr(obj, k, d[k])

    return obj


def pretty_print_object(obj, b_print=True):
    """
    Converts an arbitrary object to .json, optionally printing the .json representation.
    
    Args:
        obj (object): object to print
        b_print (bool, optional): whether to print the object
        
    Returns:
        str: .json reprepresentation of [obj]
    """

    # _ = pretty_print_object(obj)

    # TODO: it's sloppy that I'm making a module-wide change here, consider at least
    # recording these operations and re-setting them at the end of this function.
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
    a = jsonpickle.encode(obj)
    s = '{}'.format(a)
    if b_print:
        print(s)
    return s


def is_list_sorted(L, reverse=False):
    """
    Returns True if the list L appears to be sorted, otherwise False.
    
    Calling is_list_sorted(L,reverse=True) is the same as calling
    is_list_sorted(L.reverse(),reverse=False).
    
    Args:
        L (list): list to evaluate
        reverse (bool, optional): whether to reverse the list before evaluating sort status 
    
    Returns:
        bool: True if the list L appears to be sorted, otherwise False
    """
    
    if reverse:
        return all(L[i] >= L[i + 1] for i in range(len(L)-1))
    else:
        return all(L[i] <= L[i + 1] for i in range(len(L)-1))
        

def write_json(path, content, indent=1):
    """
    Standardized wrapper for json.dump().
    
    Args:
        path (str): filename to write to
        content (object): object to dump
        indent (int, optional): indentation depth passed to json.dump
    """
    
    with open(path, 'w', newline='\n') as f:
        json.dump(content, f, indent=indent)


def convert_yolo_to_xywh(yolo_box):
    """
    Converts a YOLO format bounding box [x_center, y_center, w, h] to 
    [x_min, y_min, width_of_box, height_of_box].

    Args:
        yolo_box (list): bounding box of format [x_center, y_center, width_of_box, height_of_box]

    Returns:
        list: bbox with coordinates represented as [x_min, y_min, width_of_box, height_of_box]
    """
    
    x_center, y_center, width_of_box, height_of_box = yolo_box
    x_min = x_center - width_of_box / 2.0
    y_min = y_center - height_of_box / 2.0
    return [x_min, y_min, width_of_box, height_of_box]


def convert_xywh_to_xyxy(api_box):
    """
    Converts an xywh bounding box (the MD output format) to an xyxy bounding box (the format
    produced by TF-based MD models).

    Args:
        api_box (list): bbox formatted as [x_min, y_min, width_of_box, height_of_box]

    Returns:
        list: bbox formatted as [x_min, y_min, x_max, y_max]
    """

    x_min, y_min, width_of_box, height_of_box = api_box
    x_max = x_min + width_of_box
    y_max = y_min + height_of_box
    return [x_min, y_min, x_max, y_max]


def get_iou(bb1, bb2):
    """
    Calculates the intersection over union (IoU) of two bounding boxes.

    Adapted from:
        
    https://stackoverflow.com/questions/25349178/calculating-percentage-of-bounding-box-overlap-for-image-detector-evaluation

    Args:
        bb1 (list): [x_min, y_min, width_of_box, height_of_box]
        bb2 (list): [x_min, y_min, width_of_box, height_of_box]

    Returns:
        float: intersection_over_union, a float in [0, 1]
    """

    bb1 = convert_xywh_to_xyxy(bb1)
    bb2 = convert_xywh_to_xyxy(bb2)

    assert bb1[0] < bb1[2], 'Malformed bounding box (x2 >= x1)'
    assert bb1[1] < bb1[3], 'Malformed bounding box (y2 >= y1)'

    assert bb2[0] < bb2[2], 'Malformed bounding box (x2 >= x1)'
    assert bb2[1] < bb2[3], 'Malformed bounding box (y2 >= y1)'

    # Determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Compute the area of both AABBs
    bb1_area = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])
    bb2_area = (bb2[2] - bb2[0]) * (bb2[3] - bb2[1])

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the intersection area.
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0, 'Illegal IOU < 0'
    assert iou <= 1.0, 'Illegal IOU > 1'
    return iou


def _get_max_conf_from_detections(detections):
    """
    Internal function used by get_max_conf(); don't call this directly.
    """
    
    max_conf = 0.0
    if detections is not None and len(detections) > 0:
        confidences = [det['conf'] for det in detections]
        max_conf = max(confidences)
    return max_conf


def get_max_conf(im):
    """
    Given an image dict in the MD output format, computes the maximum detection confidence for any 
    class.  Returns 0.0 if there were no detections, if there was a failure, or if 'detections' isn't 
    present.
    
    Args:
        im (dict): image dictionary in the MD output format (with a 'detections' field)
        
    Returns:
        float: the maximum detection confidence across all classes
    """
    
    max_conf = 0.0
    if 'detections' in im and im['detections'] is not None and len(im['detections']) > 0:
        max_conf = _get_max_conf_from_detections(im['detections'])
    return max_conf


def sort_results_for_image(im):
    """
    Sort classification and detection results in descending order by confidence (in place).
    
    Args:
        im (dict): image dictionary in the MD output format (with a 'detections' field)
    """
    if 'detections' not in im or im['detections'] is None:
        return

    # Sort detections in descending order by confidence
    im['detections'] = sort_list_of_dicts_by_key(im['detections'],k='conf',reverse=True)
    
    for det in im['detections']:
        
        # Sort classifications (which are (class,conf) tuples) in descending order by confidence
        if 'classifications' in det and \
            (det['classifications'] is not None) and \
            (len(det['classifications']) > 0):
            L = det['classifications']
            det['classifications'] = sorted(L,key=itemgetter(1),reverse=True)


def point_dist(p1,p2):
    """
    Computes the distance between two points, represented as length-two tuples.
    
    Args:
        p1: point, formatted as (x,y)
        p2: point, formatted as (x,y)
        
    Returns:
        float: the Euclidean distance between p1 and p2
    """
    
    return math.sqrt( ((p1[0]-p2[0])**2) + ((p1[1]-p2[1])**2) )


def rect_distance(r1, r2, format='x0y0x1y1'):
    """
    Computes the minimum distance between two axis-aligned rectangles, each represented as 
    (x0,y0,x1,y1) by default.
    
    Can also specify "format" as x0y0wh for MD-style bbox formatting (x0,y0,w,h).
    
    Args:
        r1: rectangle, formatted as (x0,y0,x1,y1) or (x0,y0,xy,y1)
        r2: rectangle, formatted as (x0,y0,x1,y1) or (x0,y0,xy,y1)
        format (str, optional): whether the boxes are formatted as 'x0y0x1y1' (default) or 'x0y0wh'
        
    Returns:
        float: the minimum distance between r1 and r2
    """
    
    assert format in ('x0y0x1y1','x0y0wh'), 'Illegal rectangle format {}'.format(format)
    
    if format == 'x0y0wh':
        # Convert to x0y0x1y1 without modifying the original rectangles
        r1 = [r1[0],r1[1],r1[0]+r1[2],r1[1]+r1[3]]
        r2 = [r2[0],r2[1],r2[0]+r2[2],r2[1]+r2[3]]
        
    # https://stackoverflow.com/a/26178015
    x1, y1, x1b, y1b = r1
    x2, y2, x2b, y2b = r2
    left = x2b < x1
    right = x1b < x2
    bottom = y2b < y1
    top = y1b < y2
    if top and left:
        return point_dist((x1, y1b), (x2b, y2))
    elif left and bottom:
        return point_dist((x1, y1), (x2b, y2b))
    elif bottom and right:
        return point_dist((x1b, y1), (x2, y2b))
    elif right and top:
        return point_dist((x1b, y1b), (x2, y2))
    elif left:
        return x1 - x2b
    elif right:
        return x2 - x1b
    elif bottom:
        return y1 - y2b
    elif top:
        return y2 - y1b
    else:
        return 0.0


def split_list_into_fixed_size_chunks(L,n):
    """
    Split the list or tuple L into chunks of size n (allowing at most one chunk with size 
    less than N, i.e. len(L) does not have to be a multiple of n).
        
    Args:
        L (list): list to split into chunks
        n (int): preferred chunk size
        
    Returns:
        list: list of chunks, where each chunk is a list of length n or n-1
    """
    
    return [L[i * n:(i + 1) * n] for i in range((len(L) + n - 1) // n )]


def split_list_into_n_chunks(L, n, chunk_strategy='greedy'):
    """
    Splits the list or tuple L into n equally-sized chunks (some chunks may be one 
    element smaller than others, i.e. len(L) does not have to be a multiple of n).
    
    chunk_strategy can be "greedy" (default, if there are k samples per chunk, the first
    k go into the first chunk) or "balanced" (alternate between chunks when pulling
    items from the list).
                                              
    Args:
        L (list): list to split into chunks
        n (int): number of chunks
        chunk_strategy (str, optiopnal): "greedy" or "balanced"; see above
        
    Returns:
        list: list of chunks, each of which is a list
    """
    
    if chunk_strategy == 'greedy':
        k, m = divmod(len(L), n)
        return list(L[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    elif chunk_strategy == 'balanced':
        chunks = [ [] for _ in range(n) ]
        for i_item,item in enumerate(L):
            i_chunk = i_item % n
            chunks[i_chunk].append(item)
        return chunks
    else:
        raise ValueError('Invalid chunk strategy: {}'.format(chunk_strategy))


def sort_list_of_dicts_by_key(L,k,reverse=False):
    """
    Sorts the list of dictionaries [L] by the key [k].
    
    Args:
        L (list): list of dictionaries to sort
        k (object, typically str): the sort key
        reverse (bool, optional): whether to sort in reverse (descending) order
        
    Returns:
        dict: sorted copy of [d]
    """
    return sorted(L, key=lambda d: d[k], reverse=reverse)
    
    
def sort_dictionary_by_key(d,reverse=False):
    """
    Sorts the dictionary [d] by key.
    
    Args:
        d (dict): dictionary to sort
        reverse (bool, optional): whether to sort in reverse (descending) order
        
    Returns:
        dict: sorted copy of [d]
    """
    
    d = dict(sorted(d.items(),reverse=reverse))
    return d
    

def sort_dictionary_by_value(d,sort_values=None,reverse=False):
    """
    Sorts the dictionary [d] by value.  If sort_values is None, uses d.values(),
    otherwise uses the dictionary sort_values as the sorting criterion.  Always 
    returns a new standard dict, so if [d] is, for example, a defaultdict, the 
    returned value is not.
    
    Args:
        d (dict): dictionary to sort
        sort_values (dict, optional): dictionary mapping keys in [d] to sort values (defaults 
            to None, uses [d] itself for sorting)
        reverse (bool, optional): whether to sort in reverse (descending) order
    
    Returns:
        dict: sorted copy of [d
    """
    
    if sort_values is None:
        d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=reverse)}
    else:
        d = {k: v for k, v in sorted(d.items(), key=lambda item: sort_values[item[0]], reverse=reverse)}
    return d


def invert_dictionary(d):
    """
    Creates a new dictionary that maps d.values() to d.keys().  Does not check
    uniqueness.
    
    Args:
        d (dict): dictionary to invert
    
    Returns:
        dict: inverted copy of [d]
    """
    
    return {v: k for k, v in d.items()}


def round_floats_in_nested_dict(obj, decimal_places=5):
    """
    Recursively rounds all floating point values in a nested structure to the 
    specified number of decimal places. Handles dictionaries, lists, tuples, 
    sets, and other iterables. Modifies mutable objects in place.
    
    Args:
        obj: The object to process (can be a dict, list, set, tuple, or primitive value)
        decimal_places: Number of decimal places to round to (default: 5)
    
    Returns:
        The processed object (useful for recursive calls)
    """
    if isinstance(obj, dict):
        for key in obj:
            obj[key] = round_floats_in_nested_dict(obj[key], decimal_places)
        return obj
    
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = round_floats_in_nested_dict(obj[i], decimal_places)
        return obj
    
    elif isinstance(obj, tuple):
        # Tuples are immutable, so we create a new one
        return tuple(round_floats_in_nested_dict(item, decimal_places) for item in obj)
    
    elif isinstance(obj, set):
        # Sets are mutable but we can't modify elements in-place
        # Convert to list, process, and convert back to set
        return set(round_floats_in_nested_dict(list(obj), decimal_places))
    
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        # Handle other iterable types - convert to list, process, and convert back
        return type(obj)(round_floats_in_nested_dict(item, decimal_places) for item in obj)
    
    elif isinstance(obj, float):
        return round(obj, decimal_places)
    
    else:
        # For other types (int, str, bool, None, etc.), return as is
        return obj

# ...def round_floats_in_nested_dict(...)    


def image_file_to_camera_folder(image_fn):
    r"""
    Removes common overflow folders (e.g. RECNX101, RECNX102) from paths, i.e. turn:
        
    a\b\c\RECNX101\image001.jpg
    
    ...into:
        
    a\b\c

    Returns the same thing as os.dirname() (i.e., just the folder name) if no overflow folders are 
    present.

    Always converts backslashes to slashes.
    
    Args:
        image_fn (str): the image filename from which we should remove overflow folders
        
    Returns:
        str: a version of [image_fn] from which camera overflow folders have been removed
    """
    
    import re
    
    # 100RECNX is the overflow folder style for Reconyx cameras
    # 100EK113 is (for some reason) the overflow folder style for Bushnell cameras
    # 100_BTCF is the overflow folder style for Browning cameras
    # 100MEDIA is the overflow folder style used on a number of consumer-grade cameras
    patterns = [r'/\d+RECNX/',r'/\d+EK\d+/',r'/\d+_BTCF/',r'/\d+MEDIA/']
    
    image_fn = image_fn.replace('\\','/')    
    for pat in patterns:
        image_fn = re.sub(pat,'/',image_fn)
    camera_folder = os.path.dirname(image_fn)
    
    return camera_folder
    

def is_float(v):
    """
    Determines whether v is either a float or a string representation of a float.
    
    Args:
        v (object): object to evaluate
        
    Returns:
        bool: True if [v] is a float or a string representation of a float, otherwise False
    """
    
    try:
        _ = float(v)
        return True
    except ValueError:
        return False


def is_iterable(x):
    """
    Uses duck typing to assess whether [x] is iterable (list, set, dict, etc.).
    
    Args:
        x (object): the object to test
    
    Returns:
        bool: True if [x] appears to be iterable, otherwise False
    """
    
    try:
        _ = iter(x)
    except:
       return False
    return True


def is_empty(v):
    """
    A common definition of "empty" used throughout the repo, particularly when loading
    data from .csv files.  "empty" includes None, '', and NaN.
    
    Args:
        v: the object to evaluate for emptiness
        
    Returns:
        bool: True if [v] is None, '', or NaN, otherwise False
    """
    if v is None:
        return True
    if isinstance(v,str) and v == '':
        return True
    if isinstance(v,float) and np.isnan(v):
        return True
    return False


def min_none(a,b):
    """
    Returns the minimum of a and b.  If both are None, returns None.  If one is None, 
    returns the other.
    
    Args:
        a (numeric): the first value to compare
        b (numeric): the second value to compare
        
    Returns:
        numeric: the minimum of a and b, or None
    """
    if a is None and b is None:
        return None
    elif a is None:
        return b
    elif b is None:
        return a
    else:
        return min(a,b)
    

def max_none(a,b):
    """
    Returns the maximum of a and b.  If both are None, returns None.  If one is None, 
    returns the other.
    
    Args:
        a (numeric): the first value to compare
        b (numeric): the second value to compare
        
    Returns:
        numeric: the maximum of a and b, or None
    """
    if a is None and b is None:
        return None
    elif a is None:
        return b
    elif b is None:
        return a
    else:
        return max(a,b)

    
def isnan(v):
    """
    Returns True if v is a nan-valued float, otherwise returns False.
    
    Args:
        v: the object to evaluate for nan-ness
    
    Returns:
        bool: True if v is a nan-valued float, otherwise False
    """
    
    try:        
        return np.isnan(v)
    except Exception:
        return False


def sets_overlap(set1, set2):
    """
    Determines whether two sets overlap.
    
    Args:
        set1 (set): the first set to compare (converted to a set if it's not already)
        set2 (set): the second set to compare (converted to a set if it's not already)
        
    Returns:
        bool: True if any elements are shared between set1 and set2
    """
    
    return not set(set1).isdisjoint(set(set2))


def is_function_name(s,calling_namespace):
    """
    Determines whether [s] is a callable function in the global or local scope, or a 
    built-in function.
    
    Args:
        s (str): the string to test for function-ness
        calling_namespace (dict): typically pass the output of locals()
    """
    
    assert isinstance(s,str), 'Input is not a string'
    
    return callable(globals().get(s)) or \
        callable(locals().get(s)) or \
        callable(calling_namespace.get(s)) or \
        callable(getattr(builtins, s, None))

        
# From https://gist.github.com/fralau/061a4f6c13251367ef1d9a9a99fb3e8d
def parse_kvp(s,kv_separator='='):
    """
    Parse a key/value pair, separated by [kv_separator].  Errors if s is not
    a valid key/value pair string.
    
    Args:
        s (str): the string to parse
        kv_separator (str, optional): the string separating keys from values.
    
    Returns:
        tuple: a 2-tuple formatted as (key,value)
    """
    
    items = s.split(kv_separator)
    assert len(items) > 1, 'Illegal key-value pair'
    key = items[0].strip()
    if len(items) > 1:
        value = kv_separator.join(items[1:])
    return (key, value)


def parse_kvp_list(items,kv_separator='=',d=None):
    """
    Parse a list key-value pairs into a dictionary.  If items is None or [],
    returns {}.
    
    Args:
        items (list): the list of KVPs to parse
        kv_separator (str, optional): the string separating keys from values.
        d (dict, optional): the initial dictionary, defaults to {}
        
    Returns:
        dict: a dict mapping keys to values
    """
    
    if d is None:
        d = {}

    if items is None or len(items) == 0:
        return d
    
    for item in items:
        key, value = parse_kvp(item)
        d[key] = value
        
    return d


def dict_to_kvp_list(d,
                     item_separator=' ',
                     kv_separator='=',
                     non_string_value_handling='error'):
    """
    Convert a string <--> string dict into a string containing list of list of
    key-value pairs.  I.e., converts {'a':'dog','b':'cat'} to 'a=dog b=cat'.  If
    d is None, returns None.  If d is empty, returns ''.
    
    Args:
        d (dict): the dictionary to convert, must contain only strings
        item_separator (str, optional): the delimiter between KV pairs
        kv_separator (str, optional): the separator betweena a key and its value
        non_string_value_handling (str, optional): what do do with non-string values,
            can be "omit", "error", or "convert"
    
    Returns:
        str: the string representation of [d]
    """
    
    if d is None:
        return None
    
    if len(d) == 0:
        return ''
    
    s = None
    for k in d.keys():
        assert isinstance(k,str), 'Input {} is not a str <--> str dict'.format(str(d))
        v = d[k]
        if not isinstance(v,str):
            if non_string_value_handling == 'error':
                raise ValueError('Input {} is not a str <--> str dict'.format(str(d)))
            elif non_string_value_handling == 'omit':
                continue
            elif non_string_value_handling == 'convert':
                v = str(v)
            else:
                raise ValueError('Unrecognized non_string_value_handling value: {}'.format(
                    non_string_value_handling))
        if s is None:
            s = ''
        else:
            s += item_separator
        s += k + kv_separator + v
    
    if s is None:
        s = ''
        
    return s
    

def parse_bool_string(s):
    """
    Convert the strings "true" or "false" to boolean values.  Case-insensitive, discards
    leading and trailing whitespace.  If s is already a bool, returns s.
    
    Args:
        s (str or bool): the string to parse, or the bool to return
        
    Returns:
        bool: the parsed value
    """
    
    if isinstance(s,bool):
        return s
    s = s.lower().strip()
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise ValueError('Cannot parse bool from string {}'.format(str(s)))
    

#%% Test driver

def __module_test__():
    """
    Module test driver
    """ 
    
    ##%% Camera folder mapping
    
    assert image_file_to_camera_folder('a/b/c/d/100EK113/blah.jpg') == 'a/b/c/d'    
    assert image_file_to_camera_folder('a/b/c/d/100RECNX/blah.jpg') == 'a/b/c/d'
    
    
    ##%% Test a few rectangle distances
    
    r1 = [0,0,1,1]; r2 = [0,0,1,1]; assert rect_distance(r1,r2)==0
    r1 = [0,0,1,1]; r2 = [0,0,1,100]; assert rect_distance(r1,r2)==0
    r1 = [0,0,1,1]; r2 = [1,1,2,2]; assert rect_distance(r1,r2)==0
    r1 = [0,0,1,1]; r2 = [1.1,0,0,1.1]; assert abs(rect_distance(r1,r2)-.1) < 0.00001
    
    r1 = [0.4,0.8,10,22]; r2 = [100, 101, 200, 210.4]; assert abs(rect_distance(r1,r2)-119.753) < 0.001
    r1 = [0.4,0.8,10,22]; r2 = [101, 101, 200, 210.4]; assert abs(rect_distance(r1,r2)-120.507) < 0.001    
    r1 = [0.4,0.8,10,22]; r2 = [120, 120, 200, 210.4]; assert abs(rect_distance(r1,r2)-147.323) < 0.001

    
    ##%% Test dictionary sorting
    
    L = [{'a':5},{'a':0},{'a':10}]
    k = 'a'
    sort_list_of_dicts_by_key(L, k, reverse=True)


    ##%% Test float rounding
    
    # Example with mixed collection types
    data = {
        "name": "Project X",
        "values": [1.23456789, 2.3456789],
        "tuple_values": (3.45678901, 4.56789012),
        "set_values": {5.67890123, 6.78901234},
        "metrics": {
            "score": 98.7654321,
            "components": [5.6789012, 6.7890123]
        }
    }
    
    result = round_floats_in_nested_dict(data)
    assert result['values'][0] == 1.23457
    assert result['tuple_values'][0] == 3.45679
    assert min(list(result['set_values'])) == 5.6789
    
    