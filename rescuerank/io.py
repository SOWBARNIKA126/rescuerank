from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from .models import Message


def load_messages(path) -> Tuple[List[Message], datetime]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    msgs = [Message(id=m["id"], sender=m["sender"], text=m["text"],
                    received_at=datetime.fromisoformat(m["received_at"]))
            for m in data["messages"]]
    return msgs, datetime.fromisoformat(data["now"])
