# FastAPI Full-Stack Boilerplate

## Features

1. All the goodness of modern, async FastAPI
2. Seamless Jinja2 templating, just like Flask
3. SQLAlchemy ORM and Alembic migrations (PostgreSQL)
4. Flask-Admin plugged right in
5. Pipenv for python dependency management

Explore the [full docs here](./docs/index.md)

## Get Started

1. Copy `.env.example` to `.env` (or create your own)
2. `docker-compose up -d` to start the database
3. `pipenv shell`
4. `uvicorn --factory app.main:create_app --reload --port=8080`

### Configuration

 - Change the database configuration/credentials in `.env` and `docker-compose.yaml`
 - Set `DEBUG_ADMIN=1` to disable the authorization for the admin panel

## Why?

The dependency-injection provided by FastAPI is such a huge improvement over any other python web framework. It's OpenAPI integration is excellent, and it's `asgi`-first, unlike Flask or Django.

But Django is famous for its admin panel, and the ability to rapidly build server side applications. For this, we include Flask-Admin, and centralied Jinja2 templates as a dependency.


## Built On

- FastAPI
- [fastapi-utils class-based-view](https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/)
- [cookiecutter-flask CRUD mixin](https://github.com/cookiecutter-flask/cookiecutter-flask)
- [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)

