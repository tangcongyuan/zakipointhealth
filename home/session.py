import base64, uuid, types, pdb
from functools import wraps
from django.db import models, IntegrityError
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.utils.decorators import available_attrs
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
#    username - username of session user (email actually, 'cause thats how we roll)
#
#    co_entity - key of whatever co, for example, admin company, the user is affiiated with
#

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

def signout(request):
    if 'username' in request.session:
        uname = request.session['username']
        logger.info('%s signed out' % uname)

    logout(request)  # logout works whether someone is signed in or not. session is wiped.
    return render_to_response('sign-in.html', {}, context_instance=RequestContext(request) )

def sign_in_form(request):
    """ this handles the sign in parameters, authenticates the user, and sets up the session

    TODO: properly redisplay the form with appropriate error messages if a problem.

    """

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if not email and password:
            logging.warning('sign_in_form missing email and/or password')
            return redirect('/signin')

        try:
            validate_email(email)
            username = email.split('@')[0]
        except ValidationError:
            username = email

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                logger.info('%s authenticated and signed in', username)

                # find the AppUser give the user.
                # TODO: make this a model method
                try:
                    app_user = AppUser.objects.get(user__username = username)
                except Exception, e:
                    # oh bother what fresh hell is this?
                    logger.error('Exception %s getting app_user %s' % (e, email))
                    app_user = None
                if not app_user:
                    logger.error('No app_user found for %s, problems will abound' % email)
                    raise SystemError('No AppUser found for %s' % email)

                # *** Set up the session
                login(request, user)
                request.session['username'] = username

                # put AppUser in the session
                request.session['app_user'] = app_user.pk

                return redirect('/choose-co')

        else:
            logger.warning('Invalid Signin %s' % email)
            return render_to_response('error.html',
                {'errmsg': 'Email and/or Password not found, redirecting...'}, context_instance=RequestContext(request) )

def choose_co(request):
    if 'username' in request.session:
        username = request.session['username']
        try:
            appuser = AppUser.objects.get(user__username = username)
        except Exception, e:
            logger.error('Exception %s getting appuser (%s)' % (e, username))
            appuser = None

        all_roles = [q for q in AppRole.objects.all().filter(appuser = appuser)]
        cos = [role.company.group.name for role in all_roles]

        logger.info('Companies %s', cos)
        if len(cos) == 1:
            set_chosen_co(request, cos[0])
            return redirect('/home')

        return render_to_response('choose-co.html', {'cos': cos}, context_instance=RequestContext(request) )
    else:
        return redirect('/signin')

def set_chosen_co(request, chosen_co_name):
    # zaki logo
    channel_logo = "/static/images/logo-blue-transparent.png"
    company_logo = "/static/dimages/tilde.png"
    if chosen_co_name == 'HSI-Rx':
        channel_logo = "/static/images/hsirx_logo.png"
        company_logo = "/static/dimages/cedar-rapids-logo.png"
    elif chosen_co_name == 'Affiliated Physicians':
        channel_logo = "/static/images/affiliated-physicians-logo.jpg"
        company_logo = "/static/dimages/cedar-rapids-logo.png"
    else:
        user_co = 'zph'
        channel_logo = '/static/images/logo-blue-transparent.png'

    request.session['user_co'] = chosen_co_name
    request.session['channel_logo'] = channel_logo
    request.session['company_logo'] = company_logo
    logger.debug('user_co %s, channel_logo %s, company_logo %s', chosen_co_name, channel_logo, company_logo)
    

def choose_co_form(request):
    """ this sets up the rest of the session

    """

    if request.method == 'POST':
        chosen_co_name = request.POST['CompanySelectList']
        logger.info('User chose %s', chosen_co_name)
        set_chosen_co(request, chosen_co_name)

        return redirect('/home')

def request_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the request object and returns True if the request passes.

    Source: http://stackoverflow.com/a/24423890
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # urlparse chokes on lazy objects in Python 3, force to str
            resolved_login_url = force_str(resolve_url(login_url or settings.LOGIN_URL))
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

def capability_required(request, power):
    logger.info('capability_required user %s, co %s, cap %s', 
                request.user,
                request.session['user_co'],
                power,
                )
    appuser = request.user.appuser
    company = Company.get(request.session['user_co'])
    answer = appuser.can_access(company, [power])
    logger.info('capability_required answer %s', answer)
    return answer
