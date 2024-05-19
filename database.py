from datetime import datetime
import os
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        DateTime,
        JSON,
        )
from sqlalchemy.orm import DeclarativeBase, Session

database_uri = os.environ.get('DATABASE_URI')
if database_uri is None:
    raise ValueError('DATABASE_URI environment variable is not set')

engine = create_engine(os.environ.get('DATABASE_URI'))


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    discord_id = Column(Integer, unique=True)
    username = Column(String)
    name = Column(String)
    battlepower = Column(Integer)

    def __repr__(self):
        return f'<User {self.username} - Discord ID {self.discord_id}>'


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    server_id = Column(Integer)
    data = Column(JSON)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    server_id = Column(Integer)
    role_id = Column(Integer)
    role_name = Column(String)
    required_battlepower = Column(Integer)


def get_session():
    return Session(engine)


def get_server_config(session, server_id):
    config = session.query(Config).filter_by(server_id=server_id).first()
    if not config:
        config = Config(server_id=server_id, data={})
        session.add(config)
        session.commit()
    return config


def get_user(session, discord_id):
    user = session.query(User).filter_by(discord_id=discord_id).first()
    return user


def create_user(session,
                discord_id=0, username=None, name=None, battlepower=0):
    user = User(
            discord_id=discord_id,
            username=username,
            name=name,
            battlepower=battlepower,
            )
    session.add(user)
    session.commit()
    return user


def update_user(session, user):
    user.updated_at = datetime.now()
    session.add(user)
    session.commit()


def update_server_config(session, config):
    session.add(config)
    flag_modified(config, 'data')
    config.updated_at = datetime.now()
    session.commit()


# Create tables
Base.metadata.create_all(engine)
