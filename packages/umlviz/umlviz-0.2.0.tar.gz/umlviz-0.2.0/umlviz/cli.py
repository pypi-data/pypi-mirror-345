from argparse import ArgumentParser
from .draw import draw
from .parser import UMLVizParser
import sys

def main():
    parser = ArgumentParser(prog='umlviz', description='Generates a UML diagram based on C-like language')
    parser.add_argument('name', help='The name of the UML diagram')
    parser.add_argument('format', help='The output format')
    parser.add_argument('input', nargs='+', help='The input file(s)')
    args = parser.parse_args()
    parser = UMLVizParser()
    ast = []
    for input in args.input:
        with open(input, 'r') as f:
            ast.extend(parser.parse(f.read()))
    draw(args.name, args.format, ast)
