import reflex as rx
from app.pages.index import index
from app.database import create_db_and_tables

app = rx.App(
    theme=rx.theme(appearance="light", accent_color="indigo", radius="medium"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
    style={"font_family": "Poppins, sans-serif"},
)
app.add_page(index)