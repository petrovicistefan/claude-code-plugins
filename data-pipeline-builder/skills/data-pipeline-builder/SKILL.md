---
name: data-pipeline-builder
description: "Use when writing or reviewing dbt models or Airflow DAGs, to add tests and docs and find reliability problems like missing retries or unsafe backfills."
---

# Data Pipeline Builder

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Review and write dbt models and Airflow DAGs that are tested, documented and safe to rerun.

## 1. Check what exists

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/pipeline_check.py            # current folder
python3 ${CLAUDE_SKILL_DIR}/scripts/pipeline_check.py analytics
```

Findings cover dbt projects (found by `dbt_project.yml`) and Airflow DAG files. They come from reading text, so confirm in context: `SELECT *` is fine in a staging model that selects from one source, and a documented model can inherit tests through a group or a `+tests` config.

## 2. Write dbt models

Match the project's layers and naming (`stg_`, `int_`, `fct_`, `dim_`). For each model:

- Select only the needed columns; reference upstream with `{{ ref('...') }}` and raw tables with `{{ source('...', '...') }}`. Never hardcode a schema.
- Add a `schema.yml` entry with a `description`, and tests on the grain: `unique` and `not_null` on the key, `relationships` for foreign keys, `accepted_values` for status columns.
- Choose the materialization on purpose: `view` for light staging, `table` for heavy marts, `incremental` with a `unique_key` and a filter on `is_incremental()` for large append-heavy tables. Say what happens on a full refresh.
- Add `freshness` and `loaded_at_field` to sources that load on a schedule.

If `dbt` is installed, run `dbt parse` and `dbt build --select <model>+` against a development target. Ask before running against a production target, and never run `dbt run --full-refresh` on incremental production models without the user's explicit yes.

## 3. Write Airflow DAGs

- `default_args` with `owner`, `retries` (2 or 3), `retry_delay` and `retry_exponential_backoff`; set `catchup=False` unless the user wants a backfill, and `max_active_runs=1` for DAGs that must not overlap.
- Keep the top level of the file cheap: no API calls, no database queries, no `Variable.get` outside templates. The scheduler imports every DAG file constantly.
- Use the run's data interval (`{{ data_interval_start }}`, `logical_date`), never `datetime.now()`, so a rerun or backfill processes the right slice.
- Credentials through Airflow Connections or a secrets backend, never in the file.
- Make each task **idempotent**: overwrite or merge the target partition (`DELETE` then `INSERT` in one transaction, `MERGE`, or `INSERT OVERWRITE`) instead of blindly appending, so a retry or rerun does not duplicate rows.
- Prefer small tasks, pass references (paths, table names) not data through XCom, and add SLAs or failure callbacks for the pipelines people depend on.

## 4. Data quality

For every new pipeline, propose checks: row count not zero, key uniqueness, null rate on required columns, referential integrity, freshness, and a reasonableness check on one business number. Say which are enforced as dbt tests, which as Airflow check tasks, and which are only suggestions.
