import unittest
from yaslis.book import Book
from yaslis.utils import ValueValidationError
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestBook(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.book = Book("001", "Test Book", "Test Author", "Fiction", 2020, 4.5)
    
    def test_book_creation_valid(self):
        """Test valid book creation with and without rating."""
        # With rating
        book1 = Book("001", "Title", "Author", "Genre", 2020, 4.0)
        self.assertEqual(book1.get_rating(), 4.0)
        
        # Without rating
        book2 = Book("002", "Title", "Author", "Genre", 2020)
        self.assertIsNone(book2.get_rating())
    
    def test_book_creation_invalid_types(self):
        """Test that invalid types raise ValueValidationError."""
        with self.assertRaises(ValueValidationError):
            Book(123, "Title", "Author", "Genre", 2020)  # Invalid id
        
        with self.assertRaises(ValueValidationError):
            Book("001", "Title", "Author", "Genre", "2020")  # Invalid year
    
    def test_invalid_rating_becomes_none(self):
        """Test that invalid rating types become None."""
        book = Book("001", "Title", "Author", "Genre", 2020, "invalid")
        self.assertIsNone(book.get_rating())
    
    def test_getters(self):
        """Test all getter methods."""
        self.assertEqual(self.book.get_id(), "001")
        self.assertEqual(self.book.get_title(), "Test Book")
        self.assertEqual(self.book.get_author(), "Test Author")
        self.assertEqual(self.book.get_genre(), "Fiction")
        self.assertEqual(self.book.get_published_year(), 2020)
        self.assertEqual(self.book.get_rating(), 4.5)
    
    def test_setters_valid(self):
        """Test setters with valid values."""
        self.book.set_title("New Title")
        self.book.set_rating(3.5)
        
        self.assertEqual(self.book.get_title(), "New Title")
        self.assertEqual(self.book.get_rating(), 3.5)
    
    def test_setters_invalid(self):
        """Test setters with invalid types."""
        with self.assertRaises(ValueValidationError):
            self.book.set_title(123)
        
        with self.assertRaises(ValueValidationError):
            self.book.set_published_year("2020")
    
    def test_equality(self):
        """Test equality operator."""
        book1 = Book("001", "Title", "Author", "Genre", 2020, 4.0)
        book2 = Book("001", "Title", "Author", "Genre", 2020, 4.0)
        book3 = Book("002", "Title", "Author", "Genre", 2020, 4.0)
        
        self.assertEqual(book1, book2)  # Same books
        self.assertNotEqual(book1, book3)  # Different IDs
        self.assertNotEqual(book1, "not a book")  # Different type
    
    def test_repr(self):
        """Test string representation."""
        expected = ("Book(title='Test Book', author='Test Author', "
                   "genre='Fiction', published_year=2020, rating=4.5)")
        self.assertEqual(repr(self.book), expected)


if __name__ == '__main__':
    unittest.main()