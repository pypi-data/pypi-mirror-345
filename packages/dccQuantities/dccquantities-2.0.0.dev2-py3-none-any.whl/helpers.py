from __future__ import annotations

try:
    # Python 3.10+
    from types import NoneType
except ImportError:
    # Older versions
    NoneType = type(None)

import datetime
from typing import TYPE_CHECKING, Optional, Callable, Union
import warnings
import operator
import numpy as np
from typing import Union
from metas_unclib import ufloat
import re
import json
from dsiUnits import dsiUnit
from enum import Enum
import locale
import sys
from collections import OrderedDict
from dataclasses import dataclass
from elementpath.datatypes.datetime import DateTime10
if TYPE_CHECKING:
    # This import is only for type-checking purposes and won't be executed at runtime.
    from DccQuantityType import DccQuantityType

# Use the type of a compiled regex for type checking.
_REGEX_TYPE = type(re.compile(''))

class DCCJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # If the object has a callable toJSON method, use it.
        if hasattr(obj, 'to_json_dict') and callable(obj.to_json_dict):
            return obj.to_json_dict()

        if hasattr(obj, 'toJSONDict') and callable(obj.toJSONDict):
            return obj.toJSONDict()

        elif hasattr(obj, 'toJSON') and callable(obj.toJSON):
            return obj.toJSON()

        elif isinstance(obj, dsiUnit):
            return str(obj)
        # 3a) explicit DateTime10
        if isinstance(obj, DateTime10):
            return str(obj)
        # 3b) other stdlib date/time types
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        # Otherwise, fallback to the default serialization.
        return super().default(obj)


@dataclass
class FieldSpec:
    """
    Specification for a field in serialization:
      - name: attribute name on the object
      - tag: output key for serialization
      - serializer: None (read attr), str (method name), callable, or (method, key) tuple
      - merge: if True, expect serializer returns a dict to merge
    """
    name: Optional[str] = None
    tag: Optional[str] = None
    serializer: Optional[Union[str, Callable, tuple]] = None
    merge: bool = False

class ExplicitSerializerMixin:
    """
    Mixin to serialize object fields in a specified order.

    Subclasses must define:
      - __serialize_fields__: List[FieldSpec]
    """
    __serialize_fields__: list[FieldSpec] = []

    def to_dict(self) -> OrderedDict:
        """
        Build an OrderedDict of serialized fields according to __serialize_fields__.
        Treat empty lists, tuples, dicts, sets, or zero-length numpy arrays as None (skip them).
        """
        out = OrderedDict()
        for spec in self.__serialize_fields__:
            try:
                # Determine raw value
                if spec.serializer is None:
                    val = getattr(self, spec.name, None)
                elif isinstance(spec.serializer, tuple):
                    method, key = spec.serializer
                    temp = getattr(self, method)() if isinstance(method, str) else method(self)
                    val = temp.get(key) if isinstance(temp, dict) else None
                elif isinstance(spec.serializer, str):
                    val = getattr(self, spec.serializer)()
                else:
                    val = spec.serializer(self)

                # Skip None or empty collections/arrays
                if val is None:
                    continue
                if isinstance(val, (list, tuple, dict, set)) and len(val) == 0:
                    continue
                if isinstance(val, np.ndarray) and val.size == 0:
                    continue

                # Merge dict or assign directly
                if spec.merge:
                    if not isinstance(val, dict):
                        raise ValueError(f"Field {spec.name} expected to merge a dict, got {type(val)}")
                    for k, v in val.items():
                        if v in [None, [], {}, (), set()] or (isinstance(v, np.ndarray) and v.size == 0):
                            continue
                        out[k] = v
                else:
                    out[spec.tag or spec.name] = val

            except Exception as e:
                # Silently skip common NoneType attribute access errors (e.g., s.name.to_json_dict())
                if isinstance(e, AttributeError) and "'NoneType'" in str(e):
                    continue
                warnings.warn(
                    f"Serialization of field {spec.name or spec.tag} failed in {self.__class__.__name__}: {e}",
                    RuntimeWarning
                )
                continue

        return out

    def to_json_dict(self) -> dict:
        """
        Default wrapper; subclasses can override to wrap under specific root keys.
        """
        return self.to_dict()

def unexpected_key_serialization_handler(result: dict, key: str, value, class_name: str) -> None:
    """
    Handles unexpected keys during JSON serialization.

    If the key contains 'dcc:' or 'si:', it is assumed to be DCC-related and is added to the result,
    otherwise a warning is issued and the key is ignored.
    """
    if 'dcc:' in str(key) or 'si:' in str(key):
        warnings.warn(
            f"Found unexpected key {key} while converting {class_name} to JSON. "
            "Assuming this is DCC data therefore adding it to the JSON."
        )
        result[key] = value
    else:
        warnings.warn(
            f"Found unexpected key {key} while converting {class_name} to JSON. "
            "Assuming this other data is unrelated to DCC and ignoring."
        )
        # Key is ignored.

def compile_regex_in_obj(obj):
    """
    Recursively traverse obj.
    For dict values and list elements: if an element is a string,
    compile it into a regex (unless it’s already compiled).
    """
    if isinstance(obj, dict):
        # Do NOT convert keys!
        return {k: compile_regex_in_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [compile_regex_in_obj(item) for item in obj]
    elif isinstance(obj, _REGEX_TYPE):
        return obj
    elif isinstance(obj, str):
        return re.compile(obj)
    else:
        return obj

def dccTypeCollector(
    jsonDict: dict,
    searchKeys: list = ["dcc:quantity"],
    recursive: bool = False,
    attributeRegex: dict = None,
    _compiled: bool = False  # internal flag for recursion, not meant to be set by callers
):
    """
    Searches a JSON-like dict for keys in searchKeys.

    Additionally, if attributeRegex is provided (e.g.,
    {'@refType': [re.compile('basic_([0-9])IndexTable')]}), then on the first call
    both jsonDict and attributeRegex are recursively processed so that every dictionary value
    (and list element) that is a string is replaced by a compiled regex (if not already).

    Returns a list of tuples: ([key_path], value)
    """
    if attributeRegex is None:
        attributeRegex = {}

    # On the top-level call, convert all values to compiled regex where appropriate.
    if not _compiled:
        attributeRegex = compile_regex_in_obj(attributeRegex)
        _compiled = True

    results = []

    # If we got a list at the top, convert it to a dict with index keys.
    if isinstance(jsonDict, list):
        jsonDict = {i: jsonDict[i] for i in range(len(jsonDict))}

    if isinstance(jsonDict, dict):
        for key, value in jsonDict.items():
            keyMatched = False
            if key in searchKeys:
                keyMatched = True
                # If the matching value is a list, enumerate its items.
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        # check regExMatching
                        if attributeRegex:
                            matchedRegEx=False
                            for attribute, regexList in attributeRegex.items():
                                if attribute in item.keys():
                                    for regex in regexList:
                                        for attrList in item[attribute]:
                                            if regex.match(attrList):
                                                matchedRegEx=True
                                                break
                            if matchedRegEx:
                                results.append(([key, index], item))
                        else:
                            results.append(([key, index], item))
                else:
                    results.append(([key], value))

            # Continue recursion if requested or if key was not matched.
            if (recursive or not keyMatched) and isinstance(value, (dict, list)):
                subResults = dccTypeCollector(
                    jsonDict=value,
                    searchKeys=searchKeys,
                    recursive=recursive,
                    attributeRegex=attributeRegex,
                    _compiled=True  # already converted in the top-level call
                )
                for subKey, subValue in subResults:
                    results.append(([key] + subKey, subValue))

    return results


def findTables(jsonDict: dict):
    tables=dccTypeCollector(jsonDict=jsonDict, searchKeys=["dcc:list"],attributeRegex={'@refType':[re.compile('basic_([0-9])IndexTable'),re.compile('basic_([0-9])IndexFlatTable')]})
    return tables

def parseAttributes(jsonDict: dict):
    attributes = {}
    try:
        if "@id" in jsonDict.keys():
            attributes["id"] = jsonDict["@id"]

        if "@refId" in jsonDict.keys():
            attributes["refId"] = jsonDict["@refId"]

        if "@refType" in jsonDict.keys():
            attributes["refType"] = jsonDict["@refType"]

        if "@lang" in jsonDict.keys():
            attributes["lang"] = jsonDict["@lang"]
    except Exception as e:
        raise e

    return attributes

def replaceQuantitiesInDict(
    jsonDict: dict, parser, searchKeys: list = ["dcc:quantity"],returnQuantityList:bool=False
):
    foundQuantities = dccTypeCollector(jsonDict=jsonDict, searchKeys=searchKeys)
    if returnQuantityList:
        quantityList = []
    for path, result in foundQuantities:
        parsedObject = parser(result)
        if returnQuantityList:
            quantityList.append((path,parsedObject))
        currentNode = jsonDict
        for key in path[:-1]:  # Traverse to the second last key
            currentNode = currentNode[key]
        currentNode[path[-1]] = parsedObject
    if returnQuantityList:
        return jsonDict, quantityList
    else:
        return jsonDict

def isListOfTypes(arg, element_types):
    if not isinstance(element_types, list):
        raise TypeError(f"Expected list, got {type(element_types)}")
    # Check if the argument is a list
    if isinstance(arg, list) or isinstance(arg, np.ndarray):
        # Check if all elements in the list are of the specified type
        return all(any(isinstance(item, element_type) for element_type in element_types) for item in arg)
    return False

def joinLabels(leftLabels: list[str], rightLabels: list[str], joiner: str) -> list[str]:
    if not leftLabels:
        leftLabels=[]
    if not rightLabels:
        rightLabels=[]
    if len(leftLabels) == 0 and len(rightLabels) == 0:
        joinedLabels = []
    elif len(leftLabels) == 0:
        joinedLabels = [joiner + item for item in rightLabels]
    elif len(rightLabels) == 0:
        joinedLabels = leftLabels
    elif len(leftLabels) == 1:
        joinedLabels = [leftLabels[0] + joiner + item for item in rightLabels]
    elif len(rightLabels) == 1:
        joinedLabels = [item + joiner + rightLabels[0] for item in leftLabels]
    elif len(leftLabels) == len(rightLabels):
        joinedLabels = [leftItem + joiner + rightItem for leftItem, rightItem in zip(leftLabels, rightLabels)]
    else:
        raise AttributeError("Left and right operands need to have length 1 or be the same length!")
    return joinedLabels

def ensureList(data):
    if isinstance(data, list):
        return data  # If it's already a list, return as is
    elif isinstance(data,NoneType):
        return []
    else:
        return [data]  # Otherwise, wrap it in a list

def mergeNames(left:Union[DccQuantityType,float,int,ufloat], insertion:str, right:Union[DccQuantityType,float,int,ufloat]):
    """
    Merge two dictionaries of multi-language names.

    For each key in names1 that is also present in names2, the function
    concatenates the corresponding values from names1 and names2 with the
    insertion string in between.

    Args:
        left (DccQuantityType,float,int): Dictionary with Names keyed with language codes.
        insertion (str): str representation of the Operator like +,-,*,/
        names2 (DccQuantityType,float,int): Dictionary with Names keyed with language codes.

    Returns:
        dict: A new dictionary where each key from names1 that is also in names2 is mapped
              to the concatenated string "name1 + insertion + name2".
    """
    merged = {}
    try:
        namesLeft=left.name
        leftNamesNotGiven = False
    except:
        leftNamesNotGiven=True
    try:
        namesRight=right.name
        rightNamesNotGiven = False
    except:
        rightNamesNotGiven=True
    if rightNamesNotGiven or leftNamesNotGiven:
        if leftNamesNotGiven and rightNamesNotGiven:
            raise ValueError("Error in name generation neither left nor right operand had any names")
        if rightNamesNotGiven:
            namesRight={}
            for lang in namesLeft:
                # we will use str repr as name in all languages
                namesRight[lang]=str(right)
        if leftNamesNotGiven:
            namesLeft={}
            for lang in namesRight:
                # we will use str repr as name in all languages
                namesLeft[lang]=str(left)
    for lang, nameLeft in namesLeft.items():
        if lang in namesRight:  # Only merge if the language exists in names2
            merged[lang] = f"{nameLeft}{insertion}{namesRight[lang]}"
    return merged


def format_slice(index: slice) -> str:
    """
    Convert a slice object into a string of the form [start:stop] or [start:stop:step].
    """
    start = '' if index.start is None else index.start
    stop = '' if index.stop is None else index.stop
    step = '' if index.step is None else f":{index.step}"
    return f"[{start}:{stop}{step}]"


def assert_dicts_equal(dict1, dict2):
    added, removed, modified, same = dict_compare(dict1, dict2)
    assert not added, f"Added keys: {added}"
    assert not removed, f"Removed keys: {removed}"
    assert not modified, f"Modified keys: {modified}"

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {}

    # Remove 'uarray' from shared_keys if present.
    try:
        shared_keys.remove('uarray')
    except KeyError:
        pass

    for key in shared_keys:
        v1, v2 = d1[key], d2[key]

        # If both values are dictionaries, compare recursively.
        if isinstance(v1, dict) and isinstance(v2, dict):
            sub_added, sub_removed, sub_modified, sub_same = dict_compare(v1, v2)
            # Only record differences if there are any.
            if sub_added or sub_removed or sub_modified:
                modified[key] = {
                    'added': sub_added,
                    'removed': sub_removed,
                    'modified': sub_modified,
                    'same': sub_same
                }
        # If one is a dict and the other is not, mark as modified.
        elif isinstance(v1, dict) or isinstance(v2, dict):
            modified[key] = (v1, v2)
        # Use np.isclose if both are floats or numpy arrays.
        elif isinstance(v1, (float, np.ndarray)) and isinstance(v2, (float, np.ndarray)):
            # np.isclose returns an array; using .all() ensures a single Boolean.
            if not np.isclose(v1, v2, atol=np.finfo(float).eps, rtol=1e-14).all():
                modified[key] = (v1, v2)
        else:
            # Fallback for other types.
            try:
                if v1 != v2:
                    modified[key] = (v1, v2)
            except Exception:
                # If the comparison raises an exception, print debug info and mark as modified.
                print("DEBUG comparing key:", key)
    same = set(key for key in shared_keys if key not in modified)
    return added, removed, modified, same


def normalize_operator(op):
    """
    Normalizes operator strings to canonical uppercase forms.
    Supports both the comparison operators and the logical operators.
    """
    if isinstance(op, str):
        op = op.strip().upper()
        if op in {"AND", "&", "&&"}:
            return "AND"
        elif op in {"OR", "|", "||"}:
            return "OR"
        elif op in {"XOR", "^"}:
            return "XOR"
        elif op in {"==", "<", "<=", ">", ">=", "!="}:
            return op
    raise ValueError(f"Invalid operator: {op}")


def evaluate_query(query, index_vector):
    """
    Recursively evaluates a query expression against a 1D index_vector.

    A query can be:
      - None: meaning unconstrained (returns all indices).
      - A simple condition tuple like ('>', 10.0), which uses get_conditional_slice.
      - A nested expression like:
            [ subexpr, operator, subexpr, operator, subexpr, ... ]
        where subexpr can itself be nested.

    Returns a set of indices (as integers) that satisfy the query.
    """
    # Unconstrained: return all indices.
    if query is None:
        return set(range(len(index_vector)))

    # Check for a simple condition tuple.
    if isinstance(query, tuple) and len(query) == 2:
        op_str = str(query[0]).strip().upper()
        # Use only the comparison operators for simple condition tuples.
        if op_str in {"==", "<", "<=", ">", ">=", "!="}:
            s = get_conditional_slice(index_vector, query)
            # get_conditional_slice returns a slice covering from min to max matching index.
            return set(range(s.start, s.stop))

    # If the query is a list or tuple (and not a simple condition), assume nested expression.
    if isinstance(query, (list, tuple)):
        # If there's only one element, evaluate that element.
        if len(query) == 1:
            return evaluate_query(query[0], index_vector)
        # Expect the form: [expr, operator, expr, ...]
        result = evaluate_query(query[0], index_vector)
        i = 1
        while i < len(query):
            op = normalize_operator(query[i])
            next_expr = evaluate_query(query[i + 1], index_vector)
            if op == "AND":
                result = result.intersection(next_expr)
            elif op == "OR":
                result = result.union(next_expr)
            elif op == "XOR":
                result = result.symmetric_difference(next_expr)
            else:
                raise ValueError(f"Unsupported logical operator: {op}")
            i += 2
        return result

    raise TypeError("Query must be a tuple, list, or None.")

def get_conditional_slice(index_vector, condition):
    """
    Given a 1D index vector and a condition tuple (operator, value),
    returns a slice covering all indices that satisfy the condition.
    REQUIRES: index_vector to be sorted in ascending order.
    """
    arr = np.array(index_vector)
    op_str, q = condition
    ops = {
        '==': operator.eq,
        '<': operator.lt,
        '<=': operator.le,
        '>': operator.gt,
        '>=': operator.ge,
        '!=': operator.ne
    }
    if op_str not in ops:
        raise ValueError("Unsupported operator: " + op_str)
    op_func = ops[op_str]
    mask = op_func(arr, q)
    matching_indices = np.where(mask)[0]
    if matching_indices.size == 0:
        raise ValueError(f"No indices satisfy condition {op_str} {q}.")
    if matching_indices.size > 1:
        warnings.warn("Multiple matching indices found; returning slice covering all matches.")
    start = int(matching_indices.min())
    stop = int(matching_indices.max()) + 1
    return slice(start, stop)


def get_exact_slice(index_vector, *query):
    """
    For a given 1D index vector and one or more query float values,
    returns the index (or indices) that exactly match the query values.

    The returned value is either a single integer (if one match is found)
    or a NumPy array of integers for multiple matches, suitable for NumPy indexing.

    Example usage:
      get_exact_slice(index_vector, 3.0)
      get_exact_slice(index_vector, 3.0, 4.0)
      get_exact_slice(index_vector, [3.0, 4.0])
    """
    # If a single list/tuple/array is passed, unpack it.
    if len(query) == 1 and isinstance(query[0], (list, tuple, np.ndarray)):
        query = query[0]

    arr = np.array(index_vector)
    matching_indices = []
    for q in query:
        idx = np.where(arr == q)[0]
        if idx.size == 0:
            raise ValueError(f"No match found for query {q}.")
        matching_indices.extend(idx)  # Allow for multiple matches per query
    matching_indices = np.unique(matching_indices)
    if matching_indices.size == 1:
        return int(matching_indices[0])
    return ints_to_slice(matching_indices)


def get_nearest_slice(index_vector, *query, mode='absolute'):
    """
    Given a 1D index vector and one or more query float values, returns the index (or indices)
    corresponding to the nearest value(s) based on the specified mode.

    Modes:
      - 'lower': nearest index with value <= query.
      - 'higher': nearest index with value >= query.
      - 'absolute': index with the smallest absolute difference.

    The returned value is either a single integer (if one match is found)
    or a NumPy array of integers for multiple matches, suitable for NumPy indexing.

    Example usage:
      get_nearest_slice(index_vector, 5.0, mode='lower')
      get_nearest_slice(index_vector, 5.0, 10.0, mode='absolute')
      get_nearest_slice(index_vector, [5.0, 10.0], mode='higher')
    """
    # If a single list/tuple/array is passed, unpack it.
    if len(query) == 1 and isinstance(query[0], (list, tuple, np.ndarray)):
        query = query[0]

    arr = np.array(index_vector)
    all_indices = []
    for q in query:
        # Use exact match if available.
        exact_idx = np.where(arr == q)[0]
        if exact_idx.size > 0:
            all_indices.append(int(exact_idx[0]))
            continue

        if mode == 'lower':
            candidates = np.where(arr <= q)[0]
            if candidates.size == 0:
                raise ValueError(f"No index found lower than or equal to {q}.")
            all_indices.append(int(candidates.max()))
        elif mode == 'higher':
            candidates = np.where(arr >= q)[0]
            if candidates.size == 0:
                raise ValueError(f"No index found higher than or equal to {q}.")
            all_indices.append(int(candidates.min()))
        elif mode == 'absolute':
            diffs = np.abs(arr - q)
            min_diff = diffs.min()
            nearest = np.where(diffs == min_diff)[0]
            if nearest.size > 1:
                warnings.warn(f"Multiple indices equally near {q}; returning all matches.")
                all_indices.extend(nearest)
            else:
                all_indices.append(int(nearest[0]))
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    all_indices = np.unique(all_indices)
    if all_indices.size == 1:
        return int(all_indices[0])
    return ints_to_slice(all_indices)


def slice_AND(*args):
    """
    Returns the intersection (logical AND) of indices from given slices and iterables of ints.
    Any input that is either None or an unconstrained slice (slice(None)) is skipped.

    If a single operand (or a single iterable containing one operand) is passed,
    that operand is returned unchanged.

    Accepts either multiple arguments or a single iterable of such objects.
    """
    # Normalize inputs: if a single iterable is provided (but not a slice/int/None), unpack it.
    if len(args) == 1 and not isinstance(args[0], (slice, int, type(None))) and hasattr(args[0], '__iter__'):
        items = list(args[0])
    else:
        items = list(args)

    # If there's only one operand, return it unchanged.
    if len(items) == 1:
        return items[0]

    constraining_sets = []
    for item in items:
        # Skip unconstrained inputs.
        if item is None:
            continue
        if isinstance(item, int):
            constraining_sets.append({item})
        elif isinstance(item, slice):
            # Skip unconstrained slice.
            if item.start is None and item.stop is None and item.step is None:
                continue
            if item.stop is None:
                raise ValueError("Slice stop cannot be None for finite range calculation (unless it's slice(None)).")
            start = item.start if item.start is not None else 0
            step = item.step if item.step is not None else 1
            constraining_sets.append(set(range(start, item.stop, step)))
        else:
            try:
                constraining_sets.append(set(int(x) for x in item))
            except Exception as e:
                raise TypeError("Invalid input. Expected a slice, None, or an iterable of integers.") from e

    if not constraining_sets:
        raise ValueError(
            "At least one constraining input is required; all inputs were unconstrained (None or slice(None))."
        )

    common = constraining_sets[0]
    for s in constraining_sets[1:]:
        common = common.intersection(s)
    return sorted(common)


def slice_OR(*args):
    """
    Returns the union (logical OR) of indices from given slices and iterables.
    Any unconstrained input (None or slice(None)) is skipped.

    If a single operand (or a single iterable containing one operand) is passed,
    that operand is returned unchanged.
    """
    if len(args) == 1 and not isinstance(args[0], (slice, int, type(None))) and hasattr(args[0], '__iter__'):
        items = list(args[0])
    else:
        items = list(args)

    if len(items) == 1:
        return items[0]

    union_set = set()
    for item in items:
        if item is None:
            continue
        if isinstance(item, int):
            union_set.add(item)
        elif isinstance(item, slice):
            if item.start is None and item.stop is None and item.step is None:
                continue
            if item.stop is None:
                raise ValueError("Slice stop cannot be None for finite range calculation (unless it's slice(None)).")
            start = item.start if item.start is not None else 0
            step = item.step if item.step is not None else 1
            union_set = union_set.union(set(range(start, item.stop, step)))
        else:
            try:
                union_set = union_set.union(set(int(x) for x in item))
            except Exception as e:
                raise TypeError("Invalid input for slice_OR. Expected a slice, None, or an iterable of integers.") from e
    if not union_set:
        raise ValueError("At least one constraining input is required; all inputs were unconstrained.")
    return sorted(union_set)


def slice_XOR(*args):
    """
    Returns the symmetric difference (logical XOR) of indices from given slices and iterables.
    For more than two inputs, the operation is applied sequentially.

    If a single operand (or a single iterable containing one operand) is passed,
    that operand is returned unchanged.
    """
    if len(args) == 1 and not isinstance(args[0], (slice, int, type(None))) and hasattr(args[0], '__iter__'):
        items = list(args[0])
    else:
        items = list(args)

    if len(items) == 1:
        return items[0]

    xor_set = None
    for item in items:
        if item is None:
            continue
        if isinstance(item, int):
            current_set = {item}
        elif isinstance(item, slice):
            if item.start is None and item.stop is None and item.step is None:
                continue
            if item.stop is None:
                raise ValueError("Slice stop cannot be None for finite range calculation (unless it's slice(None)).")
            start = item.start if item.start is not None else 0
            step = item.step if item.step is not None else 1
            current_set = set(range(start, item.stop, step))
        else:
            try:
                current_set = set(int(x) for x in item)
            except Exception as e:
                raise TypeError("Invalid input for slice_XOR. Expected a slice, None, or an iterable of integers.") from e

        if xor_set is None:
            xor_set = current_set
        else:
            xor_set = xor_set.symmetric_difference(current_set)
    if xor_set is None or not xor_set:
        raise ValueError("At least one constraining input is required; all inputs were unconstrained.")
    return sorted(xor_set)


def ints_to_slice(int_list):
    """
    Convert a list of integers to a slice if they form an arithmetic progression.

    Parameters:
        int_list (list of int): A non-empty list or array of integers.

    Returns:
        slice: A slice object representing the arithmetic progression,
               if possible.
        None: If the integers are not uniformly spaced.

    Example:
        ints_to_slice([2, 3, 4, 5]) -> slice(2, 6, 1)
        ints_to_slice([2, 4, 6, 8]) -> slice(2, 10, 2)
        ints_to_slice([2, 4, 7]) -> None
    """
    if isinstance(int_list, slice):
        return int_list
    if len(int_list)==0:
        raise ValueError("Empty list cannot be converted to a slice.")

    # With one element, return a slice that selects just that element.
    if len(int_list) == 1:
        return slice(int_list[0], int_list[0] + 1, 1)

    # Determine the expected step.
    step = int_list[1] - int_list[0]
    for i in range(2, len(int_list)):
        if int_list[i] - int_list[i - 1] != step:
            warnings.warn("Step width is not uniform slice conversion faild.",RuntimeWarning)
            return int_list  # Not uniformly spaced.

    # The stop value for a slice is non-inclusive, so add step to the last element.
    return slice(int_list[0], int_list[-1] + step, step)
# --- Recursive Query Evaluation ---


get_valsFromUFloatArrays = np.vectorize(lambda x: x.value)
get_uncerFromUFloatArrays = np.vectorize(lambda x: x.stdunc)

def get_system_language() -> str:
    """Detects the system language for Windows, Linux, and macOS."""
    try:
        system_lang = locale.getdefaultlocale()[0]  # Example: 'en_US'
        if system_lang:
            return system_lang.split('_')[0]  # Extract 'en' from 'en_US'
    except:
        pass

    if sys.platform == "win32":
        import ctypes
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return locale.windows_locale.get(lang_id, "en").split('_')[0]

    return "en"  # Default fallback


class DccConfiguration:
    _instance = None

    class CoveragePropabilityMissmatchBehavior(Enum):
        EXCEPTION = 1
        WARNING_TAKE_K_VALUE = 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DccConfiguration, cls).__new__(cls)

            # Global configuration singleton for language preferences.
            cls.systemLang = get_system_language()
            cls.preferredLangs = [get_system_language(), "en", "de"]
            cls.reprStyle = "normal"  # Can be "libDebug" or "normal"
            # For all math operations k=1 is always used to ensure consistency.
            cls.defaultSerialisatKFactor = 2  # if k>1, expanded MeasurementUncertanty (si:expandedMU) is serialized if 1 standard MeasurementUncertanty is used (si:standardMU)
            cls.allowedCoveragePropabilityMissmatch = {'normal': 0.01, 'uniform': 0.03, 'default': 0.03}
            # Set the default behavior using the enum.
            cls.coveragePropabilityMissmatchBehaivior = DccConfiguration.CoveragePropabilityMissmatchBehavior.WARNING_TAKE_K_VALUE
            cls.storeOriginalUncerForNonIntK = True
        return cls._instance

dccConfiguration = DccConfiguration()







