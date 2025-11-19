import evo_functions
import ast

def test_invalid_token():
    invalid_token = "invalid_token"
    #todo chamar parte da main com token invalido e verificar se o erro é tratado
    assert True

def test_invalid_repo():
    invalid_repo = "invalid/repo"
    #todo chamar parte da main com repositorio invalido e verificar se o erro é tratado
    assert True

def test_find_user_function_found():
    src = """
def foo():
    return 1

def bar(x):
    return x
"""
    tree = ast.parse(src)
    node = evo_functions.find_user_function(tree, "bar")
    assert isinstance(node, ast.FunctionDef)
    assert node.name == "bar"

def test_find_user_function_not_found():
    src = "def only(): pass"
    tree = ast.parse(src)
    node = evo_functions.find_user_function(tree, "missing")
    assert node is None

def test_print_distribution_loc_functions_terminal(capsys):
    src = """
def foo():
    return 1
def bar(x):
    return x
def baz(y, z):
    return y + z
"""
    tree = ast.parse(src)
    function_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    evo_functions.print_distribution_loc_functions(function_nodes)
    captured = capsys.readouterr()
    assert "2 lines: 3 function(s)" in captured.out
