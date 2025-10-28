###############################################################################
#
#    Edafa Website Branding
#    Copyright (C) 2024 Edafa Inc.
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
    'name': 'Edafa Website Branding',
    'version': '18.0.1.0',
    'license': 'LGPL-3',
    'category': 'Website',
    'sequence': 1,
    'summary': 'Edafa branding for website logo and favicon',
    'complexity': "easy",
    'author': 'Edafa Inc',
    'website': 'https://www.edafa.org',
    'depends': [
        'base',
        'website',
    ],
    'data': [
        'data/website_data.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
