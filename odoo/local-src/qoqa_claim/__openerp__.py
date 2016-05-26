# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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

{'name': 'QoQa Claim Specifics',
 'version': '0.0.2',
 'category': 'Others',
 'depends': ['crm_claim_rma',
             'crm_claim_mail',
             'connector_qoqa'
             ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Claim Specific
===================

Local claim customizations for QoQa.
 * Add related for company on the warehouse

""",
 'images': [],
 'demo': [],
 'data': ['claim_data.xml',
          'company_view.xml',
          'wizard/crm_claim_unclaimed_view.xml',
          ],
 'installable': False,
 'application': True,
 }