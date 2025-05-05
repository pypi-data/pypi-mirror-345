from graphviz import Graph # type: ignore[import-untyped]

def draw(name, format, ast):
    g = Graph(name=name)
    g.attr('node', shape='record')
    for node in ast:
        label = "{%s" % (node['name'])
        label += "|"
        member_vars = filter(lambda x : x['declaration'] == 'variable', node['members'])
        for member in member_vars:
            label += "+ %s : %s\l" % (member['name'], member['type'])
        label += "|"
        member_funcs = filter(lambda x : x['declaration'] == 'method', node['members'])
        for member in member_funcs:
            label += "+ %s\l" % (member['name'])
        label += "}"
        g.node(node['name'], label)
    g.render(filename=name, format=format, cleanup=True)
