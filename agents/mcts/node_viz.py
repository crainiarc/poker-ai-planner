__author__ = 'crainiarc'


def node_to_json(node):
    children = []
    for c in node.childNodes:
        children.append(node_to_json(c))

    return {'name': '', 'children': children}
