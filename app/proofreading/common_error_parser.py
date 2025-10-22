from typing import Callable

from utils.constants import COMERRDICT, ABBVDICT, EN2AMDICT

def consume_dict(
    input: str,
    logic_func: Callable[..., str],
    *args
) -> tuple[str, bool]:
    output = logic_func(input, *args)
    check = input != output
    return (output if check else input, check)

def comerrdict_func(input: str) -> str:
    for k, v in COMERRDICT.items():
        output = input.replace(k, v)
        if not (output == input):
            return output
    return input

def abbvdict_func(input: str) -> str:
    for k, v in ABBVDICT.items():
        output = input.replace(k, v)
        if not (output == input):
            return output
        else:
            output = input.replace(k.replace('.',''), v)
            if not (output == input):
                return output
    return input
    
def en2amdict_func(input: str, convert_english: bool = True) -> str:
    if convert_english:
        conversionDict = EN2AMDICT
    else:
        conversionDict = dict((v,k) for k,v in EN2AMDICT.items())

    for k,v in conversionDict.items():
        output = input.replace(k, v)
        if not (output == input):
            return output
    return input

def number_fixer(input: str) -> str | None:
    try:
        number = int(input.replace(' ',''))
    except ValueError:
        return None
    else:
        if len(str(number)) >= 5:
            return f"{number:,}"
        else:
            raise Exception("input number too short") 

def common_error_parser(input: str, convert_english) -> str | None:
    # check if the input is a number and add comma if necessary
    # raises error if the number is fewer than 5 digits
    if (number := number_fixer(input)) is not None:
        return number
    
    # check for word capitalization before normalizing word
    capitalized = input[0].isupper()
    input = input.lower()

    # check through possible common error, allowing for early exiting
    flag = False
    output = input
    dictList = [
        (comerrdict_func, []),
        (abbvdict_func, []),
        (en2amdict_func, [convert_english])
    ]
    for func, args in dictList:
        output, flag = consume_dict(input, func, *args)
        if flag is True:
            break

    # if nothing changes, raise an error
    if output == input:
        raise Exception(f"no match found for \"{input}\"")

    # capitalize if necessary
    if capitalized is True:
        output = output[0].upper() + output[1:]

    return output
