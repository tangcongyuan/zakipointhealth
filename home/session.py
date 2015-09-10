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
from django.core.exceptions import ValidationError

from cee1.settings import VERSION_STAMP
import logging
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('zakipoint')
logger.setLevel(logging.DEBUG)

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

def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
                                            
class AppUser(User):
    """
    Proxy for User, because we want to add some methods
    Reference: https://docs.djangoproject.com/en/1.6/topics/db/models/#proxy-models
    """
    class Meta:
        proxy = True

    def __unicode__(self):
        return "%s %s" % (self.username,
                          str([grp.name for grp in self.groups.all()]),
        )

    @classmethod
    def new(cls, email, passwd=None, superuser=False, group=None):
        new_user, created = User.objects.get_or_create(username=email, email=email)
        if created and passwd:
            new_user.set_password(passwd)
            logger.info('U/P %s/%s', email, passwd)
        if passwd:
            new_user.is_staff = True
            new_user.is_superuser = superuser
        new_user.save()
        if group:
            new_user.groups.add(group)
        return new_user

    @classmethod
    def get_by_email(cls, email):
        """ return user by email address """

        u = cls.objects.get(email = email)
        if u:
            logger.debug('Found AppUser %s' % email)
            return u
        else:
            logger.debug('Could not find AppUser %s' % email)
            return None

    @classmethod
    def get_by_username(cls, username):
        """ find entity by username
        en-passant, validates that username is an email address
        """

        is_email = validateEmail(username)
        if is_email:
            return cls.objects.get(username = username)
        else:
            # TODO - maybe this should be an assert and we can raise an exception. maybe only in dev.
            logger.error('Username %s is not a valid email address' % username)
            return None
                                                                                        
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

                # put AppUser in the session
                request.session['app_user'] = app_user.pk

                # get the entity for this user
                user_entity = AppUser.get_by_username(email)
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
                {'errmsg': 'Email and/or Password not found - TODO: we will redisplay form!'}, context_instance=RequestContext(request) )
