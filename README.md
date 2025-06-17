# Predykt v2 - Construction Management Backend

A modern construction management backend system designed to help contractors estimate unifamilial house projects in terms of workforce and material requirements. This is the second iteration of the original Predykt application, rebuilt with a scalable and maintainable architecture.

## 🏗️ Overview

Predykt v2 is a comprehensive construction estimation platform that enables contractors to:

- Create and manage project definitions
- Define construction datasheets with material and labor requirements
- Build estimation formulas for accurate cost calculations
- Manage project templates and reusable components
- Track project progress and resource allocation
- Generate detailed construction reports

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.7+** - Core programming language
- **Ariadne** - GraphQL server implementation
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **PostgreSQL** - Primary database

### Architecture Patterns
- **Clean Architecture** - Domain-driven design with clear separation of concerns
- **Dependency Injection** - Using `injector` for IoC container
- **Repository Pattern** - Data access abstraction
- **Use Cases Pattern** - Business logic encapsulation

### Key Dependencies
- **Pydantic** - Data validation and serialization
- **JWT Authentication** - Secure API access
- **Structlog** - Structured logging
- **Poetry** - Dependency management
- **Docker** - Containerization

## 🏛️ Project Structure

```
expert_dollup/
├── app/                    # Application layer
│   ├── controllers/        # REST API endpoints
│   │   ├── datasheet/     # Datasheet management
│   │   ├── project/       # Project management
│   │   └── formulas/      # Formula calculations
│   ├── dtos/              # Data Transfer Objects
│   ├── schemas/           # GraphQL schemas
│   └── middlewares/       # Request/response middleware
├── core/                  # Domain layer
│   ├── domains/           # Domain entities
│   ├── usecases/          # Business logic
│   ├── exceptions/        # Domain exceptions
│   └── utils/             # Core utilities
├── infra/                 # Infrastructure layer
│   ├── providers/         # External service providers
│   ├── services/          # Data services
│   └── validators/        # Data validation
└── shared/                # Shared components
    ├── database_services/ # Database abstractions
    ├── fastapi_jwt_auth/  # Authentication
    └── modeling/          # Data modeling utilities
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Poetry (for dependency management)
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd expert-dollop
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Start the database**
   ```bash
   docker-compose up -d postgres
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   poetry run invoke db:upgrade:head
   ```

6. **Start the development server**
   ```bash
   poetry run invoke start-http
   ```

The API will be available at `http://localhost:8000`

### Development Commands

The project uses `invoke` for task management. Available commands:

```bash
# Start HTTP server (development)
poetry run invoke start-http

# Start HTTPS server (with SSL)
poetry run invoke start

# Run tests
poetry run invoke test

# Run specific test
poetry run invoke test --test="test_name"

# Format code with Black
poetry run invoke black

# Create new migration
poetry run invoke migration:new --message="description"

# Run migrations
poetry run invoke db:upgrade:head
```

## 📊 Core Features

### Project Management
- **Project Definitions**: Create template projects with predefined structures
- **Project Instances**: Generate specific project instances from definitions
- **Project Nodes**: Hierarchical project component organization

### Datasheet System
- **Datasheet Definitions**: Define templates for construction data collection
- **Datasheet Elements**: Individual components within datasheets
- **Dynamic Properties**: Configurable fields for different construction elements
- **Validation**: Schema-based validation for data integrity

### Formula Engine
- **Dynamic Calculations**: Create complex formulas for cost estimation
- **Dependency Management**: Handle formula dependencies and relationships
- **Formula Staging**: Test and validate formulas before deployment
- **Expression Evaluation**: Parse and evaluate mathematical expressions

### Translation Support
- **Multi-language**: Support for multiple languages and locales
- **Resource Management**: Centralized translation resource management
- **Dynamic Content**: Runtime translation of user-generated content

## 🔧 API Endpoints

### REST API
The application provides RESTful endpoints for all core functionality:

- `/datasheets/*` - Datasheet management
- `/definitions/*` - Project and datasheet definitions
- `/projects/*` - Project management
- `/formulas/*` - Formula management
- `/translations/*` - Translation services

### GraphQL API
A comprehensive GraphQL API is available at `/graphql` with:
- Query operations for data retrieval
- Mutation operations for data modification
- Real-time subscriptions (where applicable)
- Type-safe schema definitions

## 🔐 Authentication & Authorization

The system uses JWT-based authentication with role-based access control:

- **User Authentication**: Secure login with JWT tokens
- **Organization-based**: Multi-tenant support with organization isolation
- **Permission System**: Granular permissions for different operations
- **Resource-based Access**: Dynamic authorization based on resource ownership

## 🗄️ Database Schema

The application uses PostgreSQL with the following key entities:

- **Projects** - Main project containers
- **ProjectDefinitions** - Project templates
- **Datasheets** - Data collection sheets
- **DatasheetElements** - Individual datasheet components
- **Formulas** - Calculation formulas
- **Users** - System users
- **Organizations** - Multi-tenant organizations

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=expert_dollup

# Run specific test file
poetry run pytest tests/e2e/datasheet_test.py

# Run with verbose output
poetry run pytest -v
```

Test structure:
- `tests/units/` - Unit tests for individual components
- `tests/e2e/` - End-to-end integration tests
- `tests/fixtures/` - Test data and factories

## 🐳 Docker Deployment

The application includes Docker configuration for easy deployment:

```bash
# Build and start all services
docker-compose up --build

# Start only the database
docker-compose up -d postgres

# View logs
docker-compose logs -f
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://mit-license.org/) file for details.

