from pydoc import describe

import flet as ft
import itertools
import os
import shutil
import uuid
from datetime import datetime

from unicodedata import category

from database import DatabaseManager
from views.ui_factory import UIFactory


class FinanceTRackerApp:
    # Основной класс для UI главного экрана
    def __init__(self, page: ft.Page, user: dict, db: DatabaseManager):
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
        self.file_picker_context = 'add'  # or edit
        self._init_controls()

    def toggle_theme(self, e):
        if self.page.theme_mode == 'dark':
            self.page.theme_mode = 'light'
            self.controls['theme_button'].icon = ft.Icons.DARK_MODE
            self.controls['content_area'].bgcolor = "#f5f5f5"
            self.controls['header'].bgcolor = "#f5f5f5"
            self.controls['sidebar_container'].bgcolor = "#f5f5f5"
        else:
            self.page.theme_mode = 'dark'
            self.controls['theme_button'].icon = ft.Icons.LIGHT_MODE
            self.controls['content_area'].bgcolor = "#1e1e1e"
            self.controls['header'].bgcolor = "#1e1e1e"
            self.controls['sidebar_container'].bgcolor = "#001a33"
        self.page.update()

    def _get_controls(self, name):
        return self.controls[name]

    def get_content(self, tab_index):
        return self.tab_contents.get(tab_index, ft.Text("Неизвестная вкладка"))

    def set_content(self, e, index):
        self._get_controls('content_area').content = self.get_content(index)
        self.page.update()

    def divider_update(self, e: ft.DragUpdateEvent):
        new_width = self.sidebar_size + e.delta_x
        if self.min_sidebar_width <= new_width <= self.max_sidebar_width:
            self._get_controls('sidebar_container').width = new_width
            self.sidebar_size = new_width
            self._get_controls('sidebar_container').update()

    def add_operation_value(self, e):
        amount_value = self._get_controls('amount_field').value
        type_value = self._get_controls('type_dropdown').value
        category_value = self._get_controls('category_field').value
        description_value = self._get_controls('description_field').value

        if not amount_value or not type_value or not category_value:
            self._get_controls('error_banner').visible = True
            self._get_controls('error_banner').content=ft.Text("Заполните все обизательные поля")
            self.page.update()
            return
        try:
            amount=float(amount_value)
        except ValueError:
            self._get_controls('error_banner').visible = True
            self._get_controls('error_banner').content=ft.Text("Сумма должна быть числом")
            self.page.update()
            return

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
                title=ft.Text("Учет доходов и расходов"), leading=ft.Icon(ft.Icons.ATTACH_MONEY),
                on_click=lambda e: self.set_content(e, 0)
            ),
            ft.ListTile(
                title=ft.Text("Категории"), leading=ft.Icon(ft.Icons.PIE_CHART_OUTLINE),
                on_click=lambda e: self.set_content(e, 1)
            ),
            ft.ListTile(
                title=ft.Text("Аналитика доходов и расходов"), leading=ft.Icon(ft.Icons.INSERT_CHART),
                on_click=lambda e: self.set_content(e, 2)
            ),
            ft.ListTile(
                title=ft.Text("Цели и накопления"), leading=ft.Icon(ft.Icons.SAVINGS),
                on_click=lambda e: self.set_content(e, 3)
            ),
            ft.Divider(),
            ft.ListTile(
                title=ft.Text("Выйти"), leading=ft.Icon(ft.Icons.LOGOUT),
                on_click=logout
            )
        ])

        sidebar_container = ft.Container(
            content=ft.Column([
                ft.Row([username_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                sidebar_content
            ]),
            width=self.sidebar_size, bgcolor='#001a33', padding=10
        )
        self.controls['sidebar_container'] = sidebar_container

        sidebar_wrapper = ft.Container(
            content=ft.Column([sidebar_container], alignment=ft.MainAxisAlignment.CENTER),
            expand=False
        )

        divider = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
            drag_interval=10,
            content=ft.VerticalDivider(width=2.5, color=ft.Colors.LIME_700),
            on_horizontal_drag_update=self.divider_update
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




