# Power Lines Core

Local development orchestration for [Power Lines Web](https://github.com/johnwatson484/power-lines-web) and [Power Lines Data Service](https://github.com/johnwatson484/power-lines-data-service). Keep these repositories as sibling directories. Core contains no application code or dependency containers.

## Setup and native development

Install the .NET 10 SDK, Docker with Compose 2.24+, Bash and optionally VS Code with its C# extension. Use WSL for Bash tasks on Windows.

```sh
./install
./open
```

`install` clones missing active repositories, copies each `.env.example` to `.env` only when absent, and restores .NET dependencies. Existing env files are preserved. Re-run it after checking out the companion local-development PRs if they have not merged yet. `open` opens `power-lines.code-workspace` with core, web and data service.

In VS Code, run **Tasks: Run Task > Local: Start all**. It starts dependencies sequentially, then opens native web under `dotnet watch` and a ready importer terminal in dedicated split terminals. It does not download data automatically. Other workspace tasks provide independent terminals, builds, tests, dependency shutdown and Docker execution.

From the command line:

```sh
./start                   # dependency startup and workspace instructions
./build                   # native builds
# In a web terminal:
../power-lines-web/scripts/dev
# After web logs that its consumers are ready, in another terminal:
./data-service-run --results --all
./data-service-run --fixtures
```

Web is at `http://localhost:5000`; RabbitMQ management is at `http://localhost:15672`. Start web consumers before imports so the subscription queues exist. Import historical results before fixtures for forecasting history. The workspace has explicit **Import: Fixtures**, **Import: Current results** and **Import: Full history** tasks.

## Shared dependencies and configuration

Each app repo owns its Compose file and supports standalone development. Both use project `power-lines`, network `power-lines` and identical `power-lines-message` definitions, sharing one RabbitMQ instance. Core calls their startup scripts sequentially and hosts no dependencies itself. Repeated startup and either repo order reuse the broker. Keep RabbitMQ credentials, AMQP and management ports identical in both `.env` files.

Web additionally owns PostgreSQL on native port `6000`, with database `power_lines_web`. Match its connection string to `POSTGRES_*` settings. Apps load optional repo-root `.env` files; existing process environment and command-line configuration take precedence. See each app README for full configuration details.

## Optional Docker apps

```sh
./build --docker
./start --docker
# Once web consumers are ready:
./data-service-run --docker --results
./data-service-run --docker --fixtures
./stop --docker
```

Docker startup launches web plus dependencies. Imports use disposable containers and exit; no idle importer is launched. Stop a Docker web app before starting native web on the same port. The native and Docker modes share development dependencies and data.

## Shutdown

```sh
./stop                    # dependencies only
./stop --docker           # also stop Docker web
```

Shared RabbitMQ shutdown affects both apps. Stop native processes with Ctrl+C or terminate their VS Code tasks. Dependency containers, networks and PostgreSQL volumes are retained. Do not use orphan removal: both repos share a Compose project. Delete `power-lines_postgres_data` only when deliberately resetting development data.

All scripts resolve sibling paths relative to core, so they work from other directories. `build`, `install`, `open` and `data-service-run` forward arguments without splitting them; `stop` forwards Compose stop options such as `--timeout 5`.

## Validation and CI

```sh
bash -n install build start stop open data-service-run
shellcheck install build start stop open data-service-run
```

PR checks run shell syntax and ShellCheck. They need no app clones, .NET SDK or Docker daemon. App repositories run their own native builds and Testcontainers suites.
