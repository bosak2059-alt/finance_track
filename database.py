from contextlib import contextmanager
from datetime import datetime, timedelta
import mysql.connector
import bcrypt
from certifi import where


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

    # === Методы работы с данными ===

    def _get_date_filter(self, period):
        if period == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return "WHERE date >= %s", (start_date,)
        elif period == 'week':
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday())).replace(hour=0, minute=0, second=0,
                                                                                             microsecond=0)
            return "WHERE date >= %s", (start_date,)
        elif period == 'month':
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return "WHERE date >= %s", (start_date,)
        return "", ()

    def add_operation(self, user_id, amount, type_, category, description, goal_id=None, receipt_path=None):
        with self._db_connection() as cursor:
            cursor.execute("""
                INSERT INTO opearations (user_id, amount, type, category, description, date, goal_id, receipt_path)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, amount, type_, category, description, datetime.now(), goal_id, receipt_path))

    def update_operation(self, user_id, operation_id, amount, type_, category, description, receipt_path):
        with self._db_connection() as cursor:
            cursor.execute("""
                UPDATE opearations
                SET amount=%s, type=%s, category=%s, description=%s,receipt_path=%s
                WHERE id = %s AND user_id = %s
            """, (user_id, operation_id, amount, type_, category, description, receipt_path))

    def delete_operation(self, user_id, operation_id):
        with self._db_connection() as cursor:
            cursor.execute("""
                DELETE FROM opearations WHERE id = %s AND user_id = %s
            """, (operation_id, user_id))

    def get_all_operations(self, user_id, period='all'):
        with self._db_connection() as cursor:
            where_clause, params = self._get_date_filter(period)
            if where_clause:
                final_where = f"{where_clause} AND user_id = %s"
                finals_params = (user_id,)
            else:
                final_where = " WHERE user_id = %s"
                finals_params = (user_id,)
            query = f"SELECT id, amount, type, category, description, date, goal_id, receipt_path FROM opearations {final_where} ORDER BY date DESC"
            cursor.execute(query, finals_params)
            return cursor.fetchall()

    def add_category(self, user_id, name):
        with self._db_connection() as cursor:
            try:
                cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (user_id, name))
            except mysql.connector.IntegrityError:
                print(f"Категория {name} уже существует.")

    def delete_category(self, user_id, name):
        with self._db_connection() as cursor:
            cursor.execute("DELETE FROM categories WHERE user_id=%s AND name=%s", (user_id, name))

    def get_all_category(self, user_id):
        with self._db_connection() as cursor:
            cursor.execute("SELECT name FROM categories WHERE user_id=%s", (user_id,))
            return [row['name'] for row in cursor.fetchall()]

    def get_balance(self, user_id, period='all'):
        with self._db_connection() as cursor:
            where_clause, date_params = self._get_date_filter(period)
            conditions = []
            params = [user_id]

            if where_clause.strip():
                conditions.append(where_clause.replace("WHERE", "").strip())
                params.extend(date_params)

            conditions.append("user_id = %s")
            conditions.append("type = %s")
            where_final = "WHERE " + " AND ".join(conditions) if conditions else ""

            query_income = f"SELECT COALESCE(SUM(amount), 0) as total FROM opearations {where_final}"
            params_income = params + ['Доход']
            cursor.execute(query_income, tuple(params_income))
            income = cursor.fetchone()['total'] or 0

            # Запрос для расходов
            query_expense = f"SELECT COALESCE(SUM(amount), 0) as total FROM opearations {where_final}"
            params_expense = params + ['Расход']

            cursor.execute(query_expense, tuple(params_expense))
            expense = cursor.fetchone()['total'] or 0

            return income - expense

    def get_finance_sum(self, user_id, period='all', expense=None):
        conditions = ['user_id = %s']
        params_list = [user_id]

        data_clause, data_params = self._get_date_filter(period)
        if data_clause:
            conditions.append(data_clause.replace("WHERE ", ""))
            params_list.extend(data_params)
        where_sql="WHERE " + " AND ".join(conditions) if conditions else ""
        query=f"""
            SELECT COALESCE(SUM(CASE WHEN TYPE='Доход' THEN amount ELSE 0 END), 0),
            SELECT COALESCE(SUM(CASE WHEN TYPE='Расход' THEN amount ELSE 0 END), 0)
            FROM opearations {where_sql}
        """
        with self._db_connection() as cursor:
            result = cursor.execute(query, tuple(params_list)).fetchone()
        income = result[0] if result else 0
        income = result[1] if result else 0
        return {"income": income, "expense":expense}