import logging
from aqt import mw
from aqt.qt import (QAction, QDialog, QListWidget, QLabel, QPushButton,
                    QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox)
from aqt.utils import showInfo
import sqlite3
import os
import uuid

from .create_notes import create_note_type


ADDON_NAME = "MindDB: Import Notes"
logger = logging.getLogger(__name__)


def get_config():
    """Get addon configuration or create default if not exists."""
    config = mw.addonManager.getConfig(__name__)
    logger.info(f"Config: {config}")
    if config is None:
        config = {
            "recent_files": [],
            "client_id": str(uuid.uuid4()),
            "active_file": None
        }
        save_config(config)

    if "client_id" not in config:
        config["client_id"] = str(uuid.uuid4())
        save_config(config)

    if "active_file" not in config:
        config["active_file"] = None
        save_config(config)

    return config


def save_config(config):
    """Save addon configuration."""
    try:
        mw.addonManager.writeConfig(__name__, config)
    except Exception as e:
        logger.error(f"Error saving config: {e}")


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_recent_files()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(ADDON_NAME)
        self.setMinimumWidth(400)
        self.resize(600, 500)

        layout = QVBoxLayout()

        # Recent files list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_file_selected)
        self.list_widget.currentItemChanged.connect(
            self.on_current_item_changed
        )
        layout.addWidget(QLabel("Recent catalogs:"))
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.open_button = QPushButton("Open New File...")
        self.open_button.clicked.connect(self.open_new_file)
        button_layout.addWidget(self.open_button)

        self.import_button = QPushButton("Import Notes")
        self.import_button.clicked.connect(self.on_file_selected)
        button_layout.addWidget(self.import_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_recent_files(self):
        """Load and display recent files from config."""
        config = get_config()
        self.list_widget.clear()
        active_file = config.get("active_file")

        for file_path in config["recent_files"]:
            if os.path.exists(file_path):
                self.list_widget.addItem(file_path)
                # Select the active file if it exists
                if file_path == active_file:
                    self.list_widget.setCurrentRow(self.list_widget.count()-1)

    def add_to_recent_files(self, file_path):
        """Add file to recent files list."""
        config = get_config()
        if file_path in config["recent_files"]:
            config["recent_files"].remove(file_path)
        config["recent_files"].insert(0, file_path)
        config["recent_files"] = config["recent_files"][:10]  # Keep 10
        save_config(config)
        self.load_recent_files()

    def set_active_file(self, file_path):
        """Set the active file in config."""
        logger.info(f"Setting active file: {file_path}")
        config = get_config()
        config["active_file"] = file_path
        save_config(config)

    def on_current_item_changed(self, current, previous):
        """Handle single-click selection of file from recent list."""
        if current:
            file_path = current.text()
            self.set_active_file(file_path)

    def open_new_file(self):
        """Open file dialog to select new database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MindNote Database",
            "",
            "SQLite Database (*.db *.sqlite);;All Files (*.*)"
        )
        logger.info(f"Selected file: {file_path}")
        if file_path:
            logger.info(f"Adding to recent files: {file_path}")
            self.add_to_recent_files(file_path)
            self.set_active_file(file_path)
            self.list_widget.setCurrentRow(0)

    def on_file_selected(self):
        """Handle selection of file from recent list."""
        current_item = self.list_widget.currentItem()
        if current_item:
            file_path = current_item.text()
            self.set_active_file(file_path)
            self.import_notes(file_path)

    def ensure_deck_exists(self, deck_name: str) -> int:
        """Ensure deck exists, create if not. Returns deck ID."""
        logger.info(f"Trying to find deck: {deck_name}")
        deck_id = mw.col.decks.id_for_name(deck_name)

        if deck_id is None:
            logger.info(f"Deck not found: {deck_name}")
            reply = QMessageBox.question(
                self,
                "Create Deck",
                (f"The deck '{deck_name}' doesn't exist.\nWould you like me to"
                 " create it?"),
                (QMessageBox.StandardButton.Ok |
                 QMessageBox.StandardButton.Cancel),
                QMessageBox.StandardButton.Ok
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return None

            result = mw.col.decks.add_normal_deck_with_name(deck_name)
            deck_id = result.id  # Extract the actual deck ID from the result
            logger.info(f"Created new deck: {deck_name} (id: {deck_id})")

        else:
            logger.info(f"Found existing deck: {deck_name} (id: {deck_id})")

        return deck_id

    def import_notes(self, file_path):
        """Import notes from selected database."""
        if not os.path.exists(file_path):
            showInfo(f"Database file not found: {file_path}")
            return

        create_note_type(mw)

        with sqlite3.connect(file_path) as src_conn:
            src_cursor = src_conn.cursor()

            # Get client ID from config
            client_id = get_config()["client_id"]

            # Get unimported notes for this client
            src_cursor.execute("""
                SELECT DISTINCT n.*, d.name as deck_name
                FROM notes n
                JOIN decks d ON n.deck_id = d.id
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM note_client_imports nci
                    JOIN client_imports ci ON nci.client_import_id = ci.id
                    WHERE nci.note_id = n.id
                    AND ci.client_id = ?
                )
            """, (client_id,))

            notes = src_cursor.fetchall()

            if not notes:
                showInfo("No new notes to import.")
                return

            # Create a new client import record
            src_cursor.execute("""
                INSERT INTO client_imports (client_id)
                VALUES (?)
                RETURNING id
            """, (client_id,))
            client_import_id = src_cursor.fetchone()[0]

            # Import each note
            for note_data in notes:
                # Ensure deck exists in Anki
                deck_name = note_data[-1]  # last column from our query
                deck_id = self.ensure_deck_exists(deck_name)
                if deck_id is None:
                    showInfo("Import cancelled - deck creation declined")
                    return

                mw.col.decks.select(deck_id)

                # Create new note
                note = mw.col.newNote()
                note.note_type()['did'] = deck_id

                # Fill note fields
                note.fields[0] = str(note_data[0])  # note_id
                note.fields[1] = note_data[2]       # question
                note.fields[2] = note_data[3]       # answer_a
                note.fields[3] = note_data[4]       # answer_b
                note.fields[4] = note_data[5]       # answer_c
                note.fields[5] = note_data[6]       # answer_d
                note.fields[6] = note_data[7]       # correct_answer
                note.fields[7] = note_data[8]       # explanation

                # Add note to collection
                mw.col.addNote(note)

                # Record the import
                src_cursor.execute("""
                    INSERT INTO note_client_imports (note_id, client_import_id)
                    VALUES (?, ?)
                """, (note_data[0], client_import_id))

            # Commit the changes
            src_conn.commit()

            showInfo(f"Successfully imported {len(notes)} notes.")
            mw.reset()
            self.accept()  # Close the dialog after successful import


def show_import_dialog():
    """Show the import dialog."""
    dialog = ImportDialog(mw)
    dialog.exec()


# Create menu item
action = QAction(ADDON_NAME, mw)
action.triggered.connect(show_import_dialog)
mw.form.menuTools.addAction(action)
