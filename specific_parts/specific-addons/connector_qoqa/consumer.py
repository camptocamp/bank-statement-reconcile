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

from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink
                                            )
from openerp.addons.connector.connector import Binder
from .unit.export_synchronizer import export_record
from .unit.delete_synchronizer import export_delete_record
from .connector import get_environment


def delay_export(session, model_name, record_id, fields=None, **kwargs):
    """ Delay a job which export a binding record.

    (A binding record being a ``qoqa.res.partner``,
    ``qoqa.product.product``, ...)

    The additional kwargs are passed to ``delay()``, they can be:
        ``priority``, ``eta``, ``max_retries``.
    """
    if session.context.get('connector_no_export'):
        return
    export_record.delay(session, model_name, record_id,
                        fields=fields, **kwargs)


def delay_export_all_bindings(session, model_name, record_id, fields=None,
                              **kwargs):
    """ Delay a job which export all the bindings of a record.

    In this case, it is called on records of normal models and will delay
    the export for all the bindings.

    The additional kwargs are passed to ``delay()``, they can be:
        ``priority``, ``eta``, ``max_retries``.
    """
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    for binding in record.qoqa_bind_ids:
        export_record.delay(session, binding._model._name, binding.id,
                            fields=fields, **kwargs)


def delay_unlink(session, model_name, record_id, **kwargs):
    """ Delay a job which delete a record on QoQa.

    Called on binding records.

    The additional kwargs are passed to ``delay()``, they can be:
        ``priority``, ``eta``, ``max_retries``.
    """
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    env = get_environment(session, model_name, record.backend_id.id)
    binder = env.get_connector_unit(Binder)
    qoqa_id = binder.to_backend(record_id)
    if qoqa_id:
        export_delete_record.delay(session, model_name,
                                   record.backend_id.id, qoqa_id, **kwargs)
