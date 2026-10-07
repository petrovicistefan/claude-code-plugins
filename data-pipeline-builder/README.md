# Data Pipeline Builder: dbt and Airflow Checks

Review and write dbt models and Airflow DAGs: missing tests and docs, unsafe SELECT *, hardcoded tables, no retries, catchup surprises, work at import time and credentials in code.

## What it does

- A bundled Python script checks dbt projects for models with no description or tests, no `unique` test on keys, sources without freshness checks, `SELECT *` outside staging and hardcoded `schema.table` names instead of `ref()` and `source()`.
- For Airflow it flags DAGs with no `retries`, `catchup` left to the default, network or file work at import time, credentials in the file, `datetime.now()` instead of the data interval, no owner and bare `except: pass`.
- Claude writes new models, schema tests and DAGs in the same style as your project, and explains how to make a load idempotent so a rerun does not double the data.

## Use it

- `/data-pipeline-builder:pipeline-check`
- `/data-pipeline-builder:pipeline-new daily revenue per customer from stg_orders`
- Or ask: "Why does this DAG backfill years of runs?"

## Requirements

Python 3. Optional: `dbt` to compile and test the models.

## Data

Runs locally on your files. The plugin never connects to a warehouse and sends nothing anywhere. If you run `dbt` yourself, it uses your own profile.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
