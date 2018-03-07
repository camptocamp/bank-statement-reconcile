# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, fields, models, SUPERUSER_ID
from .utils import install_trgm_extension, create_index


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Override _order set in account_move_base_import and which is
    # slow as hell. We redefine the original one.
    _order = 'date DESC, id DESC'

    # Reconciliation processes use intensive searches on those fields
    debit = fields.Monetary(index=True)
    credit = fields.Monetary(index=True)
    amount_residual = fields.Monetary(index=True)
    invoice_id = fields.Many2one(index=True)

    # QoQa does not use the cash basis and the
    # computation of these fields (cash basis and matched percentage)
    # is slow as hell. For instance, it takes up to 60-70% of the time
    # of a reconciliation.
    # Cut off their computation.
    debit_cash_basis = fields.Monetary(compute=lambda self: None, store=False)
    credit_cash_basis = fields.Monetary(compute=lambda self: None, store=False)

    def init(self, cr):
        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        cr.commit()

        if trgm_installed:
            index_name = 'account_move_line_transaction_ref_gin_trgm'
            create_index(cr, index_name, self._table,
                         'USING gin (transaction_ref gin_trgm_ops)')

        # in reconcile wizard, queries look for null or false values
        # for 'reconciled'. We improve the mass reconciliations with
        # this partial index
        index_name = 'account_move_line_not_reconciled_index'
        create_index(cr, index_name, self._table,
                     '(reconciled) WHERE '
                     'reconciled IS NULL OR NOT reconciled ')

        # in reconcile wizard, a query is regularly issued with an
        # order by date_maturity, id, and we improve from 6s to 0.5ms
        index_name = 'account_move_line_date_maturity_order_index'
        create_index(cr, index_name, self._table,
                     '(date_maturity, id)')