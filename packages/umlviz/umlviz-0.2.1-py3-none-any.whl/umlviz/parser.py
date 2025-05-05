import ply.yacc as yacc # type: ignore[import-untyped]
from .lexer import UMLVizLexer

class UMLVizParser:

    def p_model(self, p):
        '''model : type
                 | model type
                 | model NEWLINE'''


        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3 and isinstance(p[1], dict): 
            p[0] = p[1].append(p[2])
        elif len(p) == 3:
            p[0] = p[1]

    def p_type_object(self, p):
        'type : object'
        p[0] = p[1]

    def p_object(self, p):
        'object : OBJECT WORD OPEN_CURLY NEWLINE members NEWLINE CLOSE_CURLY'
        p[0] = {
            'name' : p[2],
            'members': p[5],
        }

    def p_members(self, p):
        '''members : member
                   | members NEWLINE member'''
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]

    def p_member(self, p):
        '''member : variable
                  | method'''
        p[0] = p[1]

    def p_variable(self, p):
        'variable : WORD WORD'
        p[0] = {
            'declaration': 'variable',
            'type': p[1],
            'name': p[2]
        }
    
    def p_method(self, p):
        'method : METHOD'
        p[0] = {
            'declaration': 'method',
            'name': p[1]
        }

    def p_error(self, p):
        raise SyntaxError("Invalid syntax.")

    def __init__(self,**kwargs):
        self.tokens = UMLVizLexer.tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data, debug=False):
        return self.parser.parse(data, debug=debug, lexer=UMLVizLexer().lexer)

