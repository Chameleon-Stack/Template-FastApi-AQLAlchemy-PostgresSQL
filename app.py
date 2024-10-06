from fastapi import FastAPI

from kanban import views
from kanban.config import get_config
from kanban.extensions import login


def create_app():
    app = FastAPI()
    app.secret_key = get_config()['SECRET_KEY']
    login.init_app(app)
    views.init_app(app)
    return app


app = create_app()
