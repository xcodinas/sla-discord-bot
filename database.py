from datetime import datetime
import os
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        BigInteger,
        String,
        DateTime,
        JSON,
        ForeignKey,
        )
from sqlalchemy.orm import (
        DeclarativeBase,
        Session,
        relationship,
        Mapped,
        mapped_column,
        )
from typing import List

database_uri = os.environ.get('DATABASE_URI')
if database_uri is None:
    print('DATABASE_URI environment variable is not set')
    database_uri = 'sqlite:///database.db'
    print(f'Using default database URI: {database_uri}')

engine = create_engine(os.environ.get('DATABASE_URI'))


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    discord_id = Column(BigInteger, unique=True)
    username = Column(String)
    name = Column(String)
    battlepower = Column(Integer)
    battlepower_role_id: Mapped[int] = mapped_column(
            ForeignKey("roles.id"),
            nullable=True)
    battlepower_role: Mapped["Role"] = relationship(
            back_populates="users",
            foreign_keys=[battlepower_role_id]
            )

    def __repr__(self):
        return f'<User {self.username} - Discord ID {self.discord_id}>'


class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    server_id = Column(BigInteger)
    data = Column(JSON)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    server_id = Column(BigInteger)
    role_id = Column(BigInteger)
    role_name = Column(String)
    required_battlepower = Column(Integer)

    users: Mapped[List["User"]] = relationship(
            "User", back_populates="battlepower_role")


def get_session():
    return Session(engine)


def get_server_config(session, server_id):
    config = session.query(Config).filter_by(server_id=server_id).first()
    if not config:
        config = Config(
                server_id=server_id,
                data={},
                created_at=datetime.now())
        session.add(config)
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
            created_at=datetime.now(),
            )
    session.add(user)
    return user


def get_or_create_user(session, author):
    user = get_user(session, author.id)
    if not user:
        user = create_user(
                session,
                discord_id=author.id,
                username=author.name,
                name=author.display_name,
                battlepower=0,
                )
    if user.name != author.display_name:
        user.name = author.display_name
    return user


def update_user(session, user):
    user.updated_at = datetime.now()
    session.add(user)


def update_server_config(session, config):
    session.add(config)
    config.updated_at = datetime.now()
    flag_modified(config, 'data')


def get_guilds(session):
    return session.query(Config).all()


def get_user_rank(session, user):
    users = session.query(User).with_entities(User.id).order_by(
            User.battlepower.desc()).all()
    return users.index((user.id,)) + 1


def get_rankings(session):
    return session.query(User).order_by(User.battlepower.desc()).all()


def get_or_create_role(session, server_id, dcrole):
    role = session.query(Role).filter_by(
            server_id=server_id, role_id=dcrole.id).first()
    if not role:
        role = Role(
                server_id=server_id,
                role_id=dcrole.id,
                role_name=dcrole.name,
                created_at=datetime.now())
        session.add(role)
    return role


def get_closest_role(session, battlepower):
    # Get the closest role given the battlepower, the role cant be higher
    # than the battlepower, if theres no role above the battlepower, return
    # the highest role
    role = session.query(Role).filter(
            Role.required_battlepower <= battlepower).order_by(
                    Role.required_battlepower.desc()).first()
    if not role:
        role = session.query(Role).order_by(
                Role.required_battlepower.desc()).first()
    return role


def get_roles(session, server_id):
    return session.query(Role).filter_by(server_id=server_id).all()


# Create tables
Base.metadata.create_all(engine)
