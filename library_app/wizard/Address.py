from odoo import api,fields,models, _
from  odoo.exceptions import ValidationError

class Address(models.TransientModel):
    _name = 'library.requester.address'
    _description = 'A transient database created for a wizard'

    book_name = fields.Many2one('library.requested.books',string='Book', domain=[('state','=','receive')])
    req_address = fields.Text(string='Address')
    req_phone = fields.Char(string='Phone Number')
    req_email = fields.Char(string='Email Address')

    def deliver(self):
        for rec in self:
            if rec.req_phone == '1234567890':
                print("success")
            else:
                raise ValidationError(_('Invaild phone number!'))

    