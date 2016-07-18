# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    active = fields.Boolean(
        'Active', default=True,
        help="The active field allows you to hide the picking dispatch "
             "without removing it."
    )