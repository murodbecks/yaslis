from typing import Union
from yaslis.utils import check_type

class Book:

    def __init__(self, id: str, title: str, author: str, genre: str, 
                 published_year: int, rating: Union[int, float] = None):
        check_type(id, str, 'id')
        check_type(title, str, 'title')
        check_type(author, str, 'author')
        check_type(genre, str, 'genre')
        check_type(published_year, int, "published_year")

        if not isinstance(rating, Union[int, float]):
            rating = None

        self.id = id
        self.title = title
        self.author = author
        self.genre = genre
        self.published_year = published_year
        self.rating = rating
    
    # getters
    def get_id(self) -> str:
        return self.id
    
    def get_title(self) -> str:
        return self.title

    def get_author(self) -> str:
        return self.author
    
    def get_genre(self) -> str:
        return self.genre

    def get_published_year(self) -> int:
        return self.published_year

    def get_rating(self) -> Union[int, float]:
        return self.rating

    # setters
    def set_id(self, new_id: str) -> None:
        check_type(new_id, str, "new_id")

        self.id = new_id
    
    def set_title(self, new_title: str) -> None:
        check_type(new_title, str, "new_title")

        self.title = new_title
    
    def set_author(self, new_author: str) -> None:
        check_type(new_author, str, "new_author")

        self.author = new_author
    
    def set_genre(self, new_genre: str) -> None:
        check_type(new_genre, str, "new_genre")

        self.genre = new_genre
    
    def set_published_year(self, new_published_year: int) -> None:
        check_type(new_published_year, int, "new_published_year")

        self.published_year = new_published_year
    
    def set_rating(self, new_rating: Union[int, float]) -> None:
        check_type(new_rating, Union[int, float], "new_rating")

        self.rating = new_rating
        
    # dunder methods
    def __repr__(self) -> str:
        return (f"Book(title='{self.get_title()}', author='{self.get_author()}', "
                f"genre='{self.get_genre()}', published_year={self.get_published_year()}, "
                f"rating={self.get_rating()})")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return False
        
        return (self.get_id(), self.get_title(), self.get_author(), 
                self.get_genre(), self.get_published_year(), self.get_rating()) == \
               (other.get_id(), other.get_title(), other.get_author(), 
                other.get_genre(), other.get_published_year(), other.get_rating())

if __name__ == "__main__":
    book = Book('01', 'Fooled by Randomness', 'Nassim Taleb', 'non-fiction', 2001, 95)
    print(f"Newly created book: {book}")
    print(f"Title: {book.get_title()}, author: {book.get_author()}, pulished year: {book.get_published_year()}, genre: {book.get_genre()}")
    print()

    new_genre = 'philosophy'
    print(f"Changing genre to {new_genre}")
    book.set_genre(new_genre)
    print(f"Current genre: {book.get_genre()}")
