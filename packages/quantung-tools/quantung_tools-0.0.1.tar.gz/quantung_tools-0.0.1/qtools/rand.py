from random import randint, choice, random
from values import strtype

def Bool(nonetype=False):
    if nonetype:
        n = randint(0,2)
        if n == 0:
            return None
        elif n == 1:
            return False
    elif randint(1, 2) == 1:
        return False
    return True

def Element(data):
    if isinstance(data, list) or isinstance(data, set):
        return choice(list(data))
    elif isinstance(data, dict):
        return choice(list(data.values()))
    else:
        raise TypeError(f"Funcion randomElement request list, set or dictionary not {strtype(data)}. Your argument have bad type!")

def Elements(data, lenght: int):
    newlist = []
    for i in range(lenght):
        newlist.append(Element(data))
    return newlist

def Digit():
    return randint(0, 9)

def String(allowed: list, lenght: int):
    size = len(allowed)-1
    string = ""
    for i in range(lenght):
        string += str(allowed[randint(0, size)])
    return string

def chance():
    return random(123)*100
