# MindDB
MindDB automates the creation of Anki flashcards from course transcripts,
making learning more efficient.

# Setup

## Install packages
I'm using [conda](https://x.com/i/grok/share/EjEzB1YyNTLWGncJ8loCl4s8V)
to manage the environment.

```bash
cd <path-to-your-project>
conda create -n minddb python=3.12
conda activate minddb
pip install -r requirements.txt
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
You should now see the 'Create Multiple Choice Note Type' entry in the Tools
menu. Click it to create the note and card types.


