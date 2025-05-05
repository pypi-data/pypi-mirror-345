from umlviz.lexer import UMLVizLexer
import unittest


class TestLexer(unittest.TestCase):

    def test_class(self):
        input_string = """class MyClass {
        int m_member1
        std::string m_member2
        }"""

        lexer = UMLVizLexer()
        result = lexer.lex(input_string)
        assert result[0].type  == "OBJECT"
        assert result[0].value == "class"
        assert result[1].type  == "WORD"
        assert result[1].value == "MyClass"
        assert result[2].type  == "OPEN_CURLY"
        assert result[2].value == "{"
        assert result[3].type  == "NEWLINE"
        assert result[3].value == "\n"
        assert result[4].type  == "WORD"
        assert result[4].value == "int"
        assert result[5].type  == "WORD"
        assert result[5].value == "m_member1"
        assert result[6].type  == "NEWLINE"
        assert result[6].value == "\n"
        assert result[7].type  == "WORD"
        assert result[7].value == "std::string"
        assert result[8].type  == "WORD"
        assert result[8].value == "m_member2"
        assert result[9].type  == "NEWLINE"
        assert result[9].value == "\n"
        assert result[10].type  == "CLOSE_CURLY"
        assert result[10].value == "}"
        assert len(result) == 11
