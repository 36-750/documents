# Common database keeps a single source of truth
# What are the separate concerns of the different objects

class Library:
    ...

class Book:
    ...

class ReferenceBook(Book):
    ...

class RareBook(Book):
    ...

class RegularBook(Book):
    ...
