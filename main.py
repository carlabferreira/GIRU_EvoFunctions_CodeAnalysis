from github import Github, Auth
import sys
import ast
from pprint import pp
from enum import Enum
import statistics
import matplotlib.pyplot as plt
import numpy as np

class option(Enum):
    SAME_FUNCTION_PREVIOUS_VERSIONS = 0 # Compara uma função específica com ela mesma em outras versões, ao longo do tempo
    OTHER_FUNCTIONS_SAME_VERSION = 1 # Compara função específica com outras no mesmo ambiente

def print_distribution_loc_functions(function_nodes):
    loc_distribution = {}
    all_locs = []
    for func in function_nodes:
        loc = func.end_lineno - func.lineno + 1
        all_locs.append(loc)
        if loc in loc_distribution:
            loc_distribution[loc] += 1
        else:
            loc_distribution[loc] = 1
    print("Distribution of lines of code in functions:")
    for loc, count in sorted(loc_distribution.items()):
        print(f"{loc} lines: {count} function(s)")

    plt.barh(list(loc_distribution.keys()), list(loc_distribution.values()), height=2)

    avg_loc = statistics.mean(all_locs)
    outlier = 2 * avg_loc # Para evitar que outliers distorçam o gráfico
    visual_limit = np.ceil(outlier).astype(int)

    plt.figure(figsize=(10, 8))
    
    counts = list(loc_distribution.values())
    locs = list(loc_distribution.keys())
    
    plt.barh(locs, counts, height=2, color='#1f77b4') 

    # Ajuste para Ticks Inteiros no Eixo X
    max_count = max(counts) if counts else 0
    plt.xticks(np.arange(0, max_count + 1, 1)) 

    plt.axhline(y=avg_loc, color='r', linestyle='--', label=f'Average LOC ({avg_loc:.2f})')
    plt.axhline(y=outlier, color='g', linestyle='-.', label=f'Outlier Limit({outlier:.2f})')

    plt.ylim(0, visual_limit) 

    plt.ylabel('Lines of Code (LOC)')
    plt.xlabel('Number of Functions')
    plt.title('Distribution of Lines of Code')
    
    outliers = [(loc, count) for loc, count in loc_distribution.items() if loc > outlier]
    outlier_info = "Excluded Outliers:\n"
    if outliers:
        for loc, count in outliers:
            outlier_info += f"- {count} function(s) with {loc} LOC\n"
        
        plt.text(
            max_count * 0.7, 
            visual_limit * 0.8, 
            outlier_info.strip(),
            color='red',
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='red')
        )
    
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('loc_distribution.png')
    plt.close()

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

    if (option.OTHER_FUNCTIONS_SAME_VERSION):
        function_nodes = [node for node in ast.walk(ast_tree) if isinstance(node, ast.FunctionDef)]
        print(f"\nAverage lines of code for functions in the current version: {statistics.mean([func.end_lineno - func.lineno + 1 for func in function_nodes]):.2f}")
        print(f"Lines of code for function '{f}': {(filtered_function.end_lineno - filtered_function.lineno + 1):.2f} \n")
        print_distribution_loc_functions(function_nodes)

    if "-l" in sys.argv:
        display_limits(g)


if __name__ == "__main__":
    main()