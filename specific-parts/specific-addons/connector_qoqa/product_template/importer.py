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

from __future__ import division

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        TranslationImporter,
                                        )
from ..unit.mapper import iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class TemplateBatchImport(DelayedBatchImport):
    """ Import the QoQa Product Templates.

    For every product in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateImport(QoQaImportSynchronizer):
    _model_name = ['qoqa.product.template']

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id,
                                 mapper=TemplateImportMapper)

    @property
    def mapper(self):
        if self._mapper is None:
            env = self.environment
            self._mapper = env.get_connector_unit(TemplateImportMapper)
        return self._mapper


@qoqa
class TemplateVariantImportMapper(ImportMapper):
    """ Some mappings are duplicated on templates and variants.

    Otherwise, OpenERP reset the template values when a variant
    is imported.

    """
    _model_name = ['qoqa.product.template',
                   'qoqa.product.product',
                   ]


@qoqa
class TemplateImportMapper(ImportMapper):
    _model_name = 'qoqa.product.template'

    translatable_fields = [
    ]

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    @mapping
    def from_translations(self, record):
        """ The translatable fields are only provided in
        a 'translations' dict, we take the translation
        for the main record in OpenERP.
        """
        binder = self.get_binder_for_model('res.lang')
        lang = self.options.lang or self.backend_record.default_lang_id
        qoqa_lang_id = binder.to_backend(lang.id, wrap=True)
        main = next((tr for tr in record['translations']
                     if str(tr['language_id']) == str(qoqa_lang_id)), {})
        values = {}
        for source, target in self.translatable_fields:
            values[target] = self._map_direct(main, source, target)
        return values

    @mapping
    def common_with_variant(self, record):
        """ Share some mappings with the variants """
        mapper = self.get_connector_unit_for_model(
            TemplateVariantImportMapper)
        map_record = mapper.map_record(record)
        return map_record.values(**self.options)