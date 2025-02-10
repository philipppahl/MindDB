# MindDB Anki Add-ons

This directory contains Anki add-ons for MindDB integration with Anki.

## Import Notes Add-on

The Import Notes add-on allows you to import notes from MindDB directly into Anki.

### Installation

1. Locate your Anki add-ons folder:
   - Windows: `%APPDATA%\Anki2\addons21\`
   - Linux: `~/.local/share/Anki2/addons21/`
   - Mac: `~/Library/Application Support/Anki2/addons21/`

2. Copy the `import_notes` directory into your Anki add-ons folder.

3. Restart Anki.

### Usage

1. In Anki, go to Tools -> 'MindDB: Import Notes'

2. Select your MindDB library file

3. Import Notes
   - Imports unprocessed notes into the corresponding Anki deck
   - Creates note and card types if they don't exist (after asking)
   - Creates decks if they don't exist (after asking)


### Requirements

- Recent Anki version (I'm using 24.11)
- MindDB library file

### Troubleshooting

If you encounter any issues:
1. Check the Anki error console (Help -> Debug Console)
2. Ask the AI

### Support

For bug reports or feature requests, please open an issue in the MindDB repository.

