###############################################################################
#
#    Edafa Inc
#    Copyright (C) 2009-TODAY Edafa Inc(<https://www.edafa.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Edafa Facility',
    'version': '18.0.1.0',
    'license': 'LGPL-3',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Facility',
    'complexity': "easy",
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': ['openeducat_core'],
    'data': [
        'security/op_facility_security.xml',
        'security/ir.model.access.csv',
        'views/facility_view.xml',
        'views/facility_line_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/facility_demo.xml'
    ],
    'images': [
        'static/description/openeducat-facility_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
