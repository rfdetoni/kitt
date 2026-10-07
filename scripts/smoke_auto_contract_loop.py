from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from kitt.core.turn_command import TurnCommand
from kitt.core.turn_events import TurnCompleted
from kitt.goals.auto_contract import iter_automatic_contract
from kitt.goals.scheduler import GoalScheduler
from kitt.goals.service import GoalService
from kitt.history.database import HistoryDatabase


def _item(local_id: str, *, kind: str = "task", depends_on=None) -> dict:
    return {
        "local_id": local_id,
        "kind": kind,
        "title": f"Smoke {local_id}",
        "prompt": f"Execute {local_id}",
        "validation_prompt": f"Validate {local_id}",
        "success_criteria": [f"{local_id} passed"],
        "check_ids": [],
        "paths": [],
        "depends_on": list(depends_on or []),
    }


def _done_result() -> dict:
    return {
        "status": "ITEM_DONE",
        "tokens": 0,
        "cost": 0.0,
        "contract_evidence": {
            "changed_paths": [],
            "host_checks": {},
            "validation": {
                "verdict": "OK",
                "evidence": ["deterministic ecosystem smoke"],
                "issues": [],
            },
            "verification": {
                "success": True,
                "score": 1.0,
                "checks": [],
            },
        },
    }


async def _exercise() -> None:
    with tempfile.TemporaryDirectory() as workspace:
        db = HistoryDatabase(":memory:")
        try:
            with db.get_connection() as connection:
                connection.execute(
                    """INSERT INTO workspaces(
                        id,canonical_path_hash,display_name,created_at,last_opened_at
                    ) VALUES(?,?,?,?,?)""",
                    ("ws-smoke", "smoke", "smoke", 1.0, 1.0),
                )
                connection.execute(
                    """INSERT INTO conversations(
                        id,workspace_id,title,status,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?)""",
                    ("conv-smoke", "ws-smoke", "smoke", "ACTIVE", 1.0, 1.0),
                )

            goals = GoalService(db)
            attempts: dict[str, int] = {}
            calls: list[str] = []

            def execute(goal, **_kwargs):
                current = goals.current_item(goal.id)
                if current is None:
                    raise AssertionError("scheduler executed without a contract item")
                calls.append(current.local_id)
                attempts[current.local_id] = attempts.get(current.local_id, 0) + 1
                if current.local_id == "T01" and attempts[current.local_id] == 1:
                    return {
                        "status": "INCOMPLETE",
                        "tokens": 0,
                        "cost": 0.0,
                        "error": "intentional first-pass validation miss",
                    }
                return _done_result()

            scheduler = GoalScheduler(
                db,
                goals,
                runtime_step_executor=execute,
                poll_interval_seconds=0.01,
            )
            runtime = SimpleNamespace(
                canonical_root=Path(workspace),
                database=db,
                workspace_id="ws-smoke",
                goals=goals,
                goal_scheduler=scheduler,
            )
            command = TurnCommand(
                conversation_id="conv-smoke",
                prompt="exercise the durable automatic contract loop",
                mode="auto",
                turn_id="turn-smoke",
            )
            plan = [
                _item("T01"),
                _item("FINAL", kind="final", depends_on=["T01"]),
            ]

            await scheduler.start()
            try:
                with (
                    patch(
                        "kitt.goals.auto_contract.ContractPlanner.plan",
                        return_value=plan,
                    ),
                    patch(
                        "kitt.goals.auto_contract.render_contract",
                        return_value="contract complete",
                    ),
                ):
                    events = await asyncio.to_thread(
                        lambda: list(iter_automatic_contract(runtime, command))
                    )
            finally:
                await scheduler.stop()

            if calls != ["T01", "T01", "FINAL"]:
                raise AssertionError(f"unexpected contract execution sequence: {calls}")
            if not events or not isinstance(events[-1], TurnCompleted):
                raise AssertionError("automatic contract did not complete")
            if events[-1].response != "contract complete":
                raise AssertionError(f"unexpected final response: {events[-1].response!r}")
        finally:
            db.close()


def main() -> int:
    asyncio.run(_exercise())
    print("automatic durable contract behavioral smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
