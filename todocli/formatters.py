"""Formatting and visual presentation helpers for Todo CLI."""

from __future__ import annotations
import sys
import json
from typing import List, Dict, Any


def _is_tty() -> bool:
    return sys.stdout.isatty()


def colorize(text: str, code: str) -> str:
    if not _is_tty():
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return colorize(text, "1")


def dim(text: str) -> str:
    return colorize(text, "90")


def red(text: str) -> str:
    return colorize(text, "91")


def green(text: str) -> str:
    return colorize(text, "92")


def yellow(text: str) -> str:
    return colorize(text, "93")


def blue(text: str) -> str:
    return colorize(text, "94")


def cyan(text: str) -> str:
    return colorize(text, "96")


PRIORITY_BADGES = {
    "urgent": lambda: bold(red("🔥 URGENTE")),
    "high": lambda: yellow("⚡ ALTA"),
    "medium": lambda: blue("🔹 MÉDIA"),
    "low": lambda: dim("▫️ BAIXA"),
}


def format_todo_item(todo: Dict[str, Any], show_details: bool = False) -> str:
    t_id = todo["id"]
    status = todo["status"]
    title = todo["title"]
    priority = todo.get("priority", "medium")
    tags = todo.get("tags", "")
    due_date = todo.get("due_date")
    notes = todo.get("notes")

    # Status checkbox
    if status == "completed":
        check = green("[✓]")
        title_str = dim(f"\033[9m{title}\033[0m" if _is_tty() else title)
    else:
        check = "[ ]"
        title_str = bold(title)

    badge = PRIORITY_BADGES.get(priority, lambda: "")()

    tags_str = ""
    if tags:
        tag_list = [f"#{t.strip()}" for t in tags.split(",") if t.strip()]
        tags_str = " " + cyan(" ".join(tag_list))

    due_str = ""
    if due_date:
        due_str = f" 📅 {yellow(due_date)}"

    line = f"{dim(f'{t_id:2d}.')} {check} {title_str} {badge}{tags_str}{due_str}"

    if show_details and notes:
        line += f"\n     {dim('↳ Nota:')} {notes}"

    return line


def format_todo_list(todos: List[Dict[str, Any]], title: str = "Minhas Tarefas") -> str:
    if not todos:
        return dim("✨ Nenhuma tarefa encontrada.")

    lines = [bold(f"📋 {title} ({len(todos)}):"), ""]
    for todo in todos:
        lines.append("  " + format_todo_item(todo, show_details=True))
    lines.append("")
    return "\n".join(lines)


def format_stats(stats: Dict[str, Any]) -> str:
    total = stats["total"]
    completed = stats["completed"]
    pending = stats["pending"]
    rate = stats["completion_rate"]
    urgent = stats["urgent_pending"]
    high = stats["high_pending"]

    # Progress bar (20 chars)
    filled = int(rate / 5)
    bar = green("█" * filled) + dim("░" * (20 - filled))

    lines = [
        bold("📊 Estatísticas de Produtividade:"),
        f"  Progresso: [{bar}] {bold(f'{rate:.1f}%')}",
        f"  Total de tarefas: {bold(str(total))}",
        f"  Concluídas:       {green(str(completed))}",
        f"  Pendentes:        {yellow(str(pending))}",
    ]
    if urgent > 0:
        lines.append(f"  🔥 Pendências urgentes: {red(str(urgent))}")
    if high > 0:
        lines.append(f"  ⚡ Pendências de alta prioridade: {yellow(str(high))}")

    return "\n".join(lines)


def format_markdown(todos: List[Dict[str, Any]]) -> str:
    lines = ["# Minhas Tarefas", ""]
    for todo in todos:
        check = "x" if todo["status"] == "completed" else " "
        priority = f"**[{todo['priority'].upper()}]**" if todo.get("priority") else ""
        tags = " " + " ".join(f"`#{t.strip()}`" for t in todo["tags"].split(",") if t.strip()) if todo.get("tags") else ""
        due = f" *(Prazo: {todo['due_date']})*" if todo.get("due_date") else ""
        lines.append(f"- [{check}] {todo['title']} {priority}{tags}{due}")
        if todo.get("notes"):
            lines.append(f"  > {todo['notes']}")
    return "\n".join(lines)


def format_json(todos: List[Dict[str, Any]]) -> str:
    return json.dumps(todos, indent=2, ensure_ascii=False)
