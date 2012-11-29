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

from tldap.schemas import rfc, samba, eduroam, other
from placard.schemas import common
from placard.schemas.pwdpolicy import pwdPolicyMixin
from placard.schemas.samba import sambaAccountMixin, sambaGroupMixin
from placard.schemas.shibboleth import shibbolethMixin
import tldap.manager
import django.conf
import time
import datetime

import placard.ldap_passwd

##########
# person #
##########

class person(rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy, common.personMixin, pwdPolicyMixin):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'uid'

    def change_password(self, password):
        self.account_change_password(password)

    def set_defaults(self):
        self.set_inet_org_person_defaults()
        self.account_set_defaults()

    def save(self, *args, **kwargs):
        self.save_inet_org_person_defaults()
        self.account_save_defaults()
        self.cn = '%s %s' % (self.givenName, self.sn)
        super(person, self).save(*args, **kwargs)

    def is_locked(self):
        return self.account_is_locked()

    def lock(self):
        self.lock_shell()
        self.account_lock()

    def unlock(self):
        self.unlock_shell()
        self.account_unlock()

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.person', 'manager')


###########
# account #
###########

class account(person, rfc.posixAccount, rfc.shadowAccount, common.accountMixin,
        samba.sambaSamAccount, sambaAccountMixin,
        eduroam.eduPerson, eduroam.auEduPerson, shibbolethMixin,
        other.ldapPublicKey):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.account', 'manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")

    def set_defaults(self):
        super(account, self).set_defaults()
        self.set_posix_account_defaults()
        self.set_shadow_account_defaults()
        self.set_samba_account_defaults()
        self.set_shibboleth_defaults(self)
        self.secondary_groups.add(group.objects.get(cn="vpac"))
        self.o = 'VPAC'

    def delete(self, using=None):
        self.prepare_for_delete()
        super(account, self).delete(using)

    def save(self, *args, **kwargs):
        self.save_posix_account_defaults()
        self.save_shadow_account_defaults()
        self.save_samba_account_defaults()
        self.save_shibboleth_defaults()
        self.mail = '%s@vpac.org' % self.uid
        super(account, self).save(*args, **kwargs)

    def change_password(self, password):
        super(account, self).change_password(password)
        self.samba_account_change_password(self, password)

    def lock(self):
        super(account, self).lock()
        self.samba_account_lock()
        self.shibboleth_lock()
        self.primary_group = placard.models.group.objects.get(cn="visitor")
        self.secondary_groups.clear()

    def unlock(self):
        super(account, self).unlock()
        self.samba_account_unlock()
        self.shibboleth_lock()


#########
# group #
#########

class group(rfc.posixGroup, samba.sambaGroupMapping, common.groupMixin, sambaGroupMixin):
    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', account, 'uid', False, "secondary_groups")

    def set_defaults(self):
        self.set_posix_group_defaults()
        self.set_samba_group_defaults()

    def save(self, *args, **kwargs):
        self.save_posix_group_defaults()
        self.save_samba_group_defaults()
        super(group, self).save(*args, **kwargs)

    def delete(self, using=None):
        super(group, self).delete(using)

