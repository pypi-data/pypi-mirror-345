import ply.lex as lex # type: ignore[import-untyped]

class UMLVizLexer:

    reserved = {
        'class': 'OBJECT',
        'struct': 'OBJECT',
        'enum': 'ENUM',
    }

    tokens = [
        'OBJECT',
        'ENUM',
        'METHOD',
        'WORD',
        'COLON',
        'OPEN_CURLY',
        'CLOSE_CURLY',
        'NEWLINE',
    ]

    def t_METHOD(self, t):
        r'[a-zA-Z]([a-zA-Z0-9_]|::)+\(\)'
        return t

    def t_WORD(self, t):
        r'[a-zA-Z]([a-zA-Z0-9_]|::)+'
        t.type = self.reserved.get(t.value, 'WORD')
        return t

    t_COLON = r':'
    t_OPEN_CURLY = r'{'
    t_CLOSE_CURLY = r'}'
    t_NEWLINE = r'\n+'

    t_ignore  = ' \t'

    def t_error(self, t):
        raise SyntaxError("Illegal character '%s' found." % (t.value[0]))

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def lex(self, data):
        self.lexer.input(data)
        token = self.lexer.token()
        result = []
        while token is not None:
            result.append(token)
            token = self.lexer.token()
        return result
