import sys
import argparse
import subprocess
import unittest
import os
from pathlib import Path
from typing import Optional

from yaslis.utils import download_and_process_data
from yaslis.library import Library
from yaslis.benchmark import LibraryBenchmark


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


def benchmark_command(args):
    """Handle benchmark command"""
    # Determine which files to use
    books_file = args.books_file
    users_file = args.users_file
    
    # Default file resolution
    if not books_file:
        main_books = Path("configs/books.jsonl")
        sample_books = Path("configs/sample_books.jsonl")
        
        if main_books.exists():
            books_file = str(main_books)
            print(f"Using main books file: {books_file}")
        elif sample_books.exists():
            books_file = str(sample_books)
            print(f"Using sample books file: {books_file}")
        else:
            print("Error: No books file found. Please run 'yaslis prepare_data' first or specify --books-file")
            sys.exit(1)
    
    if not users_file:
        main_users = Path("configs/users.jsonl")
        sample_users = Path("configs/sample_users.jsonl")
        
        if main_users.exists():
            users_file = str(main_users)
            print(f"Using main users file: {users_file}")
        elif sample_users.exists():
            users_file = str(sample_users)
            print(f"Using sample users file: {users_file}")
        else:
            print("Warning: No users file found. Continuing without users data.")
            users_file = None
    
    # Validate files exist
    if not Path(books_file).exists():
        print(f"Error: Books file '{books_file}' does not exist")
        sys.exit(1)
    
    if users_file and not Path(users_file).exists():
        print(f"Error: Users file '{users_file}' does not exist")
        sys.exit(1)
    
    try:
        # Load library
        library = Library(books_file, users_file)
        print(f"Loaded {len(library.get_books())} books and {len(library.get_users())} users")
        
        if len(library.get_books()) == 0:
            print("Error: No books loaded from the specified file")
            sys.exit(1)
        
        # Create benchmark
        output_dir = args.output_dir or "benchmarks"
        benchmark = LibraryBenchmark(library, output_dir)
        
        # Run benchmark
        results = benchmark.run_full_benchmark(num_experiments=args.experiments)
        
        # Save results
        output_file = None
        if args.output_file:
            output_file = args.output_file
        
        saved_path = benchmark.save_results(results, output_file)
        
        # Display summary
        benchmark.print_summary(results)
        
        print(f"\n✅ Benchmark completed successfully!")
        print(f"Results saved to: {saved_path}")
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
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
    
    # benchmark command
    benchmark_parser = subparsers.add_parser(
        'benchmark',
        help='Run performance benchmarks on search and recommendation algorithms'
    )
    benchmark_parser.add_argument(
        '--books-file',
        type=str,
        help='Path to books JSONL file (default: configs/books.jsonl or configs/sample_books.jsonl)'
    )
    benchmark_parser.add_argument(
        '--users-file',
        type=str,
        help='Path to users JSONL file (default: configs/users.jsonl or configs/sample_users.jsonl)'
    )
    benchmark_parser.add_argument(
        '-e', '--experiments',
        type=int,
        default=100,
        help='Number of experiments per test size (default: 100)'
    )
    benchmark_parser.add_argument(
        '-o', '--output-dir',
        type=str,
        help='Output directory for benchmark results (default: benchmarks/)'
    )
    benchmark_parser.add_argument(
        '--output-file',
        type=str,
        help='Specific output filename for results (default: auto-generated)'
    )
    benchmark_parser.set_defaults(func=benchmark_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()