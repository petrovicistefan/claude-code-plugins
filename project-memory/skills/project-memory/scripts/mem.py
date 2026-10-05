#!/usr/bin/env python3
"""Local project memory stored in .project-memory/memory.db (SQLite)."""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone

DIR = os.path.join(os.getcwd(), ".project-memory")
LEGACY = os.path.join(os.getcwd(), ".claude-mem")
if not os.path.exists(DIR) and os.path.exists(os.path.join(LEGACY, "memory.db")):
    DIR = LEGACY  # memories saved by earlier versions
DB = os.path.join(DIR, "memory.db")


def connect(create=False):
    if not os.path.exists(DB):
        if not create:
            sys.exit("No memories yet in this project (.project-memory/memory.db not found).")
        os.makedirs(DIR, exist_ok=True)
        with open(os.path.join(DIR, ".gitignore"), "w") as f:
            f.write("*\n")
    db = sqlite3.connect(DB)
    db.execute(
        "CREATE TABLE IF NOT EXISTS memories ("
        "key TEXT PRIMARY KEY, text TEXT NOT NULL, tag TEXT, updated TEXT NOT NULL)"
    )
    return db


def show(rows):
    if not rows:
        print("No matching memories.")
    for key, text, tag, updated in rows:
        label = f" [{tag}]" if tag else ""
        print(f"- {key}{label} ({updated[:10]}): {text}")


def main():
    p = argparse.ArgumentParser(prog="mem.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("key")
    a.add_argument("text", nargs="+")
    a.add_argument("--tag")
    sub.add_parser("get").add_argument("key")
    sub.add_parser("search").add_argument("words", nargs="+")
    sub.add_parser("list").add_argument("--tag")
    sub.add_parser("forget").add_argument("key")
    args = p.parse_args()

    if args.cmd == "add":
        db = connect(create=True)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        db.execute(
            "INSERT INTO memories(key, text, tag, updated) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET text=excluded.text, tag=excluded.tag, updated=excluded.updated",
            (args.key, " ".join(args.text), args.tag, now),
        )
        db.commit()
        print(f"Remembered {args.key}")
        return

    db = connect()
    cols = "key, text, tag, updated"
    if args.cmd == "get":
        show(db.execute(f"SELECT {cols} FROM memories WHERE key = ?", (args.key,)).fetchall())
    elif args.cmd == "search":
        where = " AND ".join(["(key || ' ' || text || ' ' || IFNULL(tag, '')) LIKE ?"] * len(args.words))
        params = [f"%{w}%" for w in args.words]
        show(db.execute(f"SELECT {cols} FROM memories WHERE {where} ORDER BY updated DESC", params).fetchall())
    elif args.cmd == "list":
        if args.tag:
            rows = db.execute(f"SELECT {cols} FROM memories WHERE tag = ? ORDER BY updated DESC", (args.tag,))
        else:
            rows = db.execute(f"SELECT {cols} FROM memories ORDER BY updated DESC")
        show(rows.fetchall())
    elif args.cmd == "forget":
        n = db.execute("DELETE FROM memories WHERE key = ?", (args.key,)).rowcount
        db.commit()
        print(f"Forgot {args.key}" if n else f"No memory named {args.key}")


if __name__ == "__main__":
    main()
