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

from tldap.schemas import rfc, samba, eduroam, other, helpers
import tldap.manager
import django.conf
import time
import datetime
import smbpasswd

import placard.ldap_passwd

##########
# person #
##########

class person(rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'person' ])
        pk = 'uid'

    def __unicode__(self):
        return u"P:%s"%(self.displayName or self.cn)

    def check_password(self, password):
        return tldap.connection.check_password(self.dn, password)

    def change_password(self, password):
        if isinstance(password, unicode):
            password = password.encode()

        up = placard.ldap_passwd.UserPassword()
        self.userPassword = up.encodePassword(password, "ssha")

    def set_defaults(self):
        self.pwdAttribute = 'userPassword'

    def save(self, *args, **kwargs):
        self.cn = '%s %s' % (self.givenName, self.sn)
        self.displayName = '%s %s' % (self.givenName, self.sn)
        if self.pwdAttribute is None:
            self.pwdAttribute = 'userPassword'
        super(person, self).save(*args, **kwargs)

    def is_locked(self):
        return self.pwdAccountLockedTime is not None

    def lock(self):
        if not self.loginShell.startswith("/locked"):
            self.loginShell = '/locked' + self.loginShell
        self.eduPersonAffiliation = 'affiliate'
        self.pwdAccountLockedTime='000001010000Z'
        self.sambaAcctFlags = '[DU         ]'
        self.primary_group = placard.models.group.objects.get(cn="visitor")
        self.secondary_groups.clear()

    def unlock(self):
        if self.loginShell.startswith("/locked"):
            self.loginShell = self.loginShell[7:]
        self.eduPersonAffiliation = 'staff'
        self.pwdAccountLockedTime=None
        self.sambaAcctFlags = '[ U         ]'

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.person', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.person', 'manager')

###########
# account #
###########

class account(person, rfc.posixAccount, rfc.shadowAccount, helpers.accountMixin,
        samba.sambaSamAccount, eduroam.eduPerson, eduroam.auEduPerson, other.ldapPublicKey):

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    def __unicode__(self):
        return u"A:%s"%(self.displayName or self.cn)

    managed_by = tldap.manager.ManyToOneDescriptor('manager', 'vpac_ldap.models.account', 'dn')
    manager_of = tldap.manager.OneToManyDescriptor('dn', 'vpac_ldap.models.account', 'manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")

    def change_password(self, password):
        super(account, self).change_password(password)
        if isinstance(password, unicode):
            password = password.encode()
        self.sambaNTPassword=smbpasswd.nthash(password)
        self.sambaLMPassword=smbpasswd.lmhash(password)
        self.sambaPwdMustChange=None
        self.sambaPwdLastSet=str(int(time.mktime(datetime.datetime.now().timetuple())))

    def _generate_shared_token(self):
        try:
            from hashlib import sha
        except:
            from sha import sha
        import base64
        uid = self.uid
        mail = self.mail
        entityID = django.conf.settings.SHIBBOLETH_URL
        salt = django.conf.settings.SHIBBOLETH_SALT
        return base64.urlsafe_b64encode(sha(uid + mail + entityID + salt).digest())[:-1]

    def set_defaults(self):
        super(account, self).set_defaults()

        self.set_free_uidNumber()

        self.secondary_groups.add(group.objects.get(cn="Domain Users"))
        self.secondary_groups.add(group.objects.get(cn="vpac"))

        self.o = 'VPAC'
        self.loginShell = '/bin/bash'
        self.sambaDomainName = django.conf.settings.SAMBA_DOMAIN_NAME
        self.sambaAcctFlags = '[ U         ]'
        self.shadowInactive = 10
        self.shadowLastChange = 13600
        self.shadowMax = 365
        self.shadowMin = 1
        self.shadowWarning = 10
        self.sambaSID = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2)
        self.sambaPwdLastSet = str(int(time.mktime(datetime.datetime.now().timetuple())))

    def delete(self, using=None):
        self.manager_of.clear()
        super(account, self).delete(using)

    def save(self, *args, **kwargs):
        self.gecos = '%s %s' % (self.givenName, self.sn)
        self.homeDirectory =  '/home/%s' % self.uid
        self.mail = '%s@vpac.org' % self.uid

        if self.auEduPersonSharedToken is None:
            self.auEduPersonSharedToken = self._generate_shared_token()

        super(account, self).save(*args, **kwargs)

#########
# group #
#########

class group(rfc.posixGroup, samba.sambaGroupMapping, helpers.groupMixin):
    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    def __unicode__(self):
        return u"G:%s"%self.cn

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor('gidNumber', account, 'gidNumber', "primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor('memberUid', account, 'uid', False, "secondary_groups")

    def set_defaults(self):
        self.set_free_gidNumber()
        self.sambaGroupType = 2
        self.sambaSID = "S-1-5-" + django.conf.settings.SAMBA_DOMAIN_SID + "-" + str(int(self.uidNumber)*2 + 1001)

    def save(self, *args, **kwargs):
        if self.description is None:
            self.description = self.cn
        super(group, self).save(*args, **kwargs)

    def delete(self, using=None):
        super(group, self).delete(using)
