import logging
import sqlite3
import os
from datetime import datetime
from contextlib import closing
from .models import ClientImport, Deck, Note, Transcript

logger = logging.getLogger(__name__)


class DB:
    """Database handler for persistent storage."""
    def __init__(self, db_name):
        """Initialize database connection.

        Args:
            db_name: Path to SQLite database file
        """
        self._db_name = db_name
        self._connection = None
        logger.debug("Initialized DB with database: %s", self._db_name)
        self.create_tables()

    def connect(self):
        """Get or create a database connection.

        Returns:
            sqlite3.Connection: Database connection object
        """
        if self._connection is None:
            logger.debug("Creating new database connection")
            self._connection = sqlite3.connect(self._db_name)
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self):
        """Close the database connection if it exists."""
        if self._connection is not None:
            logger.debug("Closing database connection")
            self._connection.close()
            self._connection = None

    def __del__(self):
        """Ensure connection is closed when object is destroyed.

        Example:
        >>> db = DB(':memory:')
        >>> db.create_tables()
        >>> del db
        """
        self.close()

    def create_tables(self):
        """Create database tables from schema file schema.sql."""
        schema_path = os.path.join(
            os.path.dirname(__file__),
            'schema.sql'
        )

        logger.debug(f'Creating tables from {schema_path}')

        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            with open(schema_path, 'r') as sql_file:
                sql_commands = sql_file.read().split(';')
                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)

                conn.commit()
                logger.debug("Created tables: %s",
                             self.list_tables())

    def insert_transcript(self, filename, checksum, **kwargs):
        """Insert a new transcript record.

        Args:
            filename: Name of the transcript file
            checksum: Integer checksum of the file contents

        Returns:
            int: ID of the inserted record
        """
        sql = (
            "INSERT INTO transcripts (filename, checksum, created_at)"
            "VALUES (?, ?, datetime('now'))"
        )
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, (filename, checksum))
            conn.commit()
            return cursor.lastrowid

    def get_or_insert_transcript(self, filename, checksum, **kwargs):
        """Get or insert a new transcript record.

        Args:
            filename: Name of the transcript file
            checksum: Integer checksum of the file contents

        Returns:
            int: ID of the inserted record
        """
        with closing(self.connect().cursor()) as cursor:
            sql = (
                "SELECT id FROM transcripts "
                "WHERE filename = ? AND checksum = ?"
            )
            cursor.execute(sql, (filename, checksum))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return self.insert_transcript(filename, checksum, **kwargs)

    def get_transcript(self, transcript_id):
        """Retrieve a transcript by ID.

        Args:
            transcript_id: ID of the transcript

        Returns:
            Transcript: Transcript object if found, None if not found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            sql = (
                "SELECT id, filename, checksum, created_at "
                "FROM transcripts "
                "WHERE id = ?"
            )
            cursor.execute(sql, (transcript_id,))
            row = cursor.fetchone()
            if row:
                created_at = datetime.fromisoformat(row[3]) if row[3] else None
                return Transcript(
                    id=row[0],
                    filename=row[1],
                    checksum=row[2],
                    created_at=created_at,
                )
            return None

    def get_transcripts(self, filename):
        """Retrieve all transcript records for a filename.

        Args:
            filename: Name of the transcript file

        Returns:
            list[Transcript]: List of Transcript objects (with integer
                              checksums), empty list if none found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            sql = (
                "SELECT id, filename, checksum, created_at "
                "FROM transcripts "
                "WHERE filename = ?"
                "ORDER BY created_at DESC"
            )
            cursor.execute(sql, (filename,))
            rows = cursor.fetchall()
            return [Transcript(
                id=row[0],
                filename=row[1],
                checksum=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            ) for row in rows]

    def delete_transcripts(self, filename):
        """Delete all transcript records with the given filename.

        Args:
            filename: Name of the transcript file

        Returns:
            int: Number of records deleted
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("DELETE FROM transcripts WHERE filename = ?",
                           (filename,))
            conn.commit()
            return cursor.rowcount

    def delete_deck_and_notes(self, deck_id):
        """Delete a deck, its notes and all associated entries in the following
        tables: transcript_deck_processing, notes, note_client_imports.

        Args:
            deck_id: ID of the deck to delete

        Returns:
            bool: True if deck was deleted, False if deck wasn't found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            # First check if deck exists
            cursor.execute("SELECT 1 FROM decks WHERE id = ?", (deck_id,))
            if not cursor.fetchone():
                return False

            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            try:
                # Delete transcript processing records
                cursor.execute(
                    "DELETE FROM transcript_deck_processing WHERE deck_id = ?",
                    (deck_id,)
                )

                # Delete note-client import associations for notes in this deck
                cursor.execute("""
                    DELETE FROM note_client_imports
                    WHERE note_id IN (
                        SELECT id FROM notes WHERE deck_id = ?
                    )
                """, (deck_id,))

                # Delete all notes in the deck
                cursor.execute("DELETE FROM notes WHERE deck_id = ?",
                               (deck_id,))

                # Finally delete the deck itself
                cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))

                conn.commit()
                logger.info(f"Successfully deleted deck {deck_id} and all "
                            f"associated data")
                return True

            except Exception as e:
                conn.rollback()
                logger.error(f"Error deleting deck {deck_id}: {str(e)}")
                raise

    def insert_deck(self, name):
        """Insert a new deck record.

        Args:
            name: Name of the deck

        Returns:
            int: ID of the inserted record
        """
        sql = "INSERT INTO decks (name) VALUES (?)"
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, (name,))
            conn.commit()
            return cursor.lastrowid

    def get_deck(self, deck_id):
        """Retrieve a deck by ID.

        Args:
            deck_id: ID of the deck

        Returns:
            Deck: Deck object if found, None if not found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT id, name, created_at FROM decks WHERE id = ?",
                (deck_id,)
            )
            row = cursor.fetchone()
            if row:
                created_at = datetime.fromisoformat(row[2]) if row[2] else None
                return Deck(
                    id=row[0],
                    name=row[1],
                    created_at=created_at,
                )
            return None

    def get_all_decks(self):
        """Retrieve all decks.

        Returns:
            list[Deck]: List of all Deck objects
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            sql = (
                "SELECT id, name, created_at FROM decks ORDER BY created_at "
                "DESC"
            )
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [Deck(
                id=row[0],
                name=row[1],
                created_at=datetime.fromisoformat(row[2]) if row[2] else None
            ) for row in rows]

    def get_or_create_deck(self, name):
        """Get an existing deck by name or create a new one.

        Args:
            name: Name of the deck

        Returns:
            Deck: The existing or newly created Deck object
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            # Try to find existing deck
            cursor.execute(
                "SELECT id, name, created_at FROM decks WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            if row:
                created_at = datetime.fromisoformat(row[2]) if row[2] else None
                return Deck(
                    id=row[0],
                    name=row[1],
                    created_at=created_at
                )

            # Create new deck if not found
            deck_id = self.insert_deck(name)
            return self.get_deck(deck_id)

    def is_file_processed(self, filename, checksum, deck_name):
        """Check if a file has been processed for a given deck.

        Args:
            filename: Name of the file
            checksum: Integer checksum of the file
            deck_name: Name of the deck

        Returns:
            bool: True if file has been processed, False otherwise
        """
        with closing(self.connect().cursor()) as cursor:
            cursor.execute("""
                SELECT 1 FROM transcripts t
                JOIN transcript_deck_processing tdp ON t.id = tdp.transcript_id
                JOIN decks d ON d.id = tdp.deck_id
                WHERE t.filename = ?
                AND t.checksum = ?
                AND d.name = ?
                LIMIT 1
            """, (filename, checksum, deck_name))
            return cursor.fetchone() is not None

    def link_transcript_to_deck(self, deck_id, transcript_id):
        """Create a link between a transcript and a deck.

        Args:
            deck_id: ID of the deck
            transcript_id: ID of the transcript

        Returns:
            int: ID of the inserted record
        """
        sql = (
            "INSERT INTO transcript_deck_processing (deck_id, transcript_id)"
            "VALUES (?, ?)"
        )
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, (deck_id, transcript_id))
            conn.commit()
            return cursor.lastrowid

    def get_deck_transcripts(self, deck_id):
        """Get all transcripts associated with a deck.

        Args:
            deck_id: ID of the deck

        Returns:
            list[Transcript]: List of Transcript objects
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            sql = """
                SELECT t.id, t.filename, t.checksum, t.created_at
                FROM transcripts t
                JOIN transcript_deck_processing tdp ON t.id = tdp.transcript_id
                WHERE tdp.deck_id = ?
                ORDER BY t.created_at DESC
            """
            cursor.execute(sql, (deck_id,))
            rows = cursor.fetchall()
            return [Transcript(
                id=row[0],
                filename=row[1],
                checksum=row[2],
                created_at=datetime.fromisoformat(row[3]) if row[3] else None
            ) for row in rows]

    def insert_note(self, deck_id, question, explanation, answer_a=None,
                    answer_b=None, answer_c=None, answer_d=None,
                    correct_answer=None, **kwargs):
        """Insert a new note into the database.

        Args:
            deck_id: ID of the deck this note belongs to
            question: The question text
            explanation: The explanation text
            answer_a: First multiple choice answer (optional)
            answer_b: Second multiple choice answer (optional)
            answer_c: Third multiple choice answer (optional)
            answer_d: Fourth multiple choice answer (optional)
            correct_answer: Correct answer (a,b,c,d) (optional)

        Returns:
            int: ID of the inserted note
        """

        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO notes (
                    deck_id, question, answer_a, answer_b, answer_c, answer_d,
                    correct_answer, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deck_id, question, answer_a, answer_b, answer_c,
                answer_d, correct_answer, explanation
            ))
            conn.commit()
            return cursor.lastrowid

    def get_note(self, note_id):
        """Get a note by ID.

        Args:
            note_id: ID of the note

        Returns:
            Note: Note object if found, None if not found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, deck_id, question, answer_a, answer_b, answer_c,
                       answer_d, correct_answer, explanation, created_at
                FROM notes WHERE id = ?
            """, (note_id,))
            row = cursor.fetchone()
            if row:
                created_at = datetime.fromisoformat(row[9]) if row[9] else None
                return Note(
                    id=row[0],
                    deck_id=row[1],
                    question=row[2],
                    answer_a=row[3],
                    answer_b=row[4],
                    answer_c=row[5],
                    answer_d=row[6],
                    correct_answer=row[7],
                    explanation=row[8],
                    created_at=created_at
                )
            return None

    def create_client_import(self, client_id):
        """Create a new client import.

        Args:
            client_id: External client identifier

        Returns:
            int: ID of the created client import
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO client_imports (client_id) VALUES (?)",
                (client_id,)
            )
            conn.commit()
            return cursor.lastrowid

    def get_client_import(self, import_id):
        """Get a client import by ID.

        Args:
            import_id: ID of the client import

        Returns:
            ClientImport: ClientImport object if found, None if not found
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, client_id, created_at
                FROM client_imports WHERE id = ?
            """, (import_id,))
            row = cursor.fetchone()
            if row:
                created_at = datetime.fromisoformat(row[2]) if row[2] else None
                return ClientImport(
                    id=row[0],
                    client_id=row[1],
                    created_at=created_at
                )
            return None

    def link_note_to_client_import(self, note_id, client_import_id):
        """Link a note to a client import.

        Args:
            note_id: ID of the note
            client_import_id: ID of the client import

        Raises:
            sqlite3.IntegrityError: If link already exists or IDs don't exist
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO note_client_imports (note_id, client_import_id)
                VALUES (?, ?)
            """, (note_id, client_import_id))
            conn.commit()

    def get_notes_by_client_import(self, client_import_id):
        """Get all notes for a client import.

        Args:
            client_import_id: ID of the client import

        Returns:
            list[Note]: List of notes
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT n.id, n.deck_id, n.question, n.answer_a, n.answer_b,
                       n.answer_c, n.answer_d, n.correct_answer, n.explanation,
                       n.created_at
                FROM notes n
                JOIN note_client_imports nci ON n.id = nci.note_id
                WHERE nci.client_import_id = ?
            """, (client_import_id,))
            return [Note(
                id=row[0],
                deck_id=row[1],
                question=row[2],
                answer_a=row[3],
                answer_b=row[4],
                answer_c=row[5],
                answer_d=row[6],
                correct_answer=row[7],
                explanation=row[8],
                created_at=datetime.fromisoformat(row[9]) if row[9] else None
            ) for row in cursor.fetchall()]

    def get_client_imports_by_note(self, note_id):
        """Get all client imports for a note.

        Args:
            note_id: ID of the note

        Returns:
            list[ClientImport]: List of client imports
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT ci.id, ci.client_id, ci.created_at
                FROM client_imports ci
                JOIN note_client_imports nci ON ci.id = nci.client_import_id
                WHERE nci.note_id = ?
            """, (note_id,))
            return [ClientImport(
                id=row[0],
                client_id=row[1],
                created_at=datetime.fromisoformat(row[2]) if row[2] else None
            ) for row in cursor.fetchall()]

    def list_tables(self):
        """List all tables in the database.

        Returns:
            list: List of table names
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            sql = "SELECT name FROM sqlite_master WHERE type='table'"
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]

    def list_decks(self):
        """List all deck names in the database.

        Returns:
            list[str]: List of deck names ordered by creation date (newest
                       first)
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT name FROM decks ORDER BY created_at DESC"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_notes_by_deck_id(self, deck_id):
        """Get all notes belonging to a specific deck.

        Args:
            deck_id: ID of the deck

        Returns:
            list[Note]: List of Note objects belonging to the deck
        """
        conn = self.connect()
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, deck_id, question, answer_a, answer_b, answer_c,
                       answer_d, correct_answer, explanation, created_at
                FROM notes
                WHERE deck_id = ?
                ORDER BY created_at DESC
            """, (deck_id,))
            return [Note(
                id=row[0],
                deck_id=row[1],
                question=row[2],
                answer_a=row[3],
                answer_b=row[4],
                answer_c=row[5],
                answer_d=row[6],
                correct_answer=row[7],
                explanation=row[8],
                created_at=datetime.fromisoformat(row[9]) if row[9] else None
            ) for row in cursor.fetchall()]
