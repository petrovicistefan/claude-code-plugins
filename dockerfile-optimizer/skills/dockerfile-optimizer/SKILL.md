---
name: dockerfile-optimizer
description: "Use when writing or reviewing a Dockerfile, when a container image is too large or builds slowly, or when hardening an image for production."
---

# Dockerfile Optimizer

Scripts: `${CLAUDE_SKILL_DIR}` is the folder that contains this file. If your agent does not define it, use the folder where this `SKILL.md` is located.

Make container images smaller, faster to build and safer to run.

## 1. Check the Dockerfile

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dockerfile_check.py                  # ./Dockerfile
python3 ${CLAUDE_SKILL_DIR}/scripts/dockerfile_check.py path/to/Dockerfile
python3 ${CLAUDE_SKILL_DIR}/scripts/dockerfile_check.py .                # every Dockerfile in the repo
```

Findings are grouped as:

- **security**: running as root, secrets in `ENV`/`ARG`, credentials files copied in, `curl | sh`, `chmod 777`, `ADD` from a URL without a checksum
- **size**: full base images in the final stage, single-stage builds with build tools, apt/apk/yum caches left in layers, `pip` cache, dev dependencies, missing or incomplete `.dockerignore`
- **cache**: copying all source before installing dependencies, so every code change reinstalls them
- **reliability**: shell-form `CMD`/`ENTRYPOINT` (no SIGTERM), `apt-get install` without `update` or `-y`, no `HEALTHCHECK`
- **reproducibility**: unpinned base images, `npm install` instead of `npm ci`, `apt-get upgrade`

## 2. Measure the image (if Docker is available)

```bash
docker build -t app:before .
docker image ls app:before --format '{{.Size}}'
docker history app:before --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' | head -20
```

`docker history` shows which instruction adds the most. If `dive` is installed, `dive app:before` shows wasted space per layer. Rebuild after the changes as `app:after` and compare sizes and build time (also a rebuild after touching one source file, to check the cache).

## 3. Rewrite

Typical structure for a Node app:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM deps AS build
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

Apply the same ideas for other stacks: Python with a builder stage that creates a virtualenv and a `-slim` final stage; Go and Rust with a static binary copied into `distroless/static` or `scratch`; Java with a JRE-only base (`eclipse-temurin:21-jre`).

Rules:

- Keep the app's behaviour: same port, entrypoint, environment variables and files at runtime. Check what the app reads at startup before removing files.
- Alpine uses musl; native modules (sharp, bcrypt, Prisma engines, some Python wheels) may need `-slim` (Debian) instead.
- Pass build secrets with `RUN --mount=type=secret,id=npmrc` and runtime secrets as environment at run time, never in the image.
- Pin base images to a version tag; add a digest when the user wants fully reproducible builds.
- For multi-architecture images use `docker buildx build --platform linux/amd64,linux/arm64`; with cross-compiling languages, build on `$BUILDPLATFORM` and target `$TARGETARCH` to avoid slow emulation.

## 4. Security scan (optional)

If `trivy` or `docker scout` is installed, run `trivy image app:after` or `docker scout cves app:after` and report critical and high findings in the final image. A smaller base image usually removes most of them.

## Report

Show the measured size before and after (or say that Docker was not available to measure), the findings fixed, and the new Dockerfile and `.dockerignore`.
