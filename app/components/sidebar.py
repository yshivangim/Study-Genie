import reflex as rx
from app.state import StudyGenieState
from app.states.auth_state import AuthState


def nav_item(icon: str, text: str, selected: rx.Var[bool]) -> rx.Component:
    """A single navigation item for the sidebar."""
    return rx.el.a(
        rx.el.div(
            rx.icon(tag=icon, class_name="h-5 w-5"),
            rx.el.span(text, class_name="font-medium"),
            class_name=rx.cond(
                selected,
                "flex items-center gap-3 rounded-lg bg-indigo-100 px-3 py-2 text-indigo-600 transition-all hover:text-indigo-600",
                "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
            ),
        ),
        on_click=lambda: StudyGenieState.set_mode(text),
        href="#",
    )


def user_profile() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(AuthState.user["username"].to(str), class_name="font-semibold"),
                rx.el.p(
                    AuthState.user["email"].to(str), class_name="text-xs text-gray-500"
                ),
                class_name="grid gap-0.5 text-xs",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.button(
            rx.icon(tag="log-out", class_name="h-4 w-4"),
            on_click=AuthState.logout,
            class_name="p-2 rounded-md hover:bg-gray-100",
        ),
        class_name="flex items-center justify-between border-t p-4",
    )


def sidebar() -> rx.Component:
    """The main sidebar component for navigation."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon(tag="brain-circuit", class_name="h-8 w-8 text-indigo-600"),
                    rx.el.span("StudyGenie", class_name="font-semibold text-xl"),
                    href="#",
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-16 shrink-0 items-center border-b px-6",
            ),
            rx.el.nav(
                nav_item(
                    "notebook-pen", "Notes", StudyGenieState.current_mode == "Notes"
                ),
                nav_item(
                    "file-text", "Summary", StudyGenieState.current_mode == "Summary"
                ),
                nav_item(
                    "message-circle-question",
                    "Explain",
                    StudyGenieState.current_mode == "Explain",
                ),
                nav_item(
                    "clipboard-check", "Quiz", StudyGenieState.current_mode == "Quiz"
                ),
                nav_item(
                    "layers", "Flashcards", StudyGenieState.current_mode == "Flashcards"
                ),
                class_name="flex-1 overflow-auto py-4 flex flex-col items-start px-4 text-sm font-medium gap-1",
            ),
            user_profile(),
            class_name="flex h-full max-h-screen flex-col",
        ),
        class_name="hidden border-r bg-gray-50/50 md:block w-64 shrink-0",
    )