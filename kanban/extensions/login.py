from fastapi_login import LoginManager

from kanban.database import Session
from kanban.models import User
from kanban.config import get_config


def init_app(app):
    login_manager = LoginManager(app.secret_key, token_url= get_config()['SECRET_KEY'])

    @login_manager.user_loader
    def load_user(user_id):
        with Session() as session:
            return session.get(User, int(user_id))
