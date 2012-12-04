# Copyright 2010 VPAC
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

from django.core.management.base import BaseCommand, CommandError

import vpac_ldap.schemas
import tldap.transaction

class Command(BaseCommand):
    help = "Inititlise LDAP"

    @tldap.transaction.commit_on_success(using='ad')
    def handle(self, **options):        
        verbose = int(options.get('verbosity'))

        for account in vpac_ldap.schemas.rfc_account.objects.all():
            adaccount = vpac_ldap.schemas.ad_account.objects.using("ad").get(pk=account.pk)

            if verbose:
                print
                print account.pk, account.uidNumber
                print adaccount.pk, adaccount.uidNumber

            adaccount.uid = account.uid
            adaccount.givenName = account.givenName
            adaccount.sn = account.sn
            adaccount.title = account.title
            adaccount.primary_group = vpac_ldap.schemas.ad_group.objects.using("ad").get(pk=account.primary_group.get_obj().pk)
            adaccount.gidNumber = None
            adaccount.save()

        for group in vpac_ldap.schemas.rfc_group.objects.all():
            adgroup = vpac_ldap.schemas.ad_group.objects.using("ad").get(gidNumber=group.gidNumber)

            if verbose:
                print
                print group.pk, group.gidNumber
                print adgroup.pk, adgroup.gidNumber

            if group.pk != adgroup.pk:
                if verbose:
                    print "renaming '%s' to '%s'"%(adgroup.pk,group.pk)
                    adgroup.rename(pk=group.pk)
