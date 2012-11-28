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

import placard.views
import placard.reports
import vpac_ldap.forms
import tldap

class AccountList(placard.views.AccountList):
    def get_queryset_old(self):
        group = placard.models.group.objects.get(cn="vpac")
        qs = super(AccountList, self).get_queryset()
        return qs.filter(tldap.Q(primary_group=group) | tldap.Q(secondary_groups=group))

    def get_queryset(self):
        qs = super(AccountList, self).get_queryset()
        return qs.filter(eduPersonAffiliation='staff')

    def get_queryset(self):
        qs = super(AccountList, self).get_queryset()
        return qs.filter(eduPersonAffiliation='staff')

class PdfAccountList(placard.reports.PdfAccountList):
    def get_queryset(self):
        qs = super(PdfAccountList, self).get_queryset()
        return qs.filter(eduPersonAffiliation='staff')

class LeftAccountList(placard.views.AccountList):
    def get_queryset(self):
        qs = super(LeftAccountList, self).get_queryset()
        return qs.filter(~tldap.Q(eduPersonAffiliation='staff'))

class AccountDetail(placard.views.AccountDetail):
    template_name = "vpac_ldap/user_detail.html"

class AccountAdd(placard.views.AccountAdd):
    form_class = vpac_ldap.forms.LDAPAddUserForm
    template_name = "vpac_ldap/user_form.html"

class AccountEdit(placard.views.AccountEdit):
    template_name = "vpac_ldap/user_form.html"

    def get_admin_form_class(self):
        return vpac_ldap.forms.LDAPUserForm

class AccountLock(placard.views.AccountLock):
    template_name = "vpac_ldap/user_confirm_lock.html"

class AccountUnlock(placard.views.AccountUnlock):
    template_name = "vpac_ldap/user_confirm_unlock.html"

class GroupDetail(placard.views.GroupDetail):
    template_name = "vpac_ldap/group_detail.html"
