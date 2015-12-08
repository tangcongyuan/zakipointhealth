from django.db import models, IntegrityError

# Create your models here.
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from zphalfa import json_field
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

companies = ['hsirx', 'affiliatedphysicians']

class AppError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AppUser(models.Model):
    """
    @TODO: Implement password change. Maybe use Django Password Policies?
        http://tarak.github.io/django-password-policies/api/index.html
    """
    user    = models.OneToOneField(User, primary_key=True)
        
    def __unicode__(self):
        return self.user.username

    @classmethod
    def get_or_create(cls, email, **kwargs):
        """
        This operation is designed to be idempotent -- it will not create duplicate users.
        But it is not thread-safe, intended to be used only for creating fixtures.
        kwargs are applied only at creation of the inner user, so it can not be used for changing password, etc.
        @TODO: allow kwargs to be applied every time so it CAN be used for changing password, etc.

        returns appuser, boolean, boolean
        The 1st boolean refers to whether the inner object was created
        The 2nd boolean refers to whether the outer object was created
        """
        try:
            validate_email(email)
        except ValidationError:
            raise
        username = email.split('@')[0]

        this_appuser = AppUser.get(username)
        if this_appuser:
            return this_appuser, False, False

        try:
            user = User.objects.get(username = username)
            inner_created = False
        except ObjectDoesNotExist:
            # the inner user does not exist, create it first
            try:
                user, inner_created = User.objects.get_or_create(username = username)
                user.email = email
            except MultipleObjectsReturned:
                raise # What the...

            if 'password' in kwargs.keys():
                user.set_password(kwargs['password'])
            for kw in kwargs.keys():
                if '__' in kw or kw in ['username', 'password']:
                    continue
                elif kw == 'group':
                    user.groups.add(kwargs[kw])
                elif kw == 'company':
                    user.groups.add(kwargs[kw].group)
                else:
                    setattr(user, kw, kwargs[kw])
            user.save()

        # create the outer user
        this_appuser = cls(user = user)
        this_appuser.save()
        return this_appuser, inner_created, True

    @classmethod
    def get(cls, username):
        try:
            this_user = User.objects.get(username = username)
            this_appuser = this_user.appuser
            return this_appuser
        except ObjectDoesNotExist:
            return None
        except AttributeError:
            return None

    def add_role(self, co_name, power_names):
        role = AppRole.create(self, co_name)
        role.save()
        powers = [Power.objects.get_or_create(name = pname)[0] for pname in power_names]
        role.powers = powers

    def can_access(self, company, power_names):
        if self.user.is_superuser:
            return True
        role = AppRole.get(self, company)
        if not role:
            return False
        all_permitted = set(power_names) & set(role.power_names)
        return len(all_permitted) == len(set(power_names))

co_types = [('admin_co', 'Administration'), 
            ('channel', 'Channel'), 
            ('employer', 'Employer')]

class Company(models.Model):
    group   = models.OneToOneField(Group, primary_key=True)
    co_type = models.CharField(max_length=10, choices=co_types)

    def __unicode__(self):
        return self.group.name + '(%s)'%self.co_type

    @classmethod
    def readonly_fields(cls):
        return ('uid', 'group', 'co_type')

    @classmethod
    def create(cls, name, co_type):
        try:
            this_group = Group.objects.create(name = name)
        except IntegrityError:
            this_group = Group.objects.get(name = name)
        this_co = Company(group = this_group, co_type = co_type )
        this_co.save()
        return this_co

    @classmethod
    def get(cls, name):
        """
        find the company given the name

        since the string representation of the company (see __unicode__ method) includes the type,
        we much match with the group name, then find the company relative to the group we found
        """
        try:
            this_group = Group.objects.get(name = name)
            this_co = this_group.company
            return this_co
        except ObjectDoesNotExist:
            return None

class Power(models.Model):
    name = models.CharField(max_length=48)

    def __unicode__(self):
        return self.name

    @classmethod
    def get(cls, name):
        return Power.objects.get(name = name)

    @classmethod
    def get_list(cls, names):
        return [Power.objects.get(name = name) for name in names]

class AppRole(models.Model):
    appuser = models.ForeignKey(AppUser)
    company = models.ForeignKey(Company)
    powers = models.ManyToManyField(Power)
    # https://docs.djangoproject.com/en/1.8/topics/db/examples/many_to_many/

    def __unicode__(self):
        return "%s <== (%s) ==> %s" % (self.appuser, sorted(self.power_names), self.company)

    @classmethod
    def get(cls, appuser, company):
        try:
            role = AppRole.objects.get(appuser=appuser, company=company)
        except ObjectDoesNotExist:
            role = None
        return role

    @classmethod
    def create(cls, appuser, company):
        new_role, created = AppRole.objects.get_or_create(appuser = appuser, company = company)
        new_role.save()
        return new_role

    @property
    def power_names(self):
        return [pwr.name for pwr in self.powers.all()]

class AuthObject(object):
    pass
