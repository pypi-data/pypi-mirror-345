from evalidate import Expr, base_eval_model, ExecutionException
import sys

my_model = base_eval_model.clone()
my_model.nodes.extend(
    [
        "Call",
        "Attributes",
        "ListComp",
        "DictComp",
        "comprehension",
        "Store",
        "ForOfStatement",
        "Subscript",
        "GeneratorExp",
        "For",
    ]
)
my_model.allowed_functions.append("sum")
my_model.allowed_functions.append("len")

my_shelve = {
    "height": 200,
    "boxes": {
        "box1": {"volume": 110},
        "box2": {"volume": 90},
    },
    "column_width": [20, 480, 40],
}

box_volumes = [my_shelve["boxes"][box]["volume"] for box in my_shelve["boxes"]]
total_volume = sum(box_volumes)
print(total_volume)

# works fine
exp_string = "sum( my_shelve['column_width'])"
exp = Expr(exp_string, my_model)
print("code:", exp.code)
res = exp.eval({"my_shelve": my_shelve})
print(res)


# throws an Exception:
# evalidate.ExecutionException: name 'my_shelve' is not defined

# exp_string = "sum([my_shelve['boxes'][box]['volume'] for box in my_shelve['boxes'] ])"
# exp_string = "sum([my_shelve['boxes'][box]['volume'] for box in my_shelve['boxes'] ])"
exp_string = "len(my_shelve)"
exp = Expr(exp_string, my_model)

#print("basic eval")
#res = eval(exp.code, dict(), {"my_shelve": my_shelve})
#print("basic res:",res)
# sys.exit(0)
try:
    res = exp.eval({"my_shelve": my_shelve})
except ExecutionException as e:
    print(e)

# print(res) 
