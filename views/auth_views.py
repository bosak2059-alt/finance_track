from mmap import error

import flet as ft
from flet.core import page

from database import DatabaseManager

def LoginView(page:ft.Page, db:DatabaseManager):
    username_field = ft.TextField(label='Имя пользователя', width=300, autofocus=True)
    password_field = ft.TextField(label='Пароль', width=300, autofocus=True, can_reveal_password=True)
    error_text = ft.Text(color=ft.Colors.RED, visible=False)
    
    def login_click(e):
        user = db.get_user(username_field.value)
        if user and db.check_password(username_field.value, user['password_hash']):
            page.session.set("user_id", user["id"])
            page.session.set("password", user["password"])
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
                    ft.Text('Вход в систему', size=40, width=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton('Войти', on_click=login_click, style=ft.ButtonStyle(padding=15)),
                    ft.TextButton('Нет акка? Зарегайся', on_click=lambda e: page.go('/register'))
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
    username_field = ft.TextField(label='Имя пользователя', width=300, autofocus=True)
    password_field = ft.TextField(label='Пароль', width=300, autofocus=True, can_reveal_password=True)
    error_text = ft.Text(color=ft.Colors.RED, visible=False)

    def register_click(e):
        if not username_field.value or not password_field.value:
            error_text.value='Имя ппользователя и пароль не могут быть пустыми'
            error_text.visible=True
            page.update()
            return
        user_id=db.add_user(username_field.value, password_field.value)
        if user_id:
            db.add_default_categories(user_id)
            page.go('/login')
        else:
            error_text.value = 'Ппользователь с таким иминем уже существует'
            error_text.visible = True
            page.update()


    return ft.View(
        'register',
        [
            ft.Column(
                [
                    ft.Text('Регистрация', size=40, width=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton('Зарегистрироваться', on_click=register_click, style=ft.ButtonStyle(padding=15)),
                    ft.TextButton('Есть ак? Войти', on_click=lambda e: page.go('/login'))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )