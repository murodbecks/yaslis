import unittest
import tempfile
import os
import jsonlines
from yaslis.library import Library
from yaslis.book import Book
from yaslis.user import User
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestLibrary(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test books and users
        self.book1 = Book("001", "Python Guide", "Author1", "Tech", 2020, 4.0)
        self.book2 = Book("002", "AI Basics", "Author2", "Tech", 2021, 4.5)
        self.book3 = Book("003", "Math Fun", "Author3", "Math", 2019, 3.8)
        
        self.user1 = User("user_001", "Alice", [], [])
        self.user2 = User("user_002", "Bob", [], [])
        
        # Create empty library
        self.library = Library()
        self.library._all_books = [self.book1, self.book2, self.book3]
        self.library._all_users = [self.user1, self.user2]
    
    def create_temp_config_files(self):
        """Create temporary config files for testing."""
        # Create temporary books file
        books_data = [
            {"id": "book_001", "title": "Test Book 1", "author": "Author1", 
             "genre": "Fiction", "year": 2020, "rating": 4.0},
            {"id": "book_002", "title": "Test Book 2", "author": "Author2", 
             "genre": "Science", "year": 2021, "rating": 4.5}
        ]
        
        users_data = [
            {"id": "user_001", "name": "John Doe", "borrowed_books": [], "history": []},
            {"id": "user_002", "name": "Jane Smith", "borrowed_books": [], "history": []}
        ]
        
        books_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        users_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        
        with jsonlines.open(books_file.name, 'w') as writer:
            writer.write_all(books_data)
        
        with jsonlines.open(users_file.name, 'w') as writer:
            writer.write_all(users_data)
        
        return books_file.name, users_file.name
    
    def tearDown(self):
        """Clean up temporary files."""
        for filename in getattr(self, 'temp_files', []):
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_library_creation_empty(self):
        """Test creating empty library."""
        lib = Library()
        self.assertEqual(len(lib.get_books()), 0)
        self.assertEqual(len(lib.get_users()), 0)
    
    def test_library_creation_with_config_files(self):
        """Test creating library with config files."""
        books_file, users_file = self.create_temp_config_files()
        self.temp_files = [books_file, users_file]
        
        lib = Library(books_file, users_file)
        
        self.assertEqual(len(lib.get_books()), 2)
        self.assertEqual(len(lib.get_users()), 2)
        self.assertIn("Test Book 1", lib.get_book_titles())
        self.assertIn("John Doe", lib.get_user_names())
    
    def test_library_creation_nonexistent_files(self):
        """Test creating library with non-existent files (should not crash)."""
        lib = Library("nonexistent_books.jsonl", "nonexistent_users.jsonl")
        self.assertEqual(len(lib.get_books()), 0)
        self.assertEqual(len(lib.get_users()), 0)
    
    def test_getters(self):
        """Test all getter methods."""
        self.assertEqual(len(self.library.get_books()), 3)
        self.assertEqual(len(self.library.get_users()), 2)
        
        book_titles = self.library.get_book_titles()
        self.assertIn("Python Guide", book_titles)
        self.assertIn("AI Basics", book_titles)
        
        user_names = self.library.get_user_names()
        self.assertIn("Alice", user_names)
        self.assertIn("Bob", user_names)
    
    def test_add_book(self):
        """Test adding books to library."""
        initial_count = len(self.library.get_books())
        
        result = self.library.add_book("004", "New Book", "New Author", "Fiction", 2022, 4.2)
        self.assertTrue(result)
        self.assertEqual(len(self.library.get_books()), initial_count + 1)
        self.assertIn("New Book", self.library.get_book_titles())
    
    def test_add_user(self):
        """Test adding users to library."""
        initial_count = len(self.library.get_users())
        
        result = self.library.add_user("user_003", "Charlie", [], [])
        self.assertTrue(result)
        self.assertEqual(len(self.library.get_users()), initial_count + 1)
        self.assertIn("Charlie", self.library.get_user_names())
    
    def test_remove_book(self):
        """Test removing books from library."""
        # Remove existing book
        result = self.library.remove_book("Python Guide")
        self.assertTrue(result)
        self.assertNotIn("Python Guide", self.library.get_book_titles())
        
        # Try to remove non-existent book
        result = self.library.remove_book("Non-existent Book")
        self.assertFalse(result)
    
    def test_remove_user(self):
        """Test removing users from library."""
        # Remove existing user
        result = self.library.remove_user("Alice")
        self.assertTrue(result)
        self.assertNotIn("Alice", self.library.get_user_names())
        
        # Try to remove non-existent user
        result = self.library.remove_user("Non-existent User")
        self.assertFalse(result)
    
    def test_checkout_checkin_book(self):
        """Test book checkout and checkin functionality."""
        # Valid checkout
        self.library.checkout_book("Python Guide", "Alice")
        # Note: This test assumes the checkout method updates user's borrowed books
        
        # Valid checkin
        self.library.checkin_book("Python Guide", "Alice")
        
        # Invalid checkout (non-existent book)
        result = self.library.checkout_book("Non-existent", "Alice")
        self.assertFalse(result)
        
        # Invalid checkout (non-existent user)
        result = self.library.checkout_book("Python Guide", "Non-existent")
        self.assertFalse(result)
    
    def test_search_book_basic(self):
        """Test basic book search."""
        # Find existing book
        book = self.library.search_book("Python Guide")
        self.assertIsNotNone(book)
        self.assertEqual(book.get_title(), "Python Guide")
        
        # Search for non-existent book
        book = self.library.search_book("Non-existent")
        self.assertIsNone(book)
    
    def test_search_book_improved(self):
        """Test improved book search."""
        # Exact match
        results = self.library.search_book_improved("Python Guide")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_title(), "Python Guide")
        
        # Empty search
        results = self.library.search_book_improved("")
        self.assertEqual(len(results), 0)
    
    def test_recommend_books_basic(self):
        """Test basic book recommendations."""
        recommendations = self.library.recommend_books(2)
        self.assertEqual(len(recommendations), 2)
        
        # Should be sorted by rating (highest first)
        self.assertEqual(recommendations[0].get_title(), "AI Basics")  # Rating 4.5
        self.assertEqual(recommendations[1].get_title(), "Python Guide")  # Rating 4.0
    
    def test_recommend_books_improved_with_user(self):
        """Test improved recommendation system based on user preferences"""
        user_books = [self.book1, self.book2]
        user = User("user1", "Test User", [], user_books)
        self.library._all_users.append(user)
        
        recommendations = self.library.recommend_books_improved(user, 3)
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        
        user_titles = {book.get_title() for book in user_books}
        recommended_titles = {book.get_title() for book in recommendations}
        self.assertEqual(len(user_titles.intersection(recommended_titles)), 0)

    def test_recommend_books_improved_nonexistent_user(self):
        """Test improved recommendation with non-existent user"""
        nonexistent_user = User('user_404', "Nonexistent User", [], [])
        recommendations = self.library.recommend_books_improved(nonexistent_user, 5)
        self.assertEqual(recommendations, [])

    def test_recommend_books_improved_user_no_history(self):
        user = User("user2", "Empty User", [], [])
        self.library._all_users.append(user)
        
        recommendations = self.library.recommend_books_improved(user, 3)
        
        self.assertIsInstance(recommendations, list)
        regular_recommendations = self.library.recommend_books(3)
        self.assertEqual(len(recommendations), len(regular_recommendations))
    
    def test_equality(self):
        """Test library equality."""
        lib1 = Library()
        lib1._all_books = [self.book1]
        lib1._all_users = [self.user1]
        
        lib2 = Library()
        lib2._all_books = [self.book1]
        lib2._all_users = [self.user1]
        
        lib3 = Library()
        lib3._all_books = [self.book2]
        lib3._all_users = [self.user1]
        
        self.assertEqual(lib1, lib2)  # Same contents
        self.assertNotEqual(lib1, lib3)  # Different books
        self.assertNotEqual(lib1, "not_a_library")  # Different type
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.library)
        self.assertIn("Library(", repr_str)
        self.assertIn("Python Guide", repr_str)
        self.assertIn("Alice", repr_str)


if __name__ == '__main__':
    unittest.main()