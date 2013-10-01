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
        'deal_id': fields.many2one(
            'qoqa.deal',
            string='Deal',
            readonly=True),
    }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type,
                         journal_id, context=None):
        vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.deal_id:
            vals['deal_id'] = picking.deal_id.id
        return vals


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'deal_id': fields.many2one(
            'qoqa.deal',
            string='Deal',
            readonly=True),
    }
