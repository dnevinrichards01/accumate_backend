import types
from queue import Queue

def filter_jsons(jsons, eq={}, gt={}, lt={}, lte={}, gte={}, metric_to_return_by=None,
                 **kwargs):
    import pdb
    breakpoint()

    filter_sets = [eq, gt, lt, lte, gte]
    operations = ["eq", "gt", "lt", "lte", "gte"]
    for kwarg in kwargs:
        filter = kwargs[kwarg]
        if isinstance(filter, dict) and \
            "func" in filter and isinstance(filter["func"], types.FunctionType) and \
            "filter_set" in filter and isinstance(filter["filter_set"], dict) and \
            all((isinstance(key, str) for key in filter["filter_set"].keys())) and \
            all((isinstance(val, list) for val in filter["filter_set"].values())):
            operations.append(filter["func"])
            filter_sets.append(filter["filter_set"])
        else:
            return {"error": "kwargs must each be a dict with a function 'func' " + \
                    "and a 'filter_set' of same format as eq, lt, etc"}

    if metric_to_return_by:
        filtered_jsons = {}
    else:
        filtered_jsons = []
    
    for json in jsons:
        match = True
        for filter_set, op in zip(filter_sets, operations):
            for metric in filter_set:
                filter_vals = filter_set[metric]
                try:
                    metric_val = get_nested(json, metric)
                except Exception as e:
                    return {"error": f"key {metric} not found: {str(e)}"}
                for filter_val in filter_vals:
                    try:
                        if not comparison_operation(metric_val, filter_val, op):
                            match = False
                            break
                    except Exception as e:
                        return {"error": f"comparison operation failed: {str(e)}"}
                if not match:
                    break
            if not match:
                break
        
        if match:
            try:
                append_json_to_filter_jsons(metric_to_return_by, filtered_jsons, json)
            except Exception as e:
                return {"error": f"couldn't append json to results: {str(e)}"}

    return filtered_jsons

def append_json_to_filter_jsons(metric_to_return_by, filtered_jsons, json):
    if metric_to_return_by:
        try:
            key = get_nested(json, metric_to_return_by)
            if key in filtered_jsons:
                filtered_jsons[key].append(json)
            else:
                filtered_jsons[key] = [json]
        except Exception as e:
            return {"error": f"key {metric_to_return_by} not found: {str(e)}"}
    else:
        filtered_jsons.append(json)

def comparison_operation(arg1, arg2, op):        
    if op == "eq":
        return arg1 == arg2
    elif op == "gt":
        return arg1 > arg2
    elif op == "lt":
        return arg1 < arg2
    elif op == "lte":
        return arg1 <= arg2
    elif op == "gte":
        return arg1 >= arg2
    elif isinstance(op, types.FunctionType):
        try:
            return op(arg1, arg2)
        except Exception as e:
            raise Exception(f"function {op} failed: {str(e)}")
    else:
        raise Exception(f"no such operation: {op}")

def get_nested(json, key):
    queue = Queue()
    queue.put(json)
    while queue.qsize() > 0:
        current = queue.get()
        for key_ in current:
            if key_ == key:
                return current[key]
            if isinstance(current[key_], dict):
                queue.put(current[key_])
    raise Exception(f"{key} not found")
