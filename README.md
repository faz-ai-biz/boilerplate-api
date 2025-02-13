# {{api-name}}

## Overview
A production-ready FastAPI project template implementing industry best practices 
for API development, testing, documentation, and deployment.

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI Version](https://img.shields.io/badge/FastAPI-0.95.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features
- 🚀 FastAPI with async support
- 🔐 JWT authentication with refresh tokens
- 📊 Prometheus metrics and structured logging
- 🗄️ SQLAlchemy with Alembic migrations
- 🧪 Comprehensive test suite
- 🐋 Docker and Docker Compose support
- 📝 OpenAPI documentation
- 🔍 Pre-commit hooks for code quality

## Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/pedroanisio/hello_world_project.git
cd hello_world_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  

# Install dependencies
pip install -r requirements.dev.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

### Docker Development
```bash
# clean up
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml down
docker system prune; docker volume rm $(docker volume ls -q)

# Start services
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml up --build -d

# exec into the container
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml exec web bash

# Run migrations
docker compose -f docker/docker-compose.dev.yml exec web alembic revision --autogenerate -m "initial"
# Create new migration
docker compose -f docker/docker-compose.dev.yml exec web alembic revision --autogenerate -m "create users table"
docker compose -f docker/docker-compose.dev.yml exec web alembic upgrade head
```

## Development Tools
- **API Documentation**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

## Project Structure
```
.
├── src/                    # Application source code
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── db/                # Database models and migrations
│   ├── schemas/           # Pydantic models
│   └── services/          # Business logic
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
├── docker/               # Docker configuration
└── scripts/              # Utility scripts
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

### Docker Testing

```bash
# Build test
docker compose -f docker/docker-compose.test.yml build
```

```bash
# Run test
docker compose -f docker/docker-compose.test.yml run --rm web pytest --cov=src
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run pre-commit hooks (`pre-commit install`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Documentation
- [Development Guide](docs/development.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment_guide.md)
- [API Documentation](docs/api/endpoints.md)
- [Evolution Guide](docs/evolution_guide.md)

## Clen Repo to Use as Boilerplate

```bash
chmod +x scripts/boilerplate.sh
./scripts/boilerplate.sh new-app-name
```	

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
