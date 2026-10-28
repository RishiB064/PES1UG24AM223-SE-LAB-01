"""Library catalog management module."""

import hashlib
import os
import secrets

catalog = {
    "B01": {"title": "Clean Code", "copies": 3, "total": 3},
    "B02": {"title": "The Pragmatic Programmer", "copies": 1, "total": 1},
    "B03": {"title": "Design Patterns", "copies": 2, "total": 2},
}


def issue_book(book_id, patron, active_issues=None):
    """Issue a book to a patron; return True on success, False otherwise."""
    if active_issues is None:
        active_issues = []
    if book_id not in catalog or catalog[book_id]["copies"] <= 0:
        return False
    catalog[book_id]["copies"] -= 1
    active_issues.append(f"Issued book {book_id} to patron {patron}")
    return True


def return_book(book_id):
    """Return a book to the catalog; refuse unknown books and over-returns."""
    book = catalog.get(book_id)
    if book is None:
        print(f"Cannot return unknown book: {book_id}")
        return False
    if book["copies"] >= book["total"]:
        print(f"All copies of {book_id} are already in the library")
        return False
    book["copies"] += 1
    return True


def check_availability(book_id):
    """Return True if at least one copy of the book is on the shelf."""
    if catalog.get(book_id) is None:
        return False
    return catalog[book_id]["copies"] > 0


def calculate_fine(days_overdue, daily_rate=2.0):
    """Return the overdue fine for the given days at a daily rate."""
    return days_overdue * daily_rate


def generate_patron_hash(patron_id):
    """Return a SHA-256 hex digest identifying the patron."""
    return hashlib.sha256(patron_id.encode()).hexdigest()


def generate_temp_patron_pin():
    """Return a random 4-digit PIN from a secure generator."""
    return 1000 + secrets.randbelow(9000)


def export_catalog(filename="catalog_export.txt"):
    """Write the catalog to a text file."""
    with open(filename, "w", encoding="utf-8") as export_file:
        export_file.write(str(catalog))
    print(f"Catalog backup exported to: {filename}")


def main():
    """Run a short demonstration of the catalog system."""
    librarian_key = os.environ.get("LIBRARIAN_KEY")
    issue_book("B01", "P101")
    return_book("B02")
    print("Is B01 available:", check_availability("B01"))
    print("Fine accrued:", calculate_fine(4, 2.0))
    print("Patron Hash:", generate_patron_hash("P101"))
    print("Temp PIN:", generate_temp_patron_pin())
    export_catalog()
    print("Librarian key configured:", librarian_key is not None)


if __name__ == "__main__":
    main()
