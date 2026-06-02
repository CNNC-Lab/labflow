"""Per-run context — lets an experiment learn its own output directory.

The launcher binds the current run's output directory for the duration of the
experiment function; the experiment reads it to write figures and other
artifacts beside the run's manifest:

    from labflow import current_output_dir
    fig.savefig(current_output_dir() / "fig.pdf")

This avoids changing the `fn(cfg) -> dict` experiment contract and avoids
chdir-ing the process (which would break config-relative paths).
"""

from __future__ import annotations

import contextvars
from pathlib import Path
from typing import Any

_current_output_dir: contextvars.ContextVar[Path | None] = contextvars.ContextVar(
    "labflow_current_output_dir", default=None
)


def current_output_dir() -> Path:
    """Return the output directory of the currently-running experiment.

    Raises RuntimeError if called outside a launcher-managed run.
    """
    d = _current_output_dir.get()
    if d is None:
        raise RuntimeError(
            "current_output_dir() called outside a running experiment; the "
            "launcher binds it around the experiment function."
        )
    return d


def set_output_dir(path: Path):
    """(launcher use) Bind the output dir for the current context; returns a token."""
    return _current_output_dir.set(path)


def reset_output_dir(token) -> None:
    """(launcher use) Restore the previous binding."""
    _current_output_dir.reset(token)


def config_label(config: Any) -> str | None:
    """Read an optional ``label`` from a config dataclass or dict (None if absent)."""
    if isinstance(config, dict):
        return config.get("label")
    return getattr(config, "label", None)