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


import logging
from openerp.tools.translate import _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.event import on_record_write
from ..connector import get_environment
from ..backend import qoqa

_logger = logging.getLogger(__name__)


@qoqa
class CancelSalesOrder(ExportSynchronizer):
    _model_name = 'qoqa.sale.order'

    def run(self, binding_id):
        """ Cancel a sales order on QoQa"""
        qoqa_id = self.binder.to_backend(binding_id)
        if not qoqa_id:
            return _('Sales order does not exist on QoQa')
        self.backend_adapter.cancel(qoqa_id)
        return _('Sales order canceled on QoQa')


@on_record_write(model_names='sale.order')
def delay_cancel_sales_order(session, model_name, record_id, vals):
    """ Delay a job to cancel a sales order. """
    if session.context.get('connector_no_export'):
        return
    if not 'state' in vals:
        return
    sale = session.browse(model_name, record_id)
    # canceled_in_backend means already canceled on QoQa
    if sale.state == 'cancel' and not sale.canceled_in_backend:
        for binding in sale.qoqa_bind_ids:
            # cancel as early as possible
            cancel_sales_order.delay(session,
                                     binding._model._name,
                                     binding.id,
                                     priority=1)


@job
def cancel_sales_order(session, model_name, record_id):
    """ Cancel a Sales Order """
    binding = session.browse(model_name, record_id)
    backend_id = binding.backend_id.id
    env = get_environment(session, model_name, backend_id)
    canceler = env.get_connector_unit(CancelSalesOrder)
    return canceler.run(record_id)
