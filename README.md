# mitsuba

a discord bot

## Development

Requirements:
- PostgreSQL. You can install it locally or use docker (see `docker-compose.yml`)
- Python >= 3.9
- [Poetry](https://python-poetry.org/docs/#installation)

Here's some useful commands to start with:
```
docker compose up -d
poetry install
poetry run alembic upgrade head
poetry run python -m mitsuba
```

You should also setup pre-commit hooks:
```
poetry run pre-commit install
```

If you want to run the pre-commit hooks manually:
```
poetry run pre-commit -- run --all-files
```
