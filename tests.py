import evo_functions
from evo_functions import github_setup
from evo_functions import find_repo
from github import Github, Auth, GithubException
import ast

def test_invalid_token():
    invalid_token = "invalid_token"
    try:
        github_setup(invalid_token)
    except GithubException as e:
        assert True

    assert False

def test_invalid_repo():
    invalid_repo = "invalid/repo"
    g = Github()
    try:
        find_repo(g, invalid_repo)
    except GithubException as e:
        assert True

    assert False

def test_valid_repo():
    valid_repo = "vitor-terra/CryptoChecker"
    g = Github()
    try:
        find_repo(g, valid_repo)
    except GithubException as e:
        assert False

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

