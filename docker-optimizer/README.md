# Docker Optimizer: Smaller, Safer Docker Images

Make your container images smaller, faster to build and safer to run.

## What it does

- A bundled Python script checks Dockerfiles for running as root, secrets in `ENV` and `ARG`, `curl | sh`, full base images, single-stage builds, package caches left in layers, source copied before dependency install, shell-form `CMD`, unpinned base images and a missing or incomplete `.dockerignore`.
- When Docker is available, Claude measures the image and its layers before and after with `docker history`.
- Claude rewrites the Dockerfile as a multi-stage build with a small runtime image and a non-root user, keeping the same port, entrypoint and runtime files.

## Use it

- `/docker-optimizer:docker-check` or `/docker-optimizer:docker-check services/api/Dockerfile`
- `/docker-optimizer:docker-size myapp:latest`
- Or ask: "Why is our Docker image 1.5 GB?"

## Requirements

Python 3. Docker is optional and only needed to measure image sizes.

## Data

Everything runs locally. Nothing is sent anywhere.

## About the author

<a href="https://petrovicistefan.ro"><img src="https://raw.githubusercontent.com/petrovicistefan/claude-code-plugins/main/assets/ps-logo.png" alt="Stefan Petrovici logo" width="120"></a>

Built by [Stefan Petrovici](https://petrovicistefan.ro), a software engineer open to freelance projects and full-time roles. I build websites, web and mobile apps, Meta (Facebook and Instagram) integrations, and business automations, including AI-powered ones.

Need something like this for your team? Email [hello@petrovicistefan.ro](mailto:hello@petrovicistefan.ro), or see my work at [petrovicistefan.ro](https://petrovicistefan.ro) and [iasi.dev](https://iasi.dev).

## License

MIT. Made by [Stefan Petrovici](https://petrovicistefan.ro).
