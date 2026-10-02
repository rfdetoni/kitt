from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class CatalogError(ValueError):
    pass


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    name: str
    repository: str
    description: str
    strategy: str
    order: int
    requires: tuple[str, ...]
    companions: tuple[str, ...]
    platforms: tuple[str, ...]
    prerequisites: tuple[str, ...]
    selectable: bool = True


@dataclass(frozen=True)
class Resolution:
    requested: tuple[str, ...]
    modules: tuple[ModuleSpec, ...]
    auto_selected_by: dict[str, tuple[str, ...]]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(module.id for module in self.modules)


class EcosystemCatalog:
    def __init__(self, payload: dict):
        if payload.get("schema_version") != 1:
            raise CatalogError("ecosystem schema_version must be 1")
        raw_modules = payload.get("modules")
        if not isinstance(raw_modules, dict) or not raw_modules:
            raise CatalogError("ecosystem modules must be a non-empty object")
        modules: dict[str, ModuleSpec] = {}
        repos: set[str] = set()
        for module_id, raw in raw_modules.items():
            if not isinstance(module_id, str) or not module_id:
                raise CatalogError("module ids must be non-empty strings")
            if not isinstance(raw, dict):
                raise CatalogError(f"module {module_id!r} must be an object")
            repository = str(raw.get("repository") or "")
            if not repository or "/" not in repository:
                raise CatalogError(f"module {module_id!r} has invalid repository")
            if repository in repos:
                raise CatalogError(f"repository {repository!r} is registered more than once")
            repos.add(repository)
            modules[module_id] = ModuleSpec(
                id=module_id,
                name=str(raw.get("name") or module_id),
                repository=repository,
                description=str(raw.get("description") or ""),
                strategy=str(raw.get("strategy") or ""),
                order=int(raw.get("order", 100)),
                selectable=bool(raw.get("selectable", True)),
                requires=tuple(str(v) for v in raw.get("requires", [])),
                companions=tuple(str(v) for v in raw.get("companions", [])),
                platforms=tuple(str(v) for v in raw.get("platforms", [])),
                prerequisites=tuple(str(v) for v in raw.get("prerequisites", [])),
            )

        for module in modules.values():
            for dependency in (*module.requires, *module.companions):
                if dependency not in modules:
                    raise CatalogError(
                        f"module {module.id!r} references unknown module {dependency!r}"
                    )
            if not module.strategy:
                raise CatalogError(f"module {module.id!r} has no install strategy")


        raw_presets = payload.get("presets") or {}
        if not isinstance(raw_presets, dict):
            raise CatalogError("presets must be an object")
        presets: dict[str, tuple[str, ...]] = {}
        preset_names: dict[str, str] = {}
        preset_descriptions: dict[str, str] = {}
        for preset_id, raw in raw_presets.items():
            if not isinstance(raw, dict):
                raise CatalogError(f"preset {preset_id!r} must be an object")
            members = tuple(str(v) for v in raw.get("modules", []))
            unknown = sorted(set(members) - set(modules))
            if unknown:
                raise CatalogError(f"preset {preset_id!r} references unknown modules {unknown}")
            presets[str(preset_id)] = members
            preset_names[str(preset_id)] = str(raw.get("name") or preset_id)
            preset_descriptions[str(preset_id)] = str(raw.get("description") or "")

        default_preset = str(payload.get("default_preset") or "")
        if default_preset and default_preset not in presets:
            raise CatalogError(f"default preset {default_preset!r} does not exist")

        self.name = str(payload.get("name") or "K.I.T.T. Ecosystem")
        self.modules = modules
        self.presets = presets
        self.preset_names = preset_names
        self.preset_descriptions = preset_descriptions
        self.default_preset = default_preset

    @classmethod
    def load(cls, root: str | Path) -> "EcosystemCatalog":
        root_path = Path(root)
        payload = json.loads((root_path / "ecosystem.json").read_text(encoding="utf-8"))
        return cls(payload)

    def preset(self, preset_id: str) -> tuple[str, ...]:
        try:
            return self.presets[preset_id]
        except KeyError as exc:
            raise CatalogError(
                f"unknown preset {preset_id!r}; choose one of: {', '.join(sorted(self.presets))}"
            ) from exc

    def resolve(
        self,
        requested: Iterable[str],
        *,
        include_companions: bool = True,
    ) -> Resolution:
        requested_ids = tuple(dict.fromkeys(str(v).strip() for v in requested if str(v).strip()))
        unknown = sorted(set(requested_ids) - set(self.modules))
        if unknown:
            raise CatalogError(
                f"unknown modules {unknown}; choose from: {', '.join(sorted(self.modules))}"
            )

        internal = [module_id for module_id in requested_ids if not self.modules[module_id].selectable]
        if internal:
            raise CatalogError(
                "internal dependency modules cannot be selected directly: "
                + ", ".join(sorted(internal))
                + "; select a public module or preset that composes them"
            )

        selected = set(requested_ids)
        auto_by: dict[str, set[str]] = {}
        queue = list(requested_ids)
        while queue:
            parent_id = queue.pop(0)
            parent = self.modules[parent_id]
            dependencies = parent.requires
            if include_companions:
                dependencies = (*dependencies, *parent.companions)
            for dependency in dependencies:
                if dependency not in requested_ids:
                    auto_by.setdefault(dependency, set()).add(parent_id)
                if dependency not in selected:
                    selected.add(dependency)
                    queue.append(dependency)

        ordered = tuple(
            sorted(
                (self.modules[module_id] for module_id in selected),
                key=lambda module: (module.order, module.id),
            )
        )
        reasons = {key: tuple(sorted(value)) for key, value in auto_by.items()}
        return Resolution(requested=requested_ids, modules=ordered, auto_selected_by=reasons)

    def resolve_ref(
        self,
        module: ModuleSpec,
        override_ref: str | None = None,
        component_refs: dict[str, str] | None = None,
    ) -> str:
        """Resolve one component ref for edge or immutable release installation."""
        requested = (override_ref or "main").strip() or "main"
        if requested != "main":
            return requested
        if component_refs is not None:
            try:
                return component_refs[module.id]
            except KeyError as exc:
                raise CatalogError(
                    f"release manifest has no ref for component {module.id!r}"
                ) from exc
        return "main"
