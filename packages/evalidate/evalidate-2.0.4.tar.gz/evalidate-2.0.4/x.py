import evalidate

def eval_expression(input_string):
    # Step 1
    allowed_names = {"sum": sum, "int": int, "a":1, "b":2, 'startswith': str.startswith}
    # Step 2
    code = compile(input_string, "<string>", "eval")
    # Step 3
    print(code.co_names)
    for name in code.co_names:
        if name not in allowed_names:
            # Step 4
            raise NameError(f"Use of {name!r} not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names)

try:
    src="""
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,0,0,b"BOOM",(),(),(),"","",0,b""
        ),{}
    )()
)()
"""


    #src = "'asdf'.startswith('as')"
    #src2 ="""__builtins__['eval']("print(1)")""" 

    #node = evalidate.evalidate(src, 
    #    addnodes=['Call', 'Attribute', 'ListComp', 'comprehension', 'Store'], 
    #    attrs=['startswith'])
    #code = compile(node, '<test>', 'eval')
    #r = eval(code)
    #print("eval:", r)

    r = eval_expression(src)
    print(r)
except Exception as e:
    print(e)