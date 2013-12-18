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

from tldap.schemas import rfc, ad, samba, eduroam, other
import tldap.methods as base
import tldap.methods.common as common
import tldap.methods.pwdpolicy as pwdpolicy
import tldap.methods.ad as mad
import tldap.methods.samba as msamba
import tldap.methods.shibboleth as shibboleth
import tldap.manager

class localAccountMixin(object):
    @classmethod
    def set_defaults(cls, self):
        self.o = 'VPAC'

    @classmethod
    def unlock(cls, self):
        pass

#######
# rfc #
#######

class localRfcAccountMixin(object):
    @classmethod
    def post_add(cls, self, using):
        self.secondary_groups.add(rfc_group.objects.using(using).get(cn="vpac"))
        self.secondary_groups.add(rfc_group.objects.using(using).get(cn="v3"))
        self.secondary_groups.add(rfc_group.objects.using(using).get(cn="Domain Users"))

    @classmethod
    def lock(cls, self):
        using = self._alias
        self.primary_group = rfc_group.objects.using(using).get(cn="visitor")
        self.secondary_groups.clear()

class rfc_account(base.baseMixin):
    schema_list = [
        rfc.person, rfc.organizationalPerson, rfc.inetOrgPerson, rfc.pwdPolicy,
        rfc.posixAccount, rfc.shadowAccount, samba.sambaSamAccount,
        eduroam.eduPerson, eduroam.auEduPerson,
        other.ldapPublicKey, ]
    mixin_list = [ common.personMixin, pwdpolicy.pwdPolicyMixin, common.accountMixin, common.shadowMixin, msamba.sambaAccountMixin, shibboleth.shibbolethMixin, localAccountMixin, localRfcAccountMixin, ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixAccount' ])
        pk = 'uid'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='vpac_ldap.schemas.rfc_account', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='vpac_ldap.schemas.rfc_account', linked_key='manager')
    unixHomeDirectory = tldap.manager.AliasDescriptor("homeDirectory")


class rfc_group(base.baseMixin):
    schema_list = [ rfc.posixGroup, samba.sambaGroupMapping, ]
    mixin_list = [ common.groupMixin, msamba.sambaGroupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'posixGroup' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(this_key='gidNumber', linked_cls=rfc_account, linked_key='gidNumber', related_name="primary_group")
    secondary_accounts = tldap.manager.ManyToManyDescriptor(this_key='memberUid', linked_cls=rfc_account, linked_key='uid', linked_is_p=False, related_name="secondary_groups")

######
# ad #
######

class localAdAccountMixin(object):
    @classmethod
    def post_add(cls, self, using):
        self.secondary_groups.add(ad_group.objects.using(using).get(cn="vpac"))
        # this happens automagically by the ad server
        # self.secondary_groups.add(ad_group.objects.using(using).get(cn="Domain Users"))

    @classmethod
    def lock(cls, self):
        using = self._alias
        self.primary_group = ad_group.objects.using(using).get(cn="visitor")
        self.secondary_groups.clear()


class ad_account(base.baseMixin):
    schema_list = [ ad.person, rfc.organizationalPerson, rfc.inetOrgPerson, ad.user, ad.posixAccount, ]
    mixin_list = [ common.personMixin, common.accountMixin, mad.adUserMixin, localAccountMixin, localAdAccountMixin ]

    class Meta:
        base_dn_setting = "LDAP_ACCOUNT_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'user' ])
        pk = 'cn'

    managed_by = tldap.manager.ManyToOneDescriptor(this_key='manager', linked_cls='vpac_ldap.schemas.ad_account', linked_key='dn')
    manager_of = tldap.manager.OneToManyDescriptor(this_key='dn', linked_cls='vpac_ldap.schemas.ad_account', linked_key='manager')


class ad_group(base.baseMixin):
    schema_list = [ rfc.posixGroup, ad.group, ]
    mixin_list = [ common.groupMixin, mad.adGroupMixin ]

    class Meta:
        base_dn_setting = "LDAP_GROUP_BASE"
        object_classes = set([ 'top' ])
        search_classes = set([ 'group' ])
        pk = 'cn'

    # accounts
    primary_accounts = tldap.manager.OneToManyDescriptor(this_key='gidNumber', linked_cls=ad_account, linked_key='gidNumber', related_name="primary_group")
    secondary_accounts = tldap.manager.AdAccountLinkDescriptor(linked_cls=ad_account, related_name="secondary_groups")
