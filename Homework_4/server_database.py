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

    class UserContacts(Base):
        __tablename__ = 'user_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        contact = Column(String, ForeignKey('all_users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class UserHistory(Base):
        __tablename__ = 'user_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        print(path)
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})

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
            user_history = self.UserHistory(user.id)
            self.session.add(user_history)

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, receiver):
        sender = self.session.query(self.AllUsers).filter_by(login=sender).first()
        receiver = self.session.query(self.AllUsers).filter_by(login=receiver).first()

        sender_row = self.session.query(self.UserHistory).filter_by(user=sender.id).first()
        sender_row.sent += 1

        receiver_row = self.session.query(self.UserHistory).filter_by(user=receiver.id).first()
        receiver_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(login=user).first()
        contact = self.session.query(self.AllUsers).filter_by(login=contact).first()

        if not contact or self.session.query(self.UserContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        new_contact = self.UserContacts(user.id, contact.id)
        self.session.add(new_contact)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(login=user).first()
        contact = self.session.query(self.AllUsers).filter_by(login=contact).first()

        if not contact:
            return
        self.session.query(self.UserContacts).filter_by(user=user.id, contact=contact.id).delete()
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

    def get_contacts(self, user):
        user = self.session.query(self.AllUsers).filter_by(login=user).first()
        query = self.session.query(self.UserContacts).filter_by(user=user.id).\
            join(self.AllUsers, self.UserContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    def message_history(self):
        query = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_login,
            self.UserHistory.sent,
            self.UserHistory.accepted
        ).join(self.AllUsers)
        return query.all()


if __name__ == '__main__':
    test_db = ServerDataBase()
    test_db.user_login('test1', '192.168.1.113', 8080)
    test_db.user_login('test2', '192.168.1.113', 8081)
    print(test_db.users_list())
    print(test_db.active_users_list())
    test_db.user_logout('test1')
    print(test_db.login_history('test2'))
    test_db.add_contact('test2', 'test1')
    test_db.add_contact('test2', 'Alice')
    test_db.add_contact('test2', 'Lila')
    test_db.remove_contact('test2', 'Lila')
    test_db.process_message('test2', 'test1')
    print(test_db.message_history())
