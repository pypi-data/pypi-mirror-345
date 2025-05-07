import argparse
import csv
import sys
from typing import Dict

from lark import Tree

from gnps import Cell
from gnps.parser.ast import Variable
from gnps.parser.ast.value import FloatValue
from gnps.system import GnpsSystem
from gnps.parser import parse_condition, parse_expression, parse_rule, parse_variable_assignment


def main():
    parser = argparse.ArgumentParser(description='GNPS simulator', prog='python -m gnps')
    parser.add_argument('gnps_file', type=argparse.FileType('r'),
                        help='The file containing the description of the GNPS system')
    parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin,
                        help='Input (CSV) file giving stimulus for each step (default: stdin)')
    parser.add_argument('output', type=argparse.FileType('w'), nargs='?', default=sys.stdout,
                        help='Output (CSV) file giving the results of each step (default: stdout)')
    parser.add_argument('-c', '--compute_mode', action='store_true',
                        help='Run in continuous compute mode (default: False)')
    parser.add_argument('-s', '--steps', type=int, default=1,
                        help='Number of steps to run (default: 1)')
    args = parser.parse_args()

    gnps = GnpsSystem.from_yaml(args.gnps_file.name)

    if args.compute_mode:
        if len(gnps.input_variables) > 0:
            raise ValueError("Cannot run in continuous compute mode with input variables")
        print(f"Running in continuous compute mode for {args.steps} steps")
        result = {name: str(variable.value) for name, variable in gnps.output_variables.items()}
        print(f"Step: 0: {result}")
        for i in range(args.steps):
            gnps.step()
            result = {name: str(variable.value) for name, variable in gnps.output_variables.items()}
            print(f"Step: {i+1}: {result}")
    else:  # IO mode

        reader = csv.DictReader(args.input)
        writer = None

        for row in reader:

            for input_var_name, input_var_value in row.items():
                var = gnps.get_variable(input_var_name)
                if var is None or input_var_name not in gnps.input_variables.keys():
                    raise ValueError(f"Unknown input variable {input_var_name}")
                var.value = FloatValue(input_var_value)

            gnps.step()

            result = {name: variable.value for name, variable in gnps.output_variables.items()}

            if writer is None:
                writer = csv.DictWriter(args.output, fieldnames=result.keys())
                writer.writeheader()
            writer.writerow(result)


if __name__ == '__main__':
    main()
