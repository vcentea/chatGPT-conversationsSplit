#!/usr/bin/env python3
"""
Split a ChatGPT export JSON into 10 .txt files.

Usage:
    python split_chatgpt_json.py <chatgpt_export.json>  [--parts 20]

The script:
  • walks every conversation in the file (the export is usually a list);
  • extracts messages where content_type == "text" and parts are non-empty;
  • formats each as:

        USER:
        What time is it?

        ASSISTANT:
        It's 8 PM in Luxembourg…

  • distributes the messages evenly so each output file has content.
"""

import json
import math
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def collect_text_messages(conversation):
    """Return a list of formatted strings for one conversation."""
    msgs = []
    for node in conversation.get("mapping", {}).values():
        msg = node.get("message")
        if not msg:
            continue

        content = msg.get("content", {})
        if content.get("content_type") != "text":
            continue

        parts = [p.strip() for p in content.get("parts", []) if p.strip()]
        if not parts:
            continue

        role = msg["author"]["role"].upper()
        stamp = msg.get("create_time") or 0  # for ordering
        msgs.append(
            (stamp, f"{role}:\n" + "\n".join(parts) + "\n")  # formatted chunk
        )

    # chronological order
    msgs.sort(key=lambda t: t[0])
    # return only the text
    return [m[1] for m in msgs]


def even_split(items, num_parts):
    """Split `items` into num_parts lists; every part gets ≥ 1 item (if possible)."""
    total = len(items)
    if total == 0:
        return [[] for _ in range(num_parts)]

    size = math.ceil(total / num_parts)
    parts = [
        items[i * size : min((i + 1) * size, total)] for i in range(num_parts)
    ]
    # pad with empties if needed
    while len(parts) < num_parts:
        parts.append([])
    return parts


# --------------------------------------------------------------------------- #
# main function
# --------------------------------------------------------------------------- #
def split_chatgpt_json(path, num_parts=20):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    # export is usually a list; if not, wrap in list
    conversations = data if isinstance(data, list) else [data]

    # gather messages from every conversation
    messages = []
    for conv in conversations:
        messages.extend(collect_text_messages(conv))

    if not messages:
        print("No textual messages found – nothing to split.")
        return

    chunks = even_split(messages, num_parts)

    base = path.stem
    out_dir = path.parent

    for idx, chunk in enumerate(chunks, start=1):
        target = out_dir / f"{base}_part{idx:02d}.txt"
        with target.open("w", encoding="utf-8") as fh:
            fh.write("".join(chunk).rstrip() + "\n")

    print(f"✅ Split {len(messages)} messages into {num_parts} parts in {out_dir}")


# --------------------------------------------------------------------------- #
# CLI entry
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_chatgpt_json.py <chatgpt_export.json> [--parts 10]")
        sys.exit(1)

    json_file = sys.argv[1]
    num_parts = 10

    if "--parts" in sys.argv:
        try:
            num_parts = int(sys.argv[sys.argv.index("--parts") + 1])
        except (IndexError, ValueError):
            print("`--parts` expects an integer.")
            sys.exit(1)

    split_chatgpt_json(json_file, num_parts)
