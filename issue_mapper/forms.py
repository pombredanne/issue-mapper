from django import forms
from django.conf import settings
from django.utils import timezone
import django

from django_localflavor_us.us_states import USPS_CHOICES

import models
import constants as c
from middleware import get_current_request

class IssueResponseForm(forms.Form):
    
    raw_response = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            #'style':'display:none;'
        }))
    
    def __init__(self, issue, person, creator, *args, **kwargs):
        
        self.request = get_current_request()
        
        self.issue = issue
        self.person = person
        self.creator = creator
        #self.other_person = issue.random_unpositioned_other_person
        
#        print 'person:',self.person
#        print 'creator:',self.creator
        self.position = self.issue.get_last_position(self.person, self.creator)
        self.positionable = self.issue.positionable(self.request.user)
        self.IM_WAIT_DAYS_BEFORE_REANSWER = settings.IM_WAIT_DAYS_BEFORE_REANSWER
        self.positioned = self.issue.positioned(self.person, self.creator)
        self.choice_counts = self.issue.get_choice_counts()
        
        pt = models.Priviledge.get_current()
        if not self.request.user.is_authenticated():
            # Show buttons which will trigger login/registration form.
            self.allow_answer = True
        elif self.person == self.creator or self.person is None:
            self.allow_answer = pt.can.answer_issue_for_themself
        else:
            self.allow_answer = pt.can.answer_issue_for_other
        
        self.buttons_fixed_buttom = self.allow_answer and int(self.request.COOKIES.get(c.COOKIE_BUTTONS_FLOAT, 1))
        
        super(IssueResponseForm, self).__init__(*args, **kwargs)

    @property
    def friendly_text(self):
        try:
            if self.person:
                return self.issue.friendly_text_wrt(self.person)
            else:
                return self.issue.friendly_text
        except Exception, e:
            return str(e)

    @property
    def actions(self):
        if settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING1:
            if self.person != self.creator:
                q = c.POSITION_CHOICES_PAST
            else:
                q = c.POSITION_CHOICES
        else:
            if self.person != self.creator:
                q = c.POSITION_CHOICES3_WRT
            else:
                q = c.POSITION_CHOICES3
        #q = self.issue.position_choice_list
        return [(slug, name.title()) for slug, name in q]
    
    @property
    def importances(self):
        return c.IMPORTANCE_CHOICES_FRIENDLY

class SubmitURLForm(forms.Form):
    
    url = forms.URLField(
        required=False)
    
    url_id = forms.IntegerField(required=False)
    
    issue_id = forms.IntegerField(required=False)
    
    person_id = forms.IntegerField(required=False)
    
    context_id = forms.IntegerField(required=False)

class SubmitIssueForm(forms.Form):
    
    issue = forms.CharField(
        required=True,
        #help_text='''(please be as clear and concise as possible)'''
    )
    
    def clean_issue(self):
        from models import normalize_issue_simple
        q = normalize_issue_simple(self.cleaned_data['issue'])
        return q
        
class SubmitPersonForm(forms.Form):
    
    first_name = forms.CharField(
        required=True,
    )
    
    nickname = forms.CharField(
        required=False,
        label='First name (nickname)'
    )
    
    middle_name = forms.CharField(
        required=False,
    )
    
    last_name = forms.CharField(
        required=True,
    )
    
class SubmitLinkForm(forms.Form):
    
    link = forms.URLField(
        required=False,
        label='URL',
    )


class SearchListForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(SearchListForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def no_query_found(self):
        q = self.searchqueryset.all()
        return q
    
    def clean_q(self):
        q = self.cleaned_data.get('q', '').replace('+', ' ').strip()
        return q
    
    def add_q(self, q):
        return q
    
    def search(self, *args, **kwargs):
        sqs = super(SearchListForm, self).search(*args, **kwargs)
        
        #does nothing?
        #sqs = sqs.load_all_queryset(models.Person, models.Person.objects.all().select_related(depth=2))
        #sqs = sqs.filter(term_role_name='senator', term_state='DE')
        #sqs = sqs.filter(term_role_name='senator')
        #sqs = sqs.filter(term_role_name='representative')
#        sqs = sqs.filter(
#            term_latest_start_date__lte=timezone.now(),
#            term_latest_end_date__gt=timezone.now()
#        )
        #sqs = sqs.filter(term_state__in=['DE','PA'])
        #sqs = sqs.filter(Q(term_state='DE')|Q(term_state='PA'))
        #sqs = sqs.filter(has_photo__contains=str(False))
        #sqs = sqs.filter(has_photo='false')#works!
        #print 'count:',sqs.count()
        sqs = self.add_q(sqs)
        
        sqs = sqs.order_by('-top_weight', 'rand')
        
        self.sqs = sqs
        return sqs
    
def _get_role_choices():
    yield '', '---'
    q = models.Role.objects.all()
    q = q.filter(
        terms__person__public=True,
        terms__person__active=True)
    q = q.distinct()
    q = q.order_by('name')
    for r in q:
        yield '%s,%s' % (r.level, r.slug), unicode(r)

def _get_party_choices():
    yield '', '---'
    q = models.Party.objects.all()
    q = q.filter(
        terms__person__public=True,
        terms__person__active=True)
    q = q.distinct()
    q = q.order_by('name')
    for r in q:
        yield r.slug, r.name

class IssueListForm(SearchListForm):
    
    active = django.forms.ChoiceField(
        required=False,
        choices=[
            ('','---'),
            ('false', 'No'),
            ('true', 'Yes'),
        ])
    
    agreement = django.forms.ChoiceField(
        required=False,
        label='Their position',
        choices=[
            ('','---'),
            (c.FAVOR, 'agrees with the issue'),
            (c.AGREE, 'agrees with you'),
            (c.OPPOSE, 'disagrees with the issue'),
            (c.DISAGREE, 'disagrees with you'),
            (c.UNDECIDED, 'is undecided'),
        ])
    
    positioned = django.forms.ChoiceField(
        required=False,
        label='Your position',
        choices=[
            ('','---'),
            (c.FALSE, 'is unstated'),
            (c.TRUE, 'is stated'),
            (c.FAVOR, 'agrees with the issue'),
            (c.OPPOSE, 'disagrees with the issue'),
            (c.UNDECIDED, 'is undecided'),
        ])
    
#    positioned = django.forms.ChoiceField(
#        required=False,
#        label='You have a position',
#        choices=[('','---'), ('true','Yes'), ('false','No')])

from django_localflavor_us.us_states import USPS_CHOICES

class ElectionListForm(SearchListForm):
    pass

class RationaleListForm(SearchListForm):
    pass

class LinkListForm(SearchListForm):
    
#    state = django.forms.MultipleChoiceField(
#        required=False,
#        choices=USPS_CHOICES,
#    )
    
    voted = django.forms.ChoiceField(
        required=False,
        #label='Currently in office',
        choices=[
            ('','---'),
            (c.VOTED_YES, 'Yes'),
            (c.VOTED_YES_UP, 'Yes - Up'),
            (c.VOTED_YES_DOWN, 'Yes - Down'),
            (c.VOTED_NO, 'No')
        ],
    )
    
    def clean_state(self, value=None):
        lst = []
        q = self.cleaned_data.get('state', value) or []
        for el in q:
            lst.extend(el.split(','))
        #print 'state:',lst
        return lst
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        #initial['state'] = ['DE','PA']
        super(LinkListForm, self).__init__(*args, **kwargs)
        
#        self.fields['state'].widget.attrs['no-auto-update'] = 1
#        self.fields['state'].clean = self.clean_state #TODO:why doesn't Django's default MultipleChoiceField cleaner work?!
        
#        for field in self.fields:
#            self.fields[field].widget.attrs['class'] = 'form-control'
        
        #print "self.fields['state']:",self.fields['state'].value
        self.full_clean()
        #print 'form.data:',self.data
        
        # Django doesn't call the clean method for the initial form data
        # so we have to.
        if 'state' in self.data:
            self.data = dict(self.data)
            self.data['state'] = self.clean_state(self.data['state'])

class PersonListForm(SearchListForm):
    
    current = django.forms.ChoiceField(
        required=False,
        label='Currently in office',
        choices=[('','---'), ('true','Yes'), ('false','No')])
    
    match = django.forms.ChoiceField(
        required=False,
        label='Has match',
        choices=[('','---'), ('true','Yes'), ('false','No')])
    
    photo = django.forms.ChoiceField(
        required=False,
        label='Has photo',
        choices=[('','---'), ('true','Yes'), ('false','No')])
    
    party = django.forms.ChoiceField(
        required=False,
        choices=_get_party_choices(),
    )
    
    role = django.forms.ChoiceField(
        required=False,
        choices=_get_role_choices(),
    )
    
    state = django.forms.ChoiceField(
        required=False,
        choices=(('','---'),)+USPS_CHOICES,
    )
    
    def add_q(self, q):
        if hasattr(self, 'cleaned_data'):
            if self.cleaned_data['party']:
                q = q.filter(term_latest_party=self.cleaned_data['party'])
            if self.cleaned_data['role']:
                q = q.filter(term_role_name=self.cleaned_data['role'])
            if self.cleaned_data['state']:
                q = q.filter(term_state=self.cleaned_data['state'])
            if self.cleaned_data['photo']:
                q = q.filter(has_photo=self.cleaned_data['photo'])
            if self.cleaned_data['current'] == 'true':
                q = q.filter(
                    term_latest_start_date__lte=timezone.now(),
                    term_latest_end_date__gt=timezone.now()
                )
            elif self.cleaned_data['current'] == 'false':
                q = q.filter(
                    term_latest_end_date__lt=timezone.now()
                )
        return q
    