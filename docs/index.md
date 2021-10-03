# FastAPI Full-Stack Boilerplate

# Features

## Flask-Admin 

FastAPI is a beautiful framework, but it is missing a key productivity-booster: the admin panel. 

There's two things to consider when integrating Flask-Admin:

1. Routing
2. Authentication

Routing is easily taken care of by FastAPI's [WSGIMiddleware](https://fastapi.tiangolo.com/advanced/wsgi/). Authentication requires a bit more work...

You'll notice [admin.py](../app/admin.py) implements the `admin_auth_middleware`. This middleware will authenticate all requests to the admin sub-app. The middleware only recieves a `Request`, so we need to translate our FastAPI authentication to handle a `Request`. This is done in [dependencies.py](../app/dependencies.py) `wsgi_admin`. You will want to rewrite this if you rely on a different session & authentication implementation.

NOTE: The `DEBUG_ADMIN` environment variable will allow unauthenticated access to the admin panel.

The included `UserAdmin` view implementation demonstrates how to modify the `ModelView` and integrate with your application logic.

## Jinja Templating

Server-side templates is a really efficient way to rapidly build websites. Django makes this super easy. FastAPI has built-in Jinja support, but it's a bit cumbersome out-of-the-box.

The [official FastAPI docs](https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates) demonstrate templating:

```python
templates = Jinja2Templates(directory="templates")

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})
```

This requires a moderate amount of boilerplate for each route:

- invoking `templates.TemplateResponse`
- specifying the `request: Request` parameter
- adding `{"request": request}` to the template context parameter

The `RenderTemplate` class in [dependencies.py](../app/dependencies.py) captures this boilerplate, and a bit more:

- The `__call__` interface is the dependency-injection interface. It's invoked when the `RenderTemplate` instance is invoked via `Depends`. This, in turn, returns a partially applied render method, supporting the following usage:

```python
from .dependencies import Templates # a pre-configured instance of RenderTemplate

@app.get("/items/{id}")
async def read_item(id: str, render: Depends(Templates)):
    return render("item.html", {"id": id})
```

This route is equivalent to the previous code block. The code re-use is amplified by class-based views (see below).

- The `RenderTemplate` constructor also accepts `**kwargs` and registers these key-value pairs as global variables in all your jinja templates. 


## Class-Based Views

Class-based views help reduce code duplication between similar routes. The implementation in this repo ([ext.cbv](../app/ext/cbv.py)) is borrowed from [FastAPI Utils](https://fastapi-utils.davidmontague.xyz/).

## CRUD Model Helper Mixins

The mixin classes in [ext.crud](../app/ext/crud.py) provide utility methods for creating, updating and deleting models (when given a db session). The implementation in this repo is borrowed from [cookiecutter-flask](https://github.com/cookiecutter-flask/cookiecutter-flask) (which I believe borrowed it originally from [flask-bones](https://github.com/cburmeister/flask-bones))

`PkModel` implements a serial integer primary key. If you want to use UUIDs for primary keys, you can look into [FastAPI Utils' GUID facility](https://fastapi-utils.davidmontague.xyz/user-guide/basics/guid-type/).

`reference_col` is a super helpful shorthand for defining foreign key columns.