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

from models import *

#
# Session Variables:
#
#    app_user - key of app_user entity
#    user_entity - key of user entity (django)
#    username - username of session user (email actually, 'cause thats how we roll)
#
#    co_entity - key of whatever co, for example, admin company, the user is affiiated with
#

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
                try:
                    user_co_domain  = email[email.index('@')+1:]
                    logger.debug('user_co_domain %s', user_co_domain)
                    user_co = user_co_domain[:user_co_domain.index('.com')]
                    logger.debug('user_co %s', user_co)
                    if user_co == 'hsirx':
                        channel_logo = "static/images/hsirx_logo.png"
                        company_logo = "static/dimages/cedar-rapids-logo.png"
                    elif user_co == 'aphys':
                        channel_logo = "static/images/affiliated-physicians-logo.jpg"
                except:
                    user_co = 'zph'
                    channel_logo = 'static/images/logo-blue-transparent.png'

                request.session['user_co'] = user_co
                request.session['channel_logo'] = channel_logo
                request.session['company_logo'] = company_logo
                logger.debug('user_co %s, channel_logo %s, company_logo %s', user_co, channel_logo, company_logo)

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

