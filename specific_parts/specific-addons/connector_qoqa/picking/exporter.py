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

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.event import on_record_create
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.exception import MappingError

from ..connector import get_environment
from ..backend import qoqa


@on_record_create(model_names='qoqa.stock.picking')
def delay_export(session, model_name, record_id, fields=None):
    export_picking_tracking_done.delay(session, model_name,
                                       record_id)


@qoqa
class QoQaTrackingExporter(ExportSynchronizer):
    _model_name = 'qoqa.stock.picking'

    def _get_tracking_numbers(self, binding):
        # Get the ID of the shipper service on QoQa
        carrier = binding.carrier_id
        if not carrier:
            shipper_service_id = None
        else:
            binder = self.get_binder_for_model('qoqa.shipper.service')
            shipper_service_id = binder.to_backend(carrier.id, wrap=True)
            if shipper_service_id is None:
                raise MappingError('The delivery order %s cannot be exported '
                                   'because the shipper service %s does not '
                                   'exist on the QoQa backend' %
                                   (binding.name, carrier.name))

        # get the id of the sales order on QoQa
        sale = binding.sale_id
        binder = self.get_binder_for_model('qoqa.sale.order')
        qsale_id = binder.to_backend(sale.id, wrap=True)

        # Group the lines per tracking numbers
        trackings = {}
        for line in binding.move_lines:
            trackings.setdefault(line.tracking_id, set()).add(line)

        slbinder = self.get_binder_for_model('qoqa.sale.order.line')
        numbers = []
        for tracking, lines in trackings.iteritems():
            if tracking:
                number = tracking.serial
            else:
                # if lines are not linked to a tracking, we use the
                # tracking number directly written on the picking
                number = binding.carrier_tracking_ref

            items = []
            for line in lines:
                sale_line = line.sale_id
                item_id = slbinder.to_backend(sale_line.id, wrap=True)
                items.append({'item_id': item_id,
                              'quantity': line.product_qty,
                              })
            numbers.append({
                'number': number,
                'items': items,
                'shipper_service_id': shipper_service_id,
            })

        return {'order_id': qsale_id, 'tracking_numbers': numbers}

    def run(self, binding_id):
        """ Export the tracking numbers to QoQa """
        binding = self.session.browse(self.model._name, binding_id)
        data = self._get_tracking_numbers(binding)
        import pdb; pdb.set_trace()
        adapter = self.get_connector_unit_for_model('qoqa.sale.order',
                                                    BackendAdapter)
        adapter.create(data)
        self.session.write(self.model._name, binding_id, {'exported': True})


@job
def export_picking_tracking_done(session, model_name, binding_id):
    """ Export trackings of a delivery order. """
    record = session.browse(model_name, binding_id)
    env = get_environment(session, model_name, record.backend_id.id)
    exporter = env.get_connector_unit(QoQaTrackingExporter)
    return exporter.run(binding_id)
