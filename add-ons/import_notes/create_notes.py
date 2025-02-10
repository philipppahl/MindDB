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

    question_format = """
<div class="card">
    <div class="question">{{question}}</div>
    <button class="show-answers" onclick="revealAnswers()">Show Answers</button>
    <div class="answer-options">
        <p>(a) {{answer_a}}</p>
        <p>(b) {{answer_b}}</p>
        <p>(c) {{answer_c}}</p>
        <p>(d) {{answer_d}}</p>
    </div>
</div>

<script>
    function revealAnswers() {
        var answers = document.querySelector('.answer-options');
        var button = document.querySelector('.show-answers');

        if (answers.style.display === 'none' || answers.style.display === '') {
            answers.style.display = 'block';
            button.textContent = 'Hide Answers';
        } else {
            answers.style.display = 'none';
            button.textContent = 'Show Answers';
        }
    }
</script>
"""
    answer_format = """
<div class="card">
    <div class="question">{{question}}</div>
    <div class="answer-options">
        <p>(a) {{answer_a}}</p>
        <p>(b) {{answer_b}}</p>
        <p>(c) {{answer_c}}</p>
        <p>(d) {{answer_d}}</p>
    </div>
    <div class="explanation">
        <strong>Correct Answer:</strong> {{correct_answer}}<br>
        <strong>Explanation:</strong> {{explanation}}
    </div>
</div>
"""

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
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            background-color: #f0f0f0;
        }

        .card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 80%;
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
            color: #333;
        }

        .question {
            font-size: 18px;
            margin-bottom: 15px;
            color: #000;
        }

        .answer-options {
            display: none;
            text-align: left;
            color: #000;
        }

        .answer-options p {
            margin: 5px 0;
        }

        .show-answers {
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .explanation {
            margin-top: 20px;
            font-style: italic;
            text-align: left;
            color: #000;
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
