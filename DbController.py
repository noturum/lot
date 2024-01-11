from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, insert, delete, update
from sqlalchemy.orm import Session, DeclarativeBase, relationship

from Strings import DB


class Base(DeclarativeBase):
    ...
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer)
    name = Column(String)
    # mail = relationship("Mail")
class Prof(Base):
    __tablename__ = 'prof'
    id = Column(Integer,primary_key=True, autoincrement=True)
    message_id= Column(Integer)
    text=Column(String)
class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String)
    isChecked=Column(Boolean,default=False)

class Database():
    __inst__ = None
    def __new__(cls, *args, **kwargs):
        if cls.__inst__:
            return cls.__inst__
        else:
            Base.metadata.create_all(create_engine(DB, echo=False))
            cls.__inst__ = cls
            return cls
    def __init__(self):
        self.session = Session(self.__engine)


    def insert(self, table, returning=None, **values):
        if returning:
            returns = self.session.execute(insert(table).values(**values).returning(returning)).fetchone()
            self.session.commit()

            return returns
        else:
            self.session.execute(insert(table).values(**values))
            self.session.commit()

    def update(self, table, filter, returning=None, **values):
        if returning:
            returns= self.session.execute(update(table).where(*filter).values(**values).returning(returning))
            self.session.commit()
            return returns
        else:
            self.session.execute(update(table).where(*filter).values(**values))
            self.session.commit()



    def select(self, table, filter=(True,), count=False, one=False):
        if count:
            return self.session.query(table).filter(*filter).count()
        else:
            return self.session.query(table).filter(*filter).one() if one else self.session.query(table).filter(
                *filter).all()

    def delete(self, table, filter: list, returning=None):
        if returning:
            returns = self.session.execute(delete(table).returning(returning)).fetchone()
            self.session.commit()
            return returns
        else:
            self.session.query(table).filter(*filter).delete()
            self.session.commit()

