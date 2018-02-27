# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, _
from openerp.addons.connector.session import ConnectorSession
from .exporter import create_refund, cancel_refund
from ..unit.backend_adapter import QoQaAdapter, api_handle_errors

from ..backend import qoqa


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    active = fields.Boolean('Active', default=True)
    refund_from_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Refund generated from invoice',
        ondelete='restrict',
    )
    refund_ids = fields.One2many(
        comodel_name='account.invoice',
        inverse_name='refund_from_invoice_id',
        string='Refund generated from invoice',
    )
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        compute='_compute_sale_order_ids',
        string='Sale Orders',
    )

    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_order_ids(self):
        for invoice in self:
            sales = invoice.invoice_line_ids.mapped('sale_line_ids.order_id')
            invoice.sale_order_ids = sales.ids

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        result = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id,
        )
        result['refund_from_invoice_id'] = invoice.id
        return result

    @api.multi
    def refund_on_qoqa(self):
        """ Create (synchronously) a refund in the qoqa backend.

        If the origin invoice/sales order does not comes from qoqa,
        just return.

        The call is synchronous, if it fails, the refund cannot be
        validated.  The qoqa backend will create a payment using a
        payment service (datatrans) and return a transaction ID.

        """
        for refund in self:
            invoice = refund.refund_from_invoice_id
            if not invoice:
                continue
            sales = invoice.sale_order_ids
            if not sales or not sales[0].qoqa_bind_ids:
                continue
            qsale = sales[0].qoqa_bind_ids[0]
            session = ConnectorSession.from_env(self.env)
            # with .delay() it would be created in a job,
            # here it is called synchronously
            message = _('Impossible to refund on the backend.')
            with api_handle_errors(message):
                create_refund(session,
                              'account.invoice',
                              qsale.backend_id.id,
                              refund.id)
        return True

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        self.refund_on_qoqa()
        return result

    @api.multi
    def cancel_refund_on_qoqa(self):
        """ Cancel (synchronously) a refund in the qoqa backend.

        The call is synchronous, if it fails, the refund cannot be
        canceled.

        """
        for refund in self.with_context(active=False):
            invoice = refund.refund_from_invoice_id
            if not invoice:
                continue
            sales = invoice.sale_order_ids
            if not sales or not sales[0].qoqa_bind_ids:
                continue
            qsale = sales[0].qoqa_bind_ids[0]
            session = ConnectorSession.from_env(self.env)
            # with .delay() it would be created in a job,
            # here it is called synchronously
            message = _('Impossible to cancel a refund on the backend.')
            with api_handle_errors(message):
                cancel_refund(session,
                              'account.invoice',
                              qsale.backend_id.id,
                              refund.id)
        return True

    @api.multi
    def action_cancel(self):
        result = super(AccountInvoice, self).action_cancel()
        if not self.env.context.get('no_cancel_refund'):
            self.cancel_refund_on_qoqa()
        return result

    @api.multi
    def _refund_and_get_action(self, reason):
        refund_model = self.env['account.invoice.refund']
        actions = []
        for invoice in self:
            # create a refund since the payment cannot be
            # canceled
            action = refund_model.with_context(
                active_model='account.invoice',
                active_id=invoice.id,
                active_ids=invoice.ids,
            ).create(
                {'filter_refund': 'refund',
                 'description': reason}
            ).invoice_refund()

            actions.append(action)
        return actions


@qoqa
class QoQaCreditNote(QoQaAdapter):
    _model_name = 'qoqa.credit.note'  # virtual model
    _endpoint = 'admin/credit_notes'
    _resource = 'credit_note'

    def cancel(self, id):
        url = "{}{}/cancel".format(self.url(), id)
        response = self.client.put(url)
        result = self._handle_response(response)
        return result['cancelled']
