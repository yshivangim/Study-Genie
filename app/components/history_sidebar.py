import reflex as rx
from app.state import StudyGenieState, GeneratedContentHistory


def history_item(item: GeneratedContentHistory) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.p(
                item.topic,
                class_name="font-semibold text-sm truncate",
                max_width="180px",
            ),
            rx.el.div(
                rx.el.span(
                    item.mode,
                    class_name="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium",
                ),
                rx.el.span(
                    item.created_at.to_string().split(" ")[0],
                    class_name="text-xs text-gray-500",
                ),
                class_name="flex items-center justify-between mt-1",
            ),
            class_name="w-full text-left",
        ),
        on_click=lambda: StudyGenieState.load_from_history(item),
        class_name="w-full p-2 rounded-lg hover:bg-gray-100 transition-colors",
    )


def history_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.h3("History", class_name="text-lg font-semibold"),
                class_name="flex h-16 shrink-0 items-center border-b px-6",
            ),
            rx.el.div(
                rx.cond(
                    StudyGenieState.history.length() > 0,
                    rx.foreach(StudyGenieState.history, history_item),
                    rx.el.div(
                        rx.icon(tag="history", class_name="h-8 w-8 text-gray-400"),
                        rx.el.p(
                            "No history yet.", class_name="text-sm text-gray-500 mt-2"
                        ),
                        class_name="flex flex-col items-center justify-center h-full text-center p-4",
                    ),
                ),
                class_name="flex-1 overflow-auto p-2",
            ),
            class_name="flex h-full max-h-screen flex-col",
        ),
        class_name="hidden border-l bg-gray-50/50 lg:block w-72 shrink-0",
    )