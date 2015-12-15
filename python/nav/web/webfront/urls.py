#
# Copyright (C) 2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Django URL configuration for webfront"""

from django.conf.urls import url, patterns

urlpatterns = patterns(
    'nav.web.webfront.views',
    url(r'^$', 'index', name='webfront-index'),
    url(r'^index/login/', 'login', name='webfront-login'),
    url(r'^index/logout/', 'logout', name='webfront-logout'),
    url(r'^about/', 'about', name='webfront-about'),
    url(r'^toolbox/$', 'toolbox', name='webfront-toolbox'),
    url(r'^preferences/$', 'preferences', name='webfront-preferences'),
    url(r'^preferences/savelinks$', 'save_links',
        name='webfront-preferences-savelinks'),
    url(r'^preferences/changepassword$', 'change_password',
        name='webfront-preferences-changepassword'),
    url(r'^preferences/setcolumns$', 'set_widget_columns',
        name='webfront-preferences-setwidgetcolumns'),
)
