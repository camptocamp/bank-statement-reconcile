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

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper)
from ..backend import qoqa
from ..unit.import_synchronizer import (QoQaImportSynchronizer,
                                        TranslationImporter,
                                        DelayedBatchImport,
                                        )
from ..unit.mapper import ifmissing


@qoqa
class QoQaOfferPositionBatchImport(DelayedBatchImport):
    """ Import the QoQa offer positions.

    For every offer position in the list, a delayed job is created.
    Import from a date
    """
    _model_name = ['qoqa.offer.position']


@qoqa
class QoQaOfferPositionImport(QoQaImportSynchronizer):
    """ Import the description of the offer position.

    All the offer's fields are master in OpenERP but the
    ``description`` field.
    This field is filed on the QoQa Backend and we get
    back its value on OpenERP.

    """
    _model_name = 'qoqa.offer.position'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['deal_id'], 'qoqa.offer')

    def _is_uptodate(self, binding_id):
        """ We don't mind, we want to update it because
        we want the description to be updated even if the
        rest is more recent """
        return False

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        translation_importer = self.get_connector_unit_for_model(
            TranslationImporter)
        translation_importer.run(self.qoqa_record, binding_id)


@qoqa
class QoQaOfferPositionImportMapper(ImportMapper):
    _model_name = 'qoqa.offer.position'

    translatable_fields = [
        (ifmissing('description', ''), 'description'),
        (ifmissing('highlights', ''), 'highlights'),
    ]

    @mapping
    def from_translations(self, record):
        """ The translatable fields are only provided in
        a 'translations' dict, we take the translation
        for the main record in OpenERP.

        The Mapper is called one time per language, when it
        want to map the translation, it sets the translation
        language in self.options.lang. The mapper for translations
        is called in the importer._after_import.
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