from __future__ import annotations

import os

_cpu_count = os.cpu_count()
MAX_CPU = 1 if _cpu_count is None else _cpu_count
DEFAULT_CPU = 1 if MAX_CPU == 1 else MAX_CPU - 1
