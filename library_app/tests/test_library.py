from odoo.tests import TransactionCase
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta

class TestLibrary(TransactionCase):

    def setUp(self):
        super(TestLibrary, self).setUp()
        self.Library = self.env['library.data']
        self.RequestedBooks = self.env['library.requested.books']
        self.book = self.Library.create({
            'book_name': 'Unit Test Book',
            'isbn': 'UT-123-ISBN',
            'book_category': 'fi',
            'is_it_borrowed': 'No',
        })

    def test_create_generates_lisbn_and_author(self):
        self.assertTrue(self.book.lisbn.startswith('BN'))
        self.assertEqual(self.book.author, 'Benjamin')

    def test_unique_isbn_constraint(self):
        with self.assertRaises(Exception):
            self.Library.create({
                'book_name': 'Duplicate ISBN',
                'isbn': 'UT-123-ISBN',
                'book_category': 'scifi',
            })

    def test_protected_unlink(self):
        protected_book = self.Library.create({
            'book_name': 'Protected',
            'isbn': '978-0-471-98764-3',
            'book_category': 'thriller',
        })
        with self.assertRaises(UserError):
            protected_book.unlink()

    def test_request_workflow(self):
        req = self.RequestedBooks.create({
            'book_name': self.book.id,
            'requester_dob': date(2000, 6, 19),
        })
        self.assertEqual(req.state, 'requested')
        req.prepare_book()
        self.assertEqual(req.state, 'preparing')
        req.lease_book()
        self.assertEqual(req.state, 'receive')

    def test_future_dob_validation(self):
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.RequestedBooks.create({
                'book_name': self.book.id,
                'requester_dob': future_date,
            })

    def test_age_inverse_logic(self):
        req = self.RequestedBooks.create({
            'book_name': self.book.id,
            'requester_dob': date(2005, 1, 1),
        })
        age = req.requester_age
        req.requester_age = age + 1
        self.assertTrue(req.requester_dob.year <= date.today().year - (age + 1))

    def test_no_of_requests_computation(self):
        self.RequestedBooks.create({'book_name': self.book.id})
        self.book.invalidate_cache()
        self.assertEqual(self.book.no_of_requests, 1)
