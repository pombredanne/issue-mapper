import uuid
import random

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import simplejson
from django.template import Library
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader, Library, Node, VariableDoesNotExist
from django.template.context import RequestContext
from django.utils.safestring import mark_safe
from django.template import (
    loader, Context, resolve_variable, Library, Node, TemplateSyntaxError,
    Variable, VariableDoesNotExist
)
from django.utils import timezone
from django.db.models import Model

from ..middleware import get_current_request

from admin_steroids import utils

from .. import models

c = models.c

register = Library()

@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return simplejson.dumps(object)

@register.filter('klass')
def klass(o):
    return o.__class__.__name__

@register.filter
def noplus(s):
    return (s or '').replace('+', ' ')

@register.filter
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))

# http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
@register.filter
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = timezone.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " second"+('' if second_diff == 1 else 's')+" ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minute"+('' if second_diff / 60 == 1 else 's')+" ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hour"+('' if second_diff / 3600 == 1 else 's')+" ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " day"+('' if day_diff == 1 else 's')+" ago"
    if day_diff < 31:
        return str(day_diff/7) + " week"+('' if day_diff/7 == 1 else 's')+" ago"
    if day_diff < 365:
        return str(day_diff/30) + " month"+('' if day_diff/30 == 1 else 's')+" ago"
    return str(day_diff/365) + " year"+('' if day_diff/365 == 1 else 's')+" ago"

@register.filter
def cutoff(value, length):
    length = int(length)
    value = unicode(value)
    if len(value) > length:
        value = value[:length-3] + '...'
    return value

@register.simple_tag
def random_link():
    q = models.Person.objects.get_real_active().order_by('?')
    if q.count():
        r = q[0]
        return '<a href="%s">%s</a>' % (r.get_absolute_url(), r.display_name)
    else:
        return '<a href="/">the homepage</a>'

@register.simple_tag(name='plurals')
def plurals(q):
    if isinstance(q, int):
        if q == 1:
            return ''
        return 's'
    elif isinstance(q, (tuple, list, basestring)):
        if len(q) == 1:
            return ''
        return 's'
    elif hasattr(q, 'count') and callable(q.count) and q.count() == 1:
        return ''
    return 's'

@register.simple_tag
def comment_form(parent=None, show=True):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/comment-form.html', dict(
        parent=parent,
        show=show,
        object_type=type(parent).__name__.lower(),
        uuid=str(uuid.uuid4()).replace('-', ''),
    ), context_instance=RequestContext(request))

@register.simple_tag
def inline_motion_button(object, attribute, up_icon, down_icon=None, new_value=None):
    request = get_current_request()
    if not request.user.is_authenticated():
        return ''
    object_type = type(object).__name__.lower()
    try:
        motion = models.Motion.objects.get(**{
            object_type:object,
            'pending':True,
            'attribute':attribute,
            'new_value':new_value,
        })
    except models.Motion.DoesNotExist:
        motion = None
    vote = None
    if motion:
        try:
            vote = models.MotionVote.objects.get(
                motion=motion,
                voter__user=request.user,
            )
        except models.Motion.DoesNotExist:
            pass
    print 'motion:',motion
    return loader.render_to_string('issue_mapper/inline-motion-button.html', dict(
        up_vote_url=reverse('motion_ajax', args=(object_type, object.slug, attribute, c.UPVOTE_NAME)),
        down_vote_url=reverse('motion_ajax', args=(object_type, object.slug, attribute, c.DOWNVOTE_NAME)),
        object=object,
        object_type=object_type,
        object_id=object.slug,
        attribute=attribute,
        new_value=new_value or '',
        motion=motion,
        up_icon=up_icon,
        down_icon=down_icon,
        vote=vote,
    ), context_instance=RequestContext(request))
    
@register.simple_tag
def inline_form_field(field):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/inline-form-field.html', dict(
        field=field,
    ), context_instance=RequestContext(request))

@register.simple_tag
def inline_voter(object, up_title='', down_title=''):
    request = get_current_request()
    if isinstance(object, models.URL) and object.context:
        try:
            object = models.URLContext.objects.get(
                url=object,
                context=object.context)
        except models.URLContext.DoesNotExist:
            pass
    return loader.render_to_string('issue_mapper/inline-voter.html', dict(
        object=object,
        up_title=up_title,
        down_title=down_title,
    ), context_instance=RequestContext(request))

@register.simple_tag
def person_photo(person, max_width=75, max_height=100):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/person-photo.html', dict(
        person=person,
        max_width=max_width,
        max_height=max_height,
    ), context_instance=RequestContext(request))

@register.simple_tag
def person_summary(person):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/person-summary.html', dict(
        person=person,
    ), context_instance=RequestContext(request))

@register.simple_tag
def election_summary(election):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/election-summary.html', dict(
        election=election,
    ), context_instance=RequestContext(request))

@register.simple_tag
def issue_summary(issue, person=None):
    from ..forms import IssueResponseForm
    from ..models import Person
    request = get_current_request()
    creator = None
    if request.user.is_authenticated():
        try:
            creator = Person.objects.get(user=request.user)
        except Person.DoesNotExist:
            pass
    form = IssueResponseForm(issue=issue, person=person, creator=creator)
    return loader.render_to_string('issue_mapper/issue-summary.html', dict(
        issue=issue,
        person=person,
        form=form,
    ), context_instance=RequestContext(request))

@register.simple_tag
def position_sparkline(issue, person):
    position = None
    try:
        position = models.PositionAggregate.objects.get(
            issue=issue, person=person, date__isnull=True)
    except models.PositionAggregate.DoesNotExist:
        pass
    request = get_current_request()
    return loader.render_to_string('issue_mapper/position-sparkline.html', dict(
        position=position,
    ), context_instance=RequestContext(request))

@register.simple_tag
def pagination(page):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/pagination-links.html', dict(
        page=page,
    ), context_instance=RequestContext(request))
    
@register.simple_tag
def add(*nums):
    return sum(nums)

@register.simple_tag
def show_top(type, count):
    request = get_current_request()
    model = dict(
        issue=models.Issue,
        person=models.Person,
        link=models.Link,
    )[type]
    q = model.objects.get_top()[:count]
    return loader.render_to_string('issue_mapper/show-top.html', dict(
        q=q,
        type=type,
    ), context_instance=RequestContext(request))
    
@register.simple_tag
def issue_links(links):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/issue-links.html', dict(
        links=links
    ), context_instance=RequestContext(request))

@register.simple_tag
def list_item(item, person_filter=None, full=False):
    request = get_current_request()
    noun = type(item).__name__.lower()
    return loader.render_to_string('issue_mapper/list-item-%s.html' % noun, dict(
        item=item,
        person_filter=person_filter,
        full=full,
    ), context_instance=RequestContext(request))

@register.simple_tag
def lookup_candidate(election, person, var_name):
    request = get_current_request()
    try:
        candidate = models.Candidate.objects.get(election=election, person=person)
        if var_name:
            setattr(request, var_name, candidate)
            return ''
        else:
            return candidate
    except models.Candidate.DoesNotExist:
        pass
    return ''
    
@register.simple_tag
def list_item_comment(item, show_replies=True):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/list-item-comment.html', dict(
        item=item,
        show_replies=show_replies,
    ), context_instance=RequestContext(request))
    
@register.simple_tag
def list_item_full(item, person_filter=None):
    return list_item(item, person_filter, full=True)

@register.simple_tag
def login_form(form=None):
    request = get_current_request()
    if not form:
        if request.method == "POST":
            form = settings.IM_LOGIN_FORM(data=request.POST)
        else:
            form = settings.IM_LOGIN_FORM(request)
    return loader.render_to_string('registration/login_form.html', dict(
        form=form,
        next=request.META.get('HTTP_REFERER', request.get_full_path()),
    ), context_instance=RequestContext(request))
    
@register.simple_tag
def registration_form(form=None):
    request = get_current_request()
    if not form:
        if request.method == "POST":
            form = settings.IM_REGISTRATION_FORM(data=request.POST)
        else:
            form = settings.IM_REGISTRATION_FORM()#request)
    return loader.render_to_string('registration/registration_form_form.html', dict(
        form=form
    ), context_instance=RequestContext(request))
    
@register.tag(name="switch")
def do_switch(parser, token):
    """
    http://djangosnippets.org/snippets/967/
    
    The ``{% switch %}`` tag compares a variable against one or more values in
    ``{% case %}`` tags, and outputs the contents of the matching block.  An
    optional ``{% else %}`` tag sets off the default output if no matches
    could be found::

        {% switch result_count %}
            {% case 0 %}
                There are no search results.
            {% case 1 %}
                There is one search result.
            {% else %}
                Jackpot! Your search found {{ result_count }} results.
        {% endswitch %}

    Each ``{% case %}`` tag can take multiple values to compare the variable
    against::

        {% switch username %}
            {% case "Jim" "Bob" "Joe" %}
                Me old mate {{ username }}! How ya doin?
            {% else %}
                Hello {{ username }}
        {% endswitch %}
    """
    bits = token.contents.split()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError("'%s' tag requires one argument" % tag_name)
    variable = parser.compile_filter(bits[1])

    class BlockTagList(object):
        # This is a bit of a hack, as it embeds knowledge of the behaviour
        # of Parser.parse() relating to the "parse_until" argument.
        def __init__(self, *names):
            self.names = set(names)
        def __contains__(self, token_contents):
            name = token_contents.split()[0]
            return name in self.names

    # Skip over everything before the first {% case %} tag
    parser.parse(BlockTagList('case', 'endswitch'))

    cases = []
    token = parser.next_token()
    got_case = False
    got_else = False
    while token.contents != 'endswitch':
        nodelist = parser.parse(BlockTagList('case', 'else', 'endswitch'))
        
        if got_else:
            raise template.TemplateSyntaxError("'else' must be last tag in '%s'." % tag_name)

        contents = token.contents.split()
        token_name, token_args = contents[0], contents[1:]
        
        if token_name == 'case':
            tests = map(parser.compile_filter, token_args)
            case = (tests, nodelist)
            got_case = True
        else:
            # The {% else %} tag
            case = (None, nodelist)
            got_else = True
        cases.append(case)
        token = parser.next_token()

    if not got_case:
        raise template.TemplateSyntaxError("'%s' must have at least one 'case'." % tag_name)

    return SwitchNode(variable, cases)

class SwitchNode(Node):
    def __init__(self, variable, cases):
        self.variable = variable
        self.cases = cases

    def __repr__(self):
        return "<Switch node>"

    def __iter__(self):
        for tests, nodelist in self.cases:
            for node in nodelist:
                yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        for tests, nodelist in self.cases:
            nodes.extend(nodelist.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        try:
            value_missing = False
            value = self.variable.resolve(context, True)
        except VariableDoesNotExist:
            no_value = True
            value_missing = None
        
        for tests, nodelist in self.cases:
            if tests is None:
                return nodelist.render(context)
            elif not value_missing:
                for test in tests:
                    test_value = test.resolve(context, True)
                    if value == test_value:
                        return nodelist.render(context)
        else:
            return ""

@register.simple_tag
def admin_change_url(request, obj):
    if not (request.user.is_authenticated and request.user.is_active and (request.user.is_staff or request.user.is_superuser)):
        return ''
    if not isinstance(obj, Model):
        return ''
    return utils.get_admin_change_url(obj)

class AdminLinkNode(template.Node):
    def __init__(self, nodelist, obj, field_name):
        self.nodelist = nodelist
        self.obj = Variable(obj)
        self.field_name = field_name
    
    def render(self, context):
        obj = self.obj.resolve(context)
        
        request = context['request']
        url = admin_change_url(request, obj)
        output = self.nodelist.render(context)
        
        if url:
            if self.field_name:
                url = url + '#goto_' + self.field_name
            output = '<div class="inline-admin-link-container">%s<br class="clearboth"/><a class="inline-admin-link" href="%s" target="_blank">Edit</a></div>' % (output, url,)
        return output

def do_admin_link(parser, token):
    nodelist = parser.parse(('endadminlink',))
    parser.delete_first_token()
    
    tokens = token.contents.split()
    if len(tokens) == 2:
        _, obj = tokens
        field_name = None
    elif len(tokens) != 3:
        raise TemplateSyntaxError(
            u"'%r' tag requires exactly 2 arguments." % tokens[0])
    else:
        _, obj, field_name = tokens
        field_name = field_name[1:-1]
    
    return AdminLinkNode(
        nodelist,
        obj=obj,
        field_name=field_name)

register.tag('adminlink', do_admin_link)

@register.simple_tag
def url_tags(obj):
    request = get_current_request()
#    if hasattr(request, 'context') and isinstance(obj, models.URL):
#        try:
#            obj = models.URLContext.objects.get(
#                context=request.context, url=obj)
#        except models.URLContext.DoesNotExist:
#            pass
    return loader.render_to_string('issue_mapper/url-tags.html', dict(
        item=obj,
    ), context_instance=RequestContext(request))

@register.simple_tag
def rationale_triple_list(rationale, triples):
    request = get_current_request()
    return loader.render_to_string('issue_mapper/rationale-triple.html', dict(
        rationale=rationale,
        triples=triples,
    ), context_instance=RequestContext(request))

@register.simple_tag
def triple_edit_switch(rationale, triple, part):
    assert part in ('subject', 'predicate', 'object')
    request = get_current_request()
    part_id = getattr(triple, '%s_common_id' % part)
    part_text = getattr(triple, '%s_text' % part)
    part_raw_text = getattr(triple, '%s_text_raw' % part)
    is_triple = part in ('subject', 'object') and getattr(triple, '%s_triple' % part)
    return loader.render_to_string('issue_mapper/triple-edit-switch.html', dict(
        rationale=rationale,
        triple=triple,
        part=part,
        is_triple=is_triple,
        part_id=part_id,
        part_text=part_text,
        part_raw_text=part_raw_text,
    ), context_instance=RequestContext(request))

class SetVarNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        import uuid
        print 'self.var_name:',self.var_name
        context[self.var_name] = '_'+str(uuid.uuid4()).replace('-', '')
        return ''

@register.tag
def setuuid(parser, token):
    # This version uses a regular expression to parse tag contents.
    import re
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    var_name = m.groups()[0]
#    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
#        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return SetVarNode(var_name)
