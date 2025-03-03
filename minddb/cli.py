import logging
import argparse
import os.path
import textwrap


def check_catalog_exists(catalog_path, catalog_name):
    if not os.path.exists(catalog_path):
        print(f'Catalog path {catalog_path} does not exist')
        exit(1)

    if not os.path.exists(os.path.join(catalog_path, f'{catalog_name}.db')):
        print(f'Catalog {catalog_name} does not exist in {catalog_path}')
        exit(1)


def wrap(text, initial_indent='', subsequent_indent='  '):
    """Wrap text to 80 characters and print it.

    Args:
        text: Text to wrap and print
        initial_indent: String to use for first line indentation (default: '')
        subsequent_indent: String to use for subsequent lines (default: '  ')
    """
    print(textwrap.fill(text, width=80, initial_indent=initial_indent,
                        subsequent_indent=subsequent_indent))


def get_catalog_props(args, check=False):
    """Get catalog properties from command line arguments.

    Determines the catalog path and name based on provided arguments.
    If no catalog path is specified, uses current directory.
    If no catalog name is specified, converts deck name to CamelCase.

    Args:
        args: Namespace object from argparse containing:
            - catalog_path: Optional path to catalog directory
            - catalog: Optional catalog name
            - deck: Name of the deck

    Returns:
        tuple: (catalog_path, catalog_name) where:
            - catalog_path: Directory path for the catalog (str)
            - catalog_name: Name of the catalog in CamelCase (str)
    """
    catalog_path = args.catalog_path if args.catalog_path else '.'

    catalog_name = args.catalog
    if not catalog_name and hasattr(args, 'deck'):
        deck_name = args.deck
        for char in ['_', '-', ':']:
            deck_name = deck_name.replace(char, ' ')
        catalog_name = ''.join(
            (word[0].upper() + word[1:]) for word in deck_name.split()
        )

    if not catalog_name:
        raise ValueError('Please provide a name for the catalog')

    if check:
        check_catalog_exists(catalog_path, catalog_name)

    return catalog_path, catalog_name


def add_catalog_args(parser):
    parser.add_argument('--catalog_path', '-p', default='.',
                        help='Path to the catalog. Default: current directory')
    help_text = ('Name of the catalog. Default: CamelCase(deck name) if deck '
                 'is provided')
    parser.add_argument('--catalog', '-c', help=help_text)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')



async def async_main():
    description = ('MindDB automates the creation of Anki flashcards from '
                   'course transcripts.')

    parser = argparse.ArgumentParser(description=description)

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command',
                                       help='Available commands')

    # Create parser for the "create" command
    create_parser = subparsers.add_parser('create', help='Create cards')
    create_parser.add_argument('--library', '-l',
                               help='Path to the library of transcripts')
    create_parser.add_argument('--deck', '-d', help='Name of the deck')
    add_catalog_args(create_parser)

    # Create parser for the "notes" command
    notes_parser = subparsers.add_parser('notes', help='List notes')
    notes_parser.add_argument('--deck', '-d', help='Name of the deck')
    add_catalog_args(notes_parser)

    # Create parser for the "decks" command
    decks_parser = subparsers.add_parser('decks', help='List decks')
    add_catalog_args(decks_parser)

    # Create parser for the "delete_deck" command
    delete_parser = subparsers.add_parser('delete_deck',
                                          help='Delete a deck and its notes')
    delete_parser.add_argument('--deck', '-d', required=True,
                               help='Name of the deck to delete')
    add_catalog_args(delete_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        exit(1)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.command == 'create':
        if args.library is None:
            print('Please provide a library of transcripts\n')
            create_parser.print_help()
            exit(1)
        if args.deck is None:
            print('Please provide a name for the deck\n')
            notes_parser.print_help()
            exit(1)

        import minddb.mindnote
        import minddb.storage

        minddb.storage.setup(*get_catalog_props(args, check=False))
        processor = minddb.mindnote.Processor(args.library)
        await processor.create(args.deck)

        minddb.storage.close_catalog()

    if args.command == 'delete_deck':
        import minddb.storage

        minddb.storage.setup(*get_catalog_props(args, check=True))

        catalog = minddb.storage.get_catalog()

        if args.deck not in catalog.list_decks():
            print(f'Deck "{args.deck}" not found\n')
            exit(1)

        # Ask for confirmation
        response = input(f'Are you sure you want to delete deck "{args.deck}" '
                         f'and all its notes? [y/N] ')
        if response.lower() != 'y':
            print('Operation cancelled')
            exit(0)

        deck = catalog.get_or_create_deck(args.deck)
        catalog.delete_deck_and_notes(deck.id)
        print(f'Deleted deck "{args.deck}" and all its notes')

        minddb.storage.close_catalog()

    if args.command == 'notes':
        if args.deck is None:
            print('Please provide a name for the deck\n')
            notes_parser.print_help()
            exit(1)
        else:
            deck_name = args.deck

        import minddb.storage

        minddb.storage.setup(*get_catalog_props(args, check=True))
        catalog = minddb.storage.get_catalog()

        if deck_name not in catalog.list_decks():
            print(f'Deck "{deck_name}" not found\n')
            exit(1)

        deck = catalog.get_or_create_deck(deck_name)
        notes = catalog.get_notes_by_deck_id(deck.id)
        if not notes:
            print(f'No notes found for deck "{deck_name}"\n')
            exit(1)
        else:
            print(f'Found {len(notes)} notes for deck "{deck_name}"\n')

        for note in notes:
            wrap(f'Question: {note.question}')
            wrap(f'  (a) {note.answer_a}')
            wrap(f'  (b) {note.answer_b}')
            wrap(f'  (c) {note.answer_c}')
            wrap(f'  (d) {note.answer_d}')
            wrap(f'Correct answer: ({note.correct_answer})')
            wrap('Explanation:')
            wrap(note.explanation, initial_indent='  ', subsequent_indent='  ')
            print('-' * 80)
        minddb.storage.close_catalog()

    if args.command == 'decks':
        if args.catalog is None:
            print('Please provide a name for the catalog\n')
            decks_parser.print_help()
            exit(1)

        import minddb.storage

        catalog_path, catalog_name = get_catalog_props(args, check=True)
        minddb.storage.setup(catalog_path, catalog_name)

        decks = minddb.storage.get_catalog().list_decks()

        print(f'Catalog: {catalog_name}')
        print('-' * 80)
        print(f'Found {len(decks)} deck(s):')
        for deck in decks:
            print(f'  {deck}')

        minddb.storage.close_catalog()


def main():
    import asyncio
    asyncio.run(async_main())


if __name__ == '__main__':
    """
    Main entry point for the script.
    Usage:
    >>> minddb --help
    """
    import asyncio
    asyncio.run(main())
