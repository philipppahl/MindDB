
from aqt.gui_hooks import main_window_did_init
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import qconnect, QFileDialog


def import_from_sqlite():
    # Open file dialog to select SQLite database
    # TODO Use the last selected by default; store in config
    file_path, _ = QFileDialog.getOpenFileName(
        parent=mw,
        caption="Select SQLite Database",
        directory="",
        filter="SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*.*)"
    )

    if file_path:
        showInfo(f"Selected database: {file_path}")
    else:
        showInfo("No database selected.")


def setup_menu():
    add_action_msg = "Import Cards from SQLite"
    action = mw.form.menuTools.addAction(add_action_msg)
    qconnect(action.triggered, import_from_sqlite)


main_window_did_init.append(setup_menu)
