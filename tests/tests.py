import unittest
import time
from yaslis.book import Book
from yaslis.user import User
from yaslis.library import Library

class TestLibrarySystem(unittest.TestCase):

    def setUp(self):
        """Runs before every test — create a small library"""
        self.library = Library()
        self.book1 = Book("B01", "Learning Python", "Mark Lutz", "Programming", 2020, 90)
        self.book2 = Book("B02", "AI Revolution", "Nick Bostrom", "AI", 2019, 85)
        self.book3 = Book("B03", "Deep Learning", "Ian Goodfellow", "AI", 2016, 95)
        self.user = User("U01", "Alice")

        # Add to library
        self.library.add_book(self.book1.id, self.book1.title, self.book1.author, 
                              self.book1.genre, self.book1.published_year, self.book1.rating)
        self.library.add_book(self.book2.id, self.book2.title, self.book2.author, 
                              self.book2.genre, self.book2.published_year, self.book2.rating)
        self.library.add_book(self.book3.id, self.book3.title, self.book3.author, 
                              self.book3.genre, self.book3.published_year, self.book3.rating)
        self.library.add_user(self.user.id, self.user.name)

    # ---------------------- TESTS ----------------------

    def test_add_book(self):
        """Adding new books should increase library size"""
        self.assertEqual(len(self.library.get_books()), 3)
        titles = self.library.get_book_titles()
        self.assertIn("AI Revolution", titles)

    def test_add_user(self):
        """User should appear in the user list"""
        names = self.library.get_user_names()
        self.assertIn("Alice", names)

    def test_search_book(self):
        """Searching by ID should return correct book"""
        found = self.library.search_book("B03")
        self.assertIsNotNone(found)
        self.assertEqual(found.get_title(), "Deep Learning")

    def test_checkout_and_checkin(self):
        """User borrows and returns a book successfully"""
        self.library.checkout_book("B01", "U01")
        user = self.library.get_users()[0]
        borrowed_titles = user.get_borrowed_book_titles()
        self.assertIn("Learning Python", borrowed_titles)

        # Return book
        user.return_book("B01")
        self.assertNotIn("Learning Python", user.get_borrowed_book_titles())

    def test_remove_book_and_user(self):
        """Removing a book and user should update lists"""
        self.library.remove_book("B02")
        ids = self.library.get_book_ids()
        self.assertNotIn("B02", ids)

        self.library.remove_user("U01")
        user_ids = self.library.get_user_ids()
        self.assertNotIn("U01", user_ids)



    def test_search_timing(self):
        # measure average search time for large library
        for size in [1000, 10000]:
            lib = Library()
            for i in range(size):
                lib.add_book(f"B{i}", f"Title{i}", "Author", "Genre", 2020, 50)
            start = time.perf_counter()
            lib.search_book(f"B{size-1}")
            elapsed = time.perf_counter() - start
            print(f"Search time for {size} books: {elapsed:.6f}s")



if __name__ == "__main__":
    unittest.main()

