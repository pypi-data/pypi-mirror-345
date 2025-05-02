import evalidate
from dataclasses import dataclass
from evalidate import Expr, EvalException, base_eval_model

@dataclass
class Person:
    name: str
    weight: float

john = Person(name="John", weight=100)
jack = Person(name="Jack", weight=60)
passengers = {"john": john, "jack": jack}

sum_expr = "john.weight + jack.weight"

mymodel = base_eval_model.clone()
mymodel.nodes.append('Attribute')
mymodel.attributes.append('weight')

validated_expr = evalidate.Expr(sum_expr, model=mymodel)


total_weight = eval(validated_expr.code, passengers, None)

print(total_weight)

