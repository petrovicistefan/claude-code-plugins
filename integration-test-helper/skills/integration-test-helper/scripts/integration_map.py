#!/usr/bin/env python3
"""Map the integration points of a service: what it talks to and what already tests it.

  integration_map.py [folder]     default: current folder

Finds databases, caches, queues, object stores and outbound HTTP calls from imports,
docker-compose and environment variable names, then lists existing integration and
contract tests. Output is the starting list for integration and contract tests.
Reads files only.
"""
import os
import re
import sys

SKIP = {"node_modules", ".git", "venv", ".venv", "dist", "build", "__pycache__", ".next", "target", "vendor", "coverage"}
EXT = (".js", ".ts", ".tsx", ".mjs", ".py", ".go", ".rb", ".java", ".kt", ".cs", ".php")

KINDS = {
    "PostgreSQL": r"\bpg\b|psycopg|asyncpg|postgres(ql)?://|pgx|org\.postgresql",
    "MySQL": r"mysql2?\b|pymysql|mysql://|go-sql-driver/mysql",
    "MongoDB": r"mongoose|pymongo|mongodb(\+srv)?://|mongo-driver",
    "SQLite": r"sqlite3?\b|better-sqlite3",
    "Redis": r"\bioredis\b|\bredis\b|go-redis|redis://",
    "Kafka": r"kafkajs|confluent_kafka|kafka-python|sarama|spring-kafka",
    "RabbitMQ": r"amqplib|\bpika\b|amqp://|rabbitmq",
    "AWS SQS/SNS": r"@aws-sdk/client-(sqs|sns)|boto3.*(sqs|sns)|\.sqs\b",
    "S3 / object storage": r"@aws-sdk/client-s3|boto3.*s3|\bminio\b|@google-cloud/storage",
    "Elasticsearch": r"elasticsearch|opensearch",
    "SMTP / email": r"nodemailer|smtplib|sendgrid|mailgun|ses\.send",
    "Stripe": r"\bstripe\b",
    "gRPC": r"@grpc/|grpcio|google\.golang\.org/grpc",
}
HTTP_RX = re.compile(r"(?:fetch|axios(?:\.\w+)?|requests\.\w+|httpx\.\w+|http\.(?:Get|Post)|got|ky|HttpClient\.\w+|RestTemplate\.\w+)\s*\(\s*[`\"']([^`\"']+)")
ENVURL_RX = re.compile(r"[\"']?([A-Z][A-Z0-9_]*(?:_URL|_HOST|_ENDPOINT|_BASE_URL|_API))[\"']?")


def text(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    found, http, envs, tests, pact = {}, {}, set(), [], False
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            p = os.path.join(d, f)
            rel = os.path.relpath(p, root)
            if f.endswith(EXT) or f in ("package.json", "requirements.txt", "go.mod", "pyproject.toml", "pom.xml", "build.gradle"):
                if os.path.getsize(p) > 400000:
                    continue
                t = text(p)
                for kind, rx in KINDS.items():
                    if re.search(rx, t, re.I):
                        found.setdefault(kind, []).append(rel)
                for m in HTTP_RX.finditer(t):
                    u = m.group(1)
                    if u.startswith(("http", "/", "$", "{")) or "${" in u:
                        http.setdefault(u[:80], []).append(rel)
                for m in ENVURL_RX.finditer(t):
                    envs.add(m.group(1))
                if re.search(r"@pact-foundation|from pact|pactum|dredd|schemathesis|testcontainers|supertest|MockServer|wiremock|nock\b|msw\b", t, re.I):
                    pact = True
                if re.search(r"(integration|e2e|contract)", rel, re.I) and re.search(r"(test|spec)", rel, re.I) and f.endswith(EXT):
                    tests.append(rel)
    compose = None
    for n in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        if os.path.isfile(os.path.join(root, n)):
            compose = re.findall(r"^\s+image:\s*(\S+)", text(os.path.join(root, n)), re.M)
    print("# Integration map\n")
    print("## Infrastructure this code uses")
    for k, v in sorted(found.items()):
        v = sorted(set(v))
        print(f"- {k}: {len(v)} file(s), e.g. {', '.join(v[:3])}")
    if not found:
        print("- none detected")
    print("\n## Outbound HTTP calls (candidates for contract tests or mocks)")
    for u, v in sorted(http.items())[:25]:
        print(f"- {u}  <- {sorted(set(v))[0]}")
    if not http:
        print("- none with a literal URL")
    print("\n## Configured service URLs (environment names):", ", ".join(sorted(envs)[:25]) or "none")
    print(f"\n## docker-compose images: {', '.join(compose) if compose else 'no compose file'}")
    print(f"\n## Existing integration/contract tests: {len(tests)}")
    for t in tests[:10]:
        print(f"- {t}")
    print(f"Test tooling for containers/mocks/contracts already present: {'yes' if pact else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
