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

# Django settings for placard project.
from placard.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

AUTHENTICATION_BACKENDS = (
 'placard.backends.LDAPBackend',
)
MIDDLEWARE_CLASSES += ('placard.middleware.LDAPRemoteUserMiddleware',)

DEBUG=True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'vpac_ldap.urls'

INSTALLED_APPS = (
    'south',
    'tldap.methods',
    'placard.logging',
    'vpac_ldap',
) + INSTALLED_APPS
