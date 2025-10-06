import flet as ft
import itertools
import os
import shutil
import uuid
from datetime import datetime
from database import DatabaseManager


#Основной класс для UI главного экрана
class FinanceTrackerApp:
    def __init__(self, page:ft.Page, user:dict, db:DatabaseManager):
        self.page = page
        self.user = user
        self.db = db
        self.user_id=user['id']
        self.db.add_default_categories(self.user_id)
        #Состояние приложения
        self.operations=[]
        self.goals=[]
        self.categories=[]
        self.current_filter='all'
        self.sidebar_size=200
        self.min_sidebar_width=120
        self.max_sidebar_width = 400
        self.assets_dir='assets'
        self.selected_receipt_path=None
        self.file_picker_context='add' #or edit

    def build(self):#Собирает и возвращает корневой UI
        def logout(e):
            self.page.session.clear()
            self.page.go('/login')

        username_text=ft.Text(f"Пользователь: {self.user['username']}", weight=ft.FontWeight.BOLD)
        sidebar_content=ft.Column([
            ft.ListTile(
                title=ft.Text("Учёт доходов и расходов"), leading=ft.Icons(ft.Icons.ATTACH_MONEY)
            ),
            ft.ListTile(
                title=ft.Text("Аналитика категорий"), leading=ft.Icons(ft.Icons.PIE_CHART_OUTLINE)
            ),
            ft.ListTile(
                title=ft.Text("Графики"), leading=ft.Icons(ft.Icons.INSERT_CHART)
            ),
            ft.ListTile(
                title=ft.Text("Цели и накопления"), leading=ft.Icons(ft.Icons.SAVINGS)
            ),
            ft.Divider(),
            ft.ListTile(
                title=ft.Text("Выйти"), leading=ft.Icons(ft.Icons.LOGOUT),
                on_click=logout
            )

        ])

        self.sidebar_container=ft.Container(
            content=ft.Column([
                ft.Row([username_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                sidebar_content
            ]),
            width=self.sidebar_size, bgcolor='#001a33', padding=10
        )
        sidebar_wrapper = ft.Container(
            content=ft.Column([self.sidebar_container], alignment=ft.MainAxisAlignment.CENTER),
            expand=False,

        )

        divider=ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
            drag_interval=10,
            content=ft.VerticalDivider(width=2.5, color=ft.Colors.LIME_700)
        )

        layout=ft.Row([
            sidebar_wrapper,
            divider,

        ], expand=True)

        return  ft.View(
            '/',
            [layout],
            padding=0
        )


class MainViews:
    pass