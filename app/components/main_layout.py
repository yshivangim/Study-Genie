import reflex as rx
from app.state import StudyGenieState
from app.components.sidebar import sidebar
from app.components.history_sidebar import history_sidebar


def user_input_form() -> rx.Component:
    """Form for user to enter topic or text, with image upload."""
    return rx.el.form(
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.icon(tag="cloud_upload", class_name="h-8 w-8 text-gray-400"),
                    rx.el.p(
                        "Click or drag & drop an image to upload",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="text-center p-6 border-2 border-dashed border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors",
                ),
                id="upload_image",
                multiple=False,
                accept={
                    "image/png": [".png"],
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/webp": [".webp"],
                },
                max_files=1,
                class_name="w-full mb-4",
            ),
            rx.foreach(
                rx.selected_files("upload_image"),
                lambda file: rx.el.div(
                    file, class_name="p-2 bg-indigo-50 rounded border text-sm"
                ),
            ),
            rx.cond(
                StudyGenieState.image != "",
                rx.el.div(
                    rx.image(
                        src=rx.get_upload_url(StudyGenieState.image),
                        height="100px",
                        class_name="rounded-lg",
                    ),
                    rx.el.p(StudyGenieState.image, class_name="text-sm truncate"),
                    rx.icon(
                        tag="circle_x",
                        class_name="cursor-pointer text-gray-500 hover:text-red-500",
                        on_click=lambda: StudyGenieState.set_image(""),
                    ),
                    class_name="flex items-center justify-between gap-4 mb-4 p-2 border rounded-lg bg-gray-50",
                ),
            ),
            rx.el.textarea(
                placeholder=f"Enter a topic, question, or paste text to generate {StudyGenieState.current_mode}...",
                name="user_input",
                class_name="w-full p-4 border border-gray-200 rounded-xl shadow-sm focus:ring-2 focus:ring-indigo-500 transition-shadow",
                rows=5,
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon(tag="sparkles", class_name="mr-2 h-4 w-4"),
                    f"Generate {StudyGenieState.current_mode}",
                    type="submit",
                    is_loading=StudyGenieState.is_loading,
                    class_name="bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold px-6 py-3 rounded-lg shadow-md hover:shadow-lg hover:scale-[1.02] transition-all duration-200 flex items-center",
                ),
                class_name="flex justify-end mt-4",
            ),
            class_name="w-full",
        ),
        on_submit=StudyGenieState.process_input,
        reset_on_submit=True,
        class_name="w-full",
    )


from app.components.mode_displays import (
    notes_display,
    summary_display,
    explain_display,
    quiz_display,
    flashcards_display,
)


def output_display() -> rx.Component:
    """Component to display the AI-generated content."""
    return rx.el.div(
        rx.cond(
            StudyGenieState.is_loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-4 bg-gray-200 rounded w-1/4 mb-4 animate-pulse"
                ),
                rx.el.div(
                    class_name="h-3 bg-gray-200 rounded w-full mb-2 animate-pulse"
                ),
                rx.el.div(
                    class_name="h-3 bg-gray-200 rounded w-5/6 mb-2 animate-pulse"
                ),
                rx.el.div(
                    class_name="h-3 bg-gray-200 rounded w-full mb-4 animate-pulse"
                ),
                rx.el.div(class_name="h-3 bg-gray-200 rounded w-1/2 animate-pulse"),
                class_name="p-6 border border-gray-100 rounded-xl shadow-sm",
            ),
            rx.el.div(
                rx.match(
                    StudyGenieState.current_mode,
                    ("Notes", notes_display()),
                    ("Summary", summary_display()),
                    ("Explain", explain_display()),
                    ("Quiz", quiz_display()),
                    ("Flashcards", flashcards_display()),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                tag="brain-circuit",
                                class_name="h-12 w-12 text-gray-300",
                            ),
                            rx.el.h3(
                                "No Content Generated Yet",
                                class_name="mt-4 text-lg font-semibold text-gray-600",
                            ),
                            rx.el.p(
                                "Enter a topic and click 'Generate' to start.",
                                class_name="mt-1 text-sm text-gray-500",
                            ),
                            class_name="flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-200 rounded-xl",
                        )
                    ),
                ),
                class_name=rx.cond(
                    StudyGenieState.generated_content != "",
                    "transition-opacity duration-300 opacity-100",
                    "opacity-0",
                ),
            ),
        ),
        class_name="w-full mt-8",
    )


def dashboard() -> rx.Component:
    """The main dashboard view."""
    return rx.el.main(
        rx.el.div(
            rx.el.h1(
                f"StudyGenie: {StudyGenieState.current_mode} Generator",
                class_name="text-3xl font-bold text-gray-900",
            ),
            rx.el.p(
                f"Let's create some {StudyGenieState.current_mode.lower()}! Enter your topic below to get started.",
                class_name="text-gray-600 mt-1",
            ),
            class_name="mb-8",
        ),
        user_input_form(),
        output_display(),
        class_name="flex-1 p-6 md:p-10 overflow-auto",
    )


def main_layout() -> rx.Component:
    """The main layout combining sidebar and content."""
    return rx.el.div(
        sidebar(),
        dashboard(),
        history_sidebar(),
        class_name="flex min-h-screen w-full bg-gray-50/50",
    )