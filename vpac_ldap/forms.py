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

import placard.forms

import django.forms as forms
import placard.fields as fields

import django.conf

AFFILIATIONS = (
    ('staff', 'Staff'),
    ('student', 'Student'),
    ('affiliate', 'Affiliate'),
)


class LDAPAccountForm(placard.forms.LDAPAccountForm):
    eduPersonAffiliation = forms.ChoiceField(label="Affiliation", choices=AFFILIATIONS, initial='staff')
    sshPublicKey = fields.CharField(label="SSH pub-key", required=False, widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))

    primary_groups = set([ 'systems', 'cs', 'cas', 'visitor', 'summer', 'versi', 'advcomp', 'apps', 'innovations', 'csc' ])


class LDAPAddAccountForm(placard.forms.LDAPAddAccountForm):
    eduPersonAffiliation = forms.ChoiceField(label="Affiliation", choices=AFFILIATIONS, initial='staff')
    sshPublicKey = fields.CharField(label="SSH pub-key", required=False, widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))
    force = forms.BooleanField(label='Cluster user exists', required=False)

    primary_groups = set([ 'systems', 'cs', 'cas', 'visitor', 'summer', 'versi', 'advcomp', 'apps', 'innovations', 'csc' ])

    def clean_uid(self):
        username = super(LDAPAddAccountForm, self).clean_uid()

        if 'force' not in self.cleaned_data:
            import xmlrpclib
            login = django.conf.settings.CLUSTER_USER
            password = django.conf.settings.CLUSTER_PASSWORD
            url = django.conf.settings.CLUSTER_URL
            server = xmlrpclib.Server(url)
            if server.username_exists(login, password, username):
                raise forms.ValidationError(u'Username exists on clusters')

        return username


