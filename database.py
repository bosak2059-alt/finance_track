from contextlib import contextmanager
from datetime import datetime, timedelta
import mysql.connector
import bcrypt


class DatabaseManager:
    # Класс для управления всемси операциями с БД
    def __init__(self, host, user, password, database):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
        }
        self._init_db()

    @contextmanager
    def _db_connection(self):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Ошибка БД: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def _init_db(self):
        conn = mysql.connector.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
        cursor.execute(f"USE {self.db_config['database']}")

        try:
            cursor.execute("""
                CREATE TABLE users(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE goals(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    target_amount DECIMAL(10,2) NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE opearations(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    amount REAL NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    description TEXT,
                    date DATETIME NOT NULL,
                    goal_id INT,
                    receipt_path TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE categories(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    UNIQUE(user_id, name),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"Не удалось создать таблицу {e}")
        finally:
            cursor.close()
            conn.close()

    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with self._db_connection() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username,password_hash) VALUES (%s,%s)",
                    (username, hashed_password.decode('utf-8'))
                )
                return cursor.lastrowid
            except mysql.connector.IntegrityError:
                return None  # Пользователь уже существует

    def get_user(self, username):
        with self._db_connection() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username=%s", (username,)
            )
            return cursor.fetchone()

    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def add_default_categories(self, user_id):
        default_categories = ['Продукты', 'Транспорт', "Жилье", "Развлечение", "Зарплата", "Сбережения"]
        with self._db_connection() as cursor:
            for category in default_categories:
                cursor.execute(
                    "INSERT IGNORE INTO categories (user_id, name) VALUES (%s,%s)",
                    (user_id, category)
                )



    # ===   Методы работы с данными   ===

    def get_date_filter(self, period):
        if period == "today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return "WHERE date >= %s", (start_date,)
        elif period == "week":
            start_date = (datetime.now()-timedelta(days=datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            return "WHERE date >= %s", (start_date,)
        elif period == "month":
            start_date = datetime.now().replace(day=1, minute=0, second=0, microsecond=0)
            return "WHERE date >= %s", (start_date,)
        return "", ()




    def add_opearation(self, user_id, amount, type_, category, description, goal_id=None, receipt_path=None):
        with self._db_connection() as cursor:
            cursor.execute("""
                INSERT INTO opearations (user_id, amount, type, category, description, date, goal_id, receipt_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, amount, type_, category, description,  datetime.now(), goal_id, receipt_path))

    def update_opearation(self, user_id,opearation_id ,amount, type_, category, description, receipt_path=None):
        with self._db_connection() as cursor:
            cursor.execute("""
                UPDATE opearations
                SET amount = %s, type=%s, category=%s, description=%s, receipt_path=%s,
                WHERE id = %s AND user_id = %s
            """, (user_id,opearation_id ,amount, type_, category, description, receipt_path))

    def delete_opearations(self, user_id,opearation_id):
        with self._db_connection() as cursor:
            cursor.execute("""
                DELETE FROM opearations where id = %s AND user_id = %s
            """, (opearation_id, user_id))

