import reflex as rx
from app.components.main_layout import main_layout
from app.state import StudyGenieState


def index() -> rx.Component:
    """The main entry page of the app."""
    return rx.el.div(main_layout(), on_mount=StudyGenieState.on_load)