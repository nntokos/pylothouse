import os
import subprocess


def load_column_from_file(path:str, column:int=0, from_number=None, to_number=None, delimiter:str= ',', comment_indicator:str= '#', has_header=False, out_type:str= 'float', unique_values:bool=False,
                          skip_rows=None):
    """
    Load a column from a file and return a list of numbers
    :param path: str: path to the file
    :param column: int: column number to load (0-indexed)
    :param from_number: float: minimum value to load. None means no minimum (All values). (Default: None)
    :param to_number: float: maximum value to load. None means no maximum (All values). (Default: None)
    :param delimiter: str: delimiter to split the line. (Default: ',')
    :param comment_indicator: str: character that indicates a comment line. (Default: '#')
    :param has_header: bool: whether the file has a header. (Default: False)
    :param out_type: str: output type. Either 'int' or 'float'. (Default: 'float')
    :param unique_values: bool: whether to return only unique values. (Default: False)
    :return: list: list of numbers
    """

    if skip_rows is None:
        skip_rows = []
    if out_type not in ['int', 'float']:
        raise ValueError('out_type must be either "int" or "float"')
    path_extension = path.split('.')[-1]
    if not path_extension in ['csv', 'txt', 'tsv', 'tum']:
        print('File extension not supported')
        return None
    if to_number == None:
        to_number = float('inf')
    if from_number == None:
        from_number = float('-inf')
    
    _numbers = []

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if has_header and not lines[i].strip().split(delimiter)[0].startswith(comment_indicator):
                    has_header = False
                    continue
                if i in skip_rows:
                    continue
                if lines[i]:
                    line = lines[i].strip().split(delimiter)
                    if line[0].startswith(comment_indicator):
                        continue
                    number = float(line[column].strip())
                    if from_number <= number <= to_number:
                        if unique_values and number not in _numbers:
                            _numbers.append(number)
                        else:
                            _numbers.append(number)

    except FileNotFoundError as e:
        print(path, e)
        return e
    except ValueError as e:
        print(f"Error converting to float: {e}")

    if out_type == 'int':
        _numbers = [int(number) for number in _numbers]
    return _numbers


def swap_columns(file_path: str, column1: int, column2: int, delimiter: str = ',', output_file: str = None, swap_title: bool = False):
    """
    Swap the values of two columns in a file.
    Parameters:
    -----------
    file_path : str
        The path to the file.
    column1 : int
        The column number of the first column.
    column2 : int
        The column number of the second column.
    delimiter : str
        The delimiter used in the file. Default is ','.
    output_file : str
        The path to the output file. Default is the input (None).
    swap_title : bool
        Whether to swap the column titles. Default is False.
    """
    column1 = column1 - 1
    column2 = column2 - 1
    if column1 == column2:
        print("Columns are the same")
        return
    if column1 < 0 or column2 < 0:
        raise ValueError("Column numbers must be greater than 0")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if output_file is None:
            output_file = file_path
        
        swapped_lines = []
        for i, line in enumerate(lines):
            values = line.strip().split(delimiter)
            if i == 0 and swap_title:
                values[column1], values[column2] = values[column2], values[column1]
            elif i != 0:
                values[column1], values[column2] = values[column2], values[column1]
            swapped_lines.append(delimiter.join(values) + '\n')
    except Exception as e:
        print(f"Error swapping columns: {e}")
        return
    
    with open(output_file, 'w') as f:
        f.writelines(swapped_lines)

def multiply_factor_to_column(file_path: str, column: int, factor: float, delimiter: str = ',', output_file: str = None, has_header: bool = False):
    """
    Multiply all values in a column by a factor.
    Parameters:
    -----------
    file_path : str
        The path to the file.
    column : int
        The column number to multiply.
    factor : float
        The factor to multiply the values by.
    delimiter : str
        The delimiter used in the file. Default is ','.
    output_file : str
        The path to the output file. Default is the input (None).
    has_header : bool
        Whether the file has a header. Default is False.
    """
    column = column - 1
    if column < 0:
        raise ValueError("Column number must be greater than 0.")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if output_file is None:
            output_file = file_path
        
        multiplied_lines = []
        for i, line in enumerate(lines):
            values = line.strip().split(delimiter)
            if i == 0 and has_header:
                multiplied_lines.append(line)
            else:
                try:
                    values[column] = str(float(values[column]) * factor)
                except ValueError:
                    print(f"Value in column {column + 1} is not a float: {values[column]}")
                    continue
                multiplied_lines.append(delimiter.join(values) + '\n')
    except Exception as e:
        print(f"Error multiplying column: {e}")
        return
    
    with open(output_file, 'w') as f:
        f.writelines(multiplied_lines)

def add_constant_to_column(file_path: str, column: int, constant: float, delimiter: str = ',', output_file: str = None, has_header: bool = False):
    """
    Add a constant to all values in a column.
    Parameters:
    -----------
    file_path : str
        The path to the file.
    column : int
        The column number to add the constant to.
    constant : float
        The constant to add to the values.
    delimiter : str
        The delimiter used in the file. Default is ','.
    output_file : str
        The path to the output file. Default is the input (None).
    has_header : bool
        Whether the file has a header. Default is False.
    """
    column = column - 1
    if column < 0:
        raise ValueError("Column number must be greater than 0.")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if output_file is None:
            output_file = file_path
        
        added_lines = []
        for i, line in enumerate(lines):
            values = line.strip().split(delimiter)
            if i == 0 and has_header:
                added_lines.append(line)
            else:
                try:
                    values[column] = str(float(values[column]) + constant)
                except ValueError:
                    print(f"Value in column {column + 1} is not a float or int: {values[column]}")
                    continue
                added_lines.append(delimiter.join(values) + '\n')
    except Exception as e:
        print(f"Error adding constant to column: {e}")
        return
    
    with open(output_file, 'w') as f:
        f.writelines(added_lines)

def add_constants_to_column(file_path: str, column: int, constants: list, delimiter: str = ',', output_file: str = None, has_header: bool = False):
    """
    Add constants to all values in a column.
    Parameters:
    -----------
    file_path : str
        The path to the file.
    column : int
        The column number to add the constants to.
    constants : list
        The list of constants to add to the values.
    delimiter : str
        The delimiter used in the file. Default is ','.
    output_file : str
        The path to the output file. Default is the input (None).
    has_header : bool
        Whether the file has a header. Default is False.
    """
    column = column - 1
    if column < 0:
        raise ValueError("Column number must be greater than 0.")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if output_file is None:
            output_file = file_path

        added_lines = []
        for i, line in enumerate(lines):
            values = line.strip().split(delimiter)
            if i == 0 and has_header:
                added_lines.append(line)
            else:
                try:
                    values[column] = str(float(values[column]) + constants[i - 1])
                except ValueError:
                    print(f"Value in column {column + 1} is not a float or int: {values[column]}")
                    continue
                added_lines.append(delimiter.join(values) + '\n')
    except Exception as e:
        print(f"Error adding constants to column: {e}")
        return
    
    with open(output_file, 'w') as f:
        f.writelines(added_lines)

def round_numbers_in_column(file_path: str, column: int, decimals: int, delimiter: str = ',', output_file: str = None, has_header: bool = False):
    """
    Round all values in a column to a specific number of decimal places.
    Parameters:
    -----------
    file_path : str
        The path to the file.
    column : int
        The column number to round the values. 
    decimals : int
        The number of decimal places to round the values to.
    delimiter : str
        The delimiter used in the file. Default is ','.
    output_file : str
        The path to the output file. Default is the input (None).
    has_header : bool
        Whether the file has a header. Default is False.
    """
    column = column - 1
    if column < 0:
        raise ValueError("Column number must be greater than 0.")
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if output_file is None:
            output_file = file_path
        
        rounded_lines = []
        for i, line in enumerate(lines):
            values = line.strip().split(delimiter)
            if i == 0 and has_header:
                rounded_lines.append(line)
            else:
                try:
                    values[column] = str(round(float(values[column]), decimals))
                except ValueError:
                    print(f"Value in column {column + 1} is not a float or int: {values[column]}")
                    continue
                rounded_lines.append(delimiter.join(values) + '\n')
    except Exception as e:
        print(f"Error rounding column: {e}")
        return
    
    with open(output_file, 'w') as f:
        f.writelines(rounded_lines)

def get_file_length(file_path: str):
    result = subprocess.run(['wc', '-l', file_path], stdout=subprocess.PIPE, text=True)
    return int(result.stdout.split()[0])

def binary_search(file_path: str, target: float, column: int = 0, delimiter: str = ','):
    """
    Perform a binary search on a sorted file and return the line number of the target value.
    Parameters:
    -----------
    file_path : str
        The path to the sorted file.
    target : int
        The target value to search for.
    column : int
        The column number to search for the target value. Default is 0.
    delimiter : str
        The delimiter used in the file. Default is ','.
    Returns:
    --------
    int
        The line number of the target value. Returns -1 if the target value is not found.
    """
    low = 0
    high = get_file_length(file_path) - 1
    with open(file_path, 'r') as f:
        lines = f.readlines()
        while low <= high:
            mid = (low + high) // 2
            value = float(lines[mid].strip().split(delimiter)[column])
            if value == target:
                return mid
            elif value < target:
                low = mid + 1
            else:
                high = mid - 1
    return -1

def binary_position(file_path: str, target: float, column: int = 0, delimiter: str = ','):
    """
    Perform a binary search on a sorted file and return the position of the target value.
    Parameters:
    -----------
    file_path : str
        The path to the sorted file.
    target : int
        The target value to search for.
    column : int
        The column number to search for the target value. Default is 0.
    delimiter : str
        The delimiter used in the file. Default is ','.
    Returns:
    --------
    int
        The position of the target value. Returns -1 if the target value is not found.
    """
    low = 0
    high = get_file_length(file_path) - 1
    with open(file_path, 'r') as f:
        lines = f.readlines()
        while low <= high:
            mid = (low + high) // 2
            value = float(lines[mid].strip().split(delimiter)[column])
            if value == target:
                return mid
            elif value < target:
                low = mid + 1
            else:
                high = mid - 1
    return low


def validate_output_dir(directory):
    """
    Validate the output/export directory and return the absolute path.
    Parameters:
    -----------
    directory : str
        The directory path to validate.
    Returns:
    --------
    str
        The absolute path of the directory.
    Raises:
    -------
    ValueError
        If the directory is the root directory, a symbolic link, or if it cannot be created.
    PermissionError
        If the directory does not have write permissions.

    """
    # Check if the directory is the root directory
    if os.path.abspath(directory) == '/':
        raise ValueError("Output directory cannot be the root directory ('/').")

    # Check if the directory exists
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Failed to create directory {directory}: {e}")

    # Check for write permissions
    if not os.access(directory, os.W_OK):
        raise PermissionError(f"No write permissions for the directory: {directory}")

    # Check if the directory is a symbolic link
    if os.path.islink(directory):
        raise ValueError("Output directory cannot be a symbolic link.")

    return os.path.realpath(directory)