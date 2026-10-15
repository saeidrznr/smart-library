import ast
import operator
import math

from langchain_core.tools import tool

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv
}


def _evaluate(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(
                node.value, bool
        ):
            if not math.isfinite(node.value):
                raise ValueError("Number must be finite.")
            return node.value
        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Unsupported arithmetic operator.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        result = operation(left, right)

        if isinstance(result, (int, float)):
            if abs(result) > 1e100:
                raise ValueError("Result is too large.")
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("Result is not finite.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("Unsupported unary operator.")
        return operation(_evaluate(node.operand))

    raise ValueError("Unsupported expression.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression. Use for calculations based on database results."""
    if not isinstance(expression, str):
        return "Error: expression must be a string."

    if len(expression) > 200:
        return "Error: expression is too long."
    try:
        if len(expression) > 200:
            return "Error: expression is too long."

        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
        return str(result)

    except (ValueError, TypeError, ZeroDivisionError, OverflowError, SyntaxError):
        return "Error: invalid or unsupported arithmetic expression."
