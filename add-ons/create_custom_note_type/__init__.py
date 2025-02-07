from anki.models import NotetypeDict
from aqt.gui_hooks import main_window_did_init
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import qconnect
import time


def create_multiple_choice():
    model_manager = mw.col.models
    existing_model = model_manager.byName("Multiple Choice")
    if existing_model:
        showInfo("The 'Multiple Choice' note type already exists.")
        return

    question_format = (
        "{{question}}\n{{answer_1}}\n{{answer_2}}\n{{answer_3}}\n{{answer_4}}"
    )
    answer_format = (
        "{{FrontSide}}\n{{question}}\n{{answer_1}}\n{{answer_2}}\n{{answer_3}}\n"
        "{{answer_4}}\nCorrect Answer: {{correct_answer}}\n{{explanation}}"
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
        "answer_1",
        "answer_2",
        "answer_3",
        "answer_4",
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
    showInfo("New note type 'Multiple Choice' has been added.")


# Hook into Anki's GUI to add a menu option
def setup_menu():
    add_action_msg = "Create Multiple Choice Note Type"
    action = mw.form.menuTools.addAction(add_action_msg)
    qconnect(action.triggered, create_multiple_choice)


main_window_did_init.append(setup_menu)
