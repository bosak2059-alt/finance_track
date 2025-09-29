from contextlib import contextmanager
from datetime import datetime
import _mysql_connector
import bcrypt

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.db_config={
            'host': host,
            'user': user,
            'password': password,
            'database': database,
        }

    @contextmanager
    def _db_connection(self):
        conn=_mysql_connector.connect(**self.db_config)
        cursor=conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
        except _mysql_connector.MySQLError as e:
            print(f'MySQL error: {e}')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def _init_db(self):
        conn=_mysql_connector.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
        )
        cursor = conn.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.db_config['database']};')
        cursor.execute(f'USE {self.db_config['database']};')

        try:
            cursor.execute("""
                CREATE TABLE users (
                    id int auto_increment primary key,
                    username varchar(255) unique not null,
                    password_hash text not null,   
                )
            """)
            cursor.execute("""
                CREATE TABLE goals (
                    id int auto_increment primary key,
                    user_id int not null,
                    name varchar(255) not null,
                    target_amount decimal(10,2) not null,
                    created_at datetime not null,
                    foreign key(user_id) references users(id) on delete cascade, 
                )
            """)
            cursor.execute("""
                CREATE TABLE opearations(
                    id int auto_increment primary key,
                    user_id int not null,
                    amount real not null,
                    type varchar(255) not null,
                    category varchar(255) not null,
                    description text,
                    date datetime not null,
                    goal_id int not null,
                    receipt_path text,
                    foreign key(user_id) references users(id) on delete cascade, 
                    foreign key(goal_id) references goals(id) on delete set null, 
                )
            """)
            cursor.categories("""
                CREATE TABLE opearations(
                    id int auto_increment primary key,
                    user_id int not null,
                    name varchar(255) not null,
                    unique(user_id, name)    
                    foreign key(user_id) references users(id) on delete cascade,                
                )
            """)
            conn.commit()
        except _mysql_connector.MySQLError as e:
            print(f'MySQL error: {e}')
        finally:
            cursor.close()
            conn.close()

    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with self._db_connection() as cursor:
            try:
                cursor.execute(
                    "insert into users (username, password_hash) values (%s, %s)",
                    (username, hashed_password.decode('utf-8'))
                )
                return cursor.lastrowid
            except _mysql_connector.MySQLInterityError:
                return None

    def get_user(self, username):
        with self._db_connection() as cursor:
            cursor.execute("selelect id, username, password_hash from users where username = %s", (username,))
            return cursor.fetchone()

    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def add_default_cacategories(self, user_id):
        default_categories = ['Продукты', 'Транспорт', 'Жилье', 'Развлечение', 'Зарплата', 'Сбережения']
        with self._db_connection() as cursor:
            for category in default_categories:
                cursor.execute(
                    "insert ignore into categories (user_id, name) values (%s, %s)",
                    (user_id, category)
                )