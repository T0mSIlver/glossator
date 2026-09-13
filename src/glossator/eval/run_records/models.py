"""Run statuses and the characters a run name may keep."""

from __future__ import annotations

import re

RUN_NAME_RE = re.compile(r"[^a-z0-9-]+")
STATUS_IN_PROGRESS = "in progress"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"
