import flet as ft
from unicodedata import category


class UIFactory:
    def __init__(self, app_logic):
        self.logic = app_logic

    def create_all_controls(self):
        controls = {}
     #Создаем и возвращаем UI компоненты
        controls['amount_field'] = ft.TextField(label="Сумма", keyboard_type=ft.KeyboardType.NUMBER)
        controls['type_dropdown'] = ft.Dropdown(label="Тип", options=[ft.dropdown.Option("Доход"),ft.dropdown.Option("Расход")])
        controls['category_field'] = ft.TextField(label="Категория")
        controls['description_field'] = ft.TextField(label="Описание")
        controls['category_input'] = ft.TextField(label="Новая категория")
        #Поля для вкладки цели
        controls['goal_name_field'] = ft.TextField(label="Название цели")
        controls['goal_target_field'] = ft.TextField(label="Требуемая сумма", keyboard_type=ft.KeyboardType.NUMBER)
        controls['goal_error_text'] = ft.TextField(color=ft.Colors.RED, visible=False)
        # Поля для вкладки цели
        controls['receip_filename_text'] = ft.Text("Чек не прикреплен", color = ft.Colors.GREY)
        controls['attach_receip_button'] = ft.ElevatedButton(text="Прикрепить чек",icon=ft.Icons.ATTACH_FILE)

        controls['balance_label'] = ft.Text(value="Баланс: 0 ₽", size=20, weight=ft.FontWeight.BOLD, color='#CCFF00')
        controls['operation_list'] = ft.Column(scroll=ft.ScrollMode.AUTO)
        controls['goal_list'] = ft.Column(scroll=ft.ScrollMode.AUTO, spacing= 10)
        controls['category_analytics_list'] = ft.Column(scroll=ft.ScrollMode.AUTO)

        # Компоненты для фильтрации по времени
        controls['analytics_period_label'] = ft.Text(f"Данные за все время:",italic=True, color=ft.Colors.WHITE60)
        controls['analytics_total_income'] = ft.Text("0.00 ₽", size=24, weight=ft.FontWeight.BOLD)
        controls['analytics_total_expense'] = ft.Text("0.00 ₽", size=24, weight=ft.FontWeight.BOLD)
        controls['analytics_savings_rate'] = ft.Text("0.0%", size=24, weight=ft.FontWeight.BOLD)
        controls['analytics_avg_daily_expense'] = ft.Text("0.00 ₽", size=24, weight=ft.FontWeight.BOLD)

        controls['pie_chart'] = ft.PieChart(sections=[], center_space_radius=40, expand=True)
        controls['chart_placeholder'] = ft.Container(
            content=ft.Text("Нет данных о расходах за выбранный период для построения графика", color=ft.Colors.WHITE60),
            alignment=ft.alignment.center, expand=True, visible=False
        )
        # -----Кнопки----
        controls['theme_button']=ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=self.logic.toggle_theme, icon_color="#009add")
        controls['data_filter_buttons'] = ft.SegmentedButton(
            selected={"all"},
            segments=[
                ft.Segment("all", label=ft.Text("Все")),
                ft.Segment("month", label=ft.Text("Месяц")),
                ft.Segment("week", label=ft.Text("Неделя")),
                ft.Segment("today", label=ft.Text("Сегодня"))
            ]
        )
        controls['add_button'] = ft.ElevatedButton(
            "Добавить",bgcolor='#009add', color='#ffffff',
            on_click=self.logic.add_operation_value,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=7),
                padding=ft.padding.symmetric(vertical=15, horizontal=30),
                text_style=ft.TextStyle(size=20, weight=ft.FontWeight.W_700),
            )
        )

        # Баннеры и контейнеры
        controls['error_banner'] = ft.Banner(
            actions=[ft.Container(width=0, height=0, on_click=lambda e: None)],
            visible=False,
            bgcolor="#7f0000",
            content=ft.Text("Ошибка")
        )

        controls['header'] = ft.Container(
            content=ft.Row(
                [ft.Text("Финансовый трекер", size=20, weight=ft.FontWeight.BOLD),controls['theme_button']],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.8, "#2a2b30")
        )

        controls['content_area'] = ft.Container(padding=20, expand=True, bgcolor="#1e1e1e")
        return controls

    def create_tab_content(self, controls):
        income_expense_content = ft.Column([
            controls['error_banner'],
            ft.Row([controls['balance_label']], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Учет доходов и расходов",size=20),
            ft.Divider(),
            controls['amount_field'],controls['type_dropdown'], controls['category_field'],controls['description_field'],
            ft.Row([
                controls['attach_receip_button'],
                controls['receip_filename_text']
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            controls['add_button'], ft.Divider(),
            ft.Row([
                ft.Text("Последние операции: ",weight=ft.FontWeight.BOLD),
                controls['data_filter_buttons']
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            controls['operation_list']
        ],scroll=ft.ScrollMode.AUTO)

        category_content = ft.Column([
            ft.Text("Категории", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([controls['category_input'],
                ft.ElevatedButton("Добавить категорию", on_click=self.logic.add_new_category ,style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=7),
                padding=ft.padding.symmetric(vertical=15, horizontal=30),
                text_style=ft.TextStyle(size=20, weight=ft.FontWeight.W_700, letter_spacing=2)
                ))
            ])
        ], scroll=ft.ScrollMode.AUTO)

        analytics_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Ключевые показатели", size=20, weight=ft.FontWeight.BOLD),
                        controls['analytics_period_label']
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Card(content=ft.Container(content=ft.Column([
                            ft.ListTile(leading=ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.GREEN), title=ft.Text("Общий доход")),
                            ft.Row([controls['analytics_total_income']], alignment=ft.MainAxisAlignment.END)
                        ]), width=250, padding=10)),
                        ft.Card(content=ft.Container(content=ft.Column([
                            ft.ListTile(leading=ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.RED), title=ft.Text("Общий расход")),
                            ft.Row([controls['analytics_total_expense']], alignment=ft.MainAxisAlignment.END)
                        ]), width=250, padding=10)),
                    ],
                    spacing=20, alignment= ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [
                        ft.Card(content=ft.Container(content=ft.Column([
                            ft.ListTile(leading=ft.Icon(ft.Icons.SAVINGS_OUTLINED, color=ft.Colors.BLUE), title=ft.Text("Коэффициент сбережений")),
                            ft.Row([controls['analytics_savings_rate']], alignment=ft.MainAxisAlignment.END)
                        ]), width=250, padding=10)),
                        ft.Card(content=ft.Container(content=ft.Column([
                            ft.ListTile(leading=ft.Icon(ft.Icons.CALCULATE_OUTLINED, color=ft.Colors.ORANGE), title=ft.Text("Средний расход в день")),
                            ft.Row([controls['analytics_avg_daily_expense']], alignment=ft.MainAxisAlignment.END)
                        ]), width=250, padding=10)),
                    ],
                    spacing=20, alignment= ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(),
                ft.Text("Распределение расходов", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Stack([controls['pie_chart'], controls['chart_placeholder']]),
                    height=250
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

        goals_content = ft.Column([
            ft.Text("Мои финансовые цели", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Card(content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Создать новую цель", size=16, weight=ft.FontWeight.BOLD),
                controls['goal_name_field'],
                controls['goal_target_field'],
                controls['goal_error_text'],
                ft.Row([ft.ElevatedButton("Создать")], alignment=ft.MainAxisAlignment.END)
            ]))),
            ft.Divider(height=20), controls['goal_list']
        ], scroll=ft.ScrollMode.AUTO)

        return {
            0:income_expense_content,
            1: category_content,
            2: analytics_content,
            3: goals_content
        }