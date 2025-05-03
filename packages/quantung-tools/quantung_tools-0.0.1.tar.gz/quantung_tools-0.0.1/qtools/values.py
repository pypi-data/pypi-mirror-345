digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
letters_uppercase = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
letters_lowercase =['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'w', 'x', 'y', 'z']

def strtype(variable, long=False):
    if isinstance(variable, int):
        if long:
            return "interger"
        return "int"
    elif isinstance(variable, float):
        return "float"
    elif isinstance(variable, str):
        if long:
            return "string"
        return "str"
    elif isinstance(variable, bool):
        return "bool"
    elif isinstance(variable, list):
        return "list"
    elif isinstance(variable, tuple):
        return "tuple"
    elif isinstance(variable, dict):
        if long:
            return "dictionary"
        return "dict"
    elif isinstance(variable, set):
        return "set"
    elif hasattr(variable, '__class__'):
        return variable.__class__.__name__
    else:
        return "Unknown type"

def liststrings(data: list, ignor_error=False):
    newlist = []
    for e in data:
        try:
            newlist.append(str(e))
        except:
            if ignor_error:
                newlist.append(e)
            else:
                error = f"Object {e} in list isn't string and cannot be converted into string. Object type is \'{strtype(e)}\'." \
                        f"\n Add to this object class convertion into sting or set ignore_error for not change this object."
                raise ValueError(error)
    return newlist


def onlytypelist(oldlist: list, objtype: type, tryconvert=False):
    newlist = []
    for e in oldlist:
        if type(e) == objtype:
            newlist.append(e)
        elif tryconvert:
            try:
                newlist.append(objtype(e))
            except:
                pass
    return newlist

def removetypelist(oldlist: list, objtype: type, tryconvert=False):
    newlist = []
    for e in oldlist:
        if type(e) != objtype:
            newlist.append(e)
        elif tryconvert:
            try:
                newlist.append(objtype(e))
            except:
                pass
    return newlist