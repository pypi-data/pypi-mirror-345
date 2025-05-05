from decimal import Decimal, Inexact, Context
from datetime import datetime, tzinfo
import re
import inspect
import numpy as np
from dateutil.parser import parse, isoparse
import pytz

date_regex = re.compile(r'^((-?[0-9]{4}|-)(-(1[0-2]|0[1-9]|-)(-(3[01]|0[1-9]|[12][0-9]|-)(T(2[0-3]|[01][0-9]|-)(:([0-5][0-9]|-)((:([0-5][0-9]|-))?(\.[0-9]+)?((Z|[+-](:2[0-3]|[01][0-9]):[0-5][0-9]))?)?)?)?)?)?)(\/((-?[0-9]{4}|-)(-(1[0-2]|0[1-9]|-)(-(3[01]|0[1-9]|[12][0-9]|-)(T(2[0-3]|[01][0-9]|-)(:([0-5][0-9]|-)((:([0-5][0-9]|-))?(\.[0-9]+)?((Z|[+-](:2[0-3]|[01][0-9]):[0-5][0-9]))?)?)?)?)?)?))?$')

def fn_name_to_pretty_label(name):
    return ' '.join([w.title() for w in name.split('_')])

def export_rule_data(variables, actions):
    """ export_rule_data is used to export all information about the
    variables, actions, and operators to the client. This will return a
    dictionary with three keys:
    - variables: a list of all available variables along with their label, type and options
    - actions: a list of all actions along with their label and params
    - variable_type_operators: a dictionary of all field_types -> list of available operators
    """
    from . import operators
    actions_data = actions.get_all_actions()
    variables_data = variables.get_all_variables()
    variable_type_operators = {}
    for variable_class in inspect.getmembers(operators, lambda x: getattr(x, 'export_in_rule_data', False)):
        variable_type = variable_class[1] # getmembers returns (name, value)
        variable_type_operators[variable_type.name] = variable_type.get_all_operators()

    return {"variables": variables_data,
            "actions": actions_data,
            "variable_type_operators": variable_type_operators}

def float_to_decimal(f):
    """
    Convert a floating point number to a Decimal with
    no loss of information. Intended for Python 2.6 where
    casting float to Decimal does not work.
    """
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result

def is_valid_date(date_string: str) -> bool:
    if date_string is None:
        return False
    try:
        isoparse(date_string)
    except:
        uncertainty_substrings = ["/", "--", "-:"]
        if any([substr in date_string for substr in uncertainty_substrings]):
            # date_string contains uncertainty
            # will not parse with isoparse
            return date_regex.match(date_string) is not None
        else:
            return False
    return date_regex.match(date_string) is not None

def is_valid_duration(duration: str, negative) -> bool:
    if not isinstance(duration, str):
        duration = str(duration)
    if negative:
        pattern = r'^[-]?P(?!$)(?:(?:(\d+(?:[.,]\d*)?Y)?[,]?(\d+(?:[.,]\d*)?M)?[,]?(\d+(?:[.,]\d*)?D)?[,]?(T(?=\d)(?:(\d+(?:[.,]\d*)?H)?[,]?(\d+(?:[.,]\d*)?M)?[,]?(\d+(?:[.,]\d*)?S)?)?)?)|(\d+(?:[.,]\d*)?W))$'
    else:
        pattern = r'^P(?!$)(?:(?:(\d+(?:[.,]\d*)?Y)?[,]?(\d+(?:[.,]\d*)?M)?[,]?(\d+(?:[.,]\d*)?D)?[,]?(T(?=\d)(?:(\d+(?:[.,]\d*)?H)?[,]?(\d+(?:[.,]\d*)?M)?[,]?(\d+(?:[.,]\d*)?S)?)?)?)|(\d+(?:[.,]\d*)?W))$'
    match = re.match(pattern, duration)
    if not match:
        return False

    years, months, days, time_designator, hours, minutes, seconds, weeks = match.groups()

    if time_designator and not any([hours, minutes, seconds]):
        return False

    components = [c for c in [years, months, weeks, days, hours, minutes, seconds] if c is not None]

    # Check if decimal is only in the smallest unit
    decimal_found = False
    for i, component in enumerate(components):
        if '.' in component or ',' in component:
            if decimal_found or i != len(components) - 1:
                return False
            decimal_found = True

    return True

def get_year(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.year

def get_month(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.month

def get_day(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.day

def get_hour(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.hour

def get_minute(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.minute

def get_second(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.second

def get_microsecond(date_string: str):
    timestamp = get_date(date_string)
    return timestamp.microsecond

def get_date_component(component: str, date_string: str):
    component_func_map = {
        "year": get_year,
        "month": get_month,
        "day": get_day,
        "hour": get_hour,
        "minute": get_minute,
        "microsecond": get_microsecond,
        "second": get_second
    }
    component_function = component_func_map.get(component)
    if component_function:
        return component_function(date_string)
    else:
        return get_date(date_string)

def get_date(date_string: str):
    """
    Returns a utc timestamp for comparison
    """
    date = parse(date_string)
    utc = pytz.UTC
    if date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None:
        # timezone aware
        return date.astimezone(utc)
    else:
        return utc.localize(date)

def is_complete_date(date_string: str) -> bool:
    try:
        datetime.fromisoformat(date_string)
    except:
        try:
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True

def get_dict_key_val(dict_to_get: dict, key):
    return dict_to_get.get(key)

def is_in(value, values):
    if values is None:
        return False
    return value in values

def case_insensitive_is_in(value, values):
    return str(value).lower() in str(values).lower()

def compare_dates(component, target, comparator, operator):
    if not target or not comparator:
        # Comparison should return false if either is empty or None
        return False
    else:
        return operator(get_date_component(component, target), get_date_component(component, comparator))

def apply_regex(regex: str, val: str):
    result = re.findall(regex, val)
    if result:
        return result[0]
    else:
        return None
def flatten_list(data, l):
   for item in l:
       if isinstance(item, list):
           yield from flatten_list(data, item)
       elif item in data and isinstance(data[item].iloc[0], list):
           for val in data[item].iloc[0]:
               yield val
       else:
           yield item

vectorized_apply_regex = np.vectorize(apply_regex)
vectorized_is_complete_date = np.vectorize(is_complete_date)
vectorized_compare_dates = np.vectorize(compare_dates)
vectorized_is_valid = np.vectorize(is_valid_date)
vectorized_is_valid_duration = np.vectorize(is_valid_duration)
vectorized_get_dict_key = np.vectorize(get_dict_key_val)
vectorized_is_in = np.vectorize(is_in)
vectorized_case_insensitive_is_in = np.vectorize(case_insensitive_is_in)
vectorized_len = np.vectorize(len)
