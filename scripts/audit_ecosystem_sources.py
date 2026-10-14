#!/usr/bin/env python3
"""Read-only source inventory across seven repositories; findings are candidates."""
from __future__ import annotations
import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path

REPOS = ("kitt-agent-cli", "kitt-reverse-proxy", "kitt-protocol",
         "kitt-memory", "kitt-toolbox", "kitt-assistant", "kitt-ai-workers")
SUFFIXES = {".py", ".ts", ".tsx", ".js", ".rs"}
SKIP = {".git", "node_modules", "target", "dist", "dist-test", ".venv",
        "__pycache__", "vendor", ".test-sdk"}
TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
FUNCTION = re.compile(r"(?m)^[ \t]*(?:(?:export|default|async|pub(?:\([^)]*\))?)\s+)*(?:function|fn)\s+([A-Za-z_]\w*)\s*[(<]")
CLASS = re.compile(r"(?m)^[ \t]*(?:(?:export|default|abstract)\s+)*(?:class|struct|impl)\s+([A-Za-z_]\w*)")
BRANCH = re.compile(r"\b(?:if|else\s+if|match|for|while|catch|switch|case)\b|&&|\|\|")


def python_nodes(source, repo, path):
    methods, classes, errors = [], [], []
    try:
        tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError) as exc:
        return methods, classes, [{"repo": repo, "path": path, "error": str(exc)}]

    def walk(node, owner=""):
        for item in getattr(node, "body", ()):
            if isinstance(item, ast.ClassDef):
                direct = [x for x in item.body
                          if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes.append({"repo": repo, "path": path, "line": item.lineno,
                                "name": item.name, "lines": (item.end_lineno or item.lineno) - item.lineno + 1,
                                "methods": len(direct), "language": "python"})
                walk(item, item.name)
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                branches = 0
                stack = list(ast.iter_child_nodes(item))
                while stack:
                    child = stack.pop()
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                        continue
                    if isinstance(child, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.Try,
                                          ast.Match, ast.ExceptHandler)):
                        branches += 1
                    elif isinstance(child, ast.BoolOp):
                        branches += max(0, len(child.values) - 1)
                    stack.extend(ast.iter_child_nodes(child))
                methods.append({"repo": repo, "path": path, "line": item.lineno,
                                "name": owner + "." + item.name if owner else item.name,
                                "symbol": item.name, "lines": (item.end_lineno or item.lineno) - item.lineno + 1,
                                "branches": branches, "language": "python"})
                walk(item, owner)
    walk(tree)
    return methods, classes, errors


def block_lines(source, start):
    # Lexical screening for Rust and TS/JS; exact parser needed before a fix.
    opening = source.find("{", start, min(len(source), start + 500))
    if opening < 0:
        return 1
    depth = 0
    for i in range(opening, min(len(source), opening + 200_000)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source.count("\n", start, i) + 1
    return 1


def lexical_nodes(source, repo, path, language):
    methods, classes = [], []
    for match in FUNCTION.finditer(source):
        size = block_lines(source, match.end())
        methods.append({"repo": repo, "path": path, "line": source.count("\n", 0, match.start()) + 1,
                        "name": match[1], "symbol": match[1], "lines": size,
                        "branches": len(BRANCH.findall(source[match.start():match.start() + min(10000, size * 70)])),
                        "language": language, "lexical_estimate": True})
    for match in CLASS.finditer(source):
        classes.append({"repo": repo, "path": path,
                        "line": source.count("\n", 0, match.start()) + 1,
                        "name": match[1], "lines": block_lines(source, match.end()),
                        "methods": None, "language": language, "lexical_estimate": True})
    return methods, classes


def inventory(base):
    files, methods, classes, errors = [], [], [], []
    uses = Counter()
    for repo in REPOS:
        root = base / repo
        if not root.is_dir():
            raise FileNotFoundError("Missing checkout: " + str(root))
        paths = sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink()
                       and p.suffix in SUFFIXES and not SKIP.intersection(p.parts))
        for path in paths:
            rel = path.relative_to(root).as_posix()
            try:
                source = path.read_text(encoding="utf-8")
            except (UnicodeError, OSError) as exc:
                errors.append({"repo": repo, "path": rel, "error": str(exc)})
                continue
            uses.update(TOKEN.findall(source))
            files.append({"repo": repo, "path": rel, "lines": source.count("\n") + 1,
                          "bytes": len(source.encode("utf-8")), "language": path.suffix.lstrip(".")})
            if path.suffix == ".py":
                found, decl, parse_errors = python_nodes(source, repo, rel)
                errors.extend(parse_errors)
            else:
                found, decl = lexical_nodes(source, repo, rel, path.suffix.lstrip("."))
            methods.extend(found)
            classes.extend(decl)
    brains = sorted((m for m in methods if m["lines"] >= 180 or
                     (m["language"] == "python" and m["lines"] >= 90 and m["branches"] >= 10)),
                    key=lambda x: (x["lines"], x["branches"]), reverse=True)
    gods = sorted((c for c in classes if c["lines"] >= 500 or
                   (c["methods"] is not None and c["methods"] >= 30)),
                  key=lambda x: x["lines"], reverse=True)
    unused = sorted(({**m, "occurrences": uses[m["symbol"]]}
                     for m in methods if m["language"] == "python"
                     and m["symbol"].startswith("_") and not m["symbol"].startswith("__")
                     and uses[m["symbol"]] == 1),
                    key=lambda x: (x["repo"], x["path"], x["line"]))
    return {"methodology": "Full inventory; Python AST; lexical Rust/TS/JS screening; no dead-code proof.",
            "repositories": list(REPOS), "file_count": len(files), "files": files,
            "methods": methods, "classes": classes, "brain_candidates": brains,
            "god_candidates": gods, "unreferenced_private_candidates": unused,
            "parse_errors": errors}


def report(data):
    lines = ["# KITT: auditoria integral de fontes", "",
             "Todos os arquivos-fonte legíveis dos sete checkouts são inventariados. "
             "Resultados são triagem, não prova de código morto; reflection, plugins, "
             "macros e entrada dinâmica exigem rastreamento adicional.",
             "", "| Repositório | Arquivos | Linhas |", "|---|---:|---:|"]
    for repo in REPOS:
        fs = [f for f in data["files"] if f["repo"] == repo]
        lines.append("| {} | {} | {} |".format(repo, len(fs), sum(f["lines"] for f in fs)))
    for title, key in [("Classes concentradas", "god_candidates"),
                       ("Funções extensas/decisões", "brain_candidates"),
                       ("Privados com uma ocorrência lexical", "unreferenced_private_candidates")]:
        items = data[key]
        lines.extend(("", "## " + title, "", str(len(items)) + " candidatos; top 30 abaixo.",
                      "", "| Local | Símbolo | Linhas |", "|---|---|---:|"))
        for item in items[:30]:
            lines.append("| {}/{}:{} | {} | {} |".format(
                item["repo"], item["path"], item["line"], item["name"], item["lines"]))
    lines.extend(("", "## Limitações", "",
                  "- AST Python mede funções/classes; Rust, TS/JS são estimativas lexicais.",
                  "- Uma ocorrência do identificador não significa código morto.",
                  "- Remover somente após verificar consumidores externos e testes de integração.",
                  "- Arquivos ilegíveis ou Python inválido: {}.".format(len(data["parse_errors"]))))
    return "\n".join(lines) + "\n"


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--base", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    cli.add_argument("--markdown", type=Path, required=True)
    args = cli.parse_args()
    data = inventory(args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(report(data), encoding="utf-8")
    print("Audited {} files; GOD candidates {}, brain candidates {}, lexical-private candidates {}, read/parse errors {}.".format(
        data["file_count"], len(data["god_candidates"]), len(data["brain_candidates"]),
        len(data["unreferenced_private_candidates"]), len(data["parse_errors"])))


if __name__ == "__main__":
    main()
