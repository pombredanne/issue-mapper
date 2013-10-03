"""
Tracks the current request and user using threads-awareness.

Based on code from http://stackoverflow.com/a/1057418/247542.
"""
try:
    import thread
except ImportError:
    import dummy_thread as thread
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from django.conf import settings

state = {} # {thread_ident:user}
state_person = {} # {thread_ident:person}
state_request = {} # {thread_ident:request}

class UserContextMiddleware(object):
    """
    Stores request.user to a global state variable, keyed by the current
    thread ID, so that arbitrary code can access this data even if they're not
    explicitly passed a request object.
    """
    def process_request(self, request):
        """Enters transaction management"""
        enter_user_context(request)

    def process_exception(self, request, exception):
        """Rolls back the database and leaves transaction management"""
        leave_user_context()

    def process_response(self, request, response):
        """Commits and leaves transaction management."""
        from django.utils import timezone
        from datetime import timedelta
        import constants as c
        
        person = get_current_person()
        if person:
            response.set_cookie(
                c.COOKIE_NAME,
                person.uuid,
                expires=timezone.now()+timedelta(days=c.MAX_COOKIE_DAYS),
                domain=settings.SESSION_COOKIE_DOMAIN,
            )
        
        leave_user_context()
        return response

def get_person(request, raise_404=False, only_active=False):
    """
    Gets or optionally creates the person record associated with the
    current user.
    
    By default, a record will be created if none already exists.
    """
    from django.http import Http404
    from django.utils import timezone
    from models import Person
    import constants as c
    person = None
    try:
        if request.user.is_anonymous():
            raise Person.DoesNotExist
        person = Person.objects.get(user=request.user)
    except Person.DoesNotExist:
        person_uuid = request.COOKIES.get(c.COOKIE_NAME)
        if person_uuid:
            person, _ = Person.objects.get_or_create(uuid=person_uuid)
        elif not only_active:
            person = Person.objects.create()
        if person and not request.user.is_anonymous():
            person.user = request.user
            person.save()
    if not person and raise_404:
        raise Http404
    if person:
        person.last_seen = timezone.now()
        person.save()
    return person

def enter_user_context(request):
    """
    Associates a request and user with the current thread.
    """
    thread_ident = thread.get_ident()
    if thread_ident not in state:
        state[thread_ident] = request.user
        state_request[thread_ident] = request
        state_person[thread_ident] = get_person(request)

def leave_user_context(using=None):
    """
    Unassociates the request and user with the current thread.
    """
    thread_ident = thread.get_ident()
    if thread_ident in state:
        del state[thread_ident]
    if thread_ident in state_request:
        del state_request[thread_ident]
    if thread_ident in state_person:
        del state_person[thread_ident]

def get_current_user():
    thread_ident = thread.get_ident()
    if thread_ident in state:
        return state[thread_ident]

def get_current_person(raise_404=False, only_active=False):
    from django.http import Http404
    thread_ident = thread.get_ident()
    person = None
    if thread_ident in state_person:
        person = state_person[thread_ident]
        
    if only_active and person and (not person.user or not person.user.is_active):
        person = None
        
    if raise_404 and not person:
        raise Http404
        
    return person

def get_current_request():
    thread_ident = thread.get_ident()
    if thread_ident in state_request:
        return state_request.get(thread_ident, None)
