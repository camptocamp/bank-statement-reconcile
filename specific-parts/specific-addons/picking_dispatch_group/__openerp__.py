# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Picking Dispatch - Automatic Grouping',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Stock Logistics',
 'complexity': "normal",
 'depends': ['picking_dispatch',
             ],
 'description': """
Picking Dispatch - Automatic Grouping
=====================================

Allows to create picking dispatches based on a list of Delivery Orders.

""",
 'website': 'http://www.camptocamp.com',
 'data': ['wizard/dispatch_group_view.xml',
          'picking_view.xml',
          'stock_move_view.xml',
          'report.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
}