from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(root: Path) -> dict:
    return json.loads((root / "ecosystem.json").read_text(encoding="utf-8"))


def _validate_graph(modules: dict[str, dict]) -> None:
    known = set(modules)
    for module_id, module in modules.items():
        for field in ("requires", "companions"):
            refs = tuple(module.get(field, ()))
            unknown = sorted(set(refs) - known)
            if unknown:
                raise ValueError(f"{module_id}.{field} references unknown modules: {unknown}")
            if module_id in refs:
                raise ValueError(f"{module_id}.{field} cannot reference itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module_id: str, trail: tuple[str, ...]) -> None:
        if module_id in visited:
            return
        if module_id in visiting:
            cycle = " -> ".join((*trail, module_id))
            raise ValueError(f"requires dependency cycle: {cycle}")
        visiting.add(module_id)
        for dependency in modules[module_id].get("requires", ()):
            visit(dependency, (*trail, module_id))
        visiting.remove(module_id)
        visited.add(module_id)

    for module_id in modules:
        visit(module_id, ())


def validate(root: str | Path = ROOT) -> dict[str, str]:
    root = Path(root)
    payload = _load(root)
    modules = payload.get("modules")
    if not isinstance(modules, dict) or not modules:
        raise ValueError("ecosystem.json must define modules")

    repositories: dict[str, str] = {}
    for module_id, module in modules.items():
        repository = str(module.get("repository", "")).strip()
        if not repository:
            raise ValueError(f"{module_id} has no repository")
        previous = repositories.setdefault(repository, module_id)
        if previous != module_id:
            raise ValueError(
                f"repository {repository} is owned by both {previous} and {module_id}"
            )

    _validate_graph(modules)

    architecture = (root / "docs" / "ECOSYSTEM_ARCHITECTURE.md").read_text(
        encoding="utf-8"
    )
    missing = sorted(repo for repo in repositories if f"`{repo}`" not in architecture)
    if missing:
        raise ValueError(
            "ecosystem architecture document is missing repositories: "
            + ", ".join(missing)
        )

    return {module_id: module["repository"] for module_id, module in modules.items()}


def main() -> int:
    try:
        owners = validate(sys.argv[1] if len(sys.argv) > 1 else ROOT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ecosystem architecture invalid: {exc}", file=sys.stderr)
        return 1
    for module_id, repository in sorted(owners.items()):
        print(f"{module_id}: {repository}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
