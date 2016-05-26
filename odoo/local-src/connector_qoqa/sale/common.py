# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

import json
import logging
from datetime import datetime, date
from openerp import netsvc
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession

from ..unit.backend_adapter import QoQaAdapter, api_handle_errors
from ..backend import qoqa
from .exporter import cancel_sales_order, settle_sales_order


_logger = logging.getLogger(__name__)


class qoqa_sale_order(orm.Model):
    _name = 'qoqa.sale.order'
    _inherit = 'qoqa.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _description = 'QoQa User'

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Sales Order',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
        'qoqa_shop_id': fields.many2one(
            'qoqa.shop',
            string='QoQa Shop',
            required=True,
            readonly=True),
        'qoqa_order_line_ids': fields.one2many('qoqa.sale.order.line',
                                               'qoqa_order_id',
                                               'QoQa Order Lines'),
        'qoqa_amount_total': fields.float(
            'Total amount on QoQa',
            digits_compute=dp.get_precision('Account')),
        'invoice_ref': fields.char('Invoice Ref. on QoQa'),
        # id of the main payment on qoqa, used as key for reconciliation
        'qoqa_payment_id': fields.char('ID of the payment on QoQa'),
        'qoqa_payment_date': fields.date('Date of the payment',
                                         help="Local date of the payment, "
                                              "used to know if it can be "
                                              "canceled."),
        # field with name 'transaction' in the main payment
        'qoqa_transaction': fields.char('Transaction number of the payment '
                                        'on QoQa'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A sales order with the same ID on QoQa already exists"),
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A sales order can be exported only once on the same backend"),

    ]


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.sale.order',
            'openerp_id',
            string='QBindings'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        default['canceled_in_backend'] = False
        return super(sale_order, self).copy_data(cr, uid, id,
                                                 default=default,
                                                 context=context)

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        values = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        if order.qoqa_bind_ids:
            binding = order.qoqa_bind_ids[0]
            # keep only the issued invoice from the qoqa backend
            values.update({
                'name': binding.invoice_ref,
                # restore order's name, don't want the concatenated
                # invoices numbers
                'reference': order.name,
            })
        return values

    def _call_cancel(self, cr, uid, sale, cancel_direct=False, context=None):
        # only cancel on qoqa if all the cancellations succeeded
        # canceled_in_backend means already canceled on QoQa
        if not sale.canceled_in_backend:
            session = ConnectorSession(cr, uid, context=context)
            for binding in sale.qoqa_bind_ids:
                # should be called at the very end of the method
                # so we won't call 'cancel' on qoqa if something
                # failed before
                if cancel_direct:
                    # we want to do a direct call to the API when the payment
                    # can be canceled before midnight because the job may take
                    # too long time to be executed
                    _logger.info("Cancel order %s directly on QoQa",
                                 binding.name)
                    message = _('Impossible to cancel the sales order '
                                'on the backend now.')
                    with api_handle_errors(message):
                        cancel_sales_order(session, binding._model._name,
                                           binding.id)
                else:
                    # no timing issue in this one, the sales order must be
                    # canceled but it can be done later
                    _logger.info("Cancel order %s later (job) on QoQa",
                                 binding.name)
                    cancel_sales_order.delay(session, binding._model._name,
                                             binding.id, priority=1)

    def action_cancel(self, cr, uid, ids, context=None):
        """ Automatically cancel a sales orders and related documents.

        If the sales order has been created and canceled the same day, a
        direct call to the QoQa API will cancel the order, which will
        cancel the payment as well (excepted for Paypal, handled
        manually, hence the ``payment_method_id.payment_cancellable_on_qoqa``
        field). Otherwise, a refund will be created.
        """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        wf_service = netsvc.LocalService('workflow')
        refund_wiz_obj = self.pool['account.invoice.refund']
        actions = []
        for order in self.browse(cr, uid, ids, context=context):
            cancel_direct = False
            if (order.qoqa_bind_ids and
                    order.payment_method_id.payment_cancellable_on_qoqa):
                binding = order.qoqa_bind_ids[0]
                # can be canceled only the day of the payment
                payment_date = datetime.strptime(binding.qoqa_payment_date,
                                                 DEFAULT_SERVER_DATE_FORMAT)
                if payment_date.date() == date.today():
                    cancel_direct = True
            # For SwissBilling: if the SO is not done yet, cancel directly.
            # Otherwise, refund.
            if (order.qoqa_bind_ids and
                    order.payment_method_id.payment_settlable_on_qoqa):
                cancel_direct = True
            payment_ids = None
            invoice_ids = None
            if cancel_direct:
                # If the order can be canceled on QoQa, the payment is
                # canceled as well on QoQa so the internal payments
                # can just be withdrawn.
                # Otherwise, we have to keep them, they will be
                # reconciled with the invoice
                # WARNING! Delete account.move,
                # not just payments (account.move.line)
                payment_moves = [payment.move_id
                                 for payment
                                 in order.payment_ids]
                for move in payment_moves:
                    move.unlink()
            elif order.amount_total:
                # create the invoice, open it because we need the move
                # lines so we'll be able to reconcile them with the
                # payments
                order.action_invoice_create(grouped=False,
                                            states=['confirmed', 'done',
                                                    'exception', 'draft'])
                order.refresh()
                invoices = order.invoice_ids
                invoice_ids = [invoice.id for invoice in invoices]
                for invoice in invoices:
                    wf_service.trg_validate(uid, 'account.invoice',
                                            invoice.id, 'invoice_open', cr)
                    # create a refund since the payment cannot be
                    # canceled
                    ctx = context.copy()
                    ctx.update({
                        'active_model': 'account.invoice',
                        'active_id': invoice.id,
                        'active_ids': [invoice.id],
                    })
                    wizard_id = refund_wiz_obj.create(
                        cr, uid,
                        {'filter_refund': 'refund',
                         'description': _('Order Cancellation'),
                         },
                        context=ctx)

                    action = refund_wiz_obj.invoice_refund(cr, uid,
                                                           [wizard_id],
                                                           context=ctx)
                    actions.append(action)

                # We can't cancel an order with open invoices, but
                # we still want to do that, because we need the move lines
                # to be there to reconcile them with the payments. The
                # sales order is really canceled though. So we disconnect the
                # invoices then link them again after the cancellation.
                # We have the same issue with the automatic payments so
                # we use the same trick
                payments = order.payment_ids
                payment_ids = [payment.id for payment in payments]
                payment_commands = [(3, pay_id) for pay_id in payment_ids]
                invoice_commands = [(3, inv_id) for inv_id in invoice_ids]
                order.write({'payment_ids': payment_commands,
                             'invoice_ids': invoice_commands})

            # cancel the pickings
            for picking in order.picking_ids:
                # draft pickings are already canceled by the cancellation
                # of the sale order so we don't need to take care of
                # them.

                if picking.state not in ('draft', 'cancel', 'done'):
                    wf_service.trg_validate(uid, 'stock.picking', picking.id,
                                            'button_cancel', cr)

            # cancel the invoices
            for invoice in order.invoice_ids:
                # paid invoices were set as opened due to payments
                # being deleted, or were "detached" previously since
                # they will be refunded. Draft invoices will be cancelled
                # by the sale order cancellation.

                if invoice.state not in ('draft', 'cancel', 'paid'):
                    wf_service.trg_validate(uid, 'account.invoice',
                                            invoice.id,
                                            'invoice_cancel', cr)

            super(sale_order, self).action_cancel(cr, uid, [order.id],
                                                  context=context)
            if payment_ids:
                payment_commands = [(4, pay_id) for pay_id in payment_ids]
                invoice_commands = [(4, inv_id) for inv_id in invoice_ids]
                order.write({'payment_ids': payment_commands,
                             'invoice_ids': invoice_commands})

        action_res = None
        if actions:
            # Prepare the returning action.
            # Done before we call the cancellation on QoQa so if
            # something fails here, we won't call the QoQa API
            action_res = actions[0]
            refund_ids = []
            for action in actions:
                for field, op, value in action_res['domain']:
                    if field == 'id' and op == 'in':
                        refund_ids += value
            if len(refund_ids) == 1:
                # remove the domain, replaced by res_id
                # the refund will be open in the form view
                action_res['domain'] = False
                action_res['res_id'] = refund_ids[0]
                mod_obj = self.pool['ir.model.data']
                ref = mod_obj.get_object_reference(cr, uid, 'account',
                                                   'invoice_form')
                action_res['views'] = [(ref[1] if ref else False, 'form')]
            else:
                # open as tree view, merge all the ids of the refunds
                # in the domain
                new_domain = []
                for field, op, value in action_res['domain']:
                    if field == 'id' and op == 'in':
                        new_domain.append((field, op, refund_ids))
                    else:
                        new_domain.append((field, op, value))
                action_res['domain'] = new_domain

        self._call_cancel(cr, uid, order, cancel_direct=cancel_direct,
                          context=context)

        if action_res:
            return action_res

        return True

    def action_done(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_done(
            cr, uid, ids, context=context
        )
        # Browse orders to send 'settled' to BO
        for order in self.browse(cr, uid, ids, context=context):
            if (order.qoqa_bind_ids and
                    order.payment_method_id.payment_settlable_on_qoqa):
                session = ConnectorSession(cr, uid, context=context)
                for binding in order.qoqa_bind_ids:
                    _logger.info("Settle order %s later (job) on QoQa",
                                 binding.name)
                    settle_sales_order.delay(session, binding._model._name,
                                             binding.id, priority=1)
        return res

    def action_force_cancel(self, cr, uid, ids, context=None):
        """ Force cancellation of a done sales order.

        Only usable on done sales orders (so in the final state of the
        workflow) to avoid to break the workflow in the middle of its
        course.
        At QoQa, they might deliver sales orders and only cancel the order
        afterwards. In that case, even if the sales order is done, they need
        to set it as canceled on OpenERP and on the backend.
        """
        refund_wiz_obj = self.pool['account.invoice.refund']
        sale_order_line_obj = self.pool.get('sale.order.line')
        wf_service = netsvc.LocalService('workflow')
        actions = []
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state != 'done':
                raise orm.except_orm(
                    _('Cannot cancel this sales order!'),
                    _('Only done sales orders can be forced to be canceled.'))
            sale_order_line_obj.write(cr, uid,
                                      [l.id for l in sale.order_line],
                                      {'state': 'cancel'},
                                      context=context)
            cancel_direct = False
            if (sale.qoqa_bind_ids and
                    sale.payment_method_id.payment_cancellable_on_qoqa and
                    not sale.payment_method_id.payment_settlable_on_qoqa):
                binding = sale.qoqa_bind_ids[0]
                # can be canceled only the day of the payment
                payment_date = datetime.strptime(
                    binding.qoqa_payment_date, DEFAULT_SERVER_DATE_FORMAT)
                if payment_date.date() == date.today():
                    cancel_direct = True
            if cancel_direct:
                # Done the same day; remove payments
                payment_moves = [payment.move_id
                                 for payment
                                 in sale.payment_ids]
                for move in payment_moves:
                    move.unlink()
                # Cancel now-reopened invoices
                for invoice in sale.invoice_ids:
                    wf_service.trg_validate(uid, 'account.invoice',
                                            invoice.id, 'invoice_cancel', cr)
            else:
                for invoice in sale.invoice_ids:
                    # create a refund since the payment cannot be
                    # canceled
                    ctx = context.copy()
                    ctx.update({
                        'active_model': 'account.invoice',
                        'active_id': invoice.id,
                        'active_ids': [invoice.id],
                    })
                    wizard_id = refund_wiz_obj.create(
                        cr, uid,
                        {
                            'filter_refund': 'refund',
                            'description': _('Order Cancellation'),
                        },
                        context=ctx)

                    action = refund_wiz_obj.invoice_refund(
                        cr, uid, [wizard_id], context=ctx)
                    actions.append(action)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        message = _("The sales order was done, but it has been manually "
                    "canceled.")
        self.message_post(cr, uid, ids, body=message, context=context)

        # Return view for refunds
        action_res = None
        if actions:
            # Prepare the returning action.
            # Done before we call the cancellation on QoQa so if
            # something fails here, we won't call the QoQa API
            action_res = actions[0]
            refund_ids = []
            for action in actions:
                for field, op, value in action_res['domain']:
                    if field == 'id' and op == 'in':
                        refund_ids += value
            if len(refund_ids) == 1:
                # remove the domain, replaced by res_id
                # the refund will be open in the form view
                action_res['domain'] = False
                action_res['res_id'] = refund_ids[0]
                mod_obj = self.pool['ir.model.data']
                ref = mod_obj.get_object_reference(cr, uid, 'account',
                                                   'invoice_form')
                action_res['views'] = [(ref[1] if ref else False, 'form')]
            else:
                # open as tree view, merge all the ids of the refunds
                # in the domain
                new_domain = []
                for field, op, value in action_res['domain']:
                    if field == 'id' and op == 'in':
                        new_domain.append((field, op, refund_ids))
                    else:
                        new_domain.append((field, op, value))
                action_res['domain'] = new_domain

        self._call_cancel(cr, uid, sale, cancel_direct=False,
                          context=context)

        if action_res:
            return action_res

        return True


@qoqa
class QoQaSaleOrderAdapter(QoQaAdapter):
    _model_name = 'qoqa.sale.order'
    _endpoint = 'order'

    def cancel(self, id):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.put(url + str(id),
                                   data=json.dumps({'action': 'cancel'}),
                                   headers=headers)
        self._handle_response(response)

    def refund(self, id, payment_id, amount):
        """ Create a refund on the QoQa backend, return the payment id """
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {'action': 'credit',
                   'params': {'refno': payment_id,
                              'amount': amount,
                              }
                   }
        response = self.client.put(url + str(id),
                                   data=json.dumps(payload),
                                   headers=headers)
        response = self._handle_response(response)
        return response['data']['id']

    def cancel_refund(self, id, payment_id):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {'action': 'cancel_refund',
                   'params': {'refno': payment_id,
                              }
                   }
        response = self.client.put(url + str(id),
                                   data=json.dumps(payload),
                                   headers=headers)
        response = self._handle_response(response)
        return True

    def settle(self, id):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.put(url + str(id),
                                   data=json.dumps({'action': 'settled'}),
                                   headers=headers)
        self._handle_response(response)

    def pay_by_email_url(self, id, claim, amount):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {'action': 'pay_by_email_url',
                   'params': {'refno': claim,
                              'amount': amount,
                              }
                   }
        response = self.client.put(url + str(id),
                                   data=json.dumps(payload),
                                   headers=headers)
        response = self._handle_response(response)
        return response['data']['url']