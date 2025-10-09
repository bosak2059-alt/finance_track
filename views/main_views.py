import flet as ft
import itertools
import os
import shutil
import uuid
from datetime import datetime
from database import  DatabaseManager
from views.ui_factory import UIFactory

class FinanceTRackerApp:
#Основной класс для UI главного экрана
    def __init__(self, page:ft.Page, user: dict, db:DatabaseManager):
        self.page = page
        self.user = user
        self.user_id = user['id']
        self.db = db
        self.db.add_default_categories(self.user_id)
        # Состояние приложения
        self.operations = []
        self.goals = []
        self.categories = []
        self.current_filter = 'all'
        self.sidebar_size = 220
        self.min_sidebar_width = 190
        self.max_sidebar_width = 420
        self.assets_dir = 'assets'
        self.selected_receipt_path = None
        self.file_picker_context = 'add' #or edit
        self._init_controls()


    def _get_controls(self, name):
        return self.controls[name]

    def _init_controls(self):
        ui_factory = UIFactory(self)
        self.controls = ui_factory.create_all_controls()
        self.tab_contents = ui_factory.create_tab_content(self.controls)

    def build(self):
        # Собирает и возвращает корневой UI
        def logout(e):
            self.page.session.clear()
            self.page.go('/login')
        username_text = ft.Text(f"Пользователь: {self.user['username']}", weight=ft.FontWeight.BOLD)
        sidebar_content = ft.Column([
            ft.ListTile(
                title=ft.Text("Учет доходов и расходов"), leading=ft.Icon(ft.Icons.ATTACH_MONEY)
            ),
            ft.ListTile(
                title=ft.Text("Аналитика категорий"), leading=ft.Icon(ft.Icons.PIE_CHART_OUTLINE)
            ),
            ft.ListTile(
                title=ft.Text("Графики"), leading=ft.Icon(ft.Icons.INSERT_CHART)
            ),
            ft.ListTile(
                title=ft.Text("Цели и накопления"), leading=ft.Icon(ft.Icons.SAVINGS)
            ),
            ft.Divider(),
            ft.ListTile(
                title=ft.Text("Выйти"), leading=ft.Icon(ft.Icons.LOGOUT),
                on_click=logout
            )
        ])

        self.sidebar_container = ft.Container(
            content=ft.Column([
                ft.Row([username_text],alignment= ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                sidebar_content
            ]),
            width=self.sidebar_size, bgcolor='#001a33', padding=10
        )

        sidebar_wrapper = ft.Container(
            content=ft.Column([self.sidebar_container],alignment=ft.MainAxisAlignment.CENTER),
            expand=False
        )

        divider = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
            drag_interval=10,
            content=ft.VerticalDivider(width=2.5, color=ft.Colors.LIME_700)
        )

        layout = ft.Row([
            sidebar_wrapper,
            divider,
            ft.Column(
                [self._get_controls('header'), self._get_controls('content_area')],
                expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )
        ], expand=True)

        return ft.View(
            '/',
            [layout],
            padding=0
        )



