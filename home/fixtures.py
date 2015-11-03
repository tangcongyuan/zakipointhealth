#
# run it by typing python manage.py shell < install_fixtures.py > /dev/null

from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from home.models import *
from entity.models import *
from entity.fixtures import *
from django.contrib.auth.models import User, Group
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.core import serializers
import json

initialize_entity_fixtures()

import logging
logger = logging.getLogger('zakipoint')

from session import *

@user_passes_test(lambda u: u.is_active and u.is_superuser and u.is_staff)
def entity_fixtures(request):
    user_fixtures()
    return redirect('/admin')

def user_fixtures():

    """
    making users is limited to admins who are staff and superuser
    (maybe this is redundant, because if you are superuser you are by definition also staff, but just in case.)

    """
    admin_capabilities = [
        'add_username_admin',
        'add_username_manager',
        'assign_roles',
        ]
    admin_sysadmin = UserRole.new('admin_sysadmin', ['add_username_admin', 'add_username_manager'])
    admin_admin = UserRole.new('admin_admin', ['pii','share_data'])
    admin_admin_ro = UserRole.new('admin_admin', ['share_data'])

    zph_admin, created = AdminCo.objects.get_or_create(name='ZPH Admin')
    if created:
        AppUser.new( 'j.singh@zakipoint.com', passwd='adm_zph', superuser=True, group=zph_admin)

    # AdminCo
    zakiPoint = AdminCo.new(name = 'zakipoint Health')

    # Channel
    adamEve = Channel.new(name = 'Adam and Eve')
    abelCain = Channel.new(name = 'Abel and Cain')
    Entity.new( 'adam@adameve.com', passwd='adminco', group=adamEve, role=admin_sysadmin)
    Entity.new( 'jon@adameve.com', passwd='adminco', group=adamEve, role=admin_admin)
    Entity.new( 'eve@adameve.com', passwd='adminco', group=adamEve, role=admin_admin_ro)
    Entity.new( 'abel@abelcain.com', passwd='adminco', group=abelCain, role=admin_sysadmin)
    Entity.new( 'cain@abelcain.com', passwd='adminco', group=abelCain, role=admin_admin)
    Entity.new( 'mary@abelcain.com', passwd='adminco', group=abelCain, role=admin_admin_ro)

    # Employer
    cedarRapids = Employer.new(name = 'Cedar Rapids')
    Entity.new( 'harriet@cedar-rapids.org', passwd='city1', group=cedarRapids, role=admin_sysadmin)
    Entity.new( 'freddy@cedar-rapids.org', passwd='city1', group=cedarRapids, role=admin_admin)
    Entity.new( 'manny@cedar-rapids.org', passwd='city1', group=cedarRapids, role=admin_admin_ro)

    return
