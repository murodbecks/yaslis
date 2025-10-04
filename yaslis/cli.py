import sys
import argparse
import subprocess
from typing import Optional

from yaslis.utils import download_and_process_data


def prepare_data_command(args):
    """Handle prepare_data command"""
    sample_size = args.sample_size
    num_users = args.num_users
    
    if sample_size and sample_size <= 0:
        print("Error: Sample size must be a positive integer")
        sys.exit(1)
    
    try:
        download_and_process_data(sample_size, num_users)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading dataset: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing dataset: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='yaslis',
        description='Smart Library System CLI'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # prepare_data command
    prepare_parser = subparsers.add_parser(
        'prepare_data',
        help='Download and process books dataset'
    )
    prepare_parser.add_argument(
        'sample_size',
        type=int,
        nargs='?',
        help='Number of books to sample (optional, uses all books if not specified)'
    )
    prepare_parser.add_argument(
        'num_users',
        type=int,
        nargs='?',
        const=None,
        help='Number of users to generate (optional, generates for sample_size//10)'
    )
    prepare_parser.set_defaults(func=prepare_data_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()