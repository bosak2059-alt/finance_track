import flet as ft
from views.auth_views import LoginView, RegisterView
from views.main_views import MainViews
from database import DatabaseManager
from views.main_views import FinanceTrackerApp

def main(page:ft.Page):
    page.title='Финансовый трекер'
    page.theme_mode=ft.ThemeMode.DARK
    page.window_width=1200
    page.window_height=800

    db=DatabaseManager(
        host='localhost',
        user='root',
        password='1234',
        database='sargis'
    )

    def route_change(route):
        page.views.clear()
        user_id=page.session.get('user_id')
        if page.route == '/login':
            page.views.append(LoginView(page, db))
        elif page.route == '/register':
            page.views.append(RegisterView(page, db))
        else:
             if not user_id:
                 page.go('/login')
             else:
                 user={
                     "id": user_id,"username": page.session.get('username')
                 }
                 app=FinanceTrackerApp(page, user, db)
                 page.views.append(app.build())
        page.update()

    page.on_route_change=route_change
    page.go(page.route)


ft.app(target=main)