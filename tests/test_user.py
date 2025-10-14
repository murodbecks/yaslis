import unittest
from yaslis.user import User
from yaslis.book import Book
from yaslis.utils import ValueValidationError
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestUser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.book1 = Book("001", "Python Guide", "Author1", "Tech", 2020, 4.0)
        self.book2 = Book("002", "AI Basics", "Author2", "Tech", 2021, 4.5)
        self.book3 = Book("003", "Math Fun", "Author3", "Math", 2019, 3.8)
        
        self.user = User("user_001", "John Doe", [self.book1], [self.book2, self.book3])
    
    def test_user_creation_valid(self):
        """Test valid user creation with different parameters."""
        # With books
        user1 = User("001", "Alice", [self.book1], [self.book1, self.book2])
        self.assertEqual(len(user1.get_borrowed_books()), 1)
        self.assertEqual(len(user1.get_history()), 2)
        
        # Without books (empty lists)
        user2 = User("002", "Bob")
        self.assertEqual(len(user2.get_borrowed_books()), 0)
        self.assertEqual(len(user2.get_history()), 0)
    
    def test_user_creation_invalid_types(self):
        """Test that invalid types raise ValueValidationError."""
        with self.assertRaises(ValueValidationError):
            User(123, "Name")  # Invalid id
        
        with self.assertRaises(ValueValidationError):
            User("001", None)  # Invalid name
        
        with self.assertRaises(ValueValidationError):
            User("001", "Name", "not_a_list")  # Invalid borrowed_books
    
    def test_non_book_objects_filtered_out(self):
        """Test that non-Book objects are filtered from lists."""
        mixed_list = [self.book1, "not_a_book", 123, self.book2]
        user = User("001", "Test", mixed_list, mixed_list)
        
        # Only Book objects should remain
        self.assertEqual(len(user.get_borrowed_books()), 2)
        self.assertEqual(len(user.get_history()), 2)
    
    def test_getters(self):
        """Test all getter methods."""
        self.assertEqual(self.user.get_id(), "user_001")
        self.assertEqual(self.user.get_name(), "John Doe")
        self.assertEqual(len(self.user.get_borrowed_books()), 1)
        self.assertEqual(len(self.user.get_history()), 2)
        
        # Test ID and title getters
        self.assertIn("001", self.user.get_borrowed_book_ids())
        self.assertIn("Python Guide", self.user.get_borrowed_book_titles())
        self.assertIn("002", self.user.get_book_ids_in_history())
    
    def test_returned_books(self):
        """Test returned books calculation."""
        # History has book2 and book3, borrowed has book1
        # So returned books should be book2 and book3
        returned = self.user.get_returned_books()
        self.assertEqual(len(returned), 2)
        self.assertIn(self.book2, returned)
        self.assertIn(self.book3, returned)
    
    def test_setters(self):
        """Test setters with valid and invalid values."""
        # Valid setters
        self.user.set_name("Jane Smith")
        self.user.set_id("new_id")
        
        self.assertEqual(self.user.get_name(), "Jane Smith")
        self.assertEqual(self.user.get_id(), "new_id")
        
        # Invalid setters
        with self.assertRaises(ValueValidationError):
            self.user.set_name(123)
        
        with self.assertRaises(ValueValidationError):
            self.user.set_id(None)
    
    def test_borrow_book(self):
        """Test borrowing books."""
        initial_count = len(self.user.get_borrowed_books())
        
        # Borrow valid book
        result = self.user.borrow_book(self.book2)
        self.assertTrue(result)
        self.assertEqual(len(self.user.get_borrowed_books()), initial_count + 1)
        
        # Try to borrow invalid object
        with self.assertRaises(ValueValidationError):
            self.user.borrow_book("not_a_book")
    
    def test_return_book(self):
        """Test returning books."""
        # Return existing borrowed book
        result = self.user.return_book("Python Guide")
        self.assertTrue(result)
        self.assertNotIn("Python Guide", self.user.get_borrowed_book_titles())
        
        # Try to return non-borrowed book
        result = self.user.return_book("Non-existent Book")
        self.assertFalse(result)
    
    def test_equality(self):
        """Test equality operator."""
        user1 = User("001", "Alice", [self.book1], [self.book1])
        user2 = User("001", "Alice", [self.book1], [self.book1])
        user3 = User("002", "Bob", [self.book1], [self.book1])
        
        self.assertEqual(user1, user2)  # Same users
        self.assertNotEqual(user1, user3)  # Different IDs
        self.assertNotEqual(user1, "not_a_user")  # Different type
    
    def test_repr(self):
        """Test string representation."""
        # Test with limited books to check formatting
        user = User("001", "Test User", [self.book1], [self.book1, self.book2])
        repr_str = repr(user)
        
        self.assertIn("Test User", repr_str)
        self.assertIn("Python Guide", repr_str)
        self.assertIn("User(", repr_str)


if __name__ == '__main__':
    unittest.main()