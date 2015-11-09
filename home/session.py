import base64, uuid, types, pdb
from django.db import models, IntegrityError
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from zphalfa.settings import VERSION_STAMP
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

companies = ['hsirx', 'affiliatedphysicians']


#
# Session Variables:
#
#    app_user - key of app_user entity
#    user_entity - key of user entity (django)
#    username - username of session user (email actually, 'cause thats how we roll)
#
#    co_entity - key of whatever co, for example, admin company, the user is affiiated with
#
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
            logger.debug('Found %s: %s' % (cls.__name__, vars(auth_obj)))
            return auth_obj
        else:
            logger.debug('Could not find %s(%s)' % (cls.__name__, kwargs))
            return None

co_types = ['admin_co', 'channel', 'employer']

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
        pdb.set_trace()
        this_co = Company.objects.all().filter(group__name=name).get()
        this_group = Group.objects.get(name = name)
        this_co = this_group.company
        return this_co

#class AppGroup(Group, AuthObject):
#    """
#    Proxy for Group, because we want to add some methods
#    """
#    class Meta:
#        proxy = True
#
#    def __unicode__(self):
#        return "%s (%s)" % (self.name, self.co_type)
#
#    @property
#    def co_type(self):
#        return self.company.co_type

def urlsafe_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')

def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

class UserRole(models.Model):
    name = models.CharField(max_length=48)

    def __unicode__(self):
        return self.name + str(self.get_capability_names())

    def get_capabilities(self):
        return [cap for cap in self.allowed.all()]
    capabilities = property(get_capabilities)

    def get_capability_names(self):
        return [cap.name for cap in self.allowed.all()]
    capability_names = property(get_capability_names)

    @classmethod
    def create(cls, name, capabilities):
        new_role, created = UserRole.objects.get_or_create(name=name)
        new_role.save()
        for capability in capabilities:
            new_c, created = Capability.objects.get_or_create(name=capability)
            new_c.save()
            new_c.roles.add(new_role)
        return new_role

class Capability(models.Model):
    name = models.CharField(max_length=48)
    roles = models.ManyToManyField(UserRole, related_name="allowed")
    def __unicode__(self):
        return self.name

def signin(request):
    if 'username' in request.session:
        uname = request.session['username']
        logger.info('%s signing in again?' % uname)
        return redirect('/home')
    return render_to_response('sign-in.html', {}, context_instance=RequestContext(request) )

def splash(request):
    # check to see if we are in a session
    if 'username' in request.session:
        logger.info('Redirect to home')
        return redirect('/home')
    else:
        logger.info('Splashing')
        return render_to_response('splash.html', {}, context_instance=RequestContext(request) )

@login_required
def signout(request):

    if 'username' in request.session:
        uname = request.session['username']
        logger.info('%s signed out' % uname)

    logout(request)  # logut works whether someone is signed in or not. session wiped.
    # TODO - head over to sign in now, maybe we should have a better redirect page
    return render_to_response('sign-in.html', {}, context_instance=RequestContext(request) )


def sign_in_form(request):
    """ this handles the sigin parameters, authenticates the user, and sets up the session

    TODO: properly redisplay the form with appropriate error messages if a problem.

    """

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if not email and password:
            logging.warning('sign_in_form missing email and/or password')
            return redirect('/signin')
        user = authenticate(username=email, password=password)
        if user:
            if user.is_active:
                logger.info('%s authenticated and signed in', email)

                # find the AppUser give the user. I know. Weird.
                # TODO: make this a model method
                try:
                    app_user = AppUser.objects.get(username=email)
                except Exception, e:
                    # oh bother what fresh hell is this?
                    logger.error('Exception %s getting app_user %s' % (e, email))
                    app_user = None
                if not app_user:
                    logger.error('No app_user found for %s, problems will abound' % email)
                    raise SystemError('No AppUser found for %s' % email)

                # *** Set up the session
                request.session['username'] = email

                # zaki logo
                channel_logo = "static/images/logo-blue-transparent.png"
                company_logo = "static/dimages/tilde.png"
#                company_logo = "static/dimages/0916_home_1.png"
                try:
                    user_co_domain  = email[email.index('@')+1:]
                    user_co = co_domain[:co_domain.index('.com')]
                    if co == 'hsirx':
                        channel_logo = "static/images/hsirx_logo.png"
                        company_logo = "static/dimages/cedar-rapids-logo.png"
                    elif co == 'aphys':
                        channel_logo = "static/images/affiliated-physicians-logo.jpg"
                except:
                    user_co = 'zph'
                request.session['user_co'] = user_co
                request.session['channel_logo'] = channel_logo
                request.session['company_logo'] = company_logo

                # put AppUser in the session
                request.session['app_user'] = app_user.pk

                # get the entity for this user
                user_entity = AppUser.find( username = email)
                if user_entity:
                    logger.debug('Saving User Entity in the session for %s' % email)
                    request.session['user_entity'] = user_entity.pk
                else:
                    logger.error('Could not find User Entity for %s' % email)
                    request.session['user_entity'] = None
                    # TODO: should we fail the signin? prob not, but no a customer of any kind so send to admin page? check is_admin, all that

                login(request, user)
                return redirect('/home')
            else:
                logger.warning('%s account is deactivated' % email)
                # TODO Return a 'disabled account' error message with an error page
                return render_to_response('error.html',
                    {'errmsg': 'Your account has been deactivated'}, context_instance=RequestContext(request) )
        else:
            logger.warning('Invalid Signin %s' % email)
            return render_to_response('error.html',
                {'errmsg': 'Email and/or Password not found, redirecting...'}, context_instance=RequestContext(request) )

