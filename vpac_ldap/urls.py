# Copyright 2012 VPAC
#
# This file is part of django-placard.
#
# django-placard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-placard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-placard  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
from django.contrib import admin

import vpac_ldap.views

import placard.views as views
import placard.logging.views
import placard.user_urls
import placard.group_urls

import ajax_select.urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='plac_index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lookup/', include(ajax_select.urls)),

    url(r'^search/$', views.search, name='plac_search'),
    url(r'^change_password/$', views.UserChangePassword.as_view(), name='plac_user_password'),

    url(r'^logs/$', placard.logging.views.LogView.as_view(), name='plac_log'),
    url(r'^logs/(?P<user>[-.\w]+)/$', placard.logging.views.LogView.as_view(), name='plac_log_user'),

    url(r'^users/$', vpac_ldap.views.AccountList.as_view(), name='plac_user_list'),
    url(r'^users/left/$', vpac_ldap.views.LeftAccountList.as_view(), name='plac_user_gone_list'),
    url(r'^users/add/$', vpac_ldap.views.AccountAdd.as_view(), name='plac_user_add'),
    url(r'^users/pdf/$', vpac_ldap.views.PdfAccountList.as_view(), name='plac_user_list_pdf'),
    url(r'^users/(?P<username>[-.\w\$]+)/$', vpac_ldap.views.AccountDetail.as_view(), name='plac_user_detail'),
    url(r'^users/(?P<username>[-.\w\$]+)/logs/$', placard.logging.views.LogView.as_view(), name='plac_user_log'),
    url(r'^users/(?P<username>[-.\w\$]+)/edit/$', vpac_ldap.views.AccountEdit.as_view(), name='plac_user_edit'),
    url(r'^users/(?P<username>[-.\w\$]+)/lock/$', vpac_ldap.views.AccountLock.as_view(), name='plac_user_lock'),
    url(r'^users/(?P<username>[-.\w\$]+)/unlock/$', vpac_ldap.views.AccountUnlock.as_view(), name='plac_user_unlock'),
    url(r'^users/', include(placard.user_urls)),

    url(r'^groups/(?P<group>[-.\w ]+)/$', vpac_ldap.views.GroupDetail.as_view(), name='plac_grp_detail'),
    url(r'^groups/(?P<group>[-.\w ]+)/logs/$', placard.logging.views.LogView.as_view(), name='plac_grp_log'),
    url(r'^groups/', include(placard.group_urls)),
)
