import evo_functions
from evo_functions import github_setup
from evo_functions import find_repo
from github import Github, Auth, GithubException
import ast
import os
import pytest
from types import SimpleNamespace

def test_invalid_token(monkeypatch):
    # Mocka a classe Github para simular erro ao validar token
    class FakeGithub:
        def __init__(self, *args, **kwargs):
            pass
        def get_user(self):
            raise Exception("invalid token")

    monkeypatch.setattr(evo_functions, "Github", FakeGithub)
    with pytest.raises(SystemExit):
        evo_functions.github_setup("invalid_token")

def test_invalid_repo(monkeypatch):
    # Simula um objeto Github cujo get_repo lança exceção
    class FakeGithub:
        def get_repo(self, repo_name):
            raise Exception("repo not found")

    fake_g = FakeGithub()
    with pytest.raises(SystemExit):
        evo_functions.find_repo(fake_g, "invalid/repo")

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

def test_plot_function_evolution():
    filename = "test_function_evolution.png"

    if os.path.exists(filename):
        os.remove(filename)

    loc_data = [('cod1', 5), ('cod2', 10), ('cod3', 15), ('cod4', 20)]
    evo_functions.plot_function_evolution(loc_data, "test_function")
    assert os.path.exists(filename), "Arquivo não criado"
    assert os.path.getsize(filename) > 0, "Arquivo vazio"

    os.remove(filename)

def test_plot_function_evolution_no_data(capsys):
    loc_data = []
    evo_functions.plot_function_evolution(loc_data, "empty_function")
    captured = capsys.readouterr()
    assert "No data to plot." in captured.out

def test_compare_function_with_previous_versions_missing_file():
    # Quando o arquivo não existe em commits, devolve lista vazia
    class FakeCommit:
        def __init__(self, sha):
            self.sha = sha

    class FakeRepo:
        def get_contents(self, path, ref=None):
            raise Exception("file not found")

    commits = [FakeCommit("c1")]
    repo = FakeRepo()
    sizes, nodes = evo_functions.compare_function_with_previous_versions(repo, "no.py", "foo", commits)
    assert sizes == []
    assert nodes == []

def test_filter_for_python_files():
    # Simula repo, commits e árvore com arquivos .py e outros
    class TreeItem:
        def __init__(self, path):
            self.path = path

    class FakeTree:
        def __init__(self, items):
            self.tree = items

    class FakeCommit:
        def __init__(self, sha):
            self.sha = sha

    class FakeContent:
        def __init__(self, text):
            self.decoded_content = text.encode("utf-8")

    class FakeRepo:
        def __init__(self, files):
            # files: dict path -> content
            self.files = files

        def get_git_tree(self, sha, recursive=True):
            items = [TreeItem(p) for p in self.files.keys()]
            return FakeTree(items)

        def get_contents(self, path):
            if path in self.files:
                return FakeContent(self.files[path])
            raise Exception("not found")

    files = {
        "a.py": "def a(): pass",
        "b.txt": "not python",
        "sub/c.py": "def c(): pass",
    }
    repo = FakeRepo(files)
    commits = [FakeCommit("s1")]
    result = evo_functions.filter_for_python_files(repo, commits)
    # deve retornar lista com um commit => lista de tuplas (path, content)
    assert isinstance(result, list)
    assert len(result) == 1
    assert ("a.py", "def a(): pass") in result[0]
    assert ("sub/c.py", "def c(): pass") in result[0]
    # não deve incluir b.txt
    assert not any("b.txt" in t[0] for t in result[0])

def test_display_limits(capsys):
    class FakeCore:
        def __init__(self, remaining, limit, reset):
            self.remaining = remaining
            self.limit = limit
            self.reset = reset

    class FakeResources:
        def __init__(self, core):
            self.core = core

    class FakeRateLimit:
        def __init__(self, resources):
            self.resources = resources

    class FakeGithub:
        def get_rate_limit(self):
            core = FakeCore(42, 5000, "2025-12-01T00:00:00Z")
            resources = FakeResources(core)
            return FakeRateLimit(resources)

    fake_g = FakeGithub()
    evo_functions.display_limits(fake_g)
    captured = capsys.readouterr()
    assert "42/5000" in captured.out