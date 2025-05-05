import ast

def generate_data_flow(code: str) -> str:
    """
    Generates Graphviz code for a data flow diagram by parsing the given Python code.

    :param code: The Python source code.
    :return: A string containing the Graphviz code.
    """
    tree = ast.parse(code)
    nodes = ['Global']
    edges = []
    node_ids = {'Global': 0}

    def add_node(node_name: str):
        if node_name not in node_ids:
            node_ids[node_name] = len(nodes)
            nodes.append(node_name)

    # Walk through AST and add nodes and edges
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            add_node(node.name)
            for n in node.body:
                if isinstance(n, ast.Assign):
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            add_node(target.id)
                            edges.append((node.name, target.id))
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    add_node(target.id)
                    edges.append(("Global", target.id))
    
    # Build Graphviz code
    graphviz_code = "digraph G {\n"
    for node in nodes:
        graphviz_code += f'    "{node}" [shape=box];\n'
    for edge in edges:
        graphviz_code += f'    "{edge[0]}" -> "{edge[1]}";\n'
    graphviz_code += "}\n"
    
    return graphviz_code
