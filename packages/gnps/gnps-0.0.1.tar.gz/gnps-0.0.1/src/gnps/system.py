import yaml
from .cell import Cell
from .parser import (parse_rule, parse_variable_assignment, parse_expression, parse_condition)
from .rule import Rule
from .parser.ast.variable import Variable
from .parser.ast.value import FloatValue
from .parser.ast import BooleanConstantExpression


class GnpsSystem:
    """A GNPS system is a collection of cells and rules."""

    cells: list[Cell]
    rules: list[Rule]
    variables: dict[str, Variable]

    input_variables: dict[str, Variable]
    output_variables: dict[str, Variable]

    def __init__(self):
        self.cells: list[Cell] = []
        self.rules: list[Rule] = []
        self.variables = {}
        self.input_variables = {}
        self.output_variables = {}

    def add_cell(self, cell: Cell):
        self.cells.append(cell)
        self.variables.update(cell.contents)

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def get_variable(self, variable_name):
        return self.variables.get(variable_name, None)

    def step(self):
        used_vars = []
        production_values = {}
        for rule in self.rules:
            if rule.guard.evaluate():
                used_vars.extend(rule.vars.values())
                production_values[rule] = rule.producer.evaluate()

        used_vars = set(used_vars)
        for variable in used_vars:
            variable.value = FloatValue(0.0)

        for rule in production_values:
            rule.consumer.value += production_values[rule]

    def print(self):  # pragma: no cover
        print("GNPS Configuration:")
        print("-------------------")
        for cell in self.cells:
            print(f"Cell {cell.id}:")
            for variable in cell.contents.values():
                print(f"  {variable.name}: {variable.value}")
            print("-------------------")

    @staticmethod
    def from_yaml(file_path):
        gnps = GnpsSystem()

        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        variables = {}

        cells_data = data.get("cells", [])
        for cell_data in cells_data:
            cell_id = cell_data.get("id")
            contents_data = cell_data.get("contents", [])
            contents = {}
            for variable_data in contents_data:
                if "name" in variable_data:
                    variable_name = variable_data.get("name")
                    variable_value = variable_data.get("value")
                    # Check if variable instance already exists for the given name
                    if variable_name in variables:
                        variable = variables[variable_name]
                    else:
                        variable = Variable(variable_name, variable_value)
                        variables[variable_name] = variable

                    contents[variable_name] = variable
                else:
                    parsed_variables = parse_variable_assignment(variable_data, {})
                    contents.update(parsed_variables)
                    variables.update(parsed_variables)
            cell = Cell(cell_id, contents)
            gnps.add_cell(cell)

            # Parse input/output variables
            input_variables_names = cell_data.get("input", [])
            input_variables = {}
            for variable_name in input_variables_names:
                input_variables[variable_name] = variables[variable_name]
            gnps.input_variables.update(input_variables)

            output_variables_names = cell_data.get("output", [])
            output_variables = {}
            for variable_name in output_variables_names:
                output_variables[variable_name] = variables[variable_name]
            gnps.output_variables.update(output_variables)

        rules_data = data.get("rules", [])
        for rule_data in rules_data:
            # check if it is a single string or not
            if isinstance(rule_data, str):
                # print(f"We have a string instance of {rule_data}")
                rule = parse_rule(rule_data, variables)
                gnps.add_rule(rule)
            else:
                guard_data = rule_data.get("guard", True)
                if isinstance(guard_data, bool):
                    if guard_data:
                        guard = BooleanConstantExpression(True)
                    else:
                        guard = BooleanConstantExpression(False)
                else:
                    guard = parse_condition(guard_data, variables)

                producer_data = rule_data.get("producer")
                producer = parse_expression(producer_data, variables)

                consumer_variable_name = rule_data.get("consumer")
                consumer = gnps.get_variable(consumer_variable_name)

                if guard and producer and consumer:
                    rule = Rule(consumer, producer, guard)
                    gnps.add_rule(rule)
                else:  # pragma: no cover
                    pass

        return gnps
    
    
