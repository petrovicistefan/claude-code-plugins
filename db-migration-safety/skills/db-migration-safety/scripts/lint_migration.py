#!/usr/bin/env python3
"""Check SQL migration files for operations that lock tables, lose data or
break the running application.

Standard library only. Reads the files you name, runs nothing else and never
connects to a database.

Usage: lint_migration.py [--dialect postgres|mysql] [--json] <file.sql> [...]
Exit code 1 when a HIGH finding exists, so it can gate CI.
"""
import json
import re
import sys

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def strip_comments(sql):
    """Blank out comments and string literals but keep line breaks, so line numbers stay right."""
    out, i, n = [], 0, len(sql)
    while i < n:
        c = sql[i]
        if sql.startswith("--", i):
            while i < n and sql[i] != "\n":
                out.append(" ")
                i += 1
        elif sql.startswith("/*", i):
            end = sql.find("*/", i + 2)
            end = n if end == -1 else end + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in sql[i:end]))
            i = end
        elif c == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'" and sql[j + 1:j + 2] == "'":
                    j += 2
                    continue
                if sql[j] == "'":
                    break
                j += 1
            out.append("'" + "".join("\n" if ch == "\n" else " " for ch in sql[i + 1:j]) + "'")
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def split_statements(clean):
    """Yield (start_line, statement_text) split on semicolons."""
    stmts, buf, start_line, line = [], [], None, 1
    for ch in clean:
        if start_line is None and not ch.isspace():
            start_line = line
        if ch == "\n":
            line += 1
        if ch == ";":
            text = "".join(buf).strip()
            if text:
                stmts.append((start_line or line, text))
            buf, start_line = [], None
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        stmts.append((start_line or line, tail))
    return stmts


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


VOLATILE = re.compile(r"\b(random\s*\(|gen_random_uuid\s*\(|uuid_generate_v\d\s*\(|clock_timestamp\s*\(|"
                      r"nextval\s*\(|timeofday\s*\()", re.I)


def lint_statement(stmt, dialect, created_tables):
    """Return a list of (rule, severity, message, fix) for one statement."""
    s = norm(stmt)
    low = s.lower()
    found = []

    def add(rule, sev, msg, fix):
        found.append((rule, sev, msg, fix))

    m = re.match(r"create\s+(?:temp(?:orary)?\s+)?table\s+(?:if\s+not\s+exists\s+)?([\w.\"`]+)", low)
    if m:
        created_tables.add(m.group(1).strip('"`'))

    if re.match(r"drop\s+table", low):
        add("drop-table", "HIGH", "DROP TABLE deletes data and cannot be undone by rolling back a deploy.",
            "Stop reading and writing the table in code first and deploy that. Rename it to <name>_deprecated, "
            "drop it in a later release after a backup.")
    if re.match(r"drop\s+(schema|database)", low):
        add("drop-schema", "HIGH", "DROP SCHEMA or DATABASE deletes everything in it.",
            "Take a backup and confirm the target. Never run this as part of an automatic deploy.")
    if re.match(r"truncate", low):
        add("truncate", "HIGH", "TRUNCATE removes every row and takes an ACCESS EXCLUSIVE lock.",
            "Confirm this is meant for the target environment, and back up first.")
    if re.match(r"(delete\s+from|update)\b", low) and not re.search(r"\bwhere\b", low):
        verb = "DELETE" if low.startswith("delete") else "UPDATE"
        add("no-where", "HIGH", "%s without WHERE changes every row." % verb,
            "Add a WHERE clause, or batch the change (for example 1,000-10,000 rows per transaction) on large tables.")

    if re.match(r"alter\s+table", low):
        if re.search(r"\bdrop\s+column\b", low):
            add("drop-column", "HIGH", "DROP COLUMN deletes data, and running code that still reads the column will fail.",
                "Expand and contract: deploy code that no longer uses the column, then drop it in a later migration after a backup.")
        if re.search(r"\brename\s+(column|to)\b", low) or re.search(r"\brename\s+\w+\s+to\b", low):
            add("rename", "HIGH", "Renaming a column or table breaks the old version of the app while a deploy is rolling out.",
                "Add the new name, copy data, switch the code, then drop the old name in a later release.")
        if re.search(r"\badd\s+(column\s+)?(?!constraint|primary|unique|foreign|check|index|key)[\w\"`]+\s+[^,]*\bnot\s+null\b", low) \
                and not re.search(r"\bdefault\b", low):
            add("add-not-null-no-default", "HIGH",
                "ADD COLUMN ... NOT NULL without a DEFAULT fails when the table already has rows.",
                "Add the column as nullable, backfill in batches, then add NOT NULL (see set-not-null for the safe way), "
                "or give it a constant DEFAULT.")
        if re.search(r"\badd\s+(column\s+)?[\w\"`]+\s+[^,]*\bdefault\b", low) and VOLATILE.search(s):
            add("add-volatile-default", "MEDIUM",
                "A volatile DEFAULT (random(), gen_random_uuid(), clock_timestamp(), nextval()) rewrites the whole table under an exclusive lock.",
                "Add the column without a default, set the default for new rows, and backfill existing rows in batches.")
        if re.search(r"\balter\s+(column\s+)?[\w\"`]+\s+(set\s+data\s+)?type\b", low) or \
                re.search(r"\bmodify\s+(column\s+)?[\w\"`]+\s+\w+", low) and dialect == "mysql":
            add("alter-type", "HIGH",
                "Changing a column type usually rewrites the table and blocks reads and writes while it runs.",
                "Add a new column of the new type, backfill in batches, switch the code, drop the old column later. "
                "Widening a varchar in Postgres 9.2+ and similar binary-compatible changes do not rewrite; check before assuming.")
        if dialect == "postgres":
            if re.search(r"\bset\s+not\s+null\b", low):
                add("set-not-null", "MEDIUM", "SET NOT NULL scans the whole table while holding an ACCESS EXCLUSIVE lock.",
                    "On Postgres 12+: ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID, VALIDATE CONSTRAINT, then SET NOT NULL, then drop the check.")
            if re.search(r"\badd\s+(constraint\s+[\w\"`]+\s+)?foreign\s+key\b", low) or \
                    (re.search(r"\badd\s+(column\s+)?[\w\"`]+\s+[^,]*\breferences\b", low)):
                if not re.search(r"\bnot\s+valid\b", low):
                    add("add-fk-validated", "MEDIUM",
                        "Adding a foreign key validates every row while locking both tables.",
                        "ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID, then ALTER TABLE ... VALIDATE CONSTRAINT in a separate step.")
            if re.search(r"\badd\s+(constraint\s+[\w\"`]+\s+)?check\b", low) and not re.search(r"\bnot\s+valid\b", low):
                add("add-check-validated", "MEDIUM", "Adding a CHECK constraint scans the whole table under a strong lock.",
                    "ADD CONSTRAINT ... CHECK (...) NOT VALID, then VALIDATE CONSTRAINT separately.")
            if re.search(r"\badd\s+(constraint\s+[\w\"`]+\s+)?(unique|primary\s+key)\b", low) and \
                    not re.search(r"\busing\s+index\b", low):
                add("add-unique", "MEDIUM", "Adding a UNIQUE or PRIMARY KEY constraint builds an index while holding a lock.",
                    "CREATE UNIQUE INDEX CONCURRENTLY first, then ADD CONSTRAINT ... USING INDEX.")

    m = re.match(r"create\s+(unique\s+)?index\s+(concurrently\s+)?(?:if\s+not\s+exists\s+)?[\w\"`.]*\s*on\s+(?:only\s+)?([\w.\"`]+)", low)
    if m:
        table = m.group(3).strip('"`')
        if table not in created_tables:
            if dialect == "postgres" and not m.group(2):
                add("index-not-concurrent", "HIGH",
                    "CREATE INDEX without CONCURRENTLY blocks writes to the table until it finishes.",
                    "Use CREATE INDEX CONCURRENTLY. It cannot run inside a transaction, so disable the migration's "
                    "transaction (Django atomic = False, Alembic autocommit_block, Flyway executeInTransaction=false).")
            elif dialect == "mysql" and not re.search(r"\balgorithm\s*=", low):
                add("index-no-algorithm", "MEDIUM", "Without ALGORITHM and LOCK, MySQL may pick a method that blocks writes.",
                    "Add ALGORITHM=INPLACE, LOCK=NONE so it fails fast instead of blocking if it cannot do that.")
    if dialect == "postgres" and re.match(r"drop\s+index\s+(?!concurrently)", low):
        add("drop-index-lock", "MEDIUM", "DROP INDEX without CONCURRENTLY takes a lock that waits behind running queries.",
            "Use DROP INDEX CONCURRENTLY, outside a transaction.")
    if dialect == "postgres" and re.match(r"(reindex|cluster|vacuum\s+full)\b", low) and "concurrently" not in low:
        add("heavy-maintenance", "HIGH", "REINDEX, CLUSTER and VACUUM FULL rewrite data under a lock that blocks the table.",
            "Run REINDEX ... CONCURRENTLY (Postgres 12+), or schedule it for a maintenance window.")
    return found


def lint_file(path, dialect):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    clean = strip_comments(raw)
    created, findings = set(), []
    stmts = split_statements(clean)
    for line, stmt in stmts:
        for rule, sev, msg, fix in lint_statement(stmt, dialect, created):
            findings.append({"file": path, "line": line, "rule": rule, "severity": sev,
                             "message": msg, "fix": fix, "sql": norm(stmt)[:140]})
    has_alter = any(re.match(r"alter\s+table", norm(s).lower()) for _, s in stmts)
    if dialect == "postgres" and has_alter and not re.search(r"lock_timeout", clean, re.I):
        findings.append({"file": path, "line": 1, "rule": "no-lock-timeout", "severity": "LOW",
                         "message": "No lock_timeout set. An ALTER TABLE waits for a lock and blocks every query queued behind it.",
                         "fix": "Start the migration with SET lock_timeout = '5s'; and retry on failure.", "sql": ""})
    findings.sort(key=lambda x: (SEVERITY_ORDER[x["severity"]], x["line"]))
    return findings, len(stmts)


def render(results):
    lines, high = [], 0
    for path, (findings, count) in results.items():
        lines.append("%s  (%d statements)" % (path, count))
        if not findings:
            lines.append("  no risky operations found by the rules in this check")
        for f in findings:
            if f["severity"] == "HIGH":
                high += 1
            lines.append("  [%s] line %d  %s" % (f["severity"], f["line"], f["rule"]))
            lines.append("      " + f["message"])
            if f["sql"]:
                lines.append("      sql: " + f["sql"])
            lines.append("      safer: " + f["fix"])
        lines.append("")
    lines.append("HIGH findings: %d" % high)
    return "\n".join(lines), high


def main(argv):
    dialect, as_json, files, i = "postgres", False, [], 1
    while i < len(argv):
        a = argv[i]
        if a == "--dialect" and i + 1 < len(argv):
            dialect = argv[i + 1].lower()
            i += 1
        elif a == "--json":
            as_json = True
        else:
            files.append(a)
        i += 1
    if dialect not in ("postgres", "mysql") or not files:
        sys.exit("usage: lint_migration.py [--dialect postgres|mysql] [--json] <file.sql> [...]")
    results = {}
    for f in files:
        try:
            results[f] = lint_file(f, dialect)
        except OSError as e:
            sys.exit("cannot read %s: %s" % (f, e))
    if as_json:
        flat = [x for fs, _ in results.values() for x in fs]
        print(json.dumps(flat, indent=2))
        sys.exit(1 if any(x["severity"] == "HIGH" for x in flat) else 0)
    text, high = render(results)
    print(text)
    sys.exit(1 if high else 0)


if __name__ == "__main__":
    main(sys.argv)
