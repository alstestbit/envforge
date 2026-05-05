# envforge

> A utility for generating and validating `.env` files from schema definitions across environments.

---

## Installation

```bash
pip install envforge
```

Or with [Poetry](https://python-poetry.org/):

```bash
poetry add envforge
```

---

## Usage

Define a schema file (`env.schema.yml`) describing your environment variables:

```yaml
variables:
  DATABASE_URL:
    type: string
    required: true
    description: "PostgreSQL connection string"
  DEBUG:
    type: boolean
    default: false
  PORT:
    type: integer
    default: 8080
```

Generate a `.env` file from the schema:

```bash
envforge generate --schema env.schema.yml --output .env
```

Validate an existing `.env` file against the schema:

```bash
envforge validate --schema env.schema.yml --env .env
```

Target a specific environment:

```bash
envforge generate --schema env.schema.yml --env production --output .env.production
```

---

## Features

- 📋 Schema-driven `.env` generation
- ✅ Validation with clear error reporting
- 🌍 Multi-environment support (`development`, `staging`, `production`)
- 🔒 Marks sensitive variables and enforces required fields

---

## License

This project is licensed under the [MIT License](LICENSE).