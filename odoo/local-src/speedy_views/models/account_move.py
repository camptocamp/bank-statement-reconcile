# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models
from .utils import create_index


class AccountMove(models.Model):
    _inherit = 'account.move'

    name = fields.Char(index=True)  # used for reconciliation
    journal_id = fields.Many2one(index=True)

    def init(self, cr):
        # index for the default _order of account.move
        index_name = 'account_move_order_list_sort_index'
        create_index(cr, index_name, self._table, '(date DESC, id DESC)')