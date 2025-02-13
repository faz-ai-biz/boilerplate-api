# Contribution Guidelines

## Development Environment
This project enforces full development and testing within **Docker**. All examples 
and execution should use **Docker Compose** to ensure consistency across different 
environments.

To set up the environment:
```sh
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml up --build
```

To run tests inside the container:
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run --rm test
```

---

## **CI/CD Workflow Overview**
This project uses **GitHub Actions** for CI/CD automation. The workflow is triggered 
on the following events:
- Pushes to `main` and `develop` branches.
- Pull requests targeting `main` and `develop` branches.

### **CI Jobs and Steps**
#### **1. Test Job**
Runs on `ubuntu-latest` and includes the following steps:

- **Set Up Services**
  - PostgreSQL 16 with predefined environment variables and health checks.
  - Redis (Alpine version) for caching and session management.

- **Steps Execution**
  1. **Checkout Code**
     - Uses `actions/checkout@v4` to retrieve the latest code.
  2. **Set Up Python**
     - Installs Python 3.11 with pip caching enabled.
  3. **Copy `.env.test`**
     - Copies environment variables required for testing.
  4. **Install Dependencies**
     - Upgrades pip and installs required test dependencies from `requirements.test.txt`.
  5. **Run Linting**
     - Uses `flake8`, `black`, and `isort` to enforce coding standards.
  6. **Run Security Checks**
     - Installs `bandit` and `safety` to check for security vulnerabilities.
     - Ignores specific safety warnings for known issues.
  7. **Run Tests**
     - Executes `pytest` with coverage reporting.
  8. **Upload Coverage Report**
     - Uses `codecov/codecov-action@v3` to upload the test coverage report.

### **7. Semgrep** (Static Application Security Testing)
Semgrep performs advanced static code analysis to identify security vulnerabilities, 
bugs, and code quality issues. The project uses Semgrep in CI/CD with the following 
rulesets:
- Python standard ruleset
- OWASP Top Ten vulnerabilities
- Security audit patterns

To run Semgrep locally using Docker:
```sh
docker run --rm -v "${PWD}:/src" returntocorp/semgrep semgrep \
  --config "p/python" \
  --config "p/owasp-top-ten" \
  --config "p/security-audit" \
  /src
```

---

## **Tools Used**

### **1. Black** (Code Formatter)
Black is an opinionated Python code formatter that enforces a consistent style.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test black . --check
```

### **2. Flake8** (Code Linter)
Flake8 checks for style guide enforcement and potential errors.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test flake8 .
```

### **3. Isort** (Import Sorting)
Isort ensures Python imports are properly ordered.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test isort . --check-only
```

### **4. Bandit** (Security Scanner)
Bandit analyzes Python code for security vulnerabilities.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test bandit -r src/
```

### **5. Safety** (Dependency Security Check)
Safety scans installed dependencies for known security vulnerabilities.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test safety check
```

### **6. Pytest** (Testing Framework)
Pytest runs unit tests and generates coverage reports.
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test pytest --cov=src --cov-report=xml --cov-report=term-missing
```

---

## **Contributing Guidelines**
### **1. Fork & Clone**
- Fork the repository and clone it locally:
  ```sh
  git clone https://github.com/your-username/repository-name.git
  cd repository-name
  ```

### **2. Create a Feature Branch**
- Follow a naming convention such as `feature/your-feature`:
  ```sh
  git checkout -b feature/your-feature
  ```

### **3. Run Tests in Docker**
Ensure all tests pass before pushing:
```sh
docker compose --env-file devops/.env.test -f devops/docker-compose.test.yml run \
--rm test pytest --cov=src --cov-report=term-missing
```

### **4. Lint & Format Code**
Run the following commands in Docker:
```sh
docker compose --env-files devops/.env.test -f devops/docker-compose.test.yml run --rm test flake8 .
docker compose --env-files devops/.env.test -f devops/docker-compose.test.yml run --rm test black . --check
docker compose --env-files devops/.env.test -f devops/docker-compose.test.yml run --rm test isort . --check-only
```

### **5. Commit & Push**
- Use clear commit messages:
  ```sh
  git commit -m "Add feature XYZ with tests"
  git push origin feature/your-feature
  ```

### **6. Open a Pull Request (PR)**
- Ensure the PR follows the repository's PR template.
- Reference any related issues.
- Wait for CI checks and code reviews before merging.

---

## **Code Quality & Security**
- Follow PEP8 coding standards.
- Keep dependencies updated and use security tools like `bandit` and `safety`.
- Ensure all new features include tests and documentation.
- Maintain a minimum of 70% test coverage for all code contributions. Pull requests 
  with coverage below this threshold will automatically fail CI checks.

For any questions, reach out via GitHub issues or discussions!

