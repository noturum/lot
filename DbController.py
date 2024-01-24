import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, insert, delete, update
from sqlalchemy.orm import Session, DeclarativeBase, relationship
DB = os.getenv('DB')
assert DB, 'init db string'


class Base(DeclarativeBase):
    ...
class Links(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    href = Column(String)
    isVerified = Column(Boolean,default=False)
    # mail = relationship("Mail")
class Selected(Base):
    __tablename__ = 'selected'
    id = Column(Integer,primary_key=True, autoincrement=True)
    message_id= Column(Integer)
    peer_id = Column(Integer)
    isforwarded= Column(Boolean)
class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String)
    isChecked=Column(Boolean,default=False)

class Database():
    __inst__ = None
    def __new__(cls, *args, **kwargs):
        if not cls.__inst__:
            Base.metadata.create_all(create_engine(DB, echo=False))
            cls.__inst__ = super().__new__(cls)
        return cls.__inst__

    def __init__(self):
        self.__engine = create_engine(DB, echo=False)
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

if __name__ !="__main__":
    c_database= Database()