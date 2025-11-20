from ..common import Action, istype

def function_stringifier(
    func: Action,
    *args,
    **kwargs
) -> str:
    func_name = str(func).split()[1]
    
    args = [
        f"\"{arg}\""
        if isinstance(arg, str)
        else arg
        for arg
        in args
    ] + [
        v
        for k,v
        in kwargs.items()
        if k[0] != '_'
        and not istype(v, 'State')
    ]

    func_string = f"{func_name}" + (
        f"({', '.join(str(arg) for arg in args)})"
        if args is not None
        and args != ['\"\"']
        else ''
    )
    
    return func_string
