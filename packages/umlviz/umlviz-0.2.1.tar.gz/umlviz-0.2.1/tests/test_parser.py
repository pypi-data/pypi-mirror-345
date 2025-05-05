from umlviz.parser import UMLVizParser
import unittest


class TestLexer(unittest.TestCase):

    def test_class(self):
        input_string = """class MyClass {
        int m_member1
        bool m_member2
        }"""

        parser = UMLVizParser()
        result = parser.parse(input_string)
        assert len(result) == 1
        assert 'name' in result[0] and result[0]['name'] == 'MyClass'
        assert 'members' in result[0] and isinstance(result[0]['members'], list)
        assert 'declaration' in result[0]['members'][0] and result[0]['members'][0]['declaration'] == 'variable'
        assert 'type' in result[0]['members'][0] and result[0]['members'][0]['type'] == 'int'
        assert 'name' in result[0]['members'][0] and result[0]['members'][0]['name'] == 'm_member1'
        assert 'declaration' in result[0]['members'][1] and result[0]['members'][1]['declaration'] == 'variable'
        assert 'type' in result[0]['members'][1] and result[0]['members'][1]['type'] == 'bool'
        assert 'name' in result[0]['members'][1] and result[0]['members'][1]['name'] == 'm_member2'
