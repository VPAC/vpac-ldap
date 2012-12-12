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
            ad_account = vpac_ldap.schemas.ad_account.objects.using("ad").get(pk=account.pk)

            if verbose:
                print
                print account.pk, account.uidNumber
                print ad_account.pk, ad_account.uidNumber

            ad_account.uid = account.uid
            ad_account.givenName = account.givenName
            ad_account.sn = account.sn
            ad_account.title = account.title
            ad_account.jpegPhoto = account.jpegPhoto
            ad_account.telephoneNumber = account.telephoneNumber
            ad_account.mobile = account.mobile
            ad_account.facsimileTelephoneNumber = account.facsimileTelephoneNumber
            if account.description is not None:
                ad_account.description = account.description[0:1024]
            else:
                ad_account.description = None
            ad_account.primary_group = vpac_ldap.schemas.ad_group.objects.using("ad").get(pk=account.primary_group.get_obj().pk)
            ad_account.save()

            for group in account.secondary_groups.all():
                ad_group = vpac_ldap.schemas.ad_group.objects.using("ad").get(pk=group.pk)
                if verbose:
                    print "--- ", group.pk, group.gidNumber
                    print "--- ", ad_group.pk, ad_group.gidNumber
                ad_account.secondary_groups.add(ad_group)

        for group in vpac_ldap.schemas.rfc_group.objects.all():
            ad_group = vpac_ldap.schemas.ad_group.objects.using("ad").get(gidNumber=group.gidNumber)

            if verbose:
                print
                print group.pk, group.gidNumber
                print ad_group.pk, ad_group.gidNumber

            if group.pk != ad_group.pk:
                if verbose:
                    print "renaming '%s' to '%s'"%(ad_group.pk,group.pk)
                    ad_group.rename(pk=group.pk)

            ad_group.displayName = group.displayName
            ad_group.save()
