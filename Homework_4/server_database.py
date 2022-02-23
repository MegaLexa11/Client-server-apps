from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


class ServerDataBase:
    Base = declarative_base()

    class AllUsers(Base):
        __tablename__ = 'all_users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_login = Column(DateTime)

        def __init__(self, login):
            self.login = login
            self.last_login = datetime.datetime.now()

    class ActiveUsers(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        connection_time = Column(DateTime)

        def __init__(self, user, ip, port, connection_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.connection_time = connection_time

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        ip = Column(String)
        port = Column(Integer)
        connection_time = Column(DateTime)

        def __init__(self, user, ip, port, connection_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.connection_time = connection_time

    def __init__(self):
        self.engine = create_engine('sqlite:///server_base.db3', echo=False, pool_recycle=7200)

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        res = self.session.query(self.AllUsers).filter_by(login=username)

        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_login
        )

        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.login,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.connection_time
        ).join(self.AllUsers)

        return query.all()

    def login_history(self, username=None):
        query = self.session.query(
            self.AllUsers.login,
            self.LoginHistory.ip,
            self.LoginHistory.port,
            self.LoginHistory.connection_time
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.login == username)
        return query.all()


if __name__ == '__main__':
    data_base = ServerDataBase()
    data_base.user_login('Bob', '192.168.0.1', 8989)
    data_base.user_login('Nick', '192.168.0.4', 7891)
    print(data_base.active_users_list())
    data_base.user_logout('Bob')
    print(data_base.users_list())
    print(data_base.active_users_list())
    data_base.user_logout('Nick')
    print(data_base.users_list())
    print(data_base.active_users_list())
