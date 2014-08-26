# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'offer_id': fields.many2one(
            'qoqa.offer',
            string='Offer',
            readonly=True,
            select=True,
            ondelete='restrict'),
    }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type,
                         journal_id, context=None):
        vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.offer_id:
            vals['offer_id'] = picking.offer_id.id
        return vals


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'offer_id': fields.many2one(
            'qoqa.offer',
            string='Offer',
            select=True,
            readonly=True),
    }


class stock_move(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'offer_id': fields.related(
            'picking_id', 'offer_id',
            type='many2one',
            relation='qoqa.offer',
            readonly=True,
            store=True,
            select=True,
            string='Offer'),
    }
