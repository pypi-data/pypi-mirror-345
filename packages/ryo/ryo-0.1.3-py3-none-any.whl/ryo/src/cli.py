import yaml
import os
import argparse
from ryo.src.utils import get_task
from ryo.src.runner import run_steps

__version__ = "0.1.3"

def main():
    parser = argparse.ArgumentParser(description="Um utilitário de linha de comando Ryo.")
    subparsers = parser.add_subparsers(dest="comando", help="Subcomandos disponíveis")

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    task_parser = subparsers.add_parser("task", help="Acompanha a tarefa")
    task_parser.add_argument("nome", help="O nome da task a ser implementada")

    args = parser.parse_args()

    if args.comando == "task":
        task = get_task(args.nome)
        if task:
            run_steps(task, os.getcwd())
        else:
            print(f"Task '{args.nome}' não encontrada.")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
