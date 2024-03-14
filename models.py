from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    name = Column(String)
    surname = Column(String)
    role = Column(String) 
    is_active = Column(Boolean, default=True)


class Blogs(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    is_active = Column(Boolean, default=True)
    author = Column(Integer, ForeignKey('users.id'))
