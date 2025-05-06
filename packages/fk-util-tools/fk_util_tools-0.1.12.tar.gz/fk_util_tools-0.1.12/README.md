# package-utils

## SQL Printer Middleware

SQL Printer Middleware es una librería que proporciona middlewares para imprimir las consultas SQL ejecutadas en aplicaciones Flask, Django y FastAPI cuando el modo DEBUG está activado.

### Instalación

```bash
pip install fk-util-tools
```

### Implementación Flask

```bash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from fk_utils.middlewares.flask.sql_middleware import SqlPrintingMiddleware

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

SqlPrintingMiddleware(app)
```

### Implementación Django

```bash
MIDDLEWARE = [
    # Otros middlewares...
    'fk_utils.middlewares.django.sql_middleware.SqlPrintingMiddleware',
]
```

### Implementación FastApi

```bash
from fastapi import FastAPI
from fk_utils.middlewares.fastapi.sql_middleware import SqlPrintingMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.add_middleware(SqlPrintingMiddleware, debug=True)
```
