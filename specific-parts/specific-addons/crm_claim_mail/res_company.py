# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'claim_sale_order_regexp': fields.char(
            'Regular Expression for sale number',
            help="Regular expression used to extract the sales order's "
                 "number from the body of the emails."),
        'mail_signature_template': fields.html(
            'Mail signature template',
            required=True,
            translate=True,
            help='This is the mail signature template. You can add some'
                 ' variables :'
                 '$user_signature : the current user signature'
                 '$user_email : the current user email'
        ),
    }

    _default = {
        'mail_signature_template': (u'<p>Best wishes</p>'),

        'claim_sale_order_regexp': (u'<b>Order :</b>\s*<a '
                                    'href="http[^"]+"[^>]*>(\d+)</a>'),
    }