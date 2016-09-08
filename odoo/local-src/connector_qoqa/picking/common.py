# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from openerp.addons.connector_ecommerce.models.event import on_picking_out_done


class QoqaStockPicking(models.Model):
    _name = 'qoqa.stock.picking'
    _inherit = 'qoqa.binding'
    _inherits = {'stock.picking': 'openerp_id'}
    _description = 'QoQa Delivery Order'

    openerp_id = fields.Many2one(comodel_name='stock.picking',
                                 string='Delivery Order',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    qoqa_sale_binding_id = fields.Many2one(
        'qoqa.sale.order',
        string='QoQa Sale Order',
        ondelete='set null',
    )
    exported = fields.Boolean('Exported')

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A delivery order can be exported only once on the same backend"),
    ]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.stock.picking',
        inverse_name='openerp_id',
        string='QBindings for Delivery Orders',
        copy=False,
    )


@on_picking_out_done
def picking_done_create_binding(session, model_name, record_id,
                                picking_method):
    """ Create a binding for the picking so it will be exported. """
    picking = session.env[model_name].browse(record_id)
    sale = picking.sale_id
    if not sale:
        return
    if not sale.qoqa_bind_ids:
        return  # does not comes from QoQa

    for sale_binding in sale.qoqa_bind_ids:
        session.env['qoqa.stock.picking'].create({
            'backend_id': sale_binding.backend_id.id,
            'openerp_id': picking.id,
            'qoqa_sale_binding_id': sale_binding.id,
        })