from abc import abstractmethod, ABC

from .value.numerical_value import NumericalValue
from .variable import Variable


class Expression(ABC):
    @abstractmethod
    def evaluate(self) -> NumericalValue:
        pass  # pragma: no cover

    @abstractmethod
    def get_variables(self) -> dict[str, Variable]:
        pass  # pragma: no cover


class ConstantExpression(Expression):

    value: NumericalValue

    def __init__(self, value: NumericalValue):
        self.value = value

    def evaluate(self):
        return self.value

    def get_variables(self) -> dict[str, Variable]:
        return {}

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"ConstantExpression({self.value.__repr__()})"


class VariableExpression(Expression):
    def __init__(self, variable: Variable):
        self.variable = variable

    def evaluate(self):
        return self.variable.value

    def get_variables(self) -> dict[str, Variable]:
        return {self.variable.name: self.variable}

    def __str__(self):
        return self.variable.name

    def __repr__(self):
        return f"VariableExpression({self.variable.__repr__()})"


class BinaryExpression(Expression, ABC):
    def __init__(self, left: Expression, right: Expression, op: str = ''):
        self.left = left
        self.right = right
        self.op = op

    def get_variables(self) -> dict[str, Variable]:
        variables = self.left.get_variables()
        variables.update(self.right.get_variables())
        return variables

    def __str__(self):
        ll = self.left.__str__()
        r = self.right.__str__()
        return f"({ll} {self.op} {r})"

    def __repr__(self):
        ll = self.left.__repr__()
        r = self.right.__repr__()
        return f"BinaryExpression({ll},{r},\'{self.op}\')"


class SumExpression(BinaryExpression):
    def __init__(self, left: Expression, right: Expression):
        super().__init__(left, right, '+')

    def evaluate(self):
        x = self.left.evaluate() + self.right.evaluate()
        return x


class DifferenceExpression(BinaryExpression):
    def __init__(self, left: Expression, right: Expression):
        super().__init__(left, right, '-')

    def evaluate(self):
        return self.left.evaluate() - self.right.evaluate()


class MultiplicationExpression(BinaryExpression):
    def __init__(self, left: Expression, right: Expression):
        super().__init__(left, right, '*')

    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()


class DivisionExpression(BinaryExpression):
    def __init__(self, left: Expression, right: Expression):
        super().__init__(left, right, '/')

    def evaluate(self):
        return self.left.evaluate() / self.right.evaluate()


class UnaryMinusExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression: Expression = expression

    def evaluate(self):
        return -self.expression.evaluate()

    def get_variables(self) -> dict[str, Variable]:
        variables = self.expression.get_variables()
        return variables

    def __str__(self):
        exp = self.expression.__str__()
        return f"-({exp})"

    def __repr__(self):
        exp = self.expression.__repr__()
        return f"UnaryMinusExpression({exp})"


class IntOperationExpression(Expression, ABC):
    def __init__(self, constant: int, expression: Expression, op: str = ''):
        self.expression = expression
        self.constant = constant
        self.op = op

    def get_variables(self) -> dict[str, Variable]:
        variables = self.expression.get_variables()
        return variables

    # def __str__(self):
    #     exp = self.expression.__str__()
    #     return f"({self.constant} {self.op} {exp}))"
    #
    # def __repr__(self):
    #     exp = self.expression.__repr__()
    #     return f"IntOperationExpression({self.constant},{exp},\'{self.op}\')"


class IntMultiplicationExpression(IntOperationExpression):
    def __init__(self, constant: int, expression: Expression):
        super().__init__(constant, expression)

    def evaluate(self):
        val = self.expression.evaluate()
        val_type = type(val)
        return val * val_type(self.constant)

    def __str__(self):
        exp = self.expression.__str__()
        return f"({self.constant} * {exp})"

    def __repr__(self):
        exp = self.expression.__repr__()
        return f"IntMultiplicationExpression({self.constant},{exp})"


class IntDivisionExpression(IntOperationExpression):
    def __init__(self, constant: int, expression: Expression):
        super().__init__(constant, expression)

    def evaluate(self):
        val = self.expression.evaluate()
        val_type = type(val)
        return val / val_type(self.constant)

    def __str__(self):
        exp = self.expression.__str__()
        return f"({exp} / {self.constant})"

    def __repr__(self):
        exp = self.expression.__repr__()
        return f"IntDivisionExpression({self.constant},{exp})"
