from sqlalchemy import create_engine, Column, Text, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


class ServerDataBase:
    '''
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM. Используется классический подход.
    '''
    Base = declarative_base()

    class AllUsers(Base):
        '''Класс - отображение таблицы всех пользователей.'''
        __tablename__ = 'all_users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_login = Column(DateTime)
        passwd_hash = Column(String)
        pubkey = Column(Text)

        def __init__(self, login, passwd_hash):
            self.login = login
            self.passwd_hash = passwd_hash
            self.last_login = datetime.datetime.now()

    class ActiveUsers(Base):
        '''Класс - отображение таблицы активных пользователей.'''
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        connection_time = Column(DateTime)

        def __init__(self, user, ip, port, connection_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.connection_time = connection_time

    class LoginHistory(Base):
        '''Класс - отображение таблицы истории входов.'''
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('all_users.id'))
        ip = Column(String)
        port = Column(Integer)
        connection_time = Column(DateTime)

        def __init__(self, user, ip, port, connection_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.connection_time = connection_time

    class UserContacts(Base):
        '''Класс - отображение таблицы контактов пользователей.'''
        __tablename__ = 'user_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('all_users.id'))
        contact = Column(Integer, ForeignKey('all_users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class UserHistory(Base):
        '''Класс - отображение таблицы истории действий.'''
        __tablename__ = 'user_history'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('all_users.id'))
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

    def user_login(self, username, ip_address, port, key):
        '''
        Метод, выполняющийся при входе пользователя, записывает в базу факт входа,
        обновляет открытый ключ пользователя при его изменении.
        '''
        res = self.session.query(self.AllUsers).filter_by(login=username)

        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        new_active_user = self.ActiveUsers(
            user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(
            user.id, ip_address, port, datetime.datetime.now())
        self.session.add(history)

        self.session.commit()

    def user_logout(self, username):
        '''Метод фиксирующий отключения пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, receiver):
        '''Метод записывающий в таблицу статистики факт передачи сообщения.'''
        sender = self.session.query(self.AllUsers).filter_by(login=sender).first().id
        receiver = self.session.query(self.AllUsers).filter_by(login=receiver).first().id

        sender_row = self.session.query(self.UserHistory).filter_by(user=sender).first()
        sender_row.sent += 1

        receiver_row = self.session.query(self.UserHistory).filter_by(user=receiver).first()
        receiver_row.accepted += 1

        self.session.commit()

    def add_user(self, name, passwd_hash):
        '''
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        '''
        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UserHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        '''Метод, удаляющий пользователя из базы.'''
        user = self.session.query(self.AllUsers).filter_by(login=name).first()
        self.session.query(self.ActiveUsers).filter_by(login=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(user=user.id).delete()
        self.session.query(self.UserContacts).filter_by(user=user.id).delete()
        self.session.query(self.UserContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UserHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(login=name).delete()
        self.session.commit()

    def get_hash(self, name):
        '''Метод получения хэша пароля пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        '''Метод получения публичного ключа пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=name).first()
        return user.pubkey

    def check_user(self, name):
        '''Метод, проверяющий существование пользователя.'''
        if self.session.query(self.AllUsers).filter_by(login=name).count():
            return True
        else:
            return False

    def add_contact(self, user, contact):
        '''Метод добавления контакта для пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=user).first()
        contact = self.session.query(self.AllUsers).filter_by(login=contact).first()

        if not contact or self.session.query(self.UserContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        new_contact = self.UserContacts(user.id, contact.id)
        self.session.add(new_contact)
        self.session.commit()

    def remove_contact(self, user, contact):
        '''Метод удаления контакта пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=user).first()
        contact = self.session.query(self.AllUsers).filter_by(login=contact).first()

        if not contact:
            return
        self.session.query(self.UserContacts).filter_by(user=user.id, contact=contact.id).delete()
        self.session.commit()

    def users_list(self):
        '''
        Метод, возвращающий список известных пользователей
        со временем последнего входа.
        '''
        query = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_login
        )

        return query.all()

    def active_users_list(self):
        '''Метод, возвращающий список активных пользователей.'''
        query = self.session.query(
            self.AllUsers.login,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.connection_time
        ).join(self.AllUsers)

        return query.all()

    def login_history(self, username=None):
        '''Метод, возвращающий историю входов.'''
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
        '''Метод, возвращающий список контактов пользователя.'''
        user = self.session.query(self.AllUsers).filter_by(login=user).one()
        query = self.session.query(self.UserContacts, self.AllUsers.login).filter_by(user=user.id).\
            join(self.AllUsers, self.UserContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    def message_history(self):
        '''Метод, возвращающий историю отправленных сообщений.'''
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
