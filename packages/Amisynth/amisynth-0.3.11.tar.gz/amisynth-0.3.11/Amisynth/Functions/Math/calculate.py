import xfox
import ast
import operator

@xfox.addfunc(xfox.funcs, name="calculate")
async def calculate_funcs(expression: str, *args, **kwargs):
    # Mapeo de operadores permitidos
    allowed_operators = {
        ast.Add: operator.add,       # +
        ast.Sub: operator.sub,       # -
        ast.Mult: operator.mul,      # *
        ast.Div: operator.truediv,   # /
        ast.Pow: operator.pow,       # **
        ast.Mod: operator.mod,       # %
        ast.USub: operator.neg,      # -
    }

    def eval_node(node):
        if isinstance(node, ast.Num):  # números
            return node.n
        elif isinstance(node, ast.BinOp):  # operaciones binarias
            left = eval_node(node.left)
            right = eval_node(node.right)
            op = allowed_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Operador no permitido en la expresión: '{ast.dump(node.op)}' en `$calculate[]`")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):  # operaciones unarias, como -5
            operand = eval_node(node.operand)
            op = allowed_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Operador unario no permitido: '{ast.dump(node.op)}'. Solo se permite '-' para números en `$calculate[]`.")
            return op(operand)
        else:
            raise ValueError(f"Expresión inválida: '{ast.dump(node)}'. Asegúrate de usar solo números y operadores permitidos en `$calculate[]`")

    try:
        # Analiza la expresión
        tree = ast.parse(expression, mode="eval")
        result = eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error en la expresión: {str(e)} en `$calculate[]`"
