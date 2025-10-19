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
        self._all_books_dict = {}
        self._all_books_dict_title = {} #used for faster searching by title

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
                        self._all_books_dict[book['id']] = Book(book['id'], book['title'], book['author'], 
                                                                book['genre'], book['year'], book.get('rating'))
                        
                        self._all_books_dict_title[book['title']] = Book(book['id'], book['title'], book['author'], 
                                                                book['genre'], book['year'], book.get('rating'))
                        
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
                        borrowed_books = [self._all_books_dict[book_id] for book_id in user['borrowed_books']]
                        books_in_history = [self._all_books_dict[book_id] for book_id in user['history']]

                        self.add_user(user['id'], user['name'], borrowed_books, books_in_history)
                    except Exception as e:
                        print(f"Error loading User: {e}")
            
            del self._all_books_dict
            
        except Exception as e:
            print(f"Error loading config file: {e}")

    # functions
    def add_book(self, book_id: str, title: str, author: str, genre: str, 
                 published_year: int, rating: Union[int, float] = None) -> bool:
        book = Book(book_id, title, author, genre, published_year, rating)
        self._all_books.append(book)
        #shaky code
        self._all_books_dict_title[title] = book
        self._all_books_dict[book_id] = book
        #end of shaky code
        return True
    
    def add_user(self, user_id: str, name: str, borrowed_books: list = [], history: list = []) -> bool:
        user = User(user_id, name, borrowed_books, history)
        self._all_users.append(user)
        return True
    
    def remove_book(self, book_title: str) -> bool:
        check_type(book_title, str, "book_title")

        if book_title not in self.get_book_titles():
            print(f"Warning: {book_title} not found existing books. Not removing")
            return False
        
        # removing book
        all_books = self.get_books()
        for book in all_books:
            if book.get_title() == book_title:

                self._all_books.remove(book)
                self._all_books_dict.pop(book.get_id(), None)
                self._all_books_dict_title.pop(book_title, None)
        
        # removing from user history and borrowed books
        for user in self._all_users:
            if book_title in user.get_book_titles_in_history():
                user.history.remove(book_title)
            
            if book_title in user.get_borrowed_book_titles():
                user.borrowed_books.remove(book_title)
        
        return True

    def remove_user(self, user_name: str) -> bool:
        check_type(user_name, str, "user_name")

        if user_name not in self.get_user_names():
            print(f"Warning: {user_name} not found existing users. Not removing")
            return False
        
        # removing from users
        all_users = self.get_users()
        for user in all_users:
            if user.get_name() == user_name:
                self._all_users.remove(user)
        
        return True

    def checkout_book(self, book_title: str, user_name: str) -> bool:
        check_type(book_title, str, "book_title")
        check_type(user_name, str, "user_name")

        if book_title not in self.get_book_titles():
            print(f"Warning: {book_title} not found existing books. Not checking out")
            return False
        
        if user_name not in self.get_user_names():
            print(f"Warning: {user_name} not found existing users. Not checking out")
            return False
        
        for book in self.get_books():
            if book.get_title() == book_title:
                chosen_book = book
                break

        for user in self.get_users():
            if user.get_name() == user_name:
                user.borrow_book(chosen_book)

    def checkin_book(self, book_title: str, user_name: str) -> bool:
        check_type(book_title, str, "book_title")
        check_type(user_name, str, "user_name")

        if book_title not in self.get_book_titles():
            print(f"Warning: {book_title} not found existing books. Not checking in")
            return False
        
        if user_name not in self.get_user_names():
            print(f"Warning: {user_name} not found existing users. Not checking in")
            return False
        
        for book in self.get_books():
            if book.get_title() == book_title:
                chosen_book = book
                break

        for user in self.get_users():
            if user.get_name() == user_name:
                user.return_book(chosen_book.get_title())
                return True
        
        return False

    def search_book(self, book_title: str) -> Book:
        check_type(book_title, str, "book_title")
        
        for book in self.get_books():
            if book.get_title() == book_title:
                return book
        
        print(f"Warning: {book_title} not found existing books")
        return None  

    # TODO: write faster and more efficient search
    def search_book_improved(self, book_title: str) -> list:
        check_type(book_title, str, "book_title")
        
        thebook = self._all_books_dict_title.get(book_title)
        if thebook is not None:
            return [thebook]
        
        print(f"Warning: {book_title} not found existing books")
        return []

    def recommend_books(self, num_recommendations: int = 10) -> list:
        check_type(num_recommendations, int, "num_recommendations")

        sorted_books = sorted(self.get_books(), key = lambda x: (x.get_rating() is not None, x.get_rating()), reverse=True)

        return sorted_books[:num_recommendations]
    
    def recommend_books_improved(self, user: User, num_recommendations: int = 10) -> list:
        check_type(user, User, "user")
        check_type(num_recommendations, int, "num_recommendations")

        # check whether user is in the system
        if user not in self.get_users():
            print(f"Non-existent user: '{user.get_name()}' is not in the system")
            return []
        
        # Get user's borrowed books (current + history)
        user_books_history = user.get_history()
        
        if not user_books_history:
            # print(f"Warning: User '{user.get_name()}' has no book history")
            # Fallback to general top-rated books
            return self.recommend_books(num_recommendations)
        
        # Extract genres from user's books
        genre_counts = {}
        for book in user_books_history:
            book_genres = [g.strip() for g in book.get_genre().split(',') if g.strip()]
            for genre in book_genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        if not genre_counts:
            return self.recommend_books(num_recommendations)
        
        # Score all books not in user's history
        total_user_books = len(user_books_history)

        recommendations = []
        for book in self.get_books():
            if book not in user_books_history:
                book_genres = [g.strip() for g in book.get_genre().split(',') if g.strip()]
                
                # Calculate genre similarity score
                genre_score = 0
                
                for genre in book_genres:
                    if genre in genre_counts:
                        # Weight by how often user borrowed this genre
                        genre_score += genre_counts[genre] / total_user_books
                
                # Normalize by number of genres in the book
                if book_genres:
                    genre_score /= len(book_genres)
                
                recommendations.append((book, genre_score))
        
        # Sort by genre score (primary) and rating (secondary)
        recommendations.sort(key=lambda x: (x[1], x[0].get_rating() or 0), reverse=True)
        
        # Return top recommendations
        return [book for book, _ in recommendations[:num_recommendations]]

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