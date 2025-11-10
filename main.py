from github import Github, Auth
import sys
import ast
from pprint import pp
from enum import Enum

class option(Enum):
    SAME_FUNCTION_PREVIOUS_VERSIONS = 0 # Compara uma função específica com ela mesma em outras versões, ao longo do tempo
    OTHER_FUNCTIONS_SAME_VERSION = 1 # Compara função específica com outras no mesmo ambiente

def find_user_function(ast_tree, user_function):
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == user_function:
                return node 
    return None

#Função para olhar os limites de requests que restam da API; é chamada no final do programa se ele for executado com a opção "-l"
def display_limits(g):
    rate_limit = g.get_rate_limit()
    core = rate_limit.resources.core
    print(f"You now have {core.remaining}/{core.limit} requests remaining.")
    print(f"Your next limit reset will happen at {core.reset}")

def filterForPythonFiles(repo, commits):
    python_files = []

    for commit in commits:
        current_commit_python_files = []
        tree = repo.get_git_tree(commit.sha, recursive=True).tree
        for item in tree:
            if item.path.endswith(".py"):
                current_commit_python_files.append((item.path, repo.get_contents(item.path).decoded_content.decode("utf-8")))
        python_files.append(current_commit_python_files)

    return python_files


def main():
    token = input("Type in a personal access token\nIf left blank, github API limits to 60 requests per hour\nIf a token is given, your limit will be 5000 requests per hour\n")

    ############################## Tratar erro de colocar token invalido ##############################
    try:
        if not token:
            g = Github()
        else:
            auth = Auth.Token(token)
            g = Github(auth=auth)
    except:
        print("erro token invalido")
        sys.exit()


    ############################## Tratar erro de colocar repositorio invalido ##############################
    r = input("\nType in the link to the repository you want to look at\nFormat should be: <USER/REPO-NAME>\n")
    try:
        repo = g.get_repo(r)
    except:
        print("erro repositorio invalido")

    commits = repo.get_commits()

    #Função de filtro uau
    commits = commits[:10]

    python_files = filterForPythonFiles(repo=repo, commits=commits)

    for commit in python_files:
        for file in commit:
            ast_tree = ast.parse(file[1])
            # pp(ast_tree.__dict__)

    ############################## Tratar erro de colocar função/método inválido ##############################
    f = input("\nType in the name of the function to be analyzed\nNote: It must be present in the current version\n")
    try:
        filtered_function = find_user_function(ast_tree=ast_tree, user_function=f)
        if filtered_function:
            print(f"Função '{f}' encontrada no arquivo do commit:")
            pp(filtered_function.__dict__)
        else:
            raise ValueError("Função informada não foi encontrada no arquivo do commit")  
    except:
        print("Erro: Nome de função inválido")

    if "-l" in sys.argv:
        display_limits(g)


if __name__ == "__main__":
    main()