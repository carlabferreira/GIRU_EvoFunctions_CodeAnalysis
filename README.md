# GIRU - EvoFunctions Code Analysis
Trabalho Prático da disciplina Engenharia de Software II (DCC072) em 2025/2 na UFMG

Enunciado base: Desenvolver uma ferramenta de linha de comando que identifique problemas de manutenção de software por meio da mineração de repositórios. 

Mais informações: https://github.com/andrehora/software-repo-mining/blob/main/README.md e https://github.com/andrehora/tp-software-repo-mining

Informações apresentadas:
1. [Membros da Equipe](#membros-do-grupo)
2. [Sobre o GIRU](#sobre-o-giru)
3. [Explicação do sistema](#explicação-do-sistema)
4. [Tecnologias usadas](#explicação-das-tecnologias-usadas)
5. [Requirements](#requirements)

## Membros do grupo:
1. Carla Beatriz Ferreira
2. Gabriele Pinheiro Sá
3. Manuela Monteiro Fernandes de Oliveira
4. Vitor Terra Mattos do Patrocínio Veloso

## Sobre o GIRU
GIRU é a combinação das letras dos 4 integrantes que atuam no desenvolvimento desta e de outras ferramentas, formado durante suas graduações na Universidade Federal de Minas Gerais.

<p align="center">
  <img src="./imgs/Logo.gif" alt="Demonstração" width="300">
</p>

## Explicação do sistema
O sistema tem como objetivo analisar códigos de repositórios do GitHub e exibir informações relacionadas a manutenção das funções ao longo do tempo. Para métricas comparativas, pretendemos analisar a quantidade de linhas de código em comparação com versões anteriores e em comparação com outras funções do código, na premissa que métodos/funções longos(as) são um possível CODE SMELL.

## Explicação das tecnologias usadas
Para o desenvolvimento do projeto utilizaremos as seguintes ferramentas:
- Python ast: Python parsing library (https://docs.python.org/3/library/ast.html) - como ferramenta para análise das partes do código e obtenção de informações relevantes para análise
     - Por ser um módulo que ajuda o Python a processar a gramática das árvores de sintaxe abstratas da linguagem, ele é útil para entender o desenvolvimento e as conexões existentes dentro do código.
- PyGithub: Typed interactions with the GitHub API (https://github.com/PyGithub/PyGithub) - como forma de interação principal com a API do GitHub
     - Essa ferramenta permite o acesso ao código-fonte do projeto no GitHub, possibilitando a análise de repositórios, issues, commits, pull requests, etc.
 
## Requisitos para utilização da ferramenta
- GitHub API

```pip install PyGithub```
- Token (opcional)

Criar Token em https://github.com/settings/tokens e "Generate new token (classic)"

## Como instalar a ferramenta
- Clonagem do repositório:
 ```git clone https://github.com/carlabferreira/GIRU_EvoFunctions_CodeAnalysis.git```

- Instalação das bibliotecas:
```pip install pytest pygithub statistics argparse jinja2 matplotlib numpy```

Ou alternativamente pelo arquivo requirements.txt
```pip install -r requirements.txt```

> Recomenda-se utilizar um ambiente virtual em Python para instalação das bibliotecas e execução da ferramenta

## Como executar
Para execução, é necessário seguir a ordem esperada dos parâmetros na linha de comando:

```python evo_functions.py [-h] [-t TOKEN] -r REPO -a FILE -f FUNCTION -o {0,1} [-l] [-w REPORT]```

Onde cada parâmetro segue a lógica abaixo:

    +------------+-----------+----------------------------------------------+------------------------+
    | Parâmetro  | Curto     | Descrição                                    | Obrigatório            |
    +------------+-----------+----------------------------------------------+------------------------+
    | --token    | -t        | OAuth token from GitHub                      | Não                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --repo     | -r        | Repository to be analyzed                    | Sim                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --file     | -a        | File in the given repository                 | Sim                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --function | -f        | Function to be analyzed                      | Sim                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --option   | -o        | Analysis option (0 ou 1)                     | Sim                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --limits   | -l        | Display remaining API request limits         | Não                    |
    +------------+-----------+----------------------------------------------+------------------------+
    | --report   | -w        | Generates a report file with given name      | Não                    |
    +------------+-----------+----------------------------------------------+------------------------+

Caso a opção escolhida para a análise seja 0, isso significa que a ferramenta irá comparar a função passada como parâmetro com outras versões em commits anteriores, ao longo do tempo. Para isso, é necessário inserir as datas de início e fim do período de tempo analisado quando perguntado pelo programa. Já caso a opção seja 1, a ferramenta comparará a função escolhida com as outras no mesmo arquivo. Para isso, a ferramenta pergunta qual commit deve ser considerado.

## Como executar os testes localmente:
Os testes podem ser executados através do comando abaixo:
```pytest tests.py -v```
