# MindDB
MindDB automates the creation of Anki flashcards from course transcripts,
making learning more efficient.

https://github.com/user-attachments/assets/f1369f9e-8293-4cb7-b8cd-108b8daf66ac

# Setup

## Install packages
I'm using [conda](https://x.com/i/grok/share/EjEzB1YyNTLWGncJ8loCl4s8V)
to manage the environment.

```bash
conda create -n minddb python=3.12
conda activate minddb  # Call each time you open a new shell
git clone git@github.com:philipppahl/MindDB.git
cd MindDB
```

## Installation

Basic installation:
```bash
pip install .
```

For development:
```bash
pip install ".[dev]"
```

## Setup Claude
This version uses Claude, which requires an API key.
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Setup Anki
### Add note and card types
[Intro](https://x.com/i/grok/share/Ai2VhXmGmuCqVHOtuhRxxd05f) to Anki, notes
and cards.


```bash
# Standard Anki locations:
# Linux: ~/.local/share/Anki2
# Windows: %APPDATA%/Anki2
# macOS: ~/Library/Application Support/Anki2

cp -r <path_to_your_project>/add-ons/* <path-to-anki>/addons21
```

After you've copied the files over, restart Anki.
You should now see the 'MindDB: Import Notes' entry in the Tools
menu.

For detailed information about the Anki add-ons, including installation, usage,
features, and troubleshooting, please see the
[add-ons/README.md](add-ons/README.md).

# Getting Started

Let's create and manage some flashcards:

```bash
# Create flashcards from your course materials
minddb create \
  --library ./course-materials \
  --deck "Python Basics" \
  --catalog_path ./catalog \
  --catalog python_course

# List all decks in your catalog
minddb decks \
  --catalog_path ./catalog \
  --catalog python_course

# View the flashcards in a deck
minddb notes \
  --deck "Python Basics" \
  --catalog_path ./catalog \
  --catalog python_course

# Delete a deck (will prompt for confirmation)
minddb delete_deck \
  --deck "Python Basics" \
  --catalog_path ./catalog \
  --catalog python_course
```

# Command Line Reference

Creates flashcards from course materials
```bash
usage: minddb [-h] {create,notes,decks,delete_deck} ...

MindDB automates the creation of Anki flashcards from course transcripts.

positional arguments:
  {create,notes,decks,delete_deck}
                        Available commands
    create              Create cards
    notes               List notes
    decks               List decks
    delete_deck         Delete a deck and its notes

options:
  -h, --help            show this help message and exit
```
