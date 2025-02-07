import argparse


def main():
    description = ('MindDB automates the creation of Anki flashcards from '
                   'course transcripts.')
    parser = argparse.ArgumentParser(description=description)

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command',
                                       help='Available commands')

    # Create parser for the "create" command
    create_parser = subparsers.add_parser('create', help='Create cards')
    create_parser.add_argument('--library', '-l', help='Library path')
    create_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')

    # Create parser for the "list" command
    list_parser = subparsers.add_parser('list', help='List cards')
    list_parser.add_argument('--verbose', '-v', action='store_true',
                             help='Verbose output')

    args = parser.parse_args()
    print(args)

    # result = your_function(args.input, args.output, args.verbose)


if __name__ == '__main__':
    # Add an example how the command is called
    # 'Usage: minddb [command] [options]')

    main()
