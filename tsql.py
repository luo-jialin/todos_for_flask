from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./tsql.db', echo=True)
Base = declarative_base()

class todos(Base):
    __tablename__='todos'
    __table_args__ = {'sqlite_autoincrement': True}
    todoid = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, nullable = False)
    todotext = Column(String, nullable = False)
    done = Column(Boolean, default=False)

    def to_dict(self):
        if(self.done == False):
            self.done = False
        else:
            self.done = True
        return {
            'id' : self.todoid,
            'title': self.todotext,
            'user_id': self.userid,
            'done':self.done
        }


class usertable(Base):
    __tablename__='usertable'
    __table_args__ = {'sqlite_autoincrement':True}
    userid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable = False)
    passwd = Column(String, nullable = False)


def create_table():
    Base.metadata.create_all(engine)


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

