# Project Structure Documentation

## Project: Hello World API

This document outlines the structure of the **Hello World API** repository, detailing the purpose of key directories and files.

---

## Repository Structure

### **1. `base_path/.github/workflows/`**
This directory contains GitHub Actions workflows for CI/CD automation. 

#### **Purpose:**
- Automates testing, building, and deployment processes.
- Ensures code quality and consistency across environments.
- Triggers specific actions on events such as `push`, `pull_request`, or `release`.

---

### **2. `base_path/devops/`**
This directory houses essential environment configuration and containerization files.

#### **Files:**
- `.env.prod` – Defines environment variables for the **production** environment.
- `.env.dev` – Defines environment variables for the **development** environment.
- `.env.test` – Defines environment variables for the **testing** environment.
- `docker-compose.dev.yml` – Docker Compose file for setting up the development environment.
  - **Entrypoint:** `/app/devops/scripts/startup.sh`
  - **Services:** `redis`, `web`, `db (PostgreSQL)`
- `docker-compose.prod.yml` – Docker Compose file for setting up the production environment.
- `docker-compose.test.yml` – Docker Compose file for setting up the testing environment.
  - **Entrypoint:** `/app/devops/scripts/test.sh`
- `Dockerfile.test` – Dockerfile used for testing container builds and executing test suites.

#### **Purpose:**
- Centralizes configuration for different environments, enabling smooth transitions between **development**, **testing**, and **production**.
- Facilitates container orchestration using **Docker Compose**.
- Supports automated testing in a controlled Docker environment.

---

## **Development Environment**
The `startup.sh` script is executed when the development environment is started. It ensures all dependencies are ready before launching the application.

### **Script: `startup.sh`**
```bash
#!/bin/bash
set -e

echo "Waiting for database..."
python devops/scripts/wait_for_db.py

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python devops/scripts/seed_db.py

echo "Starting application..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running the application

Running the application using Docker Compose (*from basepath*):

```bash
docker compose -f devops/docker-compose.dev.yml --env-file devops/.env.dev up --build
```

> [!IMPORTANT]
> - The application will be available at `http://localhost:8000`
> - The application will hot reload when the code changes

### Cleanup

To stop and remove all containers, networks, and volumes created by Docker Compose:

```bash
docker compose -f devops/docker-compose.dev.yml --env-file devops/.env.dev down -v
```
---

## **Testing Process**
The `test.sh` script is executed when the testing environment is launched, running the test suite with coverage reporting.

### **Script: `test.sh`**
```bash
#!/usr/bin/env bash
# test.sh: Run the test suite with coverage reporting.

pytest --cov=src --cov-report=term-missing
```

To run tests using Docker Compose (*from basepath*):

```bash
docker compose -f devops/docker-compose.test.yml --env-file devops/.env.test run --rm test
```

**Expected Output:**

*Test results summary*

*Coverage report indicating which parts of the code were tested*

*Any errors or failures in test execution*

---

### Docker Cleanup

```shell
docker volume rm $(docker volume ls -q)
```

```shell
docker network rm $(docker network ls -q)
```

```shell
docker container rm $(docker container ls -q)
```

```shell
docker image rm $(docker image ls -q)
```

```shell
docker system prune -a
```

---

## **Directory & File Overview**

| Path | Description |
|------|------------|
| `./devops/Dockerfile` | Base Dockerfile for the project. |
| `./devops/Dockerfile.test` | Dockerfile for testing environments. |
| `./devops/docker-compose.dev.yml` | Defines development services and dependencies. |
| `./devops/docker-compose.prod.yml` | Defines production services and dependencies. |
| `./devops/docker-compose.test.yml` | Defines test environment configuration. |
| `./devops/docker-compose.yml` | Default Docker Compose file. |
| `./devops/scripts/seed_db.py` | Script to seed the database with initial data. |
| `./devops/scripts/startup.sh` | Startup script for the development environment. |
| `./devops/scripts/test.sh` | Script to run test suites. |
| `./devops/scripts/wait_for_db.py` | Waits for the database to be ready before running the application. |

