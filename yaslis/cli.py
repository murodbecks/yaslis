import sys
import argparse
import subprocess
import unittest
import os
from pathlib import Path
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


def run_tests_command(args):
    """Handle run_tests command"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"Error: Tests directory '{tests_dir}' not found")
        sys.exit(1)
    
    # Change to project root for proper imports
    os.chdir(project_root)
    
    print("Running YASLIS Library System Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(tests_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with appropriate verbosity
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests failed!")
        print(f"Ran {result.testsRun} tests: "
              f"{len(result.failures)} failures, {len(result.errors)} errors")
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
    
    # run_tests command
    tests_parser = subparsers.add_parser(
        'run_tests',
        help='Run all unit tests'
    )
    tests_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Run tests with verbose output'
    )
    tests_parser.set_defaults(func=run_tests_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()