"""Command-line interface for Todo CLI."""

from __future__ import annotations
import sys
import os
import argparse
from typing import Optional, List

from todocli import __version__
from todocli.db import Database
from todocli.formatters import (
    format_todo_list,
    format_stats,
    format_markdown,
    format_json,
    green,
    yellow,
    red,
    bold,
    dim,
)


def run_cli(argv: Optional[List[str]] = None, db: Optional[Database] = None) -> int:
    args_list = argv if argv is not None else sys.argv[1:]
    database = db or Database()

    # Heuristic: Quick-add if first argument is not a registered subcommand or flag
    known_commands = {
        "add", "list", "ls", "done", "check", "undo", "rm", "delete",
        "edit", "search", "find", "clear", "stats", "export", "-h", "--help", "-v", "--version"
    }

    if args_list and not args_list[0].startswith("-") and args_list[0] not in known_commands:
        # Convert `todo "Minha tarefa"` into `todo add "Minha tarefa"`
        args_list = ["add"] + args_list

    parser = argparse.ArgumentParser(
        prog="todo",
        description="Gerenciador de tarefas elegante e ultra-rápido para Termux e Linux.",
        epilog="""Exemplos:
  todo "Comprar café"
  todo add "Estudar Python" -p high -t dev,estudos -d "2026-10-30"
  todo
  todo done 1
  todo undo 1
  todo stats
  todo export --markdown > tarefas.md
""",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # ADD
    p_add = subparsers.add_parser("add", help="Adiciona uma nova tarefa")
    p_add.add_argument("title", nargs="+", help="Título da tarefa")
    p_add.add_argument("-p", "--priority", choices=["low", "medium", "high", "urgent"], default="medium", help="Prioridade")
    p_add.add_argument("-t", "--tags", default="", help="Tags separadas por vírgula (ex: dev,pessoal)")
    p_add.add_argument("-d", "--due", dest="due_date", help="Data limite (ex: 2026-10-31)")
    p_add.add_argument("-n", "--notes", default="", help="Anotações adicionais")

    # LIST
    p_list = subparsers.add_parser("list", aliases=["ls"], help="Lista tarefas")
    p_list.add_argument("-a", "--all", action="store_true", help="Exibe todas as tarefas (incluindo concluídas)")
    p_list.add_argument("-c", "--completed", action="store_true", help="Exibe apenas concluídas")
    p_list.add_argument("-p", "--priority", choices=["low", "medium", "high", "urgent", "all"], default=None, help="Filtrar por prioridade")
    p_list.add_argument("-t", "--tag", help="Filtrar por tag")
    p_list.add_argument("-s", "--search", help="Filtrar por termo de busca")

    # DONE
    p_done = subparsers.add_parser("done", aliases=["check"], help="Marca uma ou mais tarefas como concluídas")
    p_done.add_argument("ids", nargs="+", type=int, help="IDs das tarefas")

    # UNDO
    p_undo = subparsers.add_parser("undo", help="Reabre uma tarefa concluída")
    p_undo.add_argument("ids", nargs="+", type=int, help="IDs das tarefas")

    # EDIT
    p_edit = subparsers.add_parser("edit", help="Edita uma tarefa existente")
    p_edit.add_argument("id", type=int, help="ID da tarefa")
    p_edit.add_argument("--title", help="Novo título")
    p_edit.add_argument("-p", "--priority", choices=["low", "medium", "high", "urgent"], help="Nova prioridade")
    p_edit.add_argument("-t", "--tags", help="Novas tags")
    p_edit.add_argument("-d", "--due", dest="due_date", help="Nova data de vencimento")
    p_edit.add_argument("-n", "--notes", help="Novas anotações")

    # RM
    p_rm = subparsers.add_parser("rm", aliases=["delete"], help="Remove uma ou mais tarefas")
    p_rm.add_argument("ids", nargs="+", type=int, help="IDs das tarefas a remover")

    # SEARCH
    p_search = subparsers.add_parser("search", aliases=["find"], help="Busca tarefas por texto")
    p_search.add_argument("query", help="Termo de pesquisa")

    # CLEAR
    subparsers.add_parser("clear", help="Exclui definitivamente todas as tarefas concluídas")

    # STATS
    subparsers.add_parser("stats", help="Exibe métricas e produtividade")

    # EXPORT
    p_export = subparsers.add_parser("export", help="Exporta tarefas em Markdown ou JSON")
    p_export.add_argument("-m", "--markdown", action="store_true", help="Exporta como Markdown")
    p_export.add_argument("-j", "--json", action="store_true", help="Exporta como JSON")

    # If no arguments provided, default to listing pending tasks
    if not args_list:
        todos = database.list_todos(status="pending")
        print(format_todo_list(todos, title="Tarefas Pendentes"))
        return 0

    args = parser.parse_args(args_list)

    if args.command == "add":
        full_title = " ".join(args.title)
        todo_id = database.add_todo(
            title=full_title,
            priority=args.priority,
            tags=args.tags,
            due_date=args.due_date,
            notes=args.notes,
        )
        print(f"{green('✓')} Tarefa adicionada #{bold(str(todo_id))}: {bold(full_title)}")
        return 0

    elif args.command in ("list", "ls"):
        status = "all" if args.all else ("completed" if args.completed else "pending")
        todos = database.list_todos(
            status=status,
            priority=args.priority,
            tag=args.tag,
            search=args.search,
        )
        title_str = "Todas as Tarefas" if args.all else ("Tarefas Concluídas" if args.completed else "Tarefas Pendentes")
        print(format_todo_list(todos, title=title_str))
        return 0

    elif args.command in ("done", "check"):
        for t_id in args.ids:
            if database.complete_todo(t_id):
                print(f"{green('✓')} Tarefa #{t_id} marcada como concluída!")
            else:
                print(f"{red('✗')} Tarefa #{t_id} não encontrada.", file=sys.stderr)
        return 0

    elif args.command == "undo":
        for t_id in args.ids:
            if database.uncomplete_todo(t_id):
                print(f"{yellow('↺')} Tarefa #{t_id} reaberta como pendente.")
            else:
                print(f"{red('✗')} Tarefa #{t_id} não encontrada.", file=sys.stderr)
        return 0

    elif args.command == "edit":
        updated = database.update_todo(
            args.id,
            title=args.title,
            priority=args.priority,
            tags=args.tags,
            due_date=args.due_date,
            notes=args.notes,
        )
        if updated:
            print(f"{green('✓')} Tarefa #{args.id} atualizada com sucesso.")
        else:
            print(f"{red('✗')} Nenhuma alteração feita ou tarefa #{args.id} não encontrada.", file=sys.stderr)
        return 0

    elif args.command in ("rm", "delete"):
        for t_id in args.ids:
            if database.delete_todo(t_id):
                print(f"{green('✓')} Tarefa #{t_id} removida.")
            else:
                print(f"{red('✗')} Tarefa #{t_id} não encontrada.", file=sys.stderr)
        return 0

    elif args.command in ("search", "find"):
        todos = database.list_todos(status="all", search=args.query)
        print(format_todo_list(todos, title=f"Resultados para '{args.query}'"))
        return 0

    elif args.command == "clear":
        count = database.clear_completed()
        print(f"{green('✓')} {count} tarefa(s) concluída(s) removida(s).")
        return 0

    elif args.command == "stats":
        stats = database.get_stats()
        print(format_stats(stats))
        return 0

    elif args.command == "export":
        todos = database.list_todos(status="all")
        if args.json:
            print(format_json(todos))
        else:
            print(format_markdown(todos))
        return 0

    return 0


def main():
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
