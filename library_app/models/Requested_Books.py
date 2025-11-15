from odoo import api,fields,models,_
from datetime import date, datetime

from odoo.api import ondelete
from odoo.exceptions import ValidationError

from dateutil import relativedelta

class Requested_Books(models.Model):
    _name = 'library.requested.books'
    _rec_name = 'book_name'
    _description = 'A database storing requested books to borrow'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    """@api.model
    def default_get(self, fields):
        res = super(Requested_Books,self).default_get(fields)
        res['request_time'] = fields.Datetime.now()
        return res"""

    book_name = fields.Many2one('library.data',string='Book Name',tracking=True,ondelete='restrict')
    isbn = fields.Char(string='ISBN', related='book_name.isbn', readonly=True, tracking=True)
    request_time = fields.Datetime(string='Time', default=fields.Datetime.now,readonly=True, tracking=True)
    author = fields.Char(string='Author', related='book_name.author', readonly=True, tracking=True)
    is_it_borrowed = fields.Selection([('No', 'Not borrowed yet'), ('Yes', 'Borrowed')], string='Is it borrowed?', related='book_name.is_it_borrowed', readonly=True, tracking=True)
    book_category = fields.Selection([('scifi','Science Fiction'),('fi','Fiction'),('thriller','Thriller'),('fantasy','Fantasy'),('mystery','Mystery')],string='Category', related='book_name.book_category', readonly=True, tracking=True)
    requester_dob = fields.Date(string='Requester Date Of Birth', tracking=True)
    requester_age = fields.Integer(string='Requester Age', compute='get_age', inverse='inverse_get_age', store=True, tracking=True)
    book_summary = fields.Text(string='Summary of the book', related='book_name.book_summary',tracking=True)
    author_message = fields.Char(string='A Message from the author', related='book_name.author_message',tracking=True)
    publish_date = fields.Date(String='Publish Date', related='book_name.publish_date',tracking=True)
    publish_location = fields.Char(string='Publish Location', related='book_name.publish_location',tracking=True)
    state = fields.Selection([('requested', 'Requested'), ('preparing', 'Preparing'), ('receive', 'Ready to borrow')], tracking=True, default='requested', required=True)

    @api.constrains(requester_dob)
    def _check_requester_dob(self):
        for rec in self:
            if rec.requester_dob > fields.Date.today():
                raise ValidationError (_('You cannot be born in the future and exist at the same time!'))

    def lease_book(self):
        for rec in self:
            rec.state = 'receive'

    def prepare_book(self):
        for rec in self:
            rec.state = 'preparing'

    @api.depends('requester_dob')
    def get_age(self):
        for rec in self:
            today_date = date.today()
            if rec.requester_dob:
                rec.requester_age = today_date.year - rec.requester_dob.year
            else:
                rec.requester_age = 0

    def unlink(self):
        for rec in self:
            if rec.state == 'preparing':
                raise ValidationError(_('The book is getting prepared, you cannot undo that!'))
        return super(Requested_Books,self).unlink()

    @api.depends('requester_age')
    def inverse_get_age(self):
        today = date.today()
        for rec in self:
            rec.requester_dob = today - relativedelta.relativedelta(years=rec.requester_age)

    #the below code is wrong, requester_age SHOULD be a stored field, use this for non stored fields
    #def search_age(self,operator,value):
        #print(value)
        #return[('requester_age','=',value)]