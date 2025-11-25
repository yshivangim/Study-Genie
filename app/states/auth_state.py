import reflex as rx
import bcrypt
from typing import cast
from app.database import User, get_user_by_email, add_user, get_user_by_username


class AuthState(rx.State):
    """Manages user authentication and session state."""

    user: User | None = None
    error_message: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        """Checks if a user is currently authenticated."""
        return self.user is not None

    @rx.event
    async def register(self, form_data: dict):
        """Registers a new user."""
        username = form_data.get("username")
        email = form_data.get("email")
        password = form_data.get("password")
        confirm_password = form_data.get("confirm_password")
        if not all([username, email, password, confirm_password]):
            self.error_message = "All fields are required."
            return
        if len(password) < 6:
            self.error_message = "Password must be at least 6 characters long."
            return
        if password != confirm_password:
            self.error_message = "Passwords do not match."
            return
        if await get_user_by_email(email) or await get_user_by_username(username):
            self.error_message = "User already exists."
            return
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        new_user = await add_user(username, email, hashed_password)
        if new_user:
            self.user = new_user
            self.error_message = ""
            return rx.redirect("/")
        else:
            self.error_message = "Registration failed. Please try again."

    @rx.event
    async def login(self, form_data: dict):
        """Logs a user in."""
        email = form_data.get("email")
        password = form_data.get("password")
        if not email or not password:
            self.error_message = "Email and password are required."
            return
        db_user = await get_user_by_email(email)
        if db_user and bcrypt.checkpw(
            password.encode("utf-8"), db_user["password_hash"].encode("utf-8")
        ):
            self.user = cast(User, db_user)
            self.error_message = ""
            return rx.redirect("/")
        else:
            self.error_message = "Invalid email or password."

    @rx.event
    def logout(self):
        """Logs the current user out."""
        self.reset()
        return rx.redirect("/login")