from sqlalchemy import create_engine
from channel_app.core import settings


class DatabaseService:
    def create_engine(self):
        engine = create_engine(settings.DATABASE_URI, echo=False)
        return engine