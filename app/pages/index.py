import reflex as rx
from app.components.main_layout import main_layout
from app.state import StudyGenieState, AuthState


@rx.page(on_load=StudyGenieState.on_load, route="/")
def index() -> rx.Component:
    """The main entry page of the app."""
    return rx.cond(
        AuthState.is_authenticated,
        main_layout(),
        rx.el.div(
            rx.el.h1("Welcome to StudyGenie"),
            rx.el.p("Please log in to continue."),
            rx.el.a("Login", href="/login"),
            rx.el.a("Register", href="/register"),
        ),
    )