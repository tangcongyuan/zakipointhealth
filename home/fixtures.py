from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from home.models import *
from django.contrib.auth.models import User, Group
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.core import serializers
import json

import logging
logger = logging.getLogger('zakipoint')

@user_passes_test(lambda u: u.is_staff and u.is_superuser, login_url='/admin/')
def init_fixtures(request):
    logger.info('user %s initialized fixtures', u.username)
    company_fixtures()
    appuser_fixtures()
    approle_fixtures()
    return redirect('/admin')

def company_fixtures():

    # AdminCo
    zph_admin = Company.create('ZPH Admin', 'admin_co')

    # Channel
    hsirx = Company.create('HSI-Rx', 'channel')
    aphys = Company.create('Affiliated Physicians', 'channel')
    aphys = Company.create('Affiliated Physicians', 'channel')

    # Employer
    vertex = Company.create('Vertex Pharmaceuticals', 'employer')
    cedar_rapids_city = Company.create('City of Cedar Rapids', 'employer')
    cedar_rapids_city = Company.create('City of Cedar Rapids', 'employer')

    all_company_names = [str(co) for co in Company.objects.all()]
    return sorted(all_company_names)

def appuser_fixtures():

    j,c1,c2 = AppUser.get_or_create('j.singh@zakipoint.com', password = 'alfa', is_superuser = True, is_staff = True)
    j,c1,c2 = AppUser.get_or_create('j.singh@zakipoint.com', password = 'alfa')
    heather,c1,c2 = AppUser.get_or_create('heather@zakipoint.com', password = 'alfa', first_name = 'Heather', last_name = 'Ritchie', is_staff = True)
    armen,c1,c2 =   AppUser.get_or_create('armen@zakipoint.com',   password = 'alfa', first_name = 'Armen', last_name = 'Meguerditchian', is_staff = True)
    dipali,c1,c2 =   AppUser.get_or_create('dipali@zakipoint.com',   password = 'alfa', first_name = 'Dipali', last_name = 'Dey')
    ramesh,c1,c2 =  AppUser.get_or_create('ramesh@zakipoint.com',  password = 'alfa', first_name = 'Ramesh', last_name = 'Kumar')
    snehasish,c1,c2 = AppUser.get_or_create('snehasish@zakipoint.com', password = 'alfa', first_name = 'Snehasish', last_name = 'Barman')
    yanpu,c1,c2 = AppUser.get_or_create('yanpu@zakipoint.com', password = 'alfa', first_name = 'Yanpu', last_name = 'Li')
    eric,c1,c2 = AppUser.get_or_create('eric@zakipoint.com', password = 'alfa', first_name = 'Congyuan (Eric)', last_name = 'Tang')

    all_supu_names = [str(usr)+'*' for usr in AppUser.objects.all() if usr.user.is_superuser]
    all_user_names = [str(usr) for usr in AppUser.objects.all() if not usr.user.is_superuser]
    return sorted(all_supu_names + all_user_names)

def approle_fixtures():

    cap_home = ['home']
    cap_hmtx = ['hmtx']
    cap_phii = ['phii'] # Allowed to see PII and PHI data

    j = AppUser.get('j.singh')
    zph_admin = Company.get('ZPH Admin')
    hsirx = Company.get('HSI-Rx')
    aphys = Company.get('Affiliated Physicians')
    vertex = Company.get('Vertex Pharmaceuticals')
    j.add_role(hsirx, cap_home + cap_hmtx + cap_phii)
    j.add_role(vertex, cap_home + cap_phii)

    heather = AppUser.get('heather')
    heather.add_role(hsirx, cap_home + cap_hmtx + cap_phii)
    heather.add_role(aphys, cap_home + cap_hmtx + cap_phii)
    heather.add_role(vertex, cap_home + cap_phii)
    heather.add_role(zph_admin, cap_home)

    ramesh = AppUser.get('ramesh')
    ramesh.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    dipali = AppUser.get('dipali')
    dipali.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    armen = AppUser.get('armen')
    armen.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    eric = AppUser.get('eric')
    eric.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    snehasish = AppUser.get('snehasish')
    snehasish.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    yanpu = AppUser.get('yanpu')
    yanpu.add_role(hsirx, cap_home + cap_hmtx + cap_phii)

    all_roles = [str(role) for role in AppRole.objects.all()]

    return all_roles

def validate_permission(username, co_name, pwr_names):
    user = AppUser.get(username = username)
    company = Company.get(name = co_name)
    return user.can_access(company, pwr_names)
