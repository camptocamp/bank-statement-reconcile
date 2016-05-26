# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tristan Rouiller
#    Copyright 2014 QoQa Services SA
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

{'name': 'Delivery Carrier URL',
 'version': '0.0.1',
 'category': 'Others',
 'depends': ['delivery'
             ],
 'author': 'QoQa Services SA',
 'license': 'AGPL-3',
 'website': 'http://www.qoqa.ch',
 'description': """
Delivery carrier url
===================

Display the tracking url on the stock_picking_out object
The tracking template url can be set in the delivery carrier

""",
 'images': [],
 'demo': [],
 'data': ['delivery_carrier_view.xml', 'stock_move_view.xml'],
 'installable': False,
 'application': True,
 }