from __future__ import annotations
import ast
import operator as op
import math

# Allowed operators
_ALLOWED_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
}

_ALLOWED_UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

# Allowed functions and constants
_ENV = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,  # natural log
    'exp': math.exp,
    'abs': abs,
    'pi': math.pi,
    'e': math.e,
}

def _safe_eval(node: ast.AST, names: dict) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, names)
    # numbers
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    # variable names (e.g., ans, pi, e)
    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        raise ValueError(f"Unknown name: {node.id}")
    # unary ops (+x, -x)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
        return _ALLOWED_UNARY_OPS[type(node.op)](_safe_eval(node.operand, names))
    # binary ops (x+y, x*y, ...)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
        left = _safe_eval(node.left, names)
        right = _safe_eval(node.right, names)
        return _ALLOWED_BIN_OPS[type(node.op)](left, right)
    # function calls like sqrt(9)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = node.func.id
        if fn in names and callable(names[fn]):
            args = [_safe_eval(arg, names) for arg in node.args]
            if node.keywords:
                raise ValueError("Keyword args not allowed")
            return names[fn](*args)
        raise ValueError(f"Unknown function: {fn}")
    # parentheses are represented in AST structure automatically
    raise ValueError("Unsupported expression")


def evaluate(expr: str, ans: float | int | None) -> float:
    names = dict(_ENV)
    if ans is not None:
        names['ans'] = ans
    try:
        tree = ast.parse(expr, mode='eval')
        return _safe_eval(tree, names)
    except ZeroDivisionError:
        raise ZeroDivisionError("Division by zero")
    except Exception as e:
        raise ValueError(str(e))


def repl():
    print("Python CLI Calculator. Type 'quit' or 'exit' to leave. Use 'ans' for previous result.")
    last = None
    while True:
        try:
            expr = input('calc> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if expr.lower() in {"quit", "exit"}:
            break
        if not expr:
            continue
        try:
            result = evaluate(expr, last)
            print(result)
            last = result
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    repl()
