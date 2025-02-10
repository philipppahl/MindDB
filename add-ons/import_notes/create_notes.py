import logging
from anki.models import NotetypeDict
import time

logger = logging.getLogger(__name__)


def create_note_type(mw):
    model_manager = mw.col.models
    existing_model = model_manager.by_name("Multiple Choice")
    if existing_model:
        return
    else:
        from aqt.qt import QMessageBox
        reply = QMessageBox.question(
            None,
            "Create Note Type",
            ("I didn't find the 'Multiple Choice' note type.\n"
             "I'll create it for you."),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Ok
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

    question_format = (
        "{{question}}\n{{answer_a}}\n{{answer_b}}\n{{answer_c}}\n{{answer_d}}"
    )
    answer_format = (
        "{{FrontSide}}\n{{question}}\n{{answer_a}}\n{{answer_b}}\n{{answer_c}}"
        "\n{{answer_d}}\nCorrect Answer: {{correct_answer}}\n{{explanation}}"
    )

    def create_field(name: str, ord: int) -> dict:
        """Create a field definition with default properties."""
        return {
            "name": name,
            "ord": ord,
            "sticky": False,
            "rtl": False,
            "font": "Arial",
            "size": 12,
            "media": [],
            "plainText": True,
            "collapsed": False,
            "excludeFromSearch": False
        }

    field_names = [
        "note_id",
        "question",
        "answer_a",
        "answer_b",
        "answer_c",
        "answer_d",
        "correct_answer",
        "explanation"
    ]

    # Define the new note type, aka model
    model = NotetypeDict(
        name="Multiple Choice",
        type=0,
        id=0,
        mod=int(time.time()),
        usn=-1,
        did=1,  # Default deck
        flds=[create_field(name, i) for i, name in enumerate(field_names)],
        tmpls=[{
            "name": "Multiple Choice Card",
            "qfmt": question_format,
            "afmt": answer_format,
            "bqfmt": "",
            "bafmt": "",
            "did": None,
            "ord": 0,
            "bfont": "Arial",
            "bsize": 12
        }],
        css="""
        .explanation { font-style: italic; }
        .note-id {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 8px;
        }
        """,
        latexPre=(
            "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\"
            "usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\"
            "pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\"
            "begin{document}\n"
        ),
        latexPost="\\end{document}",
        latexsvg=False,
        req=[],
        sortf=0,
        vers=[]
    )

    # Add the new note type to the collection
    model_manager.add(model)
    model_manager.update(model)
