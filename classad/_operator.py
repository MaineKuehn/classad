def isnt_operator(a, b):
    result = a.__htc_isnt__(b)
    if result == NotImplemented:
        result = b.__htc_isnt__(a)
    return result


def is_operator(a, b):
    result = a.__htc_is__(b)
    if result == NotImplemented:
        result = b.__htc_is__(a)
    return result


def eq_operator(a, b):
    result = a.__htc_eq__(b)
    if result == NotImplemented:
        result = b.__htc_eq__(a)
    return result


def ne_operator(a, b):
    result = a.__htc_ne__(b)
    if result == NotImplemented:
        result = b.__htc_ne__(a)
    return result


def not_operator(a):
    return a.__htc_not__()
