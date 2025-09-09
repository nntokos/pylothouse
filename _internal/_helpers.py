def _read_file_column(file_path, column=0, delimiter=',', header_marker="#"):
    """
    Reads the data from the input file. The data is read from the specified column.
    \nA header is allowed if it starts with a specified header_marker.
    :param file_path: Input file path.
    :param column: Column number to read the data from. The number starts at 0. (Default: 0)
    :param delimiter: Delimiter to split the data. (Default: ',')
    :param header_marker: Marker to identify the header. (Default: '#')
    :return: Returns the data as a list
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            if line.startswith(header_marker):
                continue
            data.append(float(line.strip().split(delimiter)[column]))
    return data


def func_str(func, str):
    """
    Returns the function name and the string.
    :param func: Function name
    :param str: String
    :return: Returns the formatted string
    """
    return f"{func.__name__}({str})"


import functools


def func_name_print_prefix_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Define a custom print function that prefixes output with the function name
        def custom_print(*print_args, **print_kwargs):
            # Prepend the function name to the print arguments
            prefixed_args = (f"{func.__name__}: {print_args[0]}",) + print_args[1:]
            print(*prefixed_args, **print_kwargs)

        # Temporarily override the built-in print function in the wrapper's scope
        built_in_print = print
        globals()['print'] = custom_print
        try:
            # Execute the original function
            result = func(*args, **kwargs)
        finally:
            # Restore the original print function
            globals()['print'] = built_in_print
        return result

    return wrapper

def timestamp():
    """
    Returns the current timestamp.
    :return: Returns the current timestamp
    """
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d%H%M%S")