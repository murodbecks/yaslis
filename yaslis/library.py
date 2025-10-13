import os
import jsonlines
import re, difflib
from typing import Union
from yaslis.book import Book
from yaslis.user import User
from yaslis.utils import check_type, format_list

class Library:

    def __init__(self, books_config_file_path: str = None, users_config_file_path: str = None):
        self._all_books = []
        self._all_users = []

        if books_config_file_path:
            self._load_books(books_config_file_path)
        
        if users_config_file_path:
            self._load_users(users_config_file_path)

    # getters
    def get_books(self) -> list:
        return self._all_books.copy()
    
    def get_users(self) -> list:
        return self._all_users.copy()
    
    def get_book_ids(self) -> list:
        return [book.get_id() for book in self.get_books()]
    
    def get_user_ids(self) -> list:
        return [user.get_id() for user in self.get_users()]

    def get_book_titles(self) -> list:
        return [book.get_title() for book in self.get_books()]

    def get_user_names(self) -> list:
        return [user.get_name() for user in self.get_users()]

    # loading scripts
    def _load_books(self, books_config_file_path: str) -> None:
        check_type(books_config_file_path, str, "books_config_file_path")

        if not os.path.exists(books_config_file_path):
            print(f"Warning: '{books_config_file_path}' file does not exist. Initializing from scratch.")
            return 
        
        try:
            with jsonlines.open(books_config_file_path, 'r') as books_file:
                for book in books_file:
                    if not all([key_name in book.keys() for key_name in ['id', 'title', 'author', 'genre', 'year']]):
                        print(f"Warning: Missing Book variables: {book}")
                        continue

                    try:
                        self.add_book(book['id'], book['title'], book['author'], 
                                      book['genre'], book['year'], book.get('rating'))
                    except Exception as e:
                        print(f"Error loading Book: {e}")
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    def _load_users(self, users_config_file_path: str) -> None:
        check_type(users_config_file_path, str, "users_config_file_path")

        if not os.path.exists(users_config_file_path):
            print(f"Warning: '{users_config_file_path}' file does not exist. Initializing from scratch.")
            return 
        
        try:
            with jsonlines.open(users_config_file_path, 'r') as users_file:
                for user in users_file:
                    if not all([key_name in user.keys() for key_name in ['id', 'name', 'borrowed_books', 'history']]):
                        print(f"Warning: Missing User variable: {user}")
                        continue

                    try:
                        self.add_user(user['id'], user['name'], user['borrowed_books'], user['history'])
                    except Exception as e:
                        print(f"Error loading User: {e}")

        except Exception as e:
            print(f"Error loading config file: {e}")

    # functions
    def add_book(self, book_id: str, title: str, author: str, genre: str, 
                 published_year: int, rating: Union[int, float] = None) -> bool:
        book = Book(book_id, title, author, genre, published_year, rating)
        self._all_books.append(book)
        return True
    
    def add_user(self, user_id: str, name: str, borrowed_books: list = [], history: list = []) -> bool:
        user = User(user_id, name, borrowed_books, history)
        self._all_users.append(user)
        return True
    
    def remove_book(self, book_id: str) -> bool:
        check_type(book_id, str, "book_id")

        if book_id not in self.get_book_ids():
            print(f"Warning: {book_id} not found existing books. Not removing")
            return False
        
        # removing book
        all_books = self.get_books()
        for book in all_books:
            if book.get_id() == book_id:
                self._all_books.remove(book)
        
        # removing from user history and borrowed books
        for user in self._all_users:
            if book_id in user.get_book_ids_in_history():
                user.history.remove(book_id)
            
            if book_id in user.get_borrowed_book_ids():
                user.borrowed_books.remove(book_id)
        
        return True

    def remove_user(self, user_id: str) -> bool:
        check_type(user_id, str, "user_id")

        if user_id not in self.get_user_ids():
            print(f"Warning: {user_id} not found existing users. Not removing")
            return False
        
        # removing from users
        all_users = self.get_users()
        for user in all_users:
            if user.get_id() == user_id:
                self._all_users.remove(user)
        
        return True

    def checkout_book(self, book_id: str, user_id: str) -> bool:
        check_type(book_id, str, "book_id")
        check_type(user_id, str, "user_id")

        if book_id not in self.get_book_ids():
            print(f"Warning: {book_id} not found existing books. Not checking out")
            return False
        
        if user_id not in self.get_user_ids():
            print(f"Warning: {user_id} not found existing users. Not checking out")
            return False
        
        for book in self.get_books():
            if book.get_id() == book_id:
                chosen_book = book
                break

        for user in self.get_users():
            if user.get_id() == user_id:
                user.borrow_book(chosen_book)

    def checkin_book(self, book_id: str, user_id: str) -> bool:
        check_type(book_id, str, "book_id")
        check_type(user_id, str, "user_id")

        if book_id not in self.get_book_ids():
            print(f"Warning: {book_id} not found existing books. Not checking in")
            return False
        
        if user_id not in self.get_user_ids():
            print(f"Warning: {user_id} not found existing users. Not checking in")
            return False
        
        for book in self.get_books():
            if book.get_id() == book_id:
                chosen_book = book
                break

        for user in self.get_users():
            if user.get_id() == user_id:
                user.return_book(chosen_book)

    def search_book(self, book_title: str) -> Book:
        check_type(book_title, str, "book_title")
        
        for book in self.get_books():
            if book.get_title() == book_title:
                return book
        
        print(f"Warning: {book_title} not found existing books")
        return None  

    def search_book_improved(self, title: str, fuzzy: bool = True) -> list:
        if not title:
            return []
        query = re.sub(r"\s+", " ", title).strip().lower()

        # Exact match
        exact_matches = [b for b in self._all_books if b.get_title().strip().lower() == query]
        if exact_matches:
            return exact_matches

        # Fuzzy fallback
        if fuzzy:
            all_titles = [b.get_title() for b in self._all_books]
            close_titles = difflib.get_close_matches(title, all_titles, n=10, cutoff=0.6)
            return [b for b in self._all_books if b.get_title() in close_titles]

        # no matches
        return []

    def recommend_books(self, num_recommendations: int = 10) -> list:
        check_type(num_recommendations, int, "num_recommendations")

        sorted_books = sorted(self.get_books(), key = lambda x: (x.get_rating() is not None, x.get_rating()), reverse=True)

        return sorted_books[:num_recommendations]
    
    def recommend_books_improved(self, num_recommendations: int = 10) -> list:
        check_type(num_recommendations, int, "num_recommendations")

        last_book = self.get_books()[-1]
        last_book_genres = last_book.get_genre().split(', ')

        recommendations = []
        
        for book in self.get_books():
            if book != last_book:
                book_genres = book.get_genre().split(', ')
                genre_overlap_ratio = len(set(last_book_genres)&set(book_genres))/len(last_book_genres)
                recommendations.append((book, genre_overlap_ratio))
        
        sorted_recommendations = sorted(recommendations, key = lambda x: (x[1], x[0].get_rating() is not None, x[0].get_rating()), reverse=True)

        return sorted_recommendations[:num_recommendations]

    # dunder methods
    def __repr__(self) -> str:
        book_titles_str = format_list(self.get_book_titles(), 3)
        user_names_str = format_list(self.get_user_names(), 3)

        return (f"Library(books='{book_titles_str}', users='{user_names_str}'")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Library):
            return False
        
        return (self.get_book_titles(), self.get_user_names()) == \
               (other.get_book_titles(), other.get_user_names())

if __name__ == "__main__":
    library = Library('configs/sample_books.jsonl', 'configs/sample_users.jsonl')
    print(f"Num loaded books: {len(library.get_books())}")
    print(f"Num loaded users: {len(library.get_users())}")

    print(library)
