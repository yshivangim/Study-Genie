import reflex as rx
from app.state import StudyGenieState, QuizQuestion, Flashcard


def download_buttons() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon(tag="copy", class_name="h-4 w-4 mr-2"),
            "Copy",
            on_click=rx.set_clipboard(StudyGenieState.copyable_content),
            class_name="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors",
        ),
        rx.el.button(
            rx.icon(tag="download", class_name="h-4 w-4 mr-2"),
            "PDF",
            on_click=StudyGenieState.download_pdf,
            class_name="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors",
        ),
        rx.el.button(
            rx.icon(tag="file-text", class_name="h-4 w-4 mr-2"),
            "TXT",
            on_click=StudyGenieState.download_txt,
            class_name="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors",
        ),
        class_name="flex items-center gap-4",
    )


def notes_display() -> rx.Component:
    """Display for generated notes."""
    content = StudyGenieState.generated_content.to(dict)
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                content["heading"], class_name="text-xl font-semibold text-gray-800"
            ),
            download_buttons(),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.ul(
            rx.foreach(
                content.get("bullets", []).to(list[str]),
                lambda bullet: rx.el.li(
                    rx.markdown(bullet), class_name="mb-2 list-disc ml-5"
                ),
            ),
            class_name="text-gray-700 leading-relaxed",
        ),
        rx.el.div(
            rx.icon(tag="lightbulb", class_name="mr-2 h-5 w-5 text-yellow-500"),
            rx.el.p(content.get("mnemonic"), class_name="font-medium"),
            class_name="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center",
        ),
        class_name="p-6 border border-gray-100 rounded-xl bg-white shadow-sm",
    )


def summary_display() -> rx.Component:
    """Display for generated summary."""
    content = StudyGenieState.generated_content.to(dict)
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Summary for '{StudyGenieState.user_input}'",
                class_name="text-xl font-semibold text-gray-800",
            ),
            download_buttons(),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.p(content["summary"], class_name="mb-4 text-gray-700 leading-relaxed"),
        rx.el.h3("Key Takeaways", class_name="font-semibold text-gray-800 mb-2"),
        rx.el.ol(
            rx.foreach(
                content["takeaways"].to(list[str]),
                lambda takeaway: rx.el.li(
                    takeaway, class_name="mb-1 list-decimal ml-5"
                ),
            ),
            class_name="text-gray-700 leading-relaxed",
        ),
        class_name="p-6 border border-gray-100 rounded-xl bg-white shadow-sm",
    )


def explain_display() -> rx.Component:
    """Display for generated explanation."""
    content = StudyGenieState.generated_content.to(dict)
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Explanation for '{StudyGenieState.user_input}'",
                class_name="text-xl font-semibold text-gray-800",
            ),
            download_buttons(),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.h3(
            "Step-by-step Explanation", class_name="font-semibold text-gray-800 mb-2"
        ),
        rx.el.ol(
            rx.foreach(
                content["steps"].to(list[str]),
                lambda step: rx.el.li(step, class_name="mb-1 list-decimal ml-5"),
            ),
            class_name="mb-4 text-gray-700 leading-relaxed",
        ),
        rx.el.h3("Example", class_name="font-semibold text-gray-800 mb-2"),
        rx.el.p(
            content["example"],
            class_name="mb-4 p-3 bg-gray-50 rounded-md border text-sm",
        ),
        rx.el.h3("Analogy", class_name="font-semibold text-gray-800 mb-2"),
        rx.el.p(f'''"{content["analogy"]}"''', class_name="italic text-gray-600"),
        class_name="p-6 border border-gray-100 rounded-xl bg-white shadow-sm",
    )


def quiz_question_card(question: QuizQuestion, index: int) -> rx.Component:
    """A single card for a quiz question."""
    return rx.el.div(
        rx.el.p(
            f"{index + 1}. {question['question']}", class_name="font-semibold mb-3"
        ),
        rx.el.div(
            rx.foreach(
                question["options"],
                lambda option, opt_index: rx.el.button(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                class_name=rx.cond(
                                    question["selected_option"] == opt_index,
                                    "h-2.5 w-2.5 rounded-full bg-indigo-500",
                                    "",
                                )
                            ),
                            class_name="h-4 w-4 rounded-full border border-gray-400 flex items-center justify-center",
                        ),
                        rx.el.span(option),
                        class_name="flex items-center gap-3",
                    ),
                    on_click=lambda: StudyGenieState.select_quiz_option(
                        index, opt_index
                    ),
                    class_name=rx.cond(
                        question["selected_option"] == opt_index,
                        "w-full text-left p-3 rounded-lg border-2 border-indigo-500 bg-indigo-50",
                        "w-full text-left p-3 rounded-lg border hover:bg-gray-50",
                    ),
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
        ),
        rx.cond(
            question["selected_option"].is_not_none(),
            rx.cond(
                question["selected_option"] == question["correct_answer"],
                rx.el.div(
                    rx.icon(tag="check_check", class_name="h-5 w-5 mr-2"),
                    "Correct!",
                    class_name="mt-3 flex items-center font-medium text-green-600 p-2 bg-green-50 rounded-md",
                ),
                rx.el.div(
                    rx.icon(tag="circle_x", class_name="h-5 w-5 mr-2"),
                    f"Incorrect. The right answer is: {question['options'][question['correct_answer']]}",
                    class_name="mt-3 flex items-center font-medium text-red-600 p-2 bg-red-50 rounded-md",
                ),
            ),
        ),
        class_name="p-4 border rounded-xl mb-4 bg-white",
    )


def quiz_display() -> rx.Component:
    """Display for generated quiz."""
    content = StudyGenieState.generated_content.to(dict)
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Quiz on '{StudyGenieState.user_input}'",
                class_name="text-xl font-semibold text-gray-800",
            ),
            download_buttons(),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.foreach(content["questions"].to(list[QuizQuestion]), quiz_question_card),
    )


def flashcard_item(card: Flashcard, index: int) -> rx.Component:
    """A single flashcard item."""
    return rx.el.div(
        rx.el.div(
            rx.cond(
                card["flipped"],
                rx.el.div(card["answer"], class_name="p-4 text-center"),
                rx.el.div(card["question"], class_name="p-4 text-center font-semibold"),
            ),
            class_name=rx.cond(
                card["flipped"],
                "absolute w-full h-full [transform:rotateY(180deg)] [backface-visibility:hidden] flex items-center justify-center bg-gray-100 rounded-xl",
                "absolute w-full h-full [backface-visibility:hidden] flex items-center justify-center bg-white rounded-xl",
            ),
        ),
        on_click=lambda: StudyGenieState.flip_flashcard(index),
        class_name=rx.cond(
            card["flipped"],
            "relative w-full h-32 [transform-style:preserve-3d] transition-transform duration-500 [transform:rotateY(180deg)] cursor-pointer shadow-sm border rounded-xl",
            "relative w-full h-32 [transform-style:preserve-3d] transition-transform duration-500 cursor-pointer shadow-sm border rounded-xl",
        ),
    )


def flashcards_display() -> rx.Component:
    """Display for generated flashcards."""
    content = StudyGenieState.generated_content.to(dict)
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                f"Flashcards for '{StudyGenieState.user_input}'",
                class_name="text-xl font-semibold text-gray-800",
            ),
            download_buttons(),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.div(
            rx.foreach(content["cards"].to(list[Flashcard]), flashcard_item),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 [perspective:1000px]",
        ),
    )