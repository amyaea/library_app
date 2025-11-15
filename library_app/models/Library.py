from email.policy import default

from odoo import api,fields,models
from odoo.exceptions import UserError

class Library(models.Model):
    _name = 'library.data'
    _rec_name = 'book_name'
    _description = 'A database storing library information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    book_name = fields.Char(string='Book Name',tracking=True)
    isbn = fields.Char(string='ISBN',tracking=True)
    author = fields.Char(string='Author', tracking=True)
    is_it_borrowed = fields.Selection([('No','Not borrowed yet'),('Yes','Borrowed')],string='Is it borrowed?',tracking=True)
    active = fields.Boolean(default=True,tracking=True)
    book_category = fields.Selection([('scifi','Science Fiction'),('fi','Fiction'),('thriller','Thriller'),('fantasy','Fantasy'),('mystery','Mystery')], string='Category',tracking=True)
    book_summary = fields.Text(string='Summary of the book',tracking=True)
    author_message = fields.Char(string='A Message from the author',tracking=True)
    publish_date = fields.Date(string='Publish Date',tracking=True)
    publish_location = fields.Char(string='Publish Location',tracking=True)
    book_comments = fields.Html(tracking=True)
    coverImg = fields.Image(tracking=True)
    lisbn = fields.Char(string='Library ISBN',tracking=True)
    no_of_requests = fields.Integer(string='Number of requests',tracking=True,compute='get_no_of_requests',store=True,readonly=True)
    requested_book = fields.One2many('library.requested.books','book_name',tracking=True)

    _sql_constraints = [
        ('unique_lisbn', 'unique (lisbn)', 'No book can have the same LISBN as the other!'),
        ('unique_isbn', 'unique (isbn)', 'No book can have the same ISBN as the other!'),
        ('unique_book_name', 'unique (book_name)', 'No book can have the same name as the other!')
    ]

    @api.model
    def create(self, vals):
        vals['lisbn'] = self.env['ir.sequence'].next_by_code('seq.gen.code')
        vals['author'] = 'Benjamin'
        return super(Library,self).create(vals)

    def write(self, vals):
        for rec in self:
            if not rec.lisbn and ('lisbn' not in vals or vals['lisbn'] == ''):
                vals['lisbn'] = self.env['ir.sequence'].next_by_code('seq.gen.code')
        return super(Library,self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.isbn == '978-0-471-98764-3' or rec.isbn =='978-0-8070-5310-7':
                raise UserError('You cannot delete that record!')
        return super(Library,self).unlink()

    @api.depends('requested_book')
    def get_no_of_requests(self):
        for rec in self:
            rec.no_of_requests = self.env['library.requested.books'].search_count([('book_name','=',rec.id)])