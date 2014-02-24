# -*- coding: utf-8 -*-

import csv
import logging
from contextlib import closing

from support import *
from support.tools import model

logger = logging.getLogger('openerp.behave')


def _fileopen(ctx, filename, mode='r'):
    tmp_path = ctx.feature.filename.split(os.path.sep)
    tmp_path = tmp_path[1: tmp_path.index('features')] + ['data', '%s'%filename]
    tmp_path = [str(x) for x in tmp_path]
    path = os.path.join('/', *tmp_path)
    assert os.path.exists(path)
    return closing(open(path, mode))


@step('I import from QoQa the "{import_model}" with QoQa ids from file "{path}"')
def impl(ctx, import_model, path):
    """
    Import records from QoQa using the connector
    """
    data = csv.reader(_fileopen(ctx, path))
    qoqa_ids = (row[0] for row in data)
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    connector_qoqa = openerp.addons.connector_qoqa
    import_record = connector_qoqa.unit.import_synchronizer.import_record
    ConnectorSessionHandler = openerp.addons.connector.session.ConnectorSessionHandler
    session_hdl = ConnectorSessionHandler(db_name, 1)
    with session_hdl.session() as session:
        for qoqa_id in qoqa_ids:
            import_record.delay(session, import_model,
                                1, qoqa_id, force=True)
