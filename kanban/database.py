from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kanban.config import get_config

db = create_engine(get_config()['DATABASE_URI'])
Session = sessionmaker(db)