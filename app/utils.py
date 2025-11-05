from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def create_pdf_from_content(content: dict, mode: str, topic: str) -> bytes:
    """Generates a PDF from the given content."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    title = f"StudyGenie: {mode} for '{topic}'"
    story.append(Paragraph(title, styles["h1"]))
    story.append(Spacer(1, 12))
    if mode == "Notes":
        story.append(Paragraph(content.get("heading", ""), styles["h2"]))
        for bullet in content.get("bullets", []):
            story.append(Paragraph(f"• {bullet}", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(f"Mnemonic: {content.get('mnemonic', '')}", styles["Italic"])
        )
    elif mode == "Summary":
        story.append(Paragraph("Summary", styles["h2"]))
        story.append(Paragraph(content.get("summary", ""), styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Key Takeaways", styles["h2"]))
        for i, takeaway in enumerate(content.get("takeaways", [])):
            story.append(Paragraph(f"{i + 1}. {takeaway}", styles["Normal"]))
    elif mode == "Explain":
        story.append(Paragraph("Step-by-step Explanation", styles["h2"]))
        for i, step in enumerate(content.get("steps", [])):
            story.append(Paragraph(f"{i + 1}. {step}", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Example", styles["h2"]))
        story.append(Paragraph(content.get("example", ""), styles["Code"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Analogy", styles["h2"]))
        story.append(Paragraph(f'''"{content.get("analogy", "")}"''', styles["Italic"]))
    elif mode == "Quiz":
        for i, q in enumerate(content.get("questions", [])):
            story.append(Paragraph(f"{i + 1}. {q['question']}", styles["h3"]))
            for opt in q.get("options", []):
                story.append(Paragraph(f"- {opt}", styles["Normal"]))
            story.append(Spacer(1, 6))
    elif mode == "Flashcards":
        for card in content.get("cards", []):
            story.append(Paragraph(f"Q: {card['question']}", styles["h3"]))
            story.append(Paragraph(f"A: {card['answer']}", styles["Normal"]))
            story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def create_txt_from_content(content: dict, mode: str) -> str:
    """Generates a TXT string from the given content."""
    if not content or not isinstance(content, dict):
        return ""
    if mode == "Notes":
        heading = content.get("heading", "")
        bullets = """
""".join([f"- {b}" for b in content.get("bullets", [])])
        mnemonic = content.get("mnemonic", "")
        return f"# {heading}\n\n{bullets}\n\nMnemonic: {mnemonic}"
    if mode == "Summary":
        summary = content.get("summary", "")
        takeaways = """
""".join([f"- {t}" for t in content.get("takeaways", [])])
        return f"Summary:\n{summary}\n\nKey Takeaways:\n{takeaways}"
    if mode == "Explain":
        steps = """
""".join([f"{i + 1}. {s}" for i, s in enumerate(content.get("steps", []))])
        example = content.get("example", "")
        analogy = content.get("analogy", "")
        return f"Explanation:\n{steps}\n\nExample:\n{example}\n\nAnalogy: {analogy}"
    if mode == "Quiz":
        quiz_text = []
        for i, q in enumerate(content.get("questions", [])):
            options = """
""".join([f"  - {opt}" for opt in q.get("options", [])])
            correct = q["options"][q["correct_answer"]]
            quiz_text.append(
                f"{i + 1}. {q['question']}\n{options}\nCorrect Answer: {correct}"
            )
        return """

""".join(quiz_text)
    if mode == "Flashcards":
        cards = [
            f"Q: {c['question']}\nA: {c['answer']}" for c in content.get("cards", [])
        ]
        return """

""".join(cards)
    return ""