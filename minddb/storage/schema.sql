CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    checksum INTEGER NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transcript_deck_processing (
    id INTEGER PRIMARY KEY,
    deck_id INTEGER NOT NULL,
    transcript_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(id),
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id),
    UNIQUE(deck_id, transcript_id)
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY,
    deck_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer_a TEXT,
    answer_b TEXT,
    answer_c TEXT,
    answer_d TEXT,
    correct_answer TEXT CHECK(correct_answer IN ('a', 'b', 'c', 'd')),
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(id)
);

CREATE TABLE IF NOT EXISTS client_imports (
    id INTEGER PRIMARY KEY,
    client_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS note_client_imports (
    id INTEGER PRIMARY KEY,
    note_id INTEGER NOT NULL,
    client_import_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id),
    FOREIGN KEY (client_import_id) REFERENCES client_imports(id),
    UNIQUE(note_id, client_import_id)
);
