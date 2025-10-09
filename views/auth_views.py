import flet as ft
from database import DatabaseManager


def LoginView(page: ft.Page, db: DatabaseManager):
    username_field = ft.TextField(label="Имя пользователя", width=300, autofocus=True)
    password_field = ft.TextField(label="Пароль", width=300, password=True, can_reveal_password=True)
    error_text = ft.Text(color=ft.Colors.RED, visible=False)

    def login_click(e):
        user = db.get_user(username_field.value)
        if user and db.check_password(password_field.value, user['password_hash']):
            page.session.set("user_id", user["id"])
            page.session.set("username", user["username"])
            page.go("/")
        else:
            error_text.value = "Неверное имя или пароль"
            error_text.visible = True
            page.update()

    return ft.View(
        '/login',
        [
            ft.Column(
                [
                    ft.Text("Вход в систему", size=35, weight=ft.FontWeight.BOLD),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton("Войти", on_click=login_click, style=ft.ButtonStyle(padding=20)),
                    ft.TextButton("Нет акка? Зарегайся", on_click=lambda e: page.go("/register"))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def RegisterView(page: ft.Page, db: DatabaseManager):
    username_field = ft.TextField(label="Имя пользователя", width=300, autofocus=True)
    password_field = ft.TextField(label="Пароль", width=300, password=True, can_reveal_password=True)
    error_text = ft.Text(color=ft.Colors.RED, visible=False)

    def register_click(e):
        if not username_field.value or not password_field.value:
            error_text.value = "Имя пользователя и пароль не могут быть пустыми"
            error_text.visible = True
            page.update()
            return

        user_id = db.add_user(username_field.value, password_field.value)
        if user_id:
            db.add_default_categories(user_id)
            page.go('/login')
        else:
            error_text.value = "Пользователь с таким именем уже существует"
            error_text.visible = True
            page.update()

    return ft.View(
        '/register',
        [
            ft.Column(
                [
                    ft.Text("Регистрация", size=35, weight=ft.FontWeight.BOLD),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton("Зарегаться", on_click=register_click, style=ft.ButtonStyle(padding=20)),
                    ft.TextButton("Есть аккаунт? Войти", on_click=lambda e: page.go("/login"))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

