# REF: https://docs.djangoproject.com/en/1.6/topics/auth/default/
from django.db import models

# Create your models here.
from django.contrib.auth.models import User, Group, Permission
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

class AuthObject(object):
    @classmethod
    def find(cls, **kwargs):
        auth_obj = cls.objects.get(**kwargs)
        if auth_obj:
            # logger.debug('Found %s: %s' % (cls.__name__, vars(auth_obj)))
            return auth_obj
        else:
            logger.debug('Could not find %s(%s)' % (cls.__name__, kwargs))
            return None

co_types = [('admin_co', 'Administration'), 
            ('channel', 'Channel'), 
            ('employer', 'Employer')]

def _appuser_unicode(self):
    return "%s %s" % (vars(self),
                      str([grp.name for grp in self.groups.all()]))

class AppUser(User, AuthObject):
    """
    Proxy for User, because we want to add some methods
    Reference: https://docs.djangoproject.com/en/1.6/topics/db/models/#proxy-models
    """
    class Meta:
        proxy = True

    @classmethod
    def get_or_create(cls, email, password, **kwargs):
        try:
            this_user = User.objects.create_user(username=email, email=email, password=password)
            created = True
        except IntegrityError:
            this_user = User.objects.get(username = email)
            created = False
        is_dirty = False
        # ref http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object
        this_user.__unicode__ = types.MethodType( _appuser_unicode, this_user )

        for kw  in kwargs.keys():
            if kw == 'group':
                this_user.groups.add(group)
            elif  kw != 'password':
                setattr(this_user, kw, kwargs[kw])
                logger.info('U.%s = %s', email, kw, kwargs[kw])
                is_dirty = True
        if is_dirty:
            this_user.save()
        return this_user, created

class Company(models.Model):
    group   = models.OneToOneField(Group, primary_key=True)
    co_type = models.CharField(max_length=10, choices=co_types)

#    def __init__(self, name, co_type):
#        pdb.set_trace()
#        try:
#            this_group = Group.objects.create(name = name)
#            self.group_id = this_group.id
#        except IntegrityError:
#            old_group = Group.objects.get(name = name)
#            if hasattr(old_group, 'company'):
#                old_group.company.delete()
#            self.group = old_group
#        self.co_type = co_type
        
    def __unicode__(self):
        return self.group.name + '(%s)'%self.co_type

    @classmethod
    def readonly_fields(cls):
        return ('uid', 'group', 'co_type')

    @classmethod
    def create(cls, name, co_type):
        this_group = Group.objects.create(name = name)
        this_co = Company(group = this_group, co_type = co_type )
        this_co.save()
        return this_co
    @classmethod
    def get(cls, name):
        this_co = Company.objects.all().filter(group__name=name).get()
        this_group = Group.objects.get(name = name)
        this_co = this_group.company
        return this_co
