from github import Github, Auth
from jinja2 import Environment, FileSystemLoader
import sys
import ast
from pprint import pp
from enum import Enum
from datetime import datetime
import statistics
import matplotlib.pyplot as plt
import numpy as np
import argparse


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="OAuth token from GitHub", required=False)
    parser.add_argument("-r", "--repo", help="Repository to be analyzed", required=True)
    parser.add_argument("-a", "--file", help="File in the given repository", required=True)
    parser.add_argument("-f", "--function", help="Function to be analyzed", required=True)
    parser.add_argument("-o", "--option", help="Analysis option", choices=[0, 1], type=int, required=True)
    parser.add_argument("-l", "--limits", action="store_true", help="Display remaining API request limits", required=False)
    parser.add_argument("-w", "--report", help="Generates a report file with given name", required=False)
    args = parser.parse_args()
    return args

class Option(Enum):
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

def compare_function_with_previous_versions(repo, file_path, function_name, commits):
    function_sizes = []
    function_nodes = [] #AJUDA PRO RELATORIO
    for commit in commits:
        try:
            file_content = repo.get_contents(file_path, ref=commit.sha).decoded_content.decode("utf-8")
            ast_tree = ast.parse(file_content)
            function_node = find_user_function(ast_tree, function_name)
            if function_node:
                function_nodes.append(function_node) #AJUDA PRO RELATORIO
                loc = function_node.end_lineno - function_node.lineno + 1
                function_sizes.append((commit.sha, loc))
        except:
            continue
    return function_sizes, function_nodes

def plot_function_evolution(function_sizes, function_name):
    if not function_sizes:
        print("No data to plot.")
        return

    shas, sizes = zip(*function_sizes)

    versions = [f"v{i+1}" for i in reversed(range(len(sizes)))]

    versions = versions[::-1]
    sizes = sizes[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.plot(versions, sizes, marker='o')

    plt.xlabel('Commit Versions')
    plt.ylabel('Lines of Code (LOC)')
    plt.title(f'Evolution of Function "{function_name}" Size Over Versions')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{function_name}_evolution.png')
    plt.close()

#Função para olhar os limites de requests que restam da API; é chamada no final do programa se ele for executado com a opção "-l"
def display_limits(g):
    rate_limit = g.get_rate_limit()
    core = rate_limit.resources.core
    print(f"You now have {core.remaining}/{core.limit} requests remaining.")
    print(f"Your next limit reset will happen at {core.reset}")

def filter_for_python_files(repo, commits):
    python_files = []

    for commit in commits:
        current_commit_python_files = []
        tree = repo.get_git_tree(commit.sha, recursive=True).tree
        for item in tree:
            if item.path.endswith(".py"):
                current_commit_python_files.append((item.path, repo.get_contents(item.path).decoded_content.decode("utf-8")))
        python_files.append(current_commit_python_files)

    return python_files

def generate_report(option, function_nodes, filtered_function, analyzed_file, file_name, image_path):
    if option == 0:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("template_opt0.html")

        avg = statistics.mean([func.end_lineno - func.lineno + 1 for func in function_nodes])
        qtty = len(function_nodes)

        loc_per_iteration = []

        for func in function_nodes:
            loc_per_iteration.append(func.end_lineno - func.lineno + 1)

        html = template.render(
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            analyzed_function=filtered_function.name,
            avg_loc=avg,
            total_functions=qtty,
            data=loc_per_iteration,
            chart_path=image_path,
        )

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html) 


    if option == 1:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("template_opt1.html")

        avg = statistics.mean([func.end_lineno - func.lineno + 1 for func in function_nodes])
        qtty = len(function_nodes)
        filtered_function_loc = (filtered_function.end_lineno - filtered_function.lineno + 1)

        loc_per_function = {}

        for func in function_nodes:
            loc_per_function[func.name] = func.end_lineno - func.lineno + 1

        loc_per_function = dict(sorted(loc_per_function.items(), key=lambda item: item[1]))

        html = template.render(
            analyzed_file = analyzed_file,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            analyzed_function=filtered_function.name,
            analyzed_loc=filtered_function_loc,
            avg_loc=avg,
            total_functions=qtty,
            data=loc_per_function,
            chart_path=image_path,
        )
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)  

def github_setup(token):
    try:
        if not token:
            g = Github()
        else:
            auth = Auth.Token(token)
            g = Github(auth=auth)

            g.get_user().login
    except Exception as e:
        print("Erro! Token inválido: ", e)
        sys.exit()
    return g

def find_repo(github, repo):
    try:
        r = github.get_repo(repo)
    except Exception as e:
        print("Erro! Repositório inválido: ", e)
        sys.exit()
    return r


def main():
    args = setup()

    token = args.token
    ############################## Tratar erro de colocar token invalido ##############################
    g = github_setup(token)
    ############################## Tratar erro de colocar repositorio invalido ##############################
    
    # Inicialização das variáveis comuns a ambos os argumentos escolhidos
    commits = 0
    r = args.repo
    repo = find_repo(g, r)

    opt = Option(args.option)

    #Função de filtro para determinar a quantidade de commits que serão analisados na função compare_function_with_previous_versions
    if opt == Option.SAME_FUNCTION_PREVIOUS_VERSIONS:
        try:
            start_date = input("\nEnter the start date (inclusive) of commits to be analyzed (format YYYY-MM-DD or ISO):\nLeave blank for earliest date.\n")
            if start_date == "":
                start_date = datetime.min
            else:
                start_date = datetime.fromisoformat(start_date)

            end_date = input("\nEnter the end date (inclusive) of commits to be analyzed (format YYYY-MM-DD or ISO):\nLeave blank for current date.\n")
            if end_date == "":
                end_date = datetime.now()
            else:
                end_date = datetime.fromisoformat(end_date)

        except:
            print("Error: the input must be a string datetime (format YYYY-MM-DD or ISO).")
            sys.exit(1)

        total_commits = repo.get_commits(since=start_date, until=end_date)
        commits = total_commits[:10] # Por padrão, a análise é feita com base nos últimos 10 commits
    
    elif opt == Option.OTHER_FUNCTIONS_SAME_VERSION:
        try:
            chosen_commit = input("Enter the SHA value of the commit to be analyzed. Type 000 to choose the newest commit: ")
            if chosen_commit == '000':
                commit_obj = repo.get_commits()[0]
            else:
                commit_obj = repo.get_commit(chosen_commit)

            commits = [commit_obj]
        except:
            print(f"Error: It wasn't possible to get the commit {chosen_commit}.")
            sys.exit(1)

    python_files = filter_for_python_files(repo=repo, commits=commits)

    for commit in python_files:
        for file in commit:
            ast_tree = ast.parse(file[1])

    ############################## Tratar erro de colocar função/método inválido ##############################
    f = args.function

    try:
        filtered_function = find_user_function(ast_tree=ast_tree, user_function=f)
        if filtered_function:
            print(f"Função '{f}' encontrada no arquivo do commit:")
            pp(filtered_function.__dict__)
        else:
            raise ValueError("Função informada não foi encontrada no arquivo do commit")  
    except:
        print("Erro: Nome de função inválido")

    if (opt == Option.OTHER_FUNCTIONS_SAME_VERSION):
        function_nodes = [node for node in ast.walk(ast_tree) if isinstance(node, ast.FunctionDef)]
        print(f"\nAverage lines of code for functions in the current version: {statistics.mean([func.end_lineno - func.lineno + 1 for func in function_nodes]):.2f}")
        print(f"Lines of code for function '{f}': {(filtered_function.end_lineno - filtered_function.lineno + 1):.2f} \n")
        print_distribution_loc_functions(function_nodes)
        chart_path = "loc_distribution.png"

    elif (opt == Option.SAME_FUNCTION_PREVIOUS_VERSIONS):
        function_sizes, function_nodes = compare_function_with_previous_versions(repo, args.file, f, commits)
        if not function_sizes:
            print("No history found for the given function.")
            chart_path = None
        else:
            print(f"\nAverage lines of code for function '{f}' over previous versions: {statistics.mean([size for sha, size in function_sizes]):.2f}")
            print(f"\nFunction sizes over previous versions for function '{f}':")
            for sha, size in function_sizes:
                print(f"Commit {sha[:7]}: {size} LOC")
            plot_function_evolution(function_sizes, f)
            chart_path = f"{filtered_function.name}_evolution.png"
    else:
        print("Option not implemented yet.")


    if args.report:
        report_fname = args.report
        if not report_fname.endswith(".html"):
            report_fname += ".html"
        generate_report(args.option, function_nodes, filtered_function, args.file, report_fname, chart_path)

    if args.limits:
        display_limits(g)


if __name__ == "__main__":
    main()