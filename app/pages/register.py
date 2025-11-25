import reflex as rx
from app.states.auth_state import AuthState


def registration_page() -> rx.Component:
    """The user registration page."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Create your StudyGenie Account",
                class_name="text-2xl font-bold text-center",
            ),
            rx.el.p(
                "Already have an account? ",
                rx.el.a(
                    "Log in here",
                    href="/login",
                    class_name="text-indigo-600 font-semibold",
                ),
                class_name="text-center text-gray-600 mt-2",
            ),
            rx.el.form(
                rx.cond(
                    AuthState.error_message != "",
                    rx.el.div(
                        AuthState.error_message,
                        class_name="p-3 bg-red-100 text-red-700 border border-red-200 rounded-lg mb-4 text-sm",
                    ),
                ),
                rx.el.div(
                    rx.el.label("Username", class_name="text-sm font-medium"),
                    rx.el.input(
                        placeholder="your_username",
                        name="username",
                        class_name="w-full p-3 border rounded-lg mt-1",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label("Email", class_name="text-sm font-medium"),
                    rx.el.input(
                        placeholder="you@example.com",
                        name="email",
                        type="email",
                        class_name="w-full p-3 border rounded-lg mt-1",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label("Password", class_name="text-sm font-medium"),
                    rx.el.input(
                        placeholder="••••••••",
                        name="password",
                        type="password",
                        class_name="w-full p-3 border rounded-lg mt-1",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label("Confirm Password", class_name="text-sm font-medium"),
                    rx.el.input(
                        placeholder="••••••••",
                        name="confirm_password",
                        type="password",
                        class_name="w-full p-3 border rounded-lg mt-1",
                    ),
                    class_name="mb-6",
                ),
                rx.el.button(
                    "Create Account",
                    type="submit",
                    class_name="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold py-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-200",
                ),
                on_submit=AuthState.register,
                reset_on_submit=True,
                class_name="mt-6",
            ),
            class_name="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg border",
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-50 font-['Poppins']",
        on_mount=AuthState.set_error_message(""),
    )