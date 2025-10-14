from yaslis.book import Book
from yaslis.utils import check_type, format_list

class User:

    def __init__(self, id: str, name: str, borrowed_books: list = [], history: list = []):
        check_type(id, str, "id")
        check_type(name, str, "name")
        check_type(borrowed_books, list, "borrowed_books")
        check_type(history, list, "history")

        self.id = id
        self.name = name
        self.borrowed_books = [book for book in borrowed_books if isinstance(book, Book)]
        self.history = [book for book in history if isinstance(book, Book)]
    
    # getters
    def get_id(self) -> str:
        return self.id
    
    def get_name(self) -> str:
        return self.name
    
    def get_borrowed_books(self) -> list:
        return self.borrowed_books

    def get_history(self) -> list:
        return self.history
    
    def get_returned_books(self) -> list:
        return [book for book in self.get_history() if book not in self.get_borrowed_books()]

    def get_borrowed_book_ids(self) -> list:
        return [book.get_id() for book in self.get_borrowed_books()]

    def get_book_ids_in_history(self) -> list:
        return [book.get_id() for book in self.get_history()]
    
    def get_borrowed_book_titles(self) -> list:
        return [book.get_title() for book in self.get_borrowed_books()]
    
    def get_book_titles_in_history(self) -> list:
        return [book.get_title() for book in self.get_history()]
    
    # setters
    def set_id(self, new_id: str) -> None:
        check_type(new_id, str, "new_id")

        self.id = new_id
    
    def set_name(self, new_name: str) -> None:
        check_type(new_name, str, "new_name")

        self.name = new_name
    
    # functions
    def borrow_book(self, new_book: Book) -> bool:
        check_type(new_book, Book, "new_book")

        self.borrowed_books.append(new_book)
        return True

    def return_book(self, book_title: str) -> bool:
        check_type(book_title, str, "book_title")

        for book in self.get_borrowed_books():
            if book.get_title() == book_title:
                self.borrowed_books.remove(book)
                return True
        
        print(f"Warning: Book with {book_title} title not found in borrowed books.")
        return False

    # dunder methods
    def __repr__(self) -> str:
        borrowed_book_titles_str = format_list(self.get_borrowed_book_titles(), 3)
        book_titles_in_history_str = format_list(self.get_book_titles_in_history(), 3)

        return (f"User(name='{self.get_name()}', borrowed_books='{borrowed_book_titles_str}', "
                f"history={book_titles_in_history_str})")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        
        return (self.get_id(), self.get_name(), self.get_borrowed_books(), self.get_history()) == \
            (other.get_id(), other.get_name(), other.get_borrowed_books(), other.get_history())

if __name__ == "__main__":
    book1 = Book('00', 'Learning Python', 'Mark Lutz', 'programming', 2025, 80)
    book2 = Book('01', 'Python for Data Analysis', 'Wes McKinney', 'programming', 2022, 96)
    book3 = Book('02', 'Introduction to Linear Algebra', 'Gilbert Strang', 'math', 2023)
    book4 = Book('03', 'AI Snake Oil', 'Aravind Narayanan and Sayash Kapoor', 'AI', 2024, '99')

    user = User('01', 'Bob', [book1, book2], [book1, book2, book4])
    print(f"Newly created user: {user}")
    print(f"Borrowed books: {user.get_borrowed_books()}")
    print(f"Returned books: {user.get_returned_books()}")
    print()

    print(f"Borrow another book: {book3}")
    user.borrow_book(book3)
    print(f"Borrowed books updated: {user.get_borrowed_books()}")
    print()

    print(f"Return a book: {book2}")
    user.return_book('Introduction to Linear Algebra')
    print(f"Borrowed books updated: {user.get_borrowed_books()}")
    print()

    print(f"Return not borrowed book: {book4}")
    user.return_book('AI Snake Oil')
    print(f"Returned books updated: {user.get_returned_books()}")
