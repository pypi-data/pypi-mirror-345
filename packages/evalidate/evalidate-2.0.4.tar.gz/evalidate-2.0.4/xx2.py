from dataclasses import dataclass
from evalidate import Expr, EvalException, base_eval_model

@dataclass
class Person:
    name: str
    weight: float

    def get_weight(self):
        return self.weight

john = Person(name="John", weight=100)
jack = Person(name="Jack", weight=60)
passengers = {"john": john, "jack": jack}

sum_expr = "john.get_weight() + jack.get_weight()"

mymodel = base_eval_model.clone()
mymodel.nodes.extend(['Attribute', 'Call'])
mymodel.attributes.append('get_weight')

validated_expr = Expr(sum_expr, model=mymodel)

total_weight = eval(validated_expr.code, passengers, None)

print(total_weight)

