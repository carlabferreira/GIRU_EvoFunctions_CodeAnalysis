# SE_CodeAnalysis
Trabalho Prático da disciplina Engenharia de Software II (DCC072) em 2025/2 na UFMG

Enunciado base: Desenvolver uma ferramenta de linha de comando que identifique problemas de manutenção de software por meio da mineração de repositórios. Mais informações: https://github.com/andrehora/software-repo-mining/blob/main/README.md

## Membros do grupo:
1. Carla Beatriz Ferreira
2. Gabriele Pinheiro Sá
3. Manuela Monteiro Fernandes de Oliveira
4. Vitor Terra Mattos do Patrocínio Veloso

## Explicação do sistema
O sistema tem como objetivo analisar códigos de repositórios do GitHub e exibir informações relacionadas a manutenção das funções ao longo do tempo. Para métricas comparativas, pretendemos analisar a quantidade de linhas de código em comparação com versões anteriores e em comparação com outras funções do código, na premissa que métodos/funções longos(as) são um possível CODE SMELL.

## Explicação das possíveis tecnologias usadas
Para o desenvolvimento do projeto utilizaremos as seguintes ferramentas:
- Python ast: Python parsing library (https://docs.python.org/3/library/ast.html) - como ferramenta para ánalise das partes do código e obtenção de informações relevantes para análise
     - Por ser um módulo que ajuda o Python a processar a gramática das árvores de sintaxe abstratas da linguagem, ele é útil para entender o desenvolvimento e as conexões existentes dentro do código.
- PyGithub: Typed interactions with the GitHub API (https://github.com/PyGithub/PyGithub) - como forma de interação principal com a API do GitHub
