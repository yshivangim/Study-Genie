import reflex as rx
import asyncio
from typing import Literal, TypedDict, Union
import json
from app.database import (
    GeneratedContentHistory,
    add_history,
    get_all_history,
    create_db_and_tables,
)
from app.utils import create_pdf_from_content, create_txt_from_content
from app.states.auth_state import AuthState

StudyMode = Literal["Notes", "Summary", "Explain", "Quiz", "Flashcards"]


class NotesContent(TypedDict):
    heading: str
    bullets: list[str]
    mnemonic: str | None


class SummaryContent(TypedDict):
    summary: str
    takeaways: list[str]


class ExplainContent(TypedDict):
    steps: list[str]
    example: str
    analogy: str


class QuizQuestion(TypedDict):
    question: str
    options: list[str]
    correct_answer: int
    selected_option: int | None


class QuizContent(TypedDict):
    questions: list[QuizQuestion]


class Flashcard(TypedDict):
    question: str
    answer: str
    flipped: bool


class FlashcardsContent(TypedDict):
    cards: list[Flashcard]


GeneratedContent = Union[
    str, NotesContent, SummaryContent, ExplainContent, QuizContent, FlashcardsContent
]


class StudyGenieState(rx.State):
    """Manages the state for the StudyGenie application."""

    current_mode: StudyMode = "Notes"
    user_input: str = ""
    generated_content: GeneratedContent = ""
    is_loading: bool = False
    history: list[GeneratedContentHistory] = []
    image: str = ""

    @rx.event
    async def on_load(self):
        """Load history from database on app startup."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated or not auth_state.user:
            return rx.redirect("/login")
        await create_db_and_tables()
        self.history = await get_all_history(auth_state.user["id"])

    @rx.event
    def set_mode(self, mode: StudyMode):
        """Sets the current study mode."""
        self.current_mode = mode
        self.generated_content = ""
        self.user_input = ""
        self.image = ""

    @rx.event
    def select_quiz_option(self, question_index: int, option_index: int):
        """Selects an option for a quiz question."""
        if (
            isinstance(self.generated_content, dict)
            and "questions" in self.generated_content
        ):
            self.generated_content["questions"][question_index]["selected_option"] = (
                option_index
            )

    @rx.event
    def flip_flashcard(self, card_index: int):
        """Flips a flashcard."""
        if (
            isinstance(self.generated_content, dict)
            and "cards" in self.generated_content
        ):
            self.generated_content["cards"][card_index][
                "flipped"
            ] = not self.generated_content["cards"][card_index]["flipped"]

    @rx.var
    def copyable_content(self) -> str:
        """Returns the current generated content as a string for copying."""
        if not self.generated_content or not isinstance(self.generated_content, dict):
            return ""
        return create_txt_from_content(self.generated_content, self.current_mode)

    @rx.event(background=True)
    async def process_input(self, form_data: dict):
        """Process user input to generate AI content."""
        from app.ai import generate_content, generate_content_from_image

        async with self:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_authenticated or not auth_state.user:
                return rx.redirect("/login")
            self.is_loading = True
            self.user_input = form_data.get("user_input", "")
            self.generated_content = ""
        if self.image:
            upload_dir = rx.get_upload_dir()
            file_path = upload_dir / self.image
            generated_data = await asyncio.to_thread(
                generate_content_from_image,
                self.current_mode,
                self.user_input,
                file_path,
            )
        else:
            generated_data = await asyncio.to_thread(
                generate_content, self.current_mode, self.user_input
            )
        async with self:
            if generated_data:
                if self.current_mode == "Quiz":
                    for question in generated_data.get("questions", []):
                        question["selected_option"] = None
                elif self.current_mode == "Flashcards":
                    for card in generated_data.get("cards", []):
                        card["flipped"] = False
                self.generated_content = generated_data
                auth_state = await self.get_state(AuthState)
                if auth_state.is_authenticated and auth_state.user:
                    history_item = await add_history(
                        topic=self.user_input or f"Image analysis ({self.image})",
                        mode=self.current_mode,
                        content=json.dumps(self.generated_content),
                        user_id=auth_state.user["id"],
                    )
                    if history_item:
                        self.history.insert(0, history_item)
            else:
                print("AI content generation failed.")
            self.is_loading = False
            self.image = ""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file uploads."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            yield rx.toast.error("Please log in to upload files.")
            return
        if not files:
            yield rx.toast.error("No files selected.")
            return
        file = files[0]
        upload_data = await file.read()
        upload_dir = rx.get_upload_dir()
        file_path = upload_dir / file.name
        with file_path.open("wb") as f:
            f.write(upload_data)
        self.image = file.name
        yield rx.clear_selected_files("upload_image")
        yield rx.toast.success(f"Uploaded {file.name}")

    @rx.event
    async def load_from_history(self, history_item: GeneratedContentHistory):
        """Load content from a history item."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            yield rx.redirect("/login")
            return
        if history_item["user_id"] != auth_state.user["id"]:
            yield rx.toast.error("Access denied.")
            return
        self.current_mode = history_item["mode"]
        self.user_input = history_item["topic"]
        self.generated_content = json.loads(history_item["content"])
        self.image = ""

    @rx.event
    async def download_pdf(self):
        """Download content as PDF."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            return rx.redirect("/login")
        if not self.generated_content:
            return
        pdf_bytes = create_pdf_from_content(
            self.generated_content, self.current_mode, self.user_input
        )
        return rx.download(
            data=pdf_bytes, filename=f"{self.user_input[:20]}_{self.current_mode}.pdf"
        )

    @rx.event
    async def download_txt(self):
        """Download content as TXT."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            return rx.redirect("/login")
        if not self.generated_content:
            return
        txt_content = create_txt_from_content(self.generated_content, self.current_mode)
        return rx.download(
            data=txt_content, filename=f"{self.user_input[:20]}_{self.current_mode}.txt"
        )