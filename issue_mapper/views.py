import csv
import uuid
import urlparse
import urllib
import time
import random

import settings as _settings

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import F, Q, Count
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string, get_template
from django.template.context import RequestContext, Context
from django.views.generic.edit import FormView
from django.views.generic import ListView, TemplateView
from django.utils import timezone
from django.core.urlresolvers import resolve
from django.views.decorators.cache import never_cache
from django import forms
import django
from django.utils.feedgenerator import Rss201rev2Feed

from jsonview.decorators import json_view

import forms
import models
import middleware
import constants as c

def add_vars(request):
    #if request.user.is_authenticated():
    current_person = middleware.get_current_person()
    return dict(
        settings=settings,
        priviledges=models.Priviledge.get_current(),
        c=c,
        current_person=current_person,
    )

class BaseTemplateView(TemplateView):
    
    title = None
    
    @property
    def full_title(self):
        parts = []
        if self.title:
            parts.append(self.title)
        elif settings.IM_SUBTITLE:
            parts.append(settings.IM_SUBTITLE)
        if settings.IM_SHOW_TITLE and settings.IM_TITLE:
            parts.append(settings.IM_TITLE)
        return u' - '.join(parts)
    
    def get_context_data(self, *args, **kwargs):
        context = super(BaseTemplateView, self).get_context_data(*args, **kwargs)
        context['full_title'] = self.full_title
        return context

class BaseIssueView(object):
    
    @property
    def issue_type(self):
        return c.PEOPLE#TODO:remove
        person_filter = self.person_filter
        type = self.request.GET.get(
            'type',
            self.request.COOKIES.get(
                c.COOKIE_QUESTION_TYPE,
                c.UNANSWERED
            )
        )
        if type not in c.QUESTION_TYPES \
        or (person_filter and type in (c.PEOPLE, c.MATCHES)):
            return c.UNANSWERED
        return type
    
    @property
    def issue_type_choices(self):
        request = self.request#middleware.get_current_request()
        person_filter = self.person_filter
        issue_types = []
        if person_filter:
#            if type == c.PEOPLE:
#                type = c.UNANSWERED
            pass
        else:
            issue_types.append((
                c.PEOPLE, self.get_people_queryset()
            ))
#        if request.user.is_authenticated() and not person_filter:
#            issue_types.extend([
#                (c.MATCHES, self.get_matches_queryset()),
#            ])
        return issue_types
    
    @property
    def allow_switch(self):
        """
        Returns true if issue type can be auto-switched.
        Returns false otherwise.
        """
        return 'nst' not in self.request.GET
    
    @property
    def person_filter(self):
        person_slug = None
        if 'person_slug' in self.kwargs:
            person_slug = self.kwargs['person_slug']
        elif 'person' in self.request.GET:
            person_slug = self.request.GET.get('person')
        if person_slug:
            return models.Person.objects.get(slug=person_slug, real=True)
    
    @property
    def creator(self):
        person = middleware.get_current_person()
        return person
    
    @property
    def noun(self):
        if self.issue_type == c.PEOPLE:
            return 'person'
        elif self.issue_type == c.MATCHES:
            return 'match'
        return 'issue'
    
    @property
    def sort_options(self):
        if self.issue_type == c.MATCHES:
            return [('-value', 'Match Percent')]
        return []
    
    @property
    def sort_options_next(self):
        
        def toggle(v):
            if v.startswith('-'):
                return v[1:]
            return '-'+v
        
        def name(v):
            if v.startswith('-'):
                return v[1:]
            return v
        
        current_sort_dict = dict((name(s),s) for s in self.sort)
        next = []
        for other_sort_default,_ in self.sort_options:
            other_sort_key = name(other_sort_default)
            if other_sort_key in current_sort_dict:
                print other_sort_key, other_sort_default, current_sort_dict
                next.append((toggle(current_sort_dict[other_sort_key]), _))
            else:
                next.append((other_sort_default, _))
        return next
    
    @property
    def sort(self):
        sort_options = dict(
            (k[1:] if k.startswith('-') else k,v)
            for k,v in self.sort_options
        ).keys()
        print 'sort_options:',sort_options
        default_sort = self.sort_options[0][0] if self.sort_options else ''
        sort = self.request.GET.get('sort', default_sort).strip().split(',')
        _sort = []
        for _ in sort:
            el = _
            if _.startswith('-'):
                _ = _[1:]
            if _ in sort_options:
                _sort.append(el)
        return _sort
    
    @property
    def q(self):
        return self.request.GET.get(
            'q',
            self.request.COOKIES.get(
                c.COOKIE_KEYWORDS,
                ''
            )
        ).strip()
    
    @property
    def keywords(self):
        return c.LINK_REGEX.sub('', self.q)
        
    @property
    def links(self):
        return c.LINK_REGEX.findall(self.q)

    def get_queryset(self, person=True):
        q = models.Person.get_real()
        q = q.order_by('-top_weight', 'rand')
        return q
    
    def _filter_issues_by_links(self, q):
        if not q:
            return q
        links = self.links
        if links:
            link_q = None
            for link in links:
                _q = Q(links__url__url=link)
                if link_q is None:
                    link_q = _q
                else:
                    link_q |= _q
            q = q.filter(link_q)
        return q
    
    def _filter_persons_by_links(self, q):
        links = self.links
        if links:
            link_q = None
            for link in links:
                _q = Q(positions__issue__links__url__url=link)
                if link_q is None:
                    link_q = _q
                else:
                    link_q |= _q
            q = q.filter(link_q)
        return q
    
    def get_unpositioned_queryset(self):
        request = self.request
        keywords = self.keywords
        person_filter = self.person_filter
        q = models.Issue.objects.get_unpositioned_by(
            request.user, person=person_filter)
        if keywords:
            q = q.filter(issue__icontains=keywords)
        q = self._filter_issues_by_links(q)
        q = q.annotate(null_count=Count('positions__polarity'))
        q = q.order_by('-null_count')
        q = q.distinct()
        return q
        
    def get_positioned_queryset(self):
        request = self.request
        keywords = self.keywords
        person_filter = self.person_filter
        q = models.Issue.objects.get_positioned_by(
            request.user, person=person_filter)
        #print 'q0:',len(q)
        if not q:
            return q
        if keywords:
            q = q.filter(issue__icontains=keywords)
        #print 'q1:',len(q)
        q = self._filter_issues_by_links(q)
        #print 'q2:',len(q)
        q = q.distinct()
        return q
        
    def get_updated_queryset(self):
        request = self.request
        keywords = self.keywords
        person_filter = self.person_filter
        q = models.Issue.objects.get_positioned_by_with_updates(
            request.user, person=person_filter)
        if keywords:
            q = q.filter(issue__icontains=keywords)
        q = self._filter_issues_by_links(q)
        q = q.distinct()
        return q

    def get_people_queryset(self):
        request = self.request
        keywords = self.keywords
        q = models.Person.search_objects.all()
        if keywords:
            q = q.search(keywords)
        q = models.Person.objects.get_real(q)
        return q
    
    def get_matches_queryset(self):
        if not self.request.user.is_authenticated():
            return []
        creator = self.creator
        if not creator:
            return []
        keywords = self.keywords
        q = creator.matches_for.all()
        if keywords:
            q = q.filter(matchee__slug__icontains=keywords)
        return q
    
    @property
    def switch_to_type(self):
        return False#TODO:remove
        if not self.allow_switch:
            return
        person_filter = self.person_filter
        pending = [
            (c.UNANSWERED, self.get_unpositioned_queryset()),
        ]
#        print 'req:',self.request.get_full_path()
#        print 'person_filter:',person_filter
        if not person_filter:
            pending.extend([
                (c.PEOPLE, self.get_people_queryset())
            ])
        if self.request.user.is_authenticated():
            pending.extend([
                (c.ANSWERED, self.get_positioned_queryset()),
                (c.UPDATED, self.get_updated_queryset()),
                (c.MATCHES, self.get_matches_queryset()),
            ])
        has_results = [t for t,q in pending if q]
        if has_results and self.issue_type not in has_results:
            return has_results[0]

class MotionListView(ListView):

    template_name = "issue_mapper/motion-list.html" 
    
    paginate_by = 10
    
class SearchListView(ListView):

    template = 'issue_mapper/list.html'
    
    paginate_by = results_per_page = 10
    
    show_top_search_controls = True
    
    show_keyword_search = True
    
    @property
    def type(self):
        """
        Returns the model type being shown in the search results.
        Should be ISSUE, LINK or PERSON.
        """
        
    def get_context_data(self, *args, **kwargs):
        context = super(SearchListView, self).get_context_data(*args, **kwargs)
        context['show_search_results'] = True
        context['show_top_search_controls'] = self.show_top_search_controls
        context['show_keyword_search'] = self.show_keyword_search
        return context

#TODO:delete, deprecated?
class _IssueListView(BaseIssueView, ListView):
    
    template_name = "issue_mapper/issue-list.html" 
    
    paginate_by = 10
    
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(IssueListView, self).get_form_kwargs(*args, **kwargs)
        person = middleware.get_current_person()
        self.person = kwargs['person'] = person
        return kwargs
    
    def set_cookie(self, response):
        person = middleware.get_current_person()
        if person:
            person.last_seen = timezone.now()
            person.save()
            response.set_cookie(c.COOKIE_NAME, person.uuid)
        response.set_cookie(c.COOKIE_QUESTION_TYPE, self.issue_type)
        response.set_cookie(c.COOKIE_KEYWORDS, self.keywords)
    
    def get(self, *args, **kwargs):
        response = super(IssueListView, self).get(*args, **kwargs)
#        switch_to_type = self.switch_to_type
#        person_filter = self.person_filter
#        if switch_to_type:
#            print 'switching to:',switch_to_type
#            qs = dict(urlparse.parse_qsl(self.request.META['QUERY_STRING']))
#            qs['type'] = switch_to_type
#            qs['nst'] = '' # Stop further auto-switching.
#            if person_filter:
#                qs['q'] = ''
#            qs = urllib.urlencode(qs)
#            if person_filter:
#                return HttpResponseRedirect(reverse('person', args=(person_filter.slug,))+'?'+qs)
#            else:
#                return HttpResponseRedirect(reverse('issue_list')+'?'+qs)
        self.set_cookie(response)
        return response
    
    def get_context_data(self, *args, **kwargs):
        context = super(IssueListView, self).get_context_data(*args, **kwargs)
        request = self.request 
        type = self.issue_type
        print 'type:',type
        person_filter = self.person_filter
        issue_types = self.issue_type_choices
        print 'noun:',self.noun
        context['selected_issue_type'] = type
        context['issue_types'] = issue_types
        context['noun'] = self.noun
        context['DATETIME_FORMAT'] = settings.DATETIME_FORMAT
        context['IM_WAIT_DAYS_BEFORE_REANSWER'] = settings.IM_WAIT_DAYS_BEFORE_REANSWER
        context['q'] = self.q
        context['users_online_count'] = models.Person.objects.get_online().count()
        context['person_filter'] = person_filter
        context['creator'] = middleware.get_current_person()
        context['person'] = person_filter or context['creator']
        context['sort_options'] = self.sort_options_next
        return context

class _IssueView(BaseIssueView, FormView):
    
    #template_name = 'issue_mapper/issue.html'
    template_name = 'issue_mapper/list.html'
    
    form_class = forms.IssueResponseForm

    issue = None
    
    person = None
    
    form = None
    
    redirect = None
    
    @property
    def i(self):
        try:
            return int(self.request.GET.get('i', 0))
        except ValueError:
            pass
        except TypeError:
            pass
        return 0
    
    @property
    def issue(self):
        issue_id = self.kwargs['issue_id']
        print 'issue_id:',issue_id
        try:
            issue = models.Issue.objects.get(id=issue_id)
        except ValueError, e:
            issue = models.Issue.objects.get(slug=issue_id)
        return issue
    
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(IssueView, self).get_form_kwargs(*args, **kwargs)
#        issue_id = self.kwargs['issue_id']
#        print 'issue_id:',issue_id
#        try:
#            issue = models.Issue.objects.get(id=issue_id)
#        except ValueError, e:
#            issue = models.Issue.objects.get(slug=issue_id)
        issue = kwargs['issue'] = self.issue
        issue.last_view_datetime = timezone.now()
        issue.view_count += 1
        issue.save()
        kwargs['creator'] = middleware.get_current_person()
        
        person_slug = self.kwargs.get('person_slug')
        if person_slug:
            self.person = kwargs['person'] = models.Person.objects.get(slug=person_slug, real=True)
        else:
            self.person = kwargs['person'] = self.creator
            
        return kwargs
    
    @property
    def last(self):
        if not self.request.user.is_authenticated():
            return
        if 'last' in self.request.GET:
            try:
                return models.Position.objects.get(
                    id=self.request.GET['last'],
                    creator__user=self.request.user)
            except models.Position.DoesNotExist:
                pass
    
    def get_context_data(self, *args, **kwargs):
        context = super(IssueView, self).get_context_data(*args, **kwargs)
        
        pt = models.Priviledge.get_current()
        
        context['friendly_text'] = self.issue.friendly_text
        
        context['person'] = self.person
        context['creator'] = self.creator
        if self.person == self.creator:
            print 'can:',pt.can
            context['allow_answer'] = pt.can.answer_issue_for_themself
        else:
            context['allow_answer'] = pt.can.answer_issue_for_other
            context['friendly_text'] = self.issue.friendly_text_wrt(self.person)
        
        context['position'] = self.issue.get_last_position(self.person, self.creator)
        context['positionable'] = self.issue.positionable(self.request.user)
        context['IM_WAIT_DAYS_BEFORE_REANSWER'] = settings.IM_WAIT_DAYS_BEFORE_REANSWER
        context['positioned'] = self.issue.positioned(self.person, self.creator)
        context['choice_counts'] = self.issue.get_choice_counts()
        
        context['unread_links'] = self.issue.unread_links(self.person, self.creator)
        context['read_links'] = self.issue.read_links(self.person, self.creator)
        
        context['buttons_fixed_buttom'] = int(self.request.COOKIES.get(c.COOKIE_BUTTONS_FLOAT, 1))
        
        context['last'] = self.last
        
        return context
        
    def form_valid(self, form):
        self.form = form
        
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('django.contrib.auth.views.login')+'?next='+self.request.get_full_path())
        
        choice_id = self.request.REQUEST['submit']
        person = self.person
        creator = self.request.user.person
        person_filter = self.person_filter
        
        auto_next = False
        last = None
        i = self.i
        if choice_id == c.NEXT:
            i += 1
        
        if self.issue.active and choice_id not in (c.NEXT, c.SKIP):
            print '!'*80
            print 'choice_id:',choice_id
            print 'person:',person
            print 'creator:',creator
            assert choice_id in dict(c.POSITION_CHOICES)
            position, new_position = models.Position.create(
                issue=self.issue,
                polarity=choice_id,
                person=person,
                creator=creator)
            last = position.id
            if not new_position:
                position.created = timezone.now()
                position.save()
            auto_next = True
            choice_id = c.NEXT
            print 'position:',position
        
        redirect_url = None
        nst = False
        if choice_id in (c.NEXT, c.SKIP):
            
            if not auto_next:
                last_position = self.issue.get_last_position(self.person, self.creator)
                if last_position:
                    last_position.reaffirm()
                elif choice_id == c.SKIP:
                    position, _ = models.Position.create(
                        issue=self.issue,
                        polarity=None,
                        person=person,
                        creator=creator)
            
            next_issues = self.get_queryset(person=False)
            if next_issues and next_issues.count():
                print 'next_issues:',next_issues
                i = min(i, next_issues.count()-1)
                if next_issues[i] == self.issue:
                    i += 1
                if i >= next_issues.count():
                    if person_filter:
                        redirect_url = reverse('person', args=(person_filter.slug,))
                    else:
                        redirect_url = reverse('issue_list')
                else:
                    next_issue = next_issues[i]
                    print self.person
                    print self.creator
                    if self.person != self.creator:
                        redirect_url = reverse(
                            'issue_wrt_person',
                            args=(self.person.slug, next_issue.slug,))
                    else:
                        redirect_url = reverse('issue', args=(next_issue.slug,))
            elif person_filter:
                print 'redirecting to person index'
                redirect_url = reverse('person', args=(person_filter.slug,))
            else:
                nst = True
                redirect_url = reverse('issue_list')
            
        if redirect_url:
            qs = dict(urlparse.parse_qsl(self.request.META['QUERY_STRING']))
            if nst:
                qs['nst'] = '' # Stop further auto-switching.
            if last:
                qs['last'] = last
            if i:
                qs['i'] = i
            qs = urllib.urlencode(qs)
            return HttpResponseRedirect(redirect_url+'?'+qs)
        
        return super(IssueView, self).form_valid(form)
    
    def form_invalid(self, form):
        self.form = form
        return super(IssueView, self).form_invalid(form)
        
    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
        
    def set_cookie(self, response):
        if self.person:
            self.person.last_seen = timezone.now()
            self.person.save()
            response.set_cookie(c.COOKIE_NAME, self.person.uuid)
    
    def get(self, *args, **kwargs):
        if not self.issue.public:
            raise Http404
        response = super(IssueView, self).get(*args, **kwargs)
        self.set_cookie(response)
        return response
    
    def post(self, *args, **kwargs):
        response = super(IssueView, self).post(*args, **kwargs)
        self.set_cookie(response)
        return response
#        if self.form and self.form.errors:
#            return response
#        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

def issue_export_csv(request, argument_id):
    todo
    argument = get_object_or_404(models.Issue, id=argument_id, enabled=True)
    person = middleware.get_current_person()
    responses = models.NodeResponse.objects.filter(
        responder=person, node__argument=argument).order_by('created')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="argument-%s.csv"' % argument.slug

    writer = csv.writer(response)
    writer.writerow(['Issue', 'Position'])
    for _ in responses:
        writer.writerow([_.original_statement, _.response])
    
    return response

@never_cache
def process_vote(request, object_id, object_type, vote_type):
    """
    Records a user's up or down vote on a record.
    """
#    print '!'*80
#    print 'object_id:',object_id
#    print 'object_type:',object_type
#    print 'vote_type:',vote_type
    response_type = request.GET.get('rt', c.HTML)
    object_cls = {
        c.LINK:models.Link,
        c.COMMENT:models.Comment,
        #c.URL:models.URL,
        c.URLCONTEXT:models.URLContext,
    }.get(object_type)
    if not object_cls:
        raise Http404
    object = get_object_or_404(object_cls, id=object_id)
    person = middleware.get_current_person()
    if not person.user or not person.user.is_active:
        raise Http404
    if vote_type not in c.VOTE_NAME_TO_VALUE:
        print 'invalid vote type:',vote_type
        raise Http404
    if not settings.IM_ALLOW_SELF_VOTE and person == object.creator:
        # A person may not vote on their own link.
        print 'cannot vote on your own links'
        raise Http404
    vote = c.VOTE_NAME_TO_VALUE[vote_type]
    #print 'vote:',vote
#    print 'object_cls:',object_cls
#    print 'object:',object
    
    if object_cls is models.Link:
        object_vote, _ = models.LinkVote.objects.get_or_create(
            link=object,
            voter=person,
            defaults=dict(vote=vote))
        object_vote.vote = vote
        object_vote.save()
        object = object_vote.link
#    elif object_cls is models.URL:
#        object_vote, _ = models.URLVote.objects.get_or_create(
#            url=object,
#            voter=person,
#            defaults=dict(vote=vote))
#        object_vote.vote = vote
#        object_vote.save()
#        object = object_vote.url
    elif object_cls is models.URLContext:
        object_vote, _ = models.URLContextVote.objects.get_or_create(
            url_context=object,
            voter=person,
            defaults=dict(vote=vote))
        object_vote.vote = vote
        object_vote.save()
        object = object_vote.url_context
    elif object_cls is models.Comment:
        object_vote, _ = models.CommentVote.objects.get_or_create(
            comment=object,
            voter=person,
            defaults=dict(vote=vote))
        object_vote.vote = vote
        object_vote.save()
        object = object_vote.comment
    
    if response_type == c.JSON:
        response = HttpResponse(content='1', content_type='application/json')
        return response
    else:
        return render_to_response(
            'issue_mapper/inline-voter.html',
            dict(object=object),
            context_instance=RequestContext(request))

def flag(request, object_type, object_id, confirmed=False):
    object_types = dict(
        issue=models.Issue,
        link=models.Link,
        person=models.Person,
        #comment=models.Comment,
    )
    if not request.user.is_authenticated():
        raise Htt404
    if object_type not in object_types:
        raise Http404
    if confirmed:
        person = middleware.get_current_person(raise_404=True, only_active=True)
        obj = get_object_or_404(object_types[object_type], id=object_id)
        comment = request.GET.get('comment', '').strip()[:700]
        if not comment:
            raise Http404
        flag, _ = models.Flag.objects.get_or_create(**{
            object_type:obj,
            'flagger':person,
            'defaults':dict(comment=comment),
        })
        response = HttpResponse(content=flag.id, content_type='application/json')
        return response
    else:
        return HttpResponse(content=render_to_string(
            'issue_mapper/popup-flag.html',
            dict(
                uuid='_%s'%str(uuid.uuid4()).replace('-',''),
                object_type=object_type,
                object_id=object_id,
            ),
            context_instance=RequestContext(request)).strip(),
            content_type='text/html')

def popup_ajax(request, name, type=None, id=None):
    """
    Renders generic popup html for loading via AJAX.
    """
    obj = None
    if type and id:
        if type == c.LINK:
            obj = models.Link.objects.get(id=int(id))
    return HttpResponse(
        content=render_to_string(
            'issue_mapper/popup-%s.html' % name,
            dict(
                uuid='_%s'%str(uuid.uuid4()).replace('-',''),
                obj=obj,
            ),
            context_instance=RequestContext(request)
        ).strip(),
        content_type='text/html')

def login_register(request):
    return HttpResponse(content=render_to_string(
        'issue_mapper/popup-login-register.html',
        dict(
            uuid='_%s'%str(uuid.uuid4()).replace('-',''),
        ),
        context_instance=RequestContext(request)).strip(),
        content_type='text/html')

def issue_links_older_ajax(request, issue_id):
    issue = get_object_or_404(models.Issue, id=issue_id)
    creator = middleware.get_current_person(raise_404=True, only_active=True)
    links = issue.read_links(person=None, creator=creator)
    print 'links:',links
    return render_to_response(
        'issue_mapper/issue-links.html',
        dict(links=links),
        context_instance=RequestContext(request))

class BaseSubmitView(FormView):
    
    #template_name = 'issue_mapper/issue-submit.html'
    
    #form_class = forms.SubmitForm
    
    @property
    def noun(self):
        return self.kwargs['noun']
    
    def get_context_data(self, *args, **kwargs):
        context = super(BaseSubmitView, self).get_context_data(*args, **kwargs)
        context['noun'] = self.noun
        return context
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def get(self, *args, **kwargs):
        
        pt = models.Priviledge.get_current()
        noun = self.noun
        if noun == c.ISSUE:
            if not pt.can.submit_issue:
                raise Http404
        elif noun == c.PERSON:
            if not pt.can.submit_person:
                raise Http404
        
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('%s_list' % self.noun))
        
        if self.kwargs.get('search'):
            return self.search_response()
        
        response = super(BaseSubmitView, self).get(*args, **kwargs)
        return response

class SubmitIssueView(BaseSubmitView):
    """
    Ajax issue search.
    """
    
    template_name = 'issue_mapper/issue-submit.html'
    
    form_class = forms.SubmitIssueForm
    
    def form_valid(self, form):
        Q = models.Q
        creator = middleware.get_current_person(raise_404=True, only_active=True)
        pt = models.Priviledge.get_current()
        slug = models.issue_to_slug(form.cleaned_data['issue'])
        q = models.Issue.objects.filter(slug=slug)
        if q.count():
            issue = q[0]
        else:
            issue, created = models.Issue.objects.get_or_create(
                issue=form.cleaned_data['issue'],
                defaults=dict(
                    creator=creator,
                    public=True,
                    active=False,
                    needs_review=True,
                ))
            if creator.total_karma > pt.many_approve_issue:
                issue.active = True
                issue.needs_review = False
            issue.save()
        return HttpResponseRedirect(reverse('issue', args=(issue.slug,)))
        
    def search_response(self):
        generic = self.kwargs.get('generic')
        show_no_results = bool(self.kwargs.get('show_no_results', ''))
        if generic:
            q = models.Issue.search_objects.search(self.request.GET['content'])
            q = models.Issue.objects.get_public(q)
        else:
            q = models.Issue.objects.all()
            slug = models.issue_to_slug(self.request.GET.get('issue', ''))
            if slug:
                q = q.filter(slug__icontains=slug)
        q = q[:10]
        show = q or (not q and show_no_results)
        return render_to_response(
            'issue_mapper/issue-submit-search.html',
            dict(
                q=q,
                show=show,
            ),
            context_instance=RequestContext(self.request))

class SubmitPersonView(BaseSubmitView):
    """
    Ajax person search.
    """
    
    template_name = 'issue_mapper/person-submit.html'
    
    form_class = forms.SubmitPersonForm

    def form_valid(self, form):
        creator = middleware.get_current_person(raise_404=True, only_active=True)
        pt = models.Priviledge.get_current()
        q = models.Person.objects.filter(
            first_name__iexact=form.cleaned_data['first_name'].strip().title(),
            last_name__iexact=form.cleaned_data['last_name'].strip().title(),
            real=True
        )
        if q.count():
            person = q[0]
        else:
            person, created = models.Person.objects.get_or_create(
                first_name=form.cleaned_data['first_name'].strip().title(),
                last_name=form.cleaned_data['last_name'].strip().title(),
                real=True,
                defaults=dict(
                    creator=creator,
                    nickname=form.cleaned_data['nickname'].strip().title(),
                    middle_name=form.cleaned_data['middle_name'].strip().title(),
                    public=True,
                    active=False,
                    needs_review=True
                ))
            if creator.total_karma > pt.many_approve_person:
                person.active = True
                person.needs_review = False
            person.save()
        
        if person.slug:
            return HttpResponseRedirect(reverse('person', args=(person.slug,)))
        else:
            return HttpResponseRedirect(reverse('person', args=(person.id,)))
    
    def search_response(self):
        generic = self.kwargs.get('generic')
        if generic:
            q = models.Person.search_objects.search(self.request.GET['content'])
            q = models.Person.objects.get_real(q)
        else:
            q = models.Person.objects.get_real()
            for k, v in self.request.GET.iteritems():
                q = q.filter(**{k+'__icontains': v})
        q = q[:10]
        return render_to_response(
            'issue_mapper/person-submit-search.html',
            dict(
                q=q,
                show=True,
            ),
            context_instance=RequestContext(self.request))
        
class SubmitLinkView(BaseSubmitView):
    
    template_name = 'issue_mapper/link-submit.html'
    
    form_class = forms.SubmitLinkForm

def issue_search_ajax(request):
    q = request.GET.get('q', '').strip()
    if not q:
        raise Http404
    issues = models.Issue.objects.filter(issue__icontains=q)[:5 ]
    return render_to_response(
        'issue_mapper/issue-search.html',
        dict(issues=issues),
        context_instance=RequestContext(request))

@json_view
def search_ajax(request, type, term=None):
    """
    Allows searching for various model records via ajax.
    """
    value_type = request.GET.get('value', 'id')
    if value_type not in ('id', 'slug'):
        raise Http404
    term = term or request.GET.get('term', '').strip()
    if not term.strip():
        raise Http404
    if type == c.PERSON:
        q = models.Person.search_objects.search(term)
        q = models.Person.objects.get_real_active(q)
        q = q[:5]
        label_func = lambda o: o.display_name
    elif type == c.CONTEXT:
        q = models.Context.search_objects.search(term)
        q = models.Context.objects.get_active_public(q)
        q = q[:5]
        label_func = lambda o: o.name
    elif type == c.ISSUE:
        q = models.Issue.search_objects.search(term)
        q = models.Issue.objects.get_active_public(q)
        q = q[:5]
        label_func = lambda o: o.friendly_text
    else:
        raise Http404
    return [dict(label=label_func(r), value=getattr(r, value_type)) for r in q]

@json_view
def link_add_ajax(request):
    from datetime import timedelta
    from templatetags.issue_mapper import list_item
    
    if not request.user.is_authenticated():
        raise Http404
    
    creator = middleware.get_current_person(raise_404=True, only_active=True)
    
    pt = models.Priviledge.get_current()
    if not pt.can.submit_link_unthrottled:
        links = creator.links.all().order_by('-created')
        if links:
            last_link = links[0]
            if last_link.created+timedelta(minutes=pt.submit_link_throttle_minutes) > timezone.now():
                diff = pt.submit_link_throttle_minutes - (timezone.now() - last_link.created).seconds/60
                return dict(
                    success=False,
                    message='Woah, you\'re doing that too fast. Please wait %i minutes.' % (diff,),
                    error='#ACK76'
                )
    
    form = forms.SubmitURLForm(request.REQUEST)
    if not form.is_valid():
        return dict(
            success=False,
            message='Invalid URL.',
            error='#NU98'
        )
    new_url = form.cleaned_data['url']
    if new_url:
        try:
            url, _ = models.URL.objects.get_or_create(
                url=new_url, defaults=dict(creator=creator))
        except Exception, e:
            return dict(
                success=False,
                message='Invalid URL.',
                error='#SB43'
            )
        if url.spam:
            return dict(
                success=False,
                message='Invalid URL.',
                error='#NOSPM'
            )
    else:
        url_id = form.cleaned_data['url_id']
        #print 'url_id:',url_id
        try:
            url = models.URL.objects.get(id=int(url_id))
        except Exception, e:
            return dict(
                success=False,
                message='Invalid URL.'+str(e),
                error='#SB44'
            )
            
    context_id = form.cleaned_data['context_id']
    if context_id and url:
        context = get_object_or_404(models.Context, id=context_id)
        models.URLContext.objects.get_or_create(
            context=context,
            url=url,
            defaults=dict(creator=creator))
    
    issue = None
    issue_id = form.cleaned_data.get('issue_id')
    if issue_id:
        issue = get_object_or_404(models.Issue, id=issue_id)
        
    person = None
    person_id = form.cleaned_data.get('person_id')
    if person_id:
        print 'Looking up person...'
        person = get_object_or_404(models.Person, id=person_id)
    print 'person:',person
    
#    if not issue and not person:
#        return dict(
#            success=False,
#            message='Either an issue or person must be specified.',
#            error='#NOOBJ'
#        )
    
    created = None
    if issue:
        link, created = models.Link.objects.get_or_create(
            issue=issue,
            person=None,
            url=url,
            defaults=dict(creator=creator))
        models.LinkVote.objects.get_or_create(
            voter=creator, link=link, vote=c.UPVOTE)
        
    if person:
        link, created = models.Link.objects.get_or_create(
            person=person,
            issue=None,
            url=url,
            defaults=dict(creator=creator))
        models.LinkVote.objects.get_or_create(
            voter=creator, link=link, vote=c.UPVOTE)
    
    html = ''
    resptype = request.GET.get('resptype', 'list_item') # url_tags
    if resptype == 'list_item':
#        html = render_to_string(
#            'issue_mapper/issue-links.html',
#            dict(links=[link]),
#            context_instance=RequestContext(request))
        html = list_item(item=url, person_filter=person, full=True)
    elif resptype == 'url_tags':
        from issue_mapper.templatetags.issue_mapper import url_tags
        html = url_tags(url)
    
    return dict(
        success=True,
        html=html.strip()
    )

@json_view
def link_cross_ajax(request):
    """
    Given a URL link, creates a similar link for another person or issue.
    """
    from datetime import timedelta
    from templatetags.issue_mapper import list_item
    
    if not request.user.is_authenticated():
        raise Http404
    
    creator = middleware.get_current_person(raise_404=True, only_active=True)
    
    pt = models.Priviledge.get_current()
    if not pt.can.submit_link_unthrottled:
        links = creator.links.all().order_by('-created')
        if links:
            last_link = links[0]
            if last_link.created+timedelta(minutes=pt.submit_link_throttle_minutes) > timezone.now():
                diff = pt.submit_link_throttle_minutes - (timezone.now() - last_link.created).seconds/60
                return dict(
                    success=False,
                    message='Woah, you\'re doing that too fast. Please wait %i minutes.' % (diff,),
                    error='#ACK76'
                )
    
    link = get_object_or_404(models.Link, id=request.GET.get('link_id', 0))
    issue = None
    person = None
    issue_id = request.GET.get('issue', '').strip()
    person_id = request.GET.get('person', '').strip()
    if issue_id:
        issue = get_object_or_404(models.Issue, id=issue_id)
    if person_id:
        person = get_object_or_404(models.Person, id=person_id)
    
    if not issue and not person:
        return dict(
            success=False,
            message='Either an issue or person must be specified.',
            error='#NOOBJ'
        )
    
    new_link, created = models.Link.objects.get_or_create(
        issue=issue,
        person=person,
        url=link.url,
        defaults=dict(creator=creator))
    print 'new_link:',new_link
    
    return dict(
        success=True,
        url=new_link.get_absolute_url()
    )

class MotionView(TemplateView):
    
    template_name = 'issue_mapper/motion.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(MotionView, self).get_context_data(*args, **kwargs)
        context['motion'] = models.Motion.objects.get(id=self.kwargs['motion_id'])
        return context
    
@json_view
def motion_ajax(request, object_type, object_id, attribute, vote_type):
    Q = models.Q
    
    if not request.user.is_authenticated():
        print 'Not logged in.'
        raise Http404
    
    if vote_type not in c.VOTE_NAME_TO_VALUE:
        print 'invalid vote type:',vote_type
        raise Http404
    
    new_value = request.GET.get('v', None)
    creator = middleware.get_current_person(raise_404=False, only_active=True)
    
    # Lookup object.
    issue = person = link = None
    if object_type == c.ISSUE:
        obj = issue = models.Issue.objects.get(slug=object_id)
    elif object_type == c.PERSON:
        obj = person = models.Person.objects.get(slug=object_id)
    elif object_type == c.LINK:
        obj = link = models.Link.objects.get(id=object_id)
    else:
        print 'Invalid object type.'
        raise Http404
        
    # Lookup attribute.
    if not hasattr(obj, attribute) or not obj.is_motionable(attribute):
        print 'Invalid attribute.'
        raise Http404
        
    attr = getattr(obj, attribute)
    if callable(attr):
        new_value = None
        
    motion, created = models.Motion.objects.get_or_create(
        issue=issue,
        person=person,
        link=link,
        attribute=attribute,
        new_value=new_value,
        pending=True,
        defaults=dict(
            creator=creator
        )
    )
    vote = c.VOTE_NAME_TO_VALUE[vote_type]
    motionvote, created = models.MotionVote.objects.get_or_create(
        motion=motion,
        voter=creator,
        defaults=dict(vote=vote))
    if not created:
        motionvote.flip()
    motionvote.save()
    vote_total = motionvote.motion.vote_total
    
    return dict(
        success=True,
        #votes=motion.votes.all().count(),
        vote_total=vote_total,
        vote_class=(c.UPVOTE_NAME if motionvote.is_up() else c.DOWNVOTE_NAME),
        description=motionvote.description,
        motion_id=motion.id,
    )

class BaseListViewSimple(ListView):
    
    template_name = "issue_mapper/list.html"

    title = None

    form_class = None

    paginate_by = 10

    show_top_search_controls = True

    default_type = c.ISSUE
    
    show_view_all_link = True
    
    show_issues = True
    
    show_links = True
    
    show_comments = False
    
    show_people = False
    
    show_elections = True
    
    show_replies = False
    
    # If true, indicates all comments, regardless of nesting, should be shown.
    show_all_comments = False
    
    show_comment_replies = True
    
    show_keyword_search = True

    @property
    def context_filter(self):
        request = self.request
        if hasattr(request, 'context'):
            return request.context
        
        # Otherwise, if a person is specified, use the most general context based
        # on their last term. e.g. if they're a federal senator in the U.S., then
        # lookup the context for "US".
        person_filter = self.person_filter
        if person_filter and person_filter.terms.all().count():
            term = person_filter.most_recent_term
            term_contexts = term.contexts
            if term_contexts:
                return term_contexts[0]
            
#            # Otherwise assume we're in the US default context.
#            return models.Context.objects.get(
#                country__iso='US',
#                state__isnull=True,
#                county__isnull=True)
    
    @property
    def election_filter(self):
        election_slug = self.kwargs.get('slug', '').strip()
        if not election_slug:
            return
        try:
            return models.Election.objects.get(slug=election_slug)
        except models.Election.DoesNotExist:
            try:
                return models.Election.objects.get(id=election_slug)
            except models.Election.DoesNotExist:
                pass
    
    @property
    def format(self):
        return self.request.GET.get('format', 'html')

    @property
    def creator(self):
        username = self.kwargs.get('username', '').strip()
        if not username:
            return
        try:
            return models.Person.objects.get(user__username=username)
        except models.Person.DoesNotExist:
            pass
    
    @property
    def type(self):
        """
        Returns the model type being listed.
        """
        if self.link_filter:
            return c.COMMENT
        return self.kwargs.get(
            'type',
            self.request.GET.get(
                'type',
                self.default_type)) or self.default_type

    @property
    def sort_options(self):
        if self.type == c.MATCHES:
            return [(c.SORT_BY_MATCH, 'Match Percent')]
        elif self.type == c.PERSON:
            return [
                (c.SORT_BY_COVERAGE_ASC, 'Coverage - Ascending'),
                (c.SORT_BY_COVERAGE_DSC, 'Coverage - Descending'),
                (c.SORT_BY_MAGIC_ASC, 'Magic - Ascending'),
                (c.SORT_BY_MAGIC_DSC, 'Magic - Descending'),
                (c.SORT_BY_MATCH_ASC, 'Match Percent - Ascending'),
                (c.SORT_BY_MATCH_DSC, 'Match Percent - Descending'),
                (c.SORT_BY_LINKS_DSC, 'Links - Descending'),
                (c.SORT_BY_LINKS_ASC, 'Links - Ascending'),
            ]
        elif self.type == c.LINK:
            return [
                (c.SORT_BY_MAGIC_ASC, 'Magic - Ascending'),
                (c.SORT_BY_MAGIC_DSC, 'Magic - Descending'),
                (c.SORT_BY_TOP_ASC, 'Most downvoted'),
                (c.SORT_BY_TOP_DSC, 'Most upvoted'),
                (c.SORT_BY_CREATED_DSC, 'Newest'),
                (c.SORT_BY_CREATED_ASC, 'Oldest'),
            ]
        return []
    
    @property
    def sort_default(self):
#        sort_options = self.sort_options
#        if sort_options:
        return c.SORT_BY_MAGIC_DSC
    
    @property
    def sort(self):
        return self.request.GET.get('sort', self.sort_default).strip()
    
    @property
    def page(self):
        try:
            return int(self.request.GET.get('page', 1))
        except:
            return 1
    
    @property
    def q(self):
        return self.request.GET.get(
            'q',
            self.request.COOKIES.get(
                c.COOKIE_KEYWORDS,
                ''
            )
        ).strip()

    @property
    def keywords(self):
        return c.LINK_REGEX.sub('', self.q)
    
    @property
    def person_filter(self):
        person_slug = self.kwargs.get('person_slug', '').strip()
        if not person_slug:
            return
        try:
            return models.Person.objects.get(
                slug=person_slug,
                public=True,
                #active=True,
                duplicate_of__isnull=True,
                deleted__isnull=True)
        except models.Person.DoesNotExist:
            try:
                return models.Person.objects.get(id=person_slug)
            except ValueError:
                pass
            except models.Person.DoesNotExist:
                pass
        if person_slug:
            raise Http404
    
    @property
    def link_filter(self):
        link_slug = self.kwargs.get('link_slug', '').strip()
        if not link_slug:
            return
        try:
            return models.Link.objects.get(id=link_slug)
        except models.Link.DoesNotExist:
            pass
        if link_slug:
            raise Http404
    
    @property
    def issue_filter(self):
        issue_id = self.kwargs.get('issue_id', '').strip()
        if not issue_id:
            return
        try:
            return models.Issue.objects.get(slug=issue_id)
        except models.Issue.DoesNotExist:
            try:
                return models.Issue.objects.get(id=int(issue_id))
            except models.Issue.DoesNotExist:
                pass
            except ValueError:
                pass
        if issue_id:
            raise Http404

    @property
    def url_filter(self):
        url_id = self.request.GET.get(
            'url_id',
            self.kwargs.get('url_id', '')
        ).strip()
        if not url_id:
            return
        try:
            return models.URL.objects.get(id=url_id)
        except models.URL.DoesNotExist:
            pass

    def get_issue_types(self):
        t = self.type
        lst = []
        form=self.form
        person_filter = self.person_filter
        context_filter = self.context_filter
        pre_url = ''
        if context_filter and context_filter.slug:
            #print 'context_filter.slug:',context_filter.slug
            pre_url = '/c/%s' % context_filter.slug
        # [(qt_singular, qt, qs, q_link, selected)]
        #print 'self.show_issues:',self.show_issues
        qs = self.request.META['QUERY_STRING']
        if qs:
            qs = '?' + qs
        if self.show_comments:
            lst.append((
                c.COMMENT,
                c.COMMENTS,
                self.get_comment_queryset(form=form),
                None,
                t == c.COMMENT,
            ))
        if self.show_elections:
            lst.append((
                c.ELECTION,
                c.ELECTIONS,
                self.get_election_queryset(form=form),
                pre_url + reverse('election_list') + qs,
                t == c.ELECTION,
            ))
        if self.show_issues:
            lst.append((
                c.ISSUE,
                c.ISSUES,
                self.get_issue_queryset(form=form),
                pre_url + (reverse('person', kwargs=dict(person_slug=person_filter.slug, type=c.ISSUE)) if person_filter else reverse('issue_list')) + qs,
                t == c.ISSUE,
            ))
        if self.show_links:
            lst.append((
                c.LINK,
                c.LINKS,
                self.get_link_queryset(form=form),
                pre_url + (reverse('person', kwargs=dict(person_slug=person_filter.slug, type=c.LINK)) if person_filter else reverse('link_list')) + qs,
                t == c.LINK,
            ))
        if self.show_people:
            lst.append((
                c.PERSON,
                c.PEOPLE,
                self.get_person_queryset(form=form),
                pre_url + reverse('person_list') + qs,
                t == c.PERSON,
            ))
        if self.show_replies:
            lst.append((
                c.REPLY,
                c.REPLIES,
                self.get_reply_queryset(form=form),
                None,
                t == c.REPLY,
            ))
        return lst

    @property
    def form(self):
        if self.form_class:
            #print 'self.request.GET:',self.request.GET.items()
            form = self.form_class(self.request.GET)
            form.is_valid()
            return form

    def get_context_data(self, *args, **kwargs):
        context = super(BaseListViewSimple, self).get_context_data(*args, **kwargs)
        
        person_filter = self.person_filter
        link_filter = self.link_filter
        issue_filter = self.issue_filter
        
        if person_filter and not person_filter.public:
            raise Http404
            
        show_search_results = not person_filter or person_filter.active
        
        context['form'] = self.form
        context['sort_options'] = self.sort_options
        context['sort'] = self.sort
        context['title'] = self.title
        context['person_filter'] = person_filter
        context['link_filter'] = link_filter
        context['issue_filter'] = issue_filter
        context['context_filter'] = self.context_filter
        context['election_filter'] = self.election_filter
        context['show_top_search_controls'] = self.show_top_search_controls
        #context['qs'] = self.get_queryset()
        context['page'] = context['page_obj']
        context['issue_types'] = self.get_issue_types()
        #print "context['issue_types']:",[_[0] for _ in context['issue_types']]
        context['selected_issue_type'] = context['noun'] = self.type
        context['q'] = self.q
        context['show_search_results'] = show_search_results
        context['show_view_all_link'] = self.show_view_all_link
        context['show_comment_replies'] = self.show_comment_replies
        context['show_keyword_search'] = self.show_keyword_search
        context['creator'] = self.creator
        context['random_new'] = self.get_random_new()
        
        return context

    @property
    def filter_links_by(self):
        return self.request.GET.get(c.FLB, c.FILTER_LINKS_BY_ISSUE)
        #return 'issue-and-person'
        #return 'issue'
        #return 'issue-without-person'
        return 'person-without-issue'
    
    def get_link_queryset(self, flb=None, form=None):
        request = self.request
        
        keywords = self.keywords
        if keywords:
            q = models.URL.search_objects.search(keywords)
        else:
            q = models.URL.objects.all()
            
        filter_links_by = flb or self.filter_links_by
#        print '!'*80
#        print 'filter_links_by:',filter_links_by
        person_filter = self.person_filter
        issue_filter = self.issue_filter
        context_filter = self.context_filter
        
        if context_filter:
            q = q.filter(url_contexts__context=context_filter)
        
        is_null=True
#        if keywords:
#            q = q.filter(url__title__icontains=keywords)
            #q = q.filter(content=keywords)
            
        if filter_links_by == c.FILTER_LINKS_BY_ISSUE_AND_PERSON:
            if person_filter:
                q = q.filter(links__person=person_filter.id, links__weight__gte=0)
            if issue_filter:
                q = q.filter(links__issue=issue_filter.id, links__weight__gte=0)
        elif filter_links_by == c.FILTER_LINKS_BY_ISSUE:
            if issue_filter:
                q = q.filter(links__issue=issue_filter.id, links__weight__gte=0)
        elif filter_links_by == c.FILTER_LINKS_BY_ISSUE_WITHOUT_PERSON:
            if person_filter:
                if is_null:
                    q = q.filter(links__person__isnull=True)
                else:
                    q = q.filter(links__person=0)
            if issue_filter:
                q = q.filter(links__issue=issue_filter.id)
        elif filter_links_by == c.FILTER_LINKS_BY_PERSON_WITHOUT_ISSUE:
            if person_filter:
                q = q.filter(links__person=person_filter.id, links__weight__gte=0)
            if issue_filter:
                if is_null:
                    q = q.filter(links__issue__isnull=True)
                else:
                    q = q.filter(links__issue=0)
        
        if form and form.is_valid():
            
            if form.cleaned_data.get('state'):
                state_list = form.cleaned_data.get('state')
                #print 'state_list:',state_list
                if state_list:
                    q = q.filter(links__person__terms__state__in=state_list)
                
            if self.request.user.is_authenticated():
                if form.cleaned_data.get('voted') == c.VOTED_YES:
                    q = q.filter(
                        votes__voter__user=self.request.user,
                        votes__deleted__isnull=True,
                    )
                elif form.cleaned_data.get('voted') == c.VOTED_YES_UP:
                    q = q.filter(
                        votes__voter__user=self.request.user,
                        votes__deleted__isnull=True,
                        votes__vote=c.UPVOTE,
                    )
                elif form.cleaned_data.get('voted') == c.VOTED_YES_DOWN:
                    q = q.filter(
                        votes__voter__user=self.request.user,
                        votes__deleted__isnull=True,
                        votes__vote=c.DOWNVOTE,
                    )
                elif form.cleaned_data.get('voted') == c.VOTED_NO:
                    q = q.exclude(id__in=models.LinkVote.objects\
                        .filter(voter__user=self.request.user)\
                        .values_list('link', flat=True))
        
        creator = self.creator
        if creator:
            q = q.filter(creator=creator)
            
        url_filter = self.url_filter
        print 'url_filter:',url_filter
        if url_filter:
            q = q.filter(id=url_filter.id)
            
        q = q.distinct()
            
        return q
    
    def get_election_queryset(self, form=None):
        person_filter = self.person_filter
        context_filter = self.context_filter
        
        q = models.Election.objects.get_public()
        
        if context_filter:
            q = q.filter(context__id=context_filter.id)
#            
        if person_filter:
            q = q.filter(candidates__person__id=person_filter.id)
        
        q = q.distinct()
        return q
        
    def get_issue_queryset(self, form=None):
        #TODO:allow filtering by position and update
        request = self.request
        keywords = self.keywords
        person_filter = self.person_filter
        context_filter = self.context_filter
        q = models.Issue.objects.get_public()
#            request.user, person=person_filter)
        if keywords:
            q = q.filter(issue__icontains=keywords)
        creator = self.creator
        if creator:
            q = q.filter(creator=creator)
        
        if context_filter:
            q = q.filter(contexts__id=context_filter.id)
        
        if form and form.is_valid():
            
            if form.cleaned_data.get('active') == 'true':
                q = q.filter(active=True)
            elif form.cleaned_data.get('active') == 'false':
                q = q.filter(active=False)
                        
            if self.request.user.is_authenticated():
                if form.cleaned_data.get('agreement') == c.AGREE:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__unknown=False,
                            issue_agreements__agree=True,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__unknown=False,
                            issue_agreements__agree=True,
                        )
                elif form.cleaned_data.get('agreement') == c.DISAGREE:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__unknown=False,
                            issue_agreements__agree=False,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__unknown=False,
                            issue_agreements__agree=False,
                        )
                elif form.cleaned_data.get('agreement') == c.UNKNOWN:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__unknown=True,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__unknown=True,
                        )
                elif form.cleaned_data.get('agreement') == c.UNDECIDED:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__their_polarity=c.UNDECIDED,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_polarity=c.UNDECIDED,
                        )
                elif form.cleaned_data.get('agreement') == c.FAVOR:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__their_polarity=c.FAVOR,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_polarity=c.FAVOR,
                        )
                elif form.cleaned_data.get('agreement') == c.OPPOSE:
                    if person_filter:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_person=person_filter,
                            issue_agreements__their_polarity=c.OPPOSE,
                        )
                    else:
                        q = q.filter(
                            issue_agreements__issue=F('id'),
                            issue_agreements__your_person__user=self.request.user,
                            issue_agreements__their_polarity=c.OPPOSE,
                        )
                    
                if form.cleaned_data.get('positioned') == 'true':
                    q = q.filter(
                        positions__person__user=self.request.user,
                        positions__creator__user=self.request.user,
                        positions__deleted__isnull=True,
                    )
                elif form.cleaned_data.get('positioned') == c.FAVOR:
                    q = q.filter(
                        positions__person__user=self.request.user,
                        positions__creator__user=self.request.user,
                        positions__polarity=c.FAVOR,
                        positions__deleted__isnull=True,
                    )
                elif form.cleaned_data.get('positioned') == c.UNDECIDED:
                    q = q.filter(
                        positions__person__user=self.request.user,
                        positions__creator__user=self.request.user,
                        positions__polarity=c.UNDECIDED,
                        positions__deleted__isnull=True,
                    )
                elif form.cleaned_data.get('positioned') == c.OPPOSE:
                    q = q.filter(
                        positions__person__user=self.request.user,
                        positions__creator__user=self.request.user,
                        positions__polarity=c.OPPOSE,
                        positions__deleted__isnull=True,
                    )
                elif form.cleaned_data.get('positioned') == 'false':
                    q = q.exclude(
                        id__in=models.Position.objects.filter(
                            person__user=self.request.user,
                            #deleted__isnull=False,
                            polarity__isnull=False,
                        ).values_list('issue__id', flat=True)
                    )
                
        q = q.distinct()
                
        return q
    
    def get_comment_queryset(self, for_full_count=True, form=None):
        """
        The parameter for_full_count is used to toggle between getting a full
        count of all comments or only get the top-level comments.
        """
        request = self.request
        keywords = self.keywords
        person_filter = self.person_filter
        link_filter = self.link_filter
        if for_full_count:
            q = models.Comment.objects.get_undeleted()
        else:
            # Only show stubs for deleted top-level comments if they have
            # children.
            #q = models.Comment.objects.all()
            q = models.Comment.objects.get_undeleted()
            q = q.filter(
                Q(depth=0),
                Q(
                    Q(deleted__isnull=True)|\
                    Q(deleted__isnull=False, reply_count__gt=0)))
        if link_filter:
            q = q.filter(link=link_filter)
        if person_filter:
            q = q.filter(Q(link__person=person_filter)|Q(person=person_filter))
        creator = self.creator
        if creator:
            q = q.filter(creator=creator)
        return q
    
    def get_reply_queryset(self, form=None, read=None):
        """
        Returns all replies for the current user.
        """
        if not self.request.user.is_authenticated():
            return models.Comment.objects.filter(id=0)
        request = self.request
        q = models.Comment.objects.get_undeleted()
        q = q.filter(comment__creator__user=self.request.user)
        if read is not None:
            q = q.filter(read=read)
        return q
    
    def get_person_queryset(self, form=None):
        keywords = self.keywords
        context_filter = self.context_filter
        election_filter = self.election_filter
        if keywords:
            q = models.Person.search_objects.search(keywords)
        else:
            q = models.Person.search_objects.all()
        q = models.Person.objects.get_real(q=q)
        q = models.Person.objects.get_active(q=q)
        
        if election_filter:
            q = q.filter(candidates__election=election_filter)
        
        if context_filter:
            if context_filter.country and context_filter.state and context_filter.county:
                q = q.filter(
                    terms__country=context_filter.country,
                    terms__state=context_filter.state.state,
                    terms__county=context_filter.county)
            elif context_filter.country and context_filter.state:
                q = q.filter(
                    terms__country=context_filter.country,
                    terms__state=context_filter.state.state,
                    terms__county__isnull=True)
            elif context_filter.country:
                q = q.filter(
                    Q(terms__country=context_filter.country),
                    Q(
                        Q(terms__state__isnull=True)|\
                        Q(
                            terms__state__isnull=False,
                            terms__role__level=c.ROLE_LEVEL_FEDERAL)),
                    Q(terms__county__isnull=True))
        
        if form and form.is_valid():
            #print form.cleaned_data
            if form.cleaned_data.get('state'):
                q = q.filter(terms__state=form.cleaned_data.get('state'))
                
            if form.cleaned_data.get('role'):
                role_level, role_slug = form.cleaned_data.get('role').split(',')
                q = q.filter(terms__role__slug=role_slug, terms__role__level=role_level)
                
            if form.cleaned_data.get('party'):
                q = q.filter(terms__party__slug=form.cleaned_data.get('party'))
                
            if form.cleaned_data.get('photo'):
                if form.cleaned_data.get('photo') == 'true':
                    q = q.exclude(photo_thumbnail='')
                else:
                    q = q.filter(photo_thumbnail='')
            
            if form.cleaned_data.get('current') == 'true':
                q = q.filter(
                    terms__start_date__lte=timezone.now(),
                    terms__end_date__gt=timezone.now()
                )
            elif form.cleaned_data.get('current') == 'false':
#                q = q.filter(
#                    terms__end_date__lt=timezone.now()
#                )
                q = q.exclude(
                    terms__start_date__lte=timezone.now(),
                    terms__end_date__gt=timezone.now()
                )
            
            if self.request.user.is_authenticated():
                if form.cleaned_data.get('match') == 'true':
                    q = q.filter(
                        matched_with__matcher__user=self.request.user,
                    )
                elif form.cleaned_data.get('match') == 'false':
                    q = q.exclude(
                        matched_with__matcher__user=self.request.user,
                    )
        else:
            print '!'*80
            print 'form not valid'
            print form.errors
                
        return q.distinct()
    
    def get_random_new(self):
        """
        Returns a random record for the current type that is considered "new"
        with an undefined weight or importance requiring special attention.
        """
        if self.url_filter:
            # Don't show a random URL if we're already only showing
            # a single URL.
            return
        form = self.form
        person_filter = self.person_filter
        issue_filter = self.issue_filter
        context_filter = self.context_filter
        if self.type == c.LINK:
            q = q0 = models.URL.objects.get_new()
            
            if person_filter:
                q = q.filter(links__person=person_filter)
                
            if context_filter:
                q = q.filter(url_contexts__context=context_filter)
                
            if issue_filter:
                q = q.filter(links__issue=issue_filter)
                
            if form and form.is_valid():
                if form.cleaned_data.get('state'):
                    q = q.filter(links__person__terms__state__in=form.cleaned_data.get('state'))
            
            q = q.order_by('?')
            if q.count():
                return q[0]
    
    def get_queryset(self):
        """
        Returns master queryset for listing records.
        """
        form = self.form
        sort = self.sort
        context_filter = self.context_filter
        if self.type == c.LINK:
            q = self.get_link_queryset(form=form)
            q = q.filter(top_urlcontext_weight__isnull=False)
            if sort == c.SORT_BY_TOP_ASC:
                if context_filter:
                    q = q.order_by('url_contexts__weight')
                else:
                    q = q.order_by('weight')
            elif sort == c.SORT_BY_TOP_DSC:
                if context_filter:
                    q = q.order_by('-url_contexts__weight')
                else:
                    q = q.order_by('-weight')
                    
            elif sort == c.SORT_BY_MAGIC_ASC:
                if context_filter:
                    q = q.order_by('url_contexts__top_weight', 'url_contexts__rand')
                else:
                    #q = q.order_by('top_weight', 'rand')
                    q = q.order_by('top_urlcontext_weight', 'rand')
            elif sort == c.SORT_BY_MAGIC_DSC:
                if context_filter:
                    q = q.order_by('-url_contexts__top_weight', 'url_contexts__rand')
                else:
                    #q = q.order_by('-top_weight', 'rand')
                    q = q.order_by('-top_urlcontext_weight', 'rand')
                    
            elif sort == c.SORT_BY_CREATED_ASC:
                if context_filter:
                    q = q.order_by('url_contexts__created', 'url_contexts__rand')
                else:
                    q = q.order_by('created', 'rand')
            elif sort == c.SORT_BY_CREATED_DSC:
                if context_filter:
                    q = q.order_by('-url_contexts__created', 'url_contexts__rand')
                else:
                    q = q.order_by('-created', 'rand')
        elif self.type == c.ISSUE:
            q = self.get_issue_queryset(form=form)
        elif self.type == c.PERSON:
            q = self.get_person_queryset(form=form)
            if sort in (c.SORT_BY_MATCH_ASC, c.SORT_BY_MATCH_DSC) \
            and self.request.user.is_authenticated():
                # Match percent requires a logged-in user.
                q = q.filter(matched_with__matcher__user=self.request.user)
                if sort == c.SORT_BY_MATCH_ASC:
                    q = q.order_by('matched_with__value')
                elif sort == c.SORT_BY_MATCH_DSC:
                    q = q.order_by('-matched_with__value')
            elif sort == c.SORT_BY_MAGIC_ASC:
                q = q.order_by('top_weight', 'rand')
            elif sort == c.SORT_BY_MAGIC_DSC:
                q = q.order_by('-top_weight', 'rand')
            elif sort == c.SORT_BY_COVERAGE_ASC:
                q = q.order_by('position_count', 'rand')
            elif sort == c.SORT_BY_COVERAGE_DSC:
                q = q.order_by('-position_count', 'rand')
            elif sort == c.SORT_BY_LINKS_DSC:
                q = q.order_by('-issue_link_count', 'rand')
            elif sort == c.SORT_BY_LINKS_ASC:
                q = q.order_by('issue_link_count', 'rand')
                
        elif self.type == c.COMMENT:
            if self.show_all_comments:
                q = self.get_comment_queryset(for_full_count=True, form=form)
            else:
                q = self.get_comment_queryset(for_full_count=False, form=form)
        elif self.type == c.REPLY:
            q = self.get_reply_queryset(form=form)
        elif self.type == c.ELECTION:
            q = self.get_election_queryset(form=form)
        else:
            raise Exception, 'Unknown type: %s' % (self.type,)
        
        return q
    
    def get(self, request, *args, **kwargs):
        from django.conf import settings
        if self.format == c.RSS:
            feed = Rss201rev2Feed(
                u"%s RSS - %s" % (self.type.title(), settings.SITE_NAME),
                self.request.build_absolute_uri(),
                u'' )
            object_list = self.get_queryset()[:10]
            for object in object_list:
                author = 'author'#object.get_author()
                link = 'link'#blog_link + object.get_full_path()
                feed.add_item(
                    object.feed_title.encode('utf-8'),
                    object.feed_url,
                    object.feed_teaser.encode('utf-8'), 
                    #author_email=author.email.encode('utf-8'),
                    #author_name=author.name.encode('utf-8'),
                    pubdate=object.created,
                    unique_id=object.feed_url,
                    #categories=[x.encode('utf-8') for x in object.get_simplified_categories()]
                )
            response = HttpResponse(mimetype='application/xml')
            feed.write(response, 'utf-8')
            return response

        return super(BaseListViewSimple, self).get(request, *args, **kwargs)

class PersonListView(BaseListViewSimple):

    form_class = forms.PersonListForm

    @property
    def title(self):
        election_filter = self.election_filter
        if election_filter:
            return election_filter.name
        return 'People'

    @property
    def show_comments(self):
        return False
    
    @property
    def show_elections(self):
        election_filter = self.election_filter
        if election_filter:
            return False
        return True
    
    @property
    def show_issues(self):
        election_filter = self.election_filter
        if election_filter:
            return False
        return True
    
    @property
    def show_links(self):
        election_filter = self.election_filter
        if election_filter:
            return False
        return True
    
    @property
    def show_people(self):
        return True
    
    @property
    def type(self):
        return self.request.GET.get('type', c.PERSON)

    def get_context_data(self, *args, **kwargs):
        context = super(PersonListView, self).get_context_data(*args, **kwargs)
        context.update(dict(
            selected_issue_type=c.PERSON,
#            issue_types=[
#                (
#                    c.PERSON,
#                    c.PEOPLE,
#                    self.get_queryset(),
#                )
#            ],
            noun=self.type,
            q=self.q,
            show_search_results=True,
        ))
        return context
    
class IssueListView(BaseListViewSimple):

    form_class = forms.IssueListForm
    
    show_people = True
    
    @property
    def title(self):
        return 'Issues'
    
    @property
    def type(self):
        return c.ISSUE
    
    def get_context_data(self, *args, **kwargs):
        context = super(IssueListView, self).get_context_data(*args, **kwargs)
        context.update(dict(
            selected_issue_type=c.ISSUE,
            #issue_types=[(c.ISSUE, c.ISSUES, self.get_queryset())],
            noun=c.ISSUE,
            q=self.q,
        ))
        return context

class LinkListView(BaseListViewSimple):

    form_class = forms.LinkListForm
    
    show_view_all_link = False
    
    show_people = True

    @property
    def title(self):
        return 'Links'
    
    @property
    def type(self):
        return c.LINK
    
    def get_context_data(self, *args, **kwargs):
        context = super(LinkListView, self).get_context_data(*args, **kwargs)
        
        rss_url = self.request.get_full_path()
        if '?' not in rss_url:
            rss_url += '?'
        if 'format=' not in rss_url:
            rss_url += '&format=rss'
            
        context.update(dict(
            selected_issue_type=c.LINK,
            noun=c.LINK,
            q=self.q,
            show_search_results=True,
            rss_urls=[('RSS', rss_url)],
        ))
        return context

class ElectionListView(BaseListViewSimple):

    form_class = forms.ElectionListForm
    
    show_view_all_link = False
    
    show_people = True

    @property
    def title(self):
        return 'Elections'
    
    @property
    def type(self):
        return c.ELECTION
    
    def get_context_data(self, *args, **kwargs):
        context = super(ElectionListView, self).get_context_data(*args, **kwargs)
        context.update(dict(
            selected_issue_type=c.ELECTION,
            noun=c.ELECTION,
            q=self.q,
            show_search_results=True,
            #rss_urls=[('RSS', rss_url)],
        ))
        return context

class LinkView(BaseListViewSimple):
    """
    Displays comments attached to a specific link, and optional
    issue or link.
    """
    
    #default_type = c.COMMENT
    
    show_top_search_controls = False
    
    pass
    
class IssueListViewSimple(BaseListViewSimple):
    """
    Displays a list of issues.
    """
    
    form_class = forms.IssueListForm
    
    show_comments = True
    
    @property
    def filter_links_by(self):
        person_filter = self.person_filter
        if person_filter:
            return c.FILTER_LINKS_BY_ISSUE_AND_PERSON

class LinkListViewSimple(BaseListViewSimple):
    """
    Displays a list of links.
    """
    
    show_comments = True
    
    @property
    def filter_links_by(self):
        person_filter = self.person_filter
        if person_filter:
            return c.FILTER_LINKS_BY_ISSUE_AND_PERSON

class CommentListViewSimple(BaseListViewSimple):
    """
    Displays a list of comments.
    """
    
    show_comments = True
    
    @property
    def filter_links_by(self):
        person_filter = self.person_filter
        if person_filter:
            return c.FILTER_LINKS_BY_ISSUE_AND_PERSON#TODO

class ProfileView(BaseListViewSimple):
    """
    Lists records filtered by a specific user.
    """
    
    show_view_all_link = False
    
    show_issues = True
    
    show_links = True
    
    show_comments = True
    
    show_replies = True
    
    show_all_comments = True
    
    show_comment_replies = False
    
    show_keyword_search = False
    
    def get(self, *args, **kwargs):
        if not self.creator:
            raise Http404
        return super(ProfileView, self).get(*args, **kwargs)
    
class IssueView(BaseListViewSimple):
    
    default_type = c.LINK
    
    def get(self, *args, **kwargs):
        issue_filter = self.issue_filter
        if issue_filter:
            issue_filter.view_count += 1
            issue_filter.save()
        return super(IssueView, self).get(*args, **kwargs)
        
    def get_issue_types(self):
        from url_tools.templatetags.urls import add_params
        person_filter = self.person_filter
        issue_filter = self.issue_filter
        flb = self.filter_links_by
        parts = []
        if person_filter and issue_filter:
            parts = [
                (   c.LINK,
                    'links for issue',
                    self.get_link_queryset(flb=c.FILTER_LINKS_BY_ISSUE),
                    add_params(self.request.get_full_path(), **{
                        'q':self.q,
                        'page':1,
                        c.FLB:c.FILTER_LINKS_BY_ISSUE,
                    }),
                    flb==c.FILTER_LINKS_BY_ISSUE,
                ),
                (   c.LINK,
                    'links for person on issue',
                    self.get_link_queryset(flb=c.FILTER_LINKS_BY_ISSUE_AND_PERSON),
                    add_params(self.request.get_full_path(), **{
                        'q':self.q,
                        'page':1,
                        c.FLB:c.FILTER_LINKS_BY_ISSUE_AND_PERSON,
                    }),
                    flb==c.FILTER_LINKS_BY_ISSUE_AND_PERSON,
                ),
#                (   c.LINK,
#                    'links for issue',
#                    self.get_link_queryset(flb=c.FILTER_LINKS_BY_ISSUE_WITHOUT_PERSON),
#                    None),
                (   c.LINK,
                    'links for person',
                    self.get_link_queryset(flb=c.FILTER_LINKS_BY_PERSON_WITHOUT_ISSUE),
                    add_params(self.request.get_full_path(), **{
                        'q':self.q,
                        'page':1,
                        c.FLB:c.FILTER_LINKS_BY_PERSON_WITHOUT_ISSUE,
                    }),
                    flb==c.FILTER_LINKS_BY_PERSON_WITHOUT_ISSUE,
                ),
            ]
        parts = [_ for _ in parts if _[2].count()]
        return parts
        
    pass

@json_view
def comment_create_ajax(request, object_type, object_id):
    object_types = dict(
        issue=models.Issue,
        link=models.Link,
        person=models.Person,
        comment=models.Comment,
    )
    if not request.user.is_authenticated():
        raise Htt404
    if object_type not in object_types:
        raise Http404
    person = middleware.get_current_person(raise_404=True, only_active=True)
    obj = get_object_or_404(object_types[object_type], id=object_id)
    text = request.REQUEST.get('comment', '').strip()[:700]
    if not text:
        raise Http404
    
    create_kwargs = {
        object_type:obj,
        'creator':person,
        'text':text,
    }
    
    try:
        comment = models.Comment.objects.get(**create_kwargs)
    except models.Comment.DoesNotExist:
        comment = models.Comment.objects.create(**create_kwargs)
    comment_html = render_to_string(
        'issue_mapper/list-item-comment.html',
        dict(
            full=True,
            item=comment,
        ),
        context_instance=RequestContext(request)).strip()
    
    return dict(
        success=True,
        html=comment_html,
    )

@json_view
def comment_delete_ajax(request, comment_id):
    if not request.user.is_authenticated():
        raise Htt404
    person = middleware.get_current_person(raise_404=True, only_active=True)
    comment = get_object_or_404(
        models.Comment,
        id=comment_id,
        creator=person)
    comment.deleted = timezone.now()
    comment.save()
    return dict(
        success=True,
        comment_id=comment.id,
    )

@json_view
def position_set_ajax(request):
    if not request.user.is_authenticated():
        raise Http404
    
    creator = middleware.get_current_person(raise_404=True, only_active=True)
    
    polarity = request.GET.get('polarity')
    if polarity not in c.POSITIONS:
        print 'invalid polarity:',polarity
        raise Http404
    
    issue = get_object_or_404(models.Issue, slug=request.GET.get('issue'))
    
    person = other_person = None
    importance = None
    if request.GET.get('person', '').strip():
        person = other_person = get_object_or_404(
            models.Person,
            real=True,
            active=True,
            deleted__isnull=True,
            slug=request.GET.get('person'))
    else:
        person = creator
        try:
            importance = int(request.GET.get('importance'))
        except ValueError, e:
            print e
            pass
        if importance not in c.IMPORTANCES:
            print 'invalid importance:',importance
            raise Http404
    
    position, new_position = models.Position.create(
        issue=issue,
        polarity=polarity,
        person=person,
        creator=creator,
    )
    print 'importance:',importance
    if importance is not None:
        position.importance = importance
        position.save()
        print 'importance1:',position.importance
    
    next_url = reverse('issue_list')
    next_q = models.Issue.objects.get_unpositioned_by(
        user=creator.user,
        person=other_person,
        rand=0.25)
    if next_q:
        if other_person:
            next_url = reverse(
                'issue_wrt_person',
                args=(other_person.slug, next_q[0].slug))
        else:
            next_url = next_q[0].get_absolute_url()
    
    return dict(
        success=True,
        importance=position.importance,
        polarity=position.polarity,
        next_url=next_url,
    )

def skip_issue(request, issue_id, person_slug=None):
    """
    Registers the user's skip of setting a position by creating
    a temporary position record with no polarity.
    """
    
    if not request.user.is_authenticated():
        raise Http404
    
    creator = middleware.get_current_person(raise_404=True, only_active=True)
    
    issue = get_object_or_404(models.Issue, slug=issue_id)
    
    person = creator
    other_person = None
    if person_slug:
        person = other_person = get_object_or_404(
            models.Person,
            real=True,
            deleted__isnull=True,
            duplicate_of__isnull=True,
            slug=person_slug)
    
    #print 'other_person:',other_person
    position, is_new = models.Position.objects.get_or_create(
        issue=issue,
        person=person,
        creator=creator,
        deleted=None,
        defaults=dict(polarity=None)
    )
    #print 'position:',position
    
    next_q = models.Issue.objects.get_unpositioned_by(
        user=creator.user,
        person=other_person)
    next_url = reverse('issue_list')
    if next_q:
        if other_person:
            next_url = reverse(
                'issue_wrt_person',
                args=(other_person.slug, next_q[0].slug))
        else:
            next_url = next_q[0].get_absolute_url()
    print 'next_url:',next_url
    return HttpResponseRedirect(next_url)

def comment_permalink(request, comment_id):
    todo

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    t = get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))

class UserPrivilegeView(TemplateView):
    
    template_name = 'issue_mapper/user-privileges.html'
    
    def get_context_data(self, *args, **kwargs):
        person = get_object_or_404(
            models.Person,
            user__username=self.kwargs.get('username'), real=False)
        context = super(UserPrivilegeView, self).get_context_data(*args, **kwargs)
        #context['motion'] = models.Motion.objects.get(id=self.kwargs['motion_id'])
        p = models.Priviledge.get_current()
        
        context['person'] = person
        
        list_privileges = [
            ('single_submit_issue', 'submit issues'),
            ('single_submit_link', 'submit links'),
            ('single_submit_person', 'submit people'),
            ('single_vote_link', 'vote on links'),
            ('single_answer_issue_for_themself', 'state your position'),
            ('single_answer_issue_for_other', 'state a politican\'s position'),
        ]
        context['privileges'] = sorted([
            ('single_submit_link_comment', 'comment on links', True, 0),
            ]+[
            (
                priv_name,
                priv_label,
                getattr(p.can, priv_name.replace('single_', '')), # enabled
                getattr(p, priv_name) # threshold
            )
            for priv_name, priv_label in list_privileges
        ], key=lambda o:(o[3], o[1]))
        
        return context

def test(request, name):
    if name == '404':
        raise Http404
    elif name == '500':
        raise Exception, '500'

@json_view
def quote_add_ajax(request):
    print 'A'
    url = get_object_or_404(models.URL, id=request.GET.get('url_id'))
    print 'B',request.GET.get('person_id')
    person = get_object_or_404(models.Person, id=request.GET.get('person_id'))
    print 'C'
    text = request.GET.get('text', '').strip()
    if not text:
        raise Http404
    dt = request.GET.get('dt', '').strip()
    if not dt:
        raise Http404
    import dateutil.parser
    dt = dateutil.parser.parse(dt)
    quote, _ = models.Quote.objects.get_or_create(
        url=url,
        person=person,
        said_date=dt,
        text=text,
    )
    
    html = ''
    resptype = request.GET.get('resptype', 'url_tags')
    if resptype == 'url_tags':
        from issue_mapper.templatetags.issue_mapper import url_tags
        html = url_tags(url)
    
    return dict(
        success=True,
        html=html.strip()
    )

def quote_get_ajax(request, url_id):
    url = get_object_or_404(models.URL, id=url_id)
    return HttpResponse(
        content=render_to_string(
            'issue_mapper/url-quotes.html',
            dict(
                url=url,
            ),
            context_instance=RequestContext(request)
        ).strip(),
        content_type='text/html')

def filter_context(request, context_slug, rest):
    context = get_object_or_404(models.Context, slug=context_slug)
    resolver_match = resolve(rest)
    request.context = context
    return resolver_match.func(
        request,
        *resolver_match.args,
        **resolver_match.kwargs)

class ContextsView(BaseTemplateView):
    
    title = 'Contexts'
    
    template_name = 'issue_mapper/contexts.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(ContextsView, self).get_context_data(*args, **kwargs)
        context['contexts'] = models.Context.objects.get_active_public()
        return context
    