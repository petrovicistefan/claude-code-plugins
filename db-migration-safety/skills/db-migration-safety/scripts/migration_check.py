#!/usr/bin/env python3
"""Check database migration files for operations that lock tables or lose data.

  migration_check.py                    find migration folders under the current folder
  migration_check.py <file-or-dir> ...  scan specific files or folders

Reads raw SQL, Rails, Alembic, Knex, Sequelize, TypeORM, Django and Prisma
migrations as text. Each finding names the file, line, risk and a safer pattern.
"""
import os
import re
import sys

MIG_DIR_HINTS = ("migrations", "migrate", "alembic/versions", "prisma/migrations", "db/migrate", "flyway", "liquibase")
EXTS = (".sql", ".py", ".rb", ".js", ".ts")
SKIP = {"node_modules", ".git", "venv", ".venv", "__pycache__"}

RULES = [
    (r"\bdrop\s+table\b", "high", "DROP TABLE loses data and breaks code that still reads it. Deploy the code change first, drop later in a separate migration."),
    (r"\bdrop\s+column\b|remove_column|drop_column|dropColumn", "high", "Dropping a column breaks running app versions. Stop using it in code first (expand/contract), then drop."),
    (r"\btruncate\b", "high", "TRUNCATE removes all rows and takes an exclusive lock."),
    (r"\brename\s+(column|to)\b|rename_column|rename_table|renameColumn|renameTable|\balter\s+table\s+\S+\s+rename\b", "high", "Renames break old code while a deploy rolls out. Add the new name, copy data, switch code, remove the old name."),
    (r"alter\s+table[^;]*add\s+(column\s+)?[^;]*\bnot\s+null\b(?![^;]*\bdefault\b)", "high", "Adding a NOT NULL column without a DEFAULT fails on a table with rows. Add it nullable, backfill, then set NOT NULL."),
    (r"add_column[^\n]*null:\s*false(?![^\n]*default)|addColumn[^\n]*allowNull:\s*false(?![^\n]*defaultValue)", "high", "NOT NULL column without a default fails on a table with rows. Add nullable, backfill, then tighten."),
    (r"\bcreate\s+(unique\s+)?index\b(?![^;]*\bconcurrently\b)", "medium", "On PostgreSQL, CREATE INDEX blocks writes. Use CREATE INDEX CONCURRENTLY (outside a transaction). Ignore if the table is new or small."),
    (r"add_index(?![^\n]*algorithm:\s*:concurrently)|op\.create_index(?![^\n]*concurrently)", "medium", "Index build can block writes on PostgreSQL. Use algorithm: :concurrently / postgresql_concurrently=True."),
    (r"alter\s+(column\s+)?[^;]*\b(type|set\s+data\s+type)\b", "high", "Changing a column type rewrites the table under an exclusive lock. Add a new column, backfill in batches, swap."),
    (r"change_column\b|alterColumn|op\.alter_column[^\n]*type_", "high", "Changing a column type can rewrite the table under a lock."),
    (r"add\s+constraint[^;]*\bforeign\s+key\b(?![^;]*\bnot\s+valid\b)|add_foreign_key(?![^\n]*validate:\s*false)", "medium", "Adding a foreign key validates every row under a lock. Add it NOT VALID, then VALIDATE CONSTRAINT separately."),
    (r"add\s+constraint[^;]*\bcheck\b(?![^;]*\bnot\s+valid\b)", "medium", "CHECK constraints scan the whole table. Add NOT VALID then VALIDATE."),
    (r"\block\s+table\b", "high", "Explicit table lock."),
    (r"\bdelete\s+from\s+\w+\s*;", "high", "DELETE without WHERE removes every row."),
    (r"\bupdate\s+\w+\s+set\b(?![^;]*\bwhere\b)[^;]*;", "medium", "UPDATE without WHERE rewrites every row in one transaction. Backfill in batches."),
    (r"\bset\s+not\s+null\b", "medium", "SET NOT NULL scans the table under a lock. On PostgreSQL 12+, add a validated CHECK (col IS NOT NULL) first."),
    (r"\bdrop\s+(index|constraint|schema|database)\b", "medium", "Destructive change. Confirm nothing depends on it."),
]


def migration_files(args):
    for a in args or ["."]:
        if os.path.isfile(a):
            yield a
            continue
        for root, dirs, files in os.walk(a):
            dirs[:] = [d for d in dirs if d not in SKIP]
            norm = root.replace("\\", "/")
            if args or any(h in norm for h in MIG_DIR_HINTS):
                for f in sorted(files):
                    if f.endswith(EXTS):
                        yield os.path.join(root, f)


def main():
    files = list(migration_files(sys.argv[1:]))
    if not files:
        print("No migration files found. Pass a file or folder.")
        return 0
    total, high = 0, 0
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        has_down = bool(re.search(r"\bdef\s+down\b|\bdown\s*[:=(]|exports\.down|def\s+downgrade|--\s*\+goose\s+down|\bundo\b|revert", text, re.I))
        is_rollbackable = path.endswith(".sql") or has_down
        for rx, sev, msg in RULES:
            for m in re.finditer(rx, text, re.I | re.S):
                line = text.count("\n", 0, m.start()) + 1
                print(f"[{sev.upper():6}] {path}:{line}  {msg}")
                total += 1
                high += sev == "high"
        if not is_rollbackable:
            print(f"[MEDIUM] {path}:1  no down/rollback step found. Write one, or note that this change is irreversible.")
            total += 1
    print(f"\n{len(files)} files, {total} findings, {high} high risk")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
