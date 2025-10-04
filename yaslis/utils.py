import re
import random
import subprocess
import pandas as pd
from typing import Union
from pathlib import Path

class ValueValidationError(Exception):
    """Custom exception for value validation errors"""
    pass

def check_type(variable, expected_type, var_name=None):
    """Hard validation - raises exception"""
    if not isinstance(variable, expected_type):
        name = var_name or "variable"
        type_name = expected_type.__name__
        raise ValueValidationError(f"`{name}` must be {type_name}, got {type(variable).__name__}.")
    return True

def format_list(input_list : list, max_items: int=5) -> str:
    check_type(input_list, list, "input_list")
    check_type(max_items, int, "max_items")

    if len(input_list) <= max_items:
        return '[' + ", ".join(input_list) + ']'
    else:
        return '[' + ", ".join(input_list[:max_items]) + f"... (+{len(input_list) - max_items} more)]"

def prepare_id(book_id: Union[int, str]) -> str:
    if not isinstance(book_id, Union[int, str]):
        return 'book_'
    return f'book_{book_id}'

def clean_genres(genre_and_votes: str) -> str:
    """Remove vote counts from genre string"""
    if not isinstance(genre_and_votes, str):
        return ''
    
    # Remove numbers and extra spaces, keep commas
    cleaned = re.sub(r'\s+\d+', '', genre_and_votes)
    return cleaned.strip()


def extract_year(date_published: str) -> int:
    """Extract year from various date formats"""
    if not isinstance(date_published, str):
        return 0
    
    # Find 4-digit year (1000-2999 range)
    match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', str(date_published))
    
    if match:
        return int(match.group(1))
    else:
        return 0

def generate_books_data(books_df: pd.DataFrame, sample_size: int = None) -> pd.DataFrame:
    # Sample if requested
    if sample_size:
        if sample_size > len(books_df):
            print(f"Warning: Requested {sample_size} books, but dataset only has {len(books_df)} books")
            sample_size = len(books_df)
        books_df = books_df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} books from dataset")
    
    # Process data
    books_df.rename(columns={'average_rating': 'rating'}, inplace=True)
    books_df['id'] = books_df['id'].apply(prepare_id)
    books_df['genre'] = books_df['genre_and_votes'].apply(clean_genres)
    books_df['year'] = books_df['date_published'].apply(extract_year)
    
    # Select final columns
    return books_df[['id', 'title', 'author', 'genre', 'year', 'rating']]

def generate_users_data(books_df: pd.DataFrame, num_users: int = None) -> pd.DataFrame:
    # Extract all unique author names
    all_authors = []
    for authors in books_df['author']:
        if isinstance(authors, str):
            authors_list = [author.strip() for author in authors.split(',') if len(author.strip()) > 1]
            all_authors.extend(authors_list)
    
    all_authors = list(set(all_authors))
    
    # Determine number of users
    if num_users is None:
        num_users = min(len(books_df) // 10, len(all_authors))
    else:
        num_users = min(num_users, len(all_authors))
    
    print(f"Generating {num_users} users data.")
    
    selected_names = random.sample(all_authors, num_users)
    
    user_info = []
    
    # Get rows that have recommended_books data
    valid_rows = books_df[books_df['recommended_books'].notna() & 
                         (books_df['recommended_books'] != '')].index.tolist()
    
    if not valid_rows:
        print("Warning: No books with recommended_books data found. Using empty histories.")
    
    for i, name in enumerate(selected_names):
        user_id = f"user_{10000+i}"

        row_info = {'id': user_id, 'name': name, 'borrowed_books': [], 'history': []}
        
        # Pick a random book with recommended books data
        if valid_rows:
            random_idx = random.choice(valid_rows)
            recommended_books_str = books_df.loc[random_idx, 'recommended_books']
            
            if isinstance(recommended_books_str, str) and recommended_books_str.strip():
                recommended_books = [book.strip() for book in recommended_books_str.split(', ') if book.strip()]
                
                len_history = random.randint(1, len(recommended_books))
                history = random.sample(recommended_books, len_history)
                row_info['history'] = [prepare_id(book_id) for book_id in history]

                if history:
                    len_borrowed = random.randint(0, len(history))
                    borrowed_books = random.sample(history, len_borrowed) if len_borrowed > 0 else []
                else:
                    borrowed_books = []
                
                row_info['borrowed_books'] = [prepare_id(book_id) for book_id in borrowed_books]

        user_info.append(row_info)
    
    df_users = pd.DataFrame(user_info)
    print(f"✅ Generated {len(df_users)} users")
    return df_users

def download_and_process_data(sample_size: int, num_users: int = None) -> None:
    """
    Download and process Goodreads books dataset
    
    Args:
        sample_size: If provided, sample only this many books
    """
    configs_dir = Path("configs")
    configs_dir.mkdir(exist_ok=True)
    
    # Download dataset
    print("Downloading Goodreads books dataset...")
    zip_path = configs_dir / "goodreads-books.zip"
    csv_path = configs_dir / "goodreads_books.csv"
    books_output_path = configs_dir / "books.jsonl"
    users_output_path = configs_dir / "users.jsonl"
    
    try:
        # Download
        subprocess.run([
            "curl", "-L", "-o", str(zip_path),
            "https://www.kaggle.com/api/v1/datasets/download/austinreese/goodreads-books"
        ], check=True)
        
        # Unzip
        subprocess.run(["unzip", "-d", str(configs_dir), str(zip_path)], check=True)
        
        print("Processing dataset...")
        
        # Load and process
        df = pd.read_csv(csv_path)
        
        # Generating book and user df
        book_df = generate_books_data(df, sample_size)
        user_df = generate_users_data(df, num_users)
        
        # Save processed data
        book_df.to_json(books_output_path, orient="records", lines=True)
        user_df.to_json(users_output_path, orient="records", lines=True)
        
        print(f"Successfully processed {len(book_df)} books and {len(user_df)} users.")
        print(f"Data saved to: {books_output_path} and {users_output_path}")
        
    finally:
        # Cleanup temporary files
        if zip_path.exists():
            zip_path.unlink()
        if csv_path.exists():
            csv_path.unlink()
        print("Cleaned up temporary files")