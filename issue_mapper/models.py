# -*- coding: utf-8 -*- 
import sys
import csv
import uuid
import re
import math
import urllib
import urllib2
import httplib
import simplejson
import socket
import dateutil
import dateutil.parser
import time
import random
import commands
import urlparse
from datetime import timedelta, date
from pprint import pprint

import settings as _settings

from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, connection, IntegrityError
from django.db.models import Max, Count, Sum, F, Q
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import signals
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.encoding import force_text
import django

from django_localflavor_us.models import USStateField
from django_localflavor_us.us_states import USPS_CHOICES, STATE_CHOICES

import galerts
import feedparser

from admin_steroids.utils import StringWithTitle, get_admin_change_url

JobModel = None
try:
    from chroniker.models import Job as JobModel
except ImportError:
    print>>sys.stderr, 'Install chroniker for viewing command status in admin.'

import scrapper

import constants as c
import middleware

socket.setdefaulttimeout(10)

APP_LABEL = StringWithTitle('issue_mapper', 'Issue Mapper')

def get_thumbnail_from_url(image_url, format='jpeg', size=(200, 200)):
    import random
    import sys
    import time
    import urllib2
    from django.core import files
    from PIL import Image
    from cStringIO import StringIO
    try:
        image_data = scrapper.get(url=image_url, verbose=True)
        image_file = files.temp.NamedTemporaryFile(
            dir=files.temp.gettempdir()
        )
        if not image_data:
            return
        image_file.write(image_data)
        image_file.seek(0)
        image = Image.open(StringIO(image_data))
        image.thumbnail(size, Image.ANTIALIAS)
        temp_handle = StringIO()
        image.save(temp_handle, format)
        temp_handle.seek(0)
        image_file = files.temp.NamedTemporaryFile(
            dir=files.temp.gettempdir()
        )
        image_file.write(temp_handle.getvalue())
        image_file.seek(0)
        photo_thumbnail = files.File(image_file)
        return photo_thumbnail
    except IOError, e:
        print>>sys.stderr, 'Failed to load %s: %s' % (image_url, e)
    except ValueError, e:
        print>>sys.stderr, 'ValueError: %s' % (e,)
    except urllib2.HTTPError, e:
        print>>sys.stderr, 'HTTPError: %s' % (e,)

def print_status(top_percent, sub_percent, message, max_message_length=100, newline=False):
    """
    Updates the status "xxx.x% xxx.x% message" on the same console line.
    """
    if sub_percent is None:
        sys.stdout.write('\rStatus: %05.1f%% %s' % (
            float(top_percent),
            message[:max_message_length].ljust(max_message_length)
        ))
    else:
        sys.stdout.write('\rStatus: %05.1f%% %05.1f%% %s' % (
            float(top_percent),
            float(sub_percent),
            message[:max_message_length].ljust(max_message_length)
        ))
    if newline:
        sys.stdout.write('\n')
    sys.stdout.flush()

def _get_default_country():
    from countries.models import Country
    return Country.objects.get(iso='US')

def entropy_histogram(nums):
    """Calculates the Shannon entropy of a histogram."""

    # get probability of number in list
    s = float(sum(nums))
    prob = [ n/s for n in nums if n ]

    # calculate the entropy
    entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])

    return entropy

class BaseModel(models.Model):
    
    created = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        db_index=True,
        default=timezone.now,
        editable=False,
        null=False,
        help_text="The date and time when this record was created.")
        
    updated = models.DateTimeField(
        auto_now_add=True,
        auto_now=True,
        blank=True,
        db_index=True,
        default=timezone.now,
        editable=False,
        null=True,
        help_text="The date and time when this record was last updated.")
    
    deleted = models.DateTimeField(
        blank=True,
        db_index=True,
        null=True,
        help_text="The date and time when this record was deleted.")
    
    class Meta:
        abstract = True
        
    def clean(self, *args, **kwargs):
        """
        Called to validate fields before saving.
        Override this to implement your own model validation
        for both inside and outside of admin. 
        """
        super(BaseModel, self).clean(*args, **kwargs)
        
    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(BaseModel, self).save(*args, **kwargs)

class BaseVote(BaseModel):
    """
    An abstract model for voting something up or down.
    """
    
    vote = models.IntegerField(
        choices=c.VOTE_CHOICES,
        blank=True,
        null=True
    )
    
    class Meta:
        abstract = True

    @property
    def vote_object(self):
        override
    
    @property
    def parent_target(self):
        """
        A parent object to the target, if any, which accumulates the votes from
        its children.
        """
        return
    
    @property
    def karma_field_name(self):
        override

    def save(self, *args, **kwargs):
        
        if not settings.IM_ALLOW_SELF_VOTE:
            assert self.voter != self.vote_object.creator, \
                'A person may not vote on their own record.'
        
        old_vote = None
        if self.id:
            old_vote = type(self).objects.get(id=self.id)
            
        parent_target = self.parent_target
        if parent_target:
            assert isinstance(parent_target, BaseVoteTarget), \
                'Parent vote target must inherit from BaseVoteTarget.'
            
        super(BaseModel, self).save(*args, **kwargs)
        
        # Update cached link vote totals.
        object_creator = self.vote_object.creator #or get_default_creator()
#        print '!'*80
#        print 'object_creator:',object_creator
#        print 'old_vote:',old_vote
        if old_vote:
            #print 'self.vote_object:',type(self.vote_object),self.vote_object
            if old_vote.vote != self.vote:
#                print 'vote changed'
                if old_vote.vote == c.UPVOTE:
                    self.vote_object.votes_up -= 1 #max(0, self.vote_object.votes_up - 1)
                    self.vote_object.votes_down += 1
                    if parent_target:
                        parent_target.votes_up -= 1
                        parent_target.votes_down += 1
                    if self.karma_field_name and object_creator:
                        setattr(
                            object_creator,
                            self.karma_field_name,
                            getattr(object_creator, self.karma_field_name)-2)
                else:
                    self.vote_object.votes_up += 1
                    self.vote_object.votes_down -= 1 #max(0, self.vote_object.votes_down - 1)
                    #object_creator.link_karma += 2
                    if parent_target:
                        parent_target.votes_up += 1
                        parent_target.votes_down -= 1
                    if self.karma_field_name and object_creator:
                        setattr(
                            object_creator,
                            self.karma_field_name,
                            getattr(object_creator, self.karma_field_name)+2)
                self.vote_object.save()
        else:
            # Record just created.
            if self.vote == c.UPVOTE:
                self.vote_object.votes_up += 1
                #object_creator.link_karma += 1
                if parent_target:
                    parent_target.votes_up += 1
                if self.karma_field_name and object_creator:
                    setattr(
                        object_creator,
                        self.karma_field_name,
                        getattr(object_creator, self.karma_field_name)+1)
            else:
                self.vote_object.votes_down += 1
                #object_creator.link_karma -= 1
                if parent_target:
                    parent_target.votes_down += 1
                if self.karma_field_name and object_creator:
                    setattr(
                        object_creator,
                        self.karma_field_name,
                        getattr(object_creator, self.karma_field_name)-1)
                    
            self.vote_object.save()
        
        if parent_target:
            parent_target.save()
        
        if object_creator:
            object_creator.save()

class BaseVoteTarget(object):
    """
    Base class inherited by all objects that are the target of up/down voting.
    """
    
#    votes_up = models.PositiveIntegerField(default=0)
#    
#    votes_down = models.PositiveIntegerField(default=0)
#    
#    weight = models.IntegerField(
#        default=0,
#        help_text='Count of up votes minus count of down votes.')

    def votable(self):
        request = middleware.get_current_request()
        return request and request.user.is_authenticated()
    
    @property
    def child_vote_targets(self):
        return
    
    @property
    def vote_type(self):
        override
    
    def update_votes(self, save=True):
        """
        Bulk updates cached vote totals.
        These are updated automatically when votes are created,
        so this shouldn't be necessary unless abusive or fraudulant votes
        have to be removed.
        """
        self.votes_up = self.votes.all().filter(vote=c.UPVOTE).count()
        self.votes_down = self.votes.all().filter(vote=c.DOWNVOTE).count()
        child_vote_targets = self.child_vote_targets
        if child_vote_targets:
            for child_vote_target in child_vote_targets:
                #print type(child_vote_target), child_vote_target.id
                assert isinstance(child_vote_target, BaseVoteTarget), \
                    'Child vote target %s must inherit from BaseVoteTarget.' \
                        % (child_vote_target,)
                self.votes_up += child_vote_target.votes.all().filter(vote=c.UPVOTE).count()
                self.votes_down += child_vote_target.votes.all().filter(vote=c.DOWNVOTE).count()
        if save:
            self.save()
        
    def upvoted(self):
        """
        Returns true if the current user upvoted the object.
        """
        user = middleware.get_current_user()
        return user and self.votes.filter(voter__user=user, vote=c.UPVOTE)
        
    def downvoted(self):
        """
        Returns true if the current user downvoted the object.
        """
        user = middleware.get_current_user()
        return user and self.votes.filter(voter__user=user, vote=c.DOWNVOTE)
        
    def update_vote_weight(self):
        """
        Updates the total vote weight.
        """
        self.update_votes(save=False)
        self.weight = self.votes_up - self.votes_down
        self.absolute_votes = self.votes_up + self.votes_down

class State(BaseModel):
    
    country = models.ForeignKey(
        'countries.Country',
        default=_get_default_country,
        blank=True, null=True)
    
    state = USStateField(blank=True, null=True)
    #TODO:extend to cover other countries/provinces?
    
    _state_name = models.CharField(
        max_length=300,
        verbose_name='state name',
        editable=False,
        blank=True,
        null=True)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('country', 'state'),
        )
        ordering = ('country', 'state')
    
    @property
    def state_name(self):
        return dict(STATE_CHOICES).get(self.state, self.state)
    
    def __unicode__(self):
        return '%s->%s' % (self.country, self.state)
    
    def save(self, *args, **kwargs):
        
        self._state_name = self.state_name
        
        super(State, self).save(*args, **kwargs)

class County(BaseModel):
    
    state = models.ForeignKey(
        State, blank=False, null=False)
    
    name = models.CharField(max_length=100, blank=False, null=False)
    
    class Meta:
        app_label = APP_LABEL
        verbose_name_plural = 'counties'
        unique_together = (
            ('state', 'name'),
        )
        ordering = ('state', 'name',)

class ContextManager(models.Manager):
    
    def get_active_public(self, q=None):
        if q is None:
            q = self
        return q.filter(active=True, public=True)

class Context(BaseModel):
    """
    A region or topic-specific thing used to segment other models.
    """
    
    objects = ContextManager()
    
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text='A unique description of this context. '\
            'Optional if the country/state/county is specified.')
    
    description = models.CharField(
        max_length=700,
        blank=True,
        null=True)
    
    slug = models.SlugField(max_length=700, blank=True, null=True)
    
    country = models.ForeignKey(
        'countries.Country',
        blank=True, null=True)
    
    state = models.ForeignKey(
        State, blank=True, null=True)
    
    county = models.ForeignKey(
        County, blank=True, null=True)
    
    active = models.BooleanField(default=True)
    
    public = models.BooleanField(default=True)
        
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'name',
            'description',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('name', 'country', 'state', 'county'),
        )
        ordering = ('name', 'country', 'state', 'county',)
    
    def __unicode__(self):
        if self.name:
            return self.name
        parts = [_ for _ in [self.country, self.state and self.state.state_name, self.county] if _]
        return u'->'.join(map(unicode, parts))
    
    @property
    def friendly_name(self):
        name = self.name
        name = name.replace('->', ' &rsaquo; ')
        return name
    
    @property
    def friendly_description(self):
        if self.country and not self.state and not self.county:
            return '%s national news' % (self.country.printable_name,)
        elif self.state and not self.county:
            return '%s news' % (self.state.state_name,)
        elif self.county:
            return '%s county news' % (self.county,)
    
    def clean(self, *args, **kwargs):
        super(Context, self).clean(*args, **kwargs)
        
        if not self.name:
            parts = []
            if self.country:
                parts.append(self.country.iso)
            if self.state:
                parts.append(self.state.state)
            if self.county:
                parts.append(self.county.name)
            self.name = u'->'.join(parts)
        
        if not self.description:
            parts = []
            if self.country:
                parts.append(self.country.printable_name)
                parts.append(self.country.iso3)
            if self.state:
                parts.append(self.state.state_name)
            if self.county:
                parts.append(self.county.name)
            self.description = u' '.join(parts)
        
        if not self.slug:
            parts = []
            if self.country:
                parts.append(self.country.iso.lower())
            if self.state:
                parts.append(self.state.state.lower())
            if self.county:
                parts.append(self.county.name.lower())
            self.slug = slugify(u'-'.join(parts))
        
        if not self.name and not self.country \
        and not self.state and not self.county:
            raise ValidationError, 'Either a name, country, state or county '\
                'must be specified. They cannot all be null.'
    
class PersonManager(models.Manager):
    
    def get_by_natural_key(self, user):
        return self.get_or_create(user=user)
    
    def get_online(self):
        return self.filter(last_seen__gt=timezone.now() - timedelta(minutes=5))
    
    def get_real(self, q=None, check_slug=True):
        if q is None:
            q = self
        q = q.filter(
            real=True,
            duplicate_of__isnull=True,
            deleted__isnull=True
        )
        if check_slug:
            q = q.exclude(slug__isnull=True).exclude(slug='')
        return q
        
    def get_active(self, q=None):
        if q is None:
            q = self
        return q.filter(active=True)
    
    def get_real_active(self, q=None):
        if q is None:
            q = self
        return self.get_real(self.get_active(q=q))
    
    def get_real_in_current_term(self):
        q = self.get_real()
        q = q.filter(
            terms__start_date__lte=timezone.now(),
            terms__end_date__gt=timezone.now()
        )
        return q
    
    def get_unused(self, days=None):
        """
        Retrieves person records created by anonymous users that
        have gone unused for a week or more and should be deleted.
        """
        #TODO:handle registered users that haven't been active in N time?
        #TODO:handle anonymous users who contributed something? unlink from related object?
        days = days or 7
        time_threshold = timezone.now()-timedelta(days=days)
        return self.filter(
            real=False,
            bot=False,
            user__isnull=True,
            updated__lt=time_threshold,
            terms__isnull=True,
            issues__isnull=True,
            url_votes__isnull=True,
            url_context_votes__isnull=True,
            link_votes__isnull=True,
            comment_votes__isnull=True,
            motion_votes__isnull=True,
        ).filter(
            Q(last_seen__isnull=True)|\
            Q(last_seen__isnull=False, last_seen__lt=time_threshold)
        ).distinct()
    
    def get_top(self):
        return self.get_real()\
            .filter(slug__isnull=False)\
            .order_by('-top_weight', 'rand')

class Person(BaseModel):
    
    objects = PersonManager()
    
    # This field optional so we can create temporary
    # person records for anonymous users.
    user = models.OneToOneField(
        'auth.User',
        unique=True,
        blank=True,
        null=True,
        help_text='For a non-real person, the authentication credentials '\
            'that allows them to login to the site.')
    
    bot = models.BooleanField(
        default=False,
        db_index=True,
        help_text='If checked, indicates this person represents '\
            'an automated script.')
    
    public = models.BooleanField(
        default=True,
        db_index=True,
        help_text='If checked, allows the public to see the person.')
    
    active = models.BooleanField(
        default=False,
        db_index=True,
        help_text='If checked, allows users to position the person.')
    
    creator = models.ForeignKey(
        'Person',
        blank=True,
        null=True,
        related_name='people_created',
        help_text='The person who created this person record.')
    
    # This will uniquely identify the person.
    # Primarily used with anonymous users that don't want to register.
    uuid = models.CharField(
        max_length=32,
        default=lambda:str(uuid.uuid4()).replace('-',''),
        unique=True,
        db_index=True,
        editable=False,
        blank=False,
        null=False,
        help_text="This person's secret universally unique identifier.")
    
    nickname = models.CharField(
        max_length=100,
        blank=True,
        null=True)
    
    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        editable=False,
        help_text="The date and time when this person was last seen on the site.")
    
    last_url_vote = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        editable=False,
        help_text="The date and time of their most recent URL vote.")
    
    real = models.BooleanField(
        db_index=True,
        default=False,
        help_text='If checked, represents a real unique verified person.')

    link_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
        help_text='''The total sum of all votes made on the peron\'s
            submitted links.''')

    url_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
        help_text='''The total sum of all votes made on the peron\'s
            submitted urls.''')

    @property
    def visible_link_karma(self):
        return max(self.link_karma, 0)

    issue_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
        help_text='''The total sum of all positions made on the peron\'s
            submitted issues.''')

    @property
    def visible_issue_karma(self):
        return max(self.issue_karma, 0)

    comment_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text='''The total sum of all votes made on the peron\'s
            submitted position comments.''')

    @property
    def visible_comment_karma(self):
        return max(self.comment_karma, 0)

    extra_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
        help_text='''Extra karma manually rewarded by a site admin for
            miscellaneous reasons.''')

    total_karma = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True,
        editable=False,
        help_text='''The total karma from all karma sources.''')

    photo = models.ImageField(
        upload_to='uploads/person/photo', blank=True, null=True)
    
    photo_thumbnail = models.ImageField(
        upload_to='uploads/person/photo_thumbnail', blank=True, null=True)

    photo_checked = models.BooleanField(default=False)

    slug = models.SlugField(
        max_length=1000,
        blank=True,
        null=True,
        help_text='firstname-middlename-lastname-suffix-yearborn')
    
    first_name = models.CharField(
        max_length=1000, blank=True, null=True)
    
    first_name_is_initial = models.BooleanField(
        default=False)
    
    middle_name = models.CharField(
        max_length=1000, blank=True, null=True)
    
    middle_name_is_initial = models.BooleanField(
        default=False)
    
    last_name = models.CharField(
        max_length=1000, blank=True, null=True)
    
    suffix_abbreviation = models.CharField(
        choices=c.SUFFIX_ABBREVIATION_CHOICES,
        max_length=1000, blank=True, null=True)
    
    year_born = models.IntegerField(
        blank=True, null=True,
        help_text='The year this person was born.')
    
    birthday = models.DateField(
        blank=True, null=True,
        help_text='The date this person was born.')
    
    year_died = models.IntegerField(blank=True, null=True,
        help_text='The year this person died.')

    passed_date = models.DateField(
        blank=True, null=True,
        help_text='The date this person died.')
    
    wikipedia_page = models.URLField(
        blank=True, null=True,
        help_text='This person\'s page on wikipedia.org.')
    
    wikipedia_page_confirmed = models.BooleanField(
        default=False,
        help_text='''If checked, indicates the Wikipedia page URL
            has been manually confirmed.''')
    
    wikipedia_checked = models.BooleanField(
        default=False,
        help_text='If checked, indicates the associated Wikipedia URL '\
            'was scrapped for data.')

    gender = models.CharField(
        choices=c.GENDER_CHOICES,
        default=c.UNKNOWN,
        max_length=10,
        db_index=True,
        blank=True,
        null=True)
    
    govtrack_id = models.PositiveIntegerField(
        blank=True, null=True, db_index=True,
        help_text='The unique ID used to track this person on govtrack.us.')
    
    cspan_id = models.PositiveIntegerField(
        blank=True, null=True, db_index=True,
        help_text='The unique ID used to track this person on C-Span.')
    
    twitter_id = models.CharField(
        max_length=100, blank=True, null=True, db_index=True,
        help_text='The unique ID used to track this person on twitter.com.')
    
    youtube_id = models.CharField(
        max_length=100, blank=True, null=True, db_index=True,
        help_text='The unique ID used to track this person on youtube.com.')
    
    os_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    
    pvs_id = models.CharField(
        max_length=100, blank=True, null=True, db_index=True,
        help_text='The unique ID used to track this person on votesmart.org.')
    
    bioguide_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    
    openstate_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    
    ontheissues_page = models.URLField(
        blank=True, null=True,
        help_text='This person\'s URL on ontheissues.org.')
    
    ontheissues_page_confirmed = models.BooleanField(
        default=False,
        help_text='If checked, indicates the validity of the ontheissues_page URL was manually confirmed.')
    
    govtrack_page = models.URLField(blank=True, null=True,
        help_text='This person\'s URL on govtrack.us.')
    
    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='duplicates',
        blank=True,
        null=True,
        help_text='''If given, indicates this record is an unnecessary full
            or near duplicate of the record specified. Once marked as such,
            this record will not appear on the site and all associated records
            will be merged with the original.''')
    
    duplicate_merged = models.DateTimeField(blank=True, null=True, db_index=True)

    issue_link_count = models.PositiveIntegerField(
        default=0,
        db_index=True)

    position_count = models.PositiveIntegerField(
        default=0,
        db_index=True)

    needs_review = models.BooleanField(default=False,
        help_text='If checked, indicates this data should be manually checked.')

    download_from_wikipedia = models.BooleanField(default=False,
        help_text='''If checked, and the Wikipedia URL is set, the page will be
            downloaded and empty fields (like photo and birthday) will be
            automatically set.''')
    
    default_notification_method = models.CharField(
        max_length=25,
        choices=c.NOTIFICATION_CHOICES,
        default=c.EMAIL_NOTIFICATION,
        blank=True,
        null=True)

    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True)
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
    
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'nickname',
            'first_name',
            'middle_name',
            'last_name',
            'slug',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('slug', 'real', 'deleted'),
        )
        ordering = ('-top_weight', 'rand',)
        
        permissions = (
            (c.PERM_PERSON_SUBMIT, u'Publically submit a person to be tracked.'),
            (c.PERM_PERSON_FLAG, u'Flag a person for moderation.'),
        )

    @property
    def most_recent_term(self):
        q = self.terms.all().order_by('-end_date')
        if q.count():
            return q[0]

    def update_position_count(self):
        self.position_count = self.positions.count()

    def urls_submitted(self):
        return self.url_contexts_created.all().count()
    
    def urls_voted_on(self):
        return self.url_context_votes.all().count()
    
    def issue_tags_created(self):
        return self.links.all().filter(issue__isnull=False).count()
    
    def issue_tags_voted_on(self):
        return self.link_votes.all().filter(link__issue__isnull=False).count()
    
    def person_tags_created(self):
        return self.links.all().filter(person__isnull=False).count()
    
    def person_tags_voted_on(self):
        return self.link_votes.all().filter(link__person__isnull=False).count()
    
    def flags_created_count(self):
        return self.flags_created.all().count()
    
    @property
    def object(self):
        return self

    def is_duplicate(self):
        return bool(self.duplicate_of)
    is_duplicate.boolean = True

    @property
    def has_pending_action(self):
        q = self.unpositioned_issues()
        if q.count():
            return True
        return False

    @property
    def pending_action_name(self):
        q = self.unpositioned_issues()
        if q.count():
            return '%i unpositioned issues' % (q.count(),)
        return False

    @property
    def pending_action_url(self):
        q = self.unpositioned_issues()
        if q.count():
            q = q.order_by('?')
            return q[0].get_absolute_url()
        return False

    @property
    def unread_reply_count(self):
        q = Comment.objects.filter(
            comment__creator=self,
            read=False,
            deleted__isnull=True,
            comment__deleted__isnull=True)
        return q.count()

    @property
    def last_term_title(self):
        q = self.terms.all().order_by('-end_date')
        if not q.count():
            return ''
        term = q[0]
        #return '%s %s' % (term.country, term.role)
        if term.role.slug in ('senator', 'representative') and term.state:
            if term.party:
                return '%s, %s - %s' % (term.role, term.state, term.party)
            else:
                return '%s, %s' % (term.role, term.state)
        elif 'president' in term.role.slug:
            return '%s - %s' % (term.role, term.party)
        elif 'governor' in term.role.slug:
            return '%s %s' % (dict(USPS_CHOICES).get(term.state, term.state), term.role)
        return '%s' % (term.role,)

    @classmethod
    def delete_unused(cls, dryrun=False, days=None, *args, **kwargs):
        """
        Permanently deletes all unused anonymous person records.
        """
        if days:
            days = int(days)
        q = cls.objects.get_unused(days=days)
        total = q.count()
        if dryrun:
            print total
            return
#        print 'Deleting %i records...' % (total,)
        q.delete(); return #TODO:?
        i = 0
        for p in q.iterator():
            i += 1
            print_status(
                top_percent=(i/float(total)*100),
                sub_percent=None,
                message='%i of %i' % (i, total),
                max_message_length=100,
                newline=False)
            p.delete()

    def is_motionable(self, attr):
#        if attr in (,):
#            return True
        return False
    
    @classmethod
    def merge_all(cls, *args, **kwargs):
        q = cls.objects.get_real_active()
        q = q.filter(duplicates__id__isnull=False, duplicates__duplicate_merged__isnull=True)
        print 'Total:',q.count()
        
        copy_if_blank_fields = (
            'wikipedia_page',
            'year_born',
            'birthday',
            'photo_thumbnail',
            'nickname',
            'first_name',
            'middle_name',
            'last_name',
            'suffix_abbreviation',
            'slug',
            'year_died',
            'passed_date',
            'gender',
            'govtrack_id',
            'cspan_id',
            'twitter_id',
            'youtube_id',
            'os_id',
            'pvs_id',
            'bioguide_id',
            'openstate_id',
            'govtrack_page',
        )
        
        for person in q:
            duplicates = person.duplicates.all().filter(duplicate_merged__isnull=True)
            print person.id, person, [(pd.id, pd) for pd in duplicates]
            
            for duplicate in duplicates:
                
                print 'Copying terms...'
                for term in duplicate.terms.all():
                    try:
                        term.person = person
                        term.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
#                        django.db.transaction.rollback()
#                        django.db.connection.rollback()
#                        django.db.connection.close()
                        pass
                
                print 'Copying links...'
                for link in duplicate.issue_links.all():
                    try:
                        link.person = person
                        link.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying positions...'
                for position in duplicate.positions.all():
                    try:
                        position.person = person
                        position.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying motions...'
                for motion in duplicate.motions.all():
                    try:
                        motion.person = person
                        motion.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying flags...'
                for flag in duplicate.flags.all():
                    try:
                        flag.person = person
                        flag.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying matches...'
                for match in duplicate.matched_with.all():
                    try:
                        match.matchee = person
                        match.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying feeds...'
                for feed in duplicate.feeds.all():
                    try:
                        feed.person = person
                        feed.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying quotes...'
                for quote in duplicate.quotes.all():
                    try:
                        quote.person = person
                        quote.save()
                    except IntegrityError, e:
                        print e
                        connection._rollback()
                        pass
                
                print 'Copying fields...'
                for field in copy_if_blank_fields:
                    if getattr(person, field) in ('', None) and getattr(duplicate, field) not in ('', None):
                        setattr(person, field, getattr(duplicate, field))
                person.save()
                
                duplicate.duplicate_merged = timezone.now()
                duplicate.active = False
                duplicate.public = False
                duplicate.save()
    
    def update_top_weight(self):
        back = 30.
        top_weight = self.top_weight = 0.
        links = self.issue_links.all()\
            .filter(created__gte=timezone.now()-timedelta(days=back))
        if not links:
            return
        #print 'links:',links.count()
        for link in links:
            top_weight += 1 - (timezone.now() - link.created).days/float(back)
        self.top_weight = top_weight
        #print 'top_weight0:',self.top_weight

    @classmethod
    def update_weights(cls, **kwargs):
        q = cls.objects.get_real().filter(active=True, issue_links__id__isnull=False)
        total = q.count()
        i = 0
        for person in q:
            i += 1
            print '%i of %i' % (i, total)
            #person.update_top_weight()
            person.save()
            print 'top_weight1:',person.top_weight

    @property
    def current_user_match(self):
        """
        Returns the match record for this person and the current user.
        """
        request = middleware.get_current_request()
        if not request.user.is_authenticated():
            return
        try:
            person = Person.objects.get(user=request.user)
        except Person.DoesNotExist:
            return
        try:
            match = Match.objects.get(matcher=person, matchee=self)
        except Match.DoesNotExist:
            return
        return match

    def has_current_user_match(self):
        match = self.current_user_match
        return match is not None

    def current_user_match_ratio(self):
        match = self.current_user_match
        if match is not None:
            return match.value

    def current_user_match_percent(self):
        match = self.current_user_match
        if match is not None:
            return match.value*100

    def current_user_match_issues(self):
        request = middleware.get_current_request()
        if not request.user.is_authenticated():
            return
        q = Position.objects.filter(
            creator__user=request.user,
            person__user=request.user,
            deleted__isnull=True,
            issue__id__in=Position.objects.filter(
                person=self,
                deleted__isnull=True,
            ).values_list('issue__id', flat=True).distinct()
        ).values_list('issue', flat=True)
        return q

    def useful_links(self):
        lst = []
        if self.govtrack_page:
            lst.append((self.govtrack_page, 'Govtrack Profile'))
        if self.wikipedia_page:
            lst.append((self.wikipedia_page, 'Wikipedia Page'))
        return lst

    def all(self):
        return [self]
    
    def get_admin_url(self):
        return get_admin_change_url(self)
        
    def get_absolute_url(self):
        return reverse('person', args=(self.slug,))

    def __unicode__(self):
        if self.user:
            return unicode(self.user).strip()
        elif self.nickname and not self.real:
            return self.nickname.strip()
        dn = self.display_name_long
        if dn != 'anonymous':
            return dn.strip()
        return unicode(self.uuid).strip()
    
    def natural_key(self):
        return (self.user.natural_key(),)
    natural_key.dependencies = ['auth.user']
    
    @property
    def display_name(self):
        if self.slug:
            return self.slug.replace('-', ' ').title()
        elif self.nickname:
            if self.last_name:
                return self.nickname + ' ' + self.last_name
            else:
                return self.nickname
        elif self.user:
            return self.user.username
        elif self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        else:
            return 'anonymous'
    
    @property
    def display_name_long(self):
        return '%s %s %s %s' % (
            self.first_name or '',
            self.middle_name or '',
            self.last_name or '',
            self.birthday or ''
        )
    
    @property
    def has_unpositioned_issues(self):
        return self.unpositioned_issues.count() > 0
    
    @property
    def has_unpositioned_issues(self):
        return self.unpositioned_issues.count() > 0
    
    @property
    def unpositioned_issues(self):
        return Issue.objects.get_unpositioned_by(self.user)
    
    @property
    def positioned_issues_with_updates(self):
        return Issue.objects.get_positioned_by_with_updates(self.user)
    
    @property
    def positioned_issues(self):
        return Issue.objects.get_positioned_by(self.user)
    
    def flagged(self):
        user = middleware.get_current_user()
        if not user.is_authenticated():
            return False
        person = user.person
        q = Flag.objects.filter(person=self, flagger=person)
        return bool(q.count())
    
    def update_karma(self):
        """
        Bulk updates all karma scores for the person.
        """
        self.link_karma = self.links.all()\
            .aggregate(Sum('weight'))['weight__sum'] or 0
        self.issue_karma = self.issues.all()\
            .aggregate(Sum('position_count'))['position_count__sum'] or 0
        self.url_karma = self.urls.all()\
            .aggregate(Sum('weight'))['weight__sum'] or 0
        self.save()
    
    @classmethod
    def register_feeds(cls, **kwargs):
        """
        Attempts to creates a feed for every real person
        in a current term.
        """
        #q = cls.objects.get_real_in_current_term()\
        q = cls.objects.get_real_active()\
            .exclude(id__in=Feed.objects\
                .filter(person__isnull=False, account__active=True)\
                .values_list('person_id', flat=True))\
            .distinct()
        total = q.count()
        print 'Total:',total
        i = 0
        for person in q:
            i += 1
            print '%i of %i' % (i, total)
            accounts = FeedAccount.objects.get_unfilled().order_by('?')
            if not accounts.count():
                print 'No unfilled accounts.'
                return
            account = accounts[0]
            query = account.get_query(person=person)
            Feed.objects.get_or_create(
                account=account,
                person=person,
                defaults=dict(query=query),
            )
            account.save()
            #time.sleep(random.randint(1,5))
    
    def load_wikipedia_photo(self, show_messages=False):
        from django.core import files
        from pyquery import PyQuery as pq
        from lxml import etree
        from webarticle2text import tidyHTML
        from PIL import Image
        from cStringIO import StringIO
        
        request = middleware.get_current_request()
        
        self.photo_checked = True
        try:
            print 'wikipedia_page:',self.wikipedia_page
            html = scrapper.get(url=self.wikipedia_page)
            html = unicode(html, encoding='ascii', errors='ignore')
            
            # Check for birthdate.
            if not self.birthday:
                bd_matches = re.findall(r'\(\s*born\s+([^\)]+)\)', html, flags=re.IGNORECASE)
                print 'bd_matches:',bd_matches
                if bd_matches:
                    self.birthday = dateutil.parser.parse(bd_matches[0])
                    if show_messages:
                        messages.add_message(request, messages.SUCCESS, 'Set birthday.')
            
            d = pq(etree.fromstring(html))
            p = d('.infobox a.image img')# a.image img')
            if not p:
                print>>sys.stderr, 'Infobox not found.'
                return
            image_src = p.attr('src')
            if not image_src:
                print>>sys.stderr, 'Infobox image src not found'
                return
            image_src_parts = re.split('(?<=\.[a-z]{3})/', image_src)
            image_src = 'http:' + ('/'.join(image_src_parts[:-1]))
            image_url = image_src.replace('/thumb', '')
            print 'image_url:',image_url
            #break
            image_data = scrapper.get(url=image_url)
            
            image_file = files.temp.NamedTemporaryFile(
                dir=files.temp.gettempdir()
            )
            image_file.write(image_data)
            image_file.seek(0)
            self.photo = files.File(image_file)
            
            PIL_TYPE = 'jpeg'
            THUMBNAIL_SIZE = (200, 200)
            try:
                image = Image.open(StringIO(image_data))
                image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                temp_handle = StringIO()
                image.save(temp_handle, PIL_TYPE)
                temp_handle.seek(0)
                image_file = files.temp.NamedTemporaryFile(
                    dir=files.temp.gettempdir()
                )
                image_file.write(temp_handle.getvalue())
                image_file.seek(0)
                self.photo_thumbnail = files.File(image_file)
                print>>sys.stderr, 'Success!'
                if show_messages:
                    messages.add_message(request, messages.SUCCESS, 'Set photo.')
            except IOError, e:
                print>>sys.stderr, 'Failed to load %s: %s' % (self, e)
                if show_messages:
                    messages.add_message(request, messages.ERROR, str(e))
        except ValueError, e:
            print>>sys.stderr, 'ValueError: %s' % (e,)
            if show_messages:
                messages.add_message(request, messages.ERROR, str(e))
        except urllib2.HTTPError, e:
            print>>sys.stderr, 'HTTPError: %s' % (e,)
            if show_messages:
                messages.add_message(request, messages.ERROR, str(e))
    
    @classmethod
    def load_photo(cls, person_ids=None, **kwargs):
        q = cls.objects.get_real().filter(
            #photo_checked=False,
            photo='',
            terms__end_date__gte=date.today(),
            wikipedia_page__isnull=False
        )
        if person_ids:
            q = q.filter(id__in=map(int, person_ids))
        total = q.count()
        i = 0
        for person in q:
            i += 1
            print '%i of %i' % (i, total)
            time.sleep(random.randint(1, 5))
            person.load_wikipedia_photo(show_messages=True)
            person.save()
    
    def _generate_photo_thumbnail(self, show_messages=False):
        if self.photo_thumbnail:
            return
        elif not self.photo:
            return
        
        try:
            from django.core import files
            from PIL import Image
            from cStringIO import StringIO
            image_data = self.photo.read()
            PIL_TYPE = 'jpeg'
            THUMBNAIL_SIZE = (200, 200)
    #        try:
            image = Image.open(StringIO(image_data))
            image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
            temp_handle = StringIO()
            image.save(temp_handle, PIL_TYPE)
            temp_handle.seek(0)
            image_file = files.temp.NamedTemporaryFile(
                dir=files.temp.gettempdir()
            )
            image_file.write(temp_handle.getvalue())
            image_file.seek(0)
            self.photo_thumbnail = files.File(image_file)
    #        except IOError, e:
    #            print>>sys.stderr, 'Failed to generate thumbnail: %s' % (e,)
        except IOError, e:
            request = middleware.get_current_request()
            if show_messages and request:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                raise
    
    def update_wikipedia_page(self, **kwargs):
        """
        Attempts to guess the person's Wikipedia page.
        """
        BASE_URL = u'http://en.wikipedia.org'
        SEARCH_URL_TEMPLATE = u'http://en.wikipedia.org/w/index.php?title=Special%%3ASearch&profile=default&search=%(full_name)s&fulltext=Search'
        SEARCH_RESULT_URL = re.compile(u'<div\s+class=[\'"]mw-search-result-heading[\'"]>\s*<a\s+(?:title="[^"]+"\s+)?href="([^"]+)"', re.MULTILINE|re.DOTALL)
        
        url = SEARCH_URL_TEMPLATE % dict(full_name=self.display_name.replace(' ', '+'))
        #url = unicode(url, encoding='ascii', errors='ignore')
        url = url.encode("UTF-8")
        print 'URL:',url
        html = scrapper.get(url=url)
        #print html[:1000]
        html = unicode(html, encoding='ascii', errors='ignore')
        matches = SEARCH_RESULT_URL.findall(html)#[:top_n]
        print 'matches:',matches
        if matches:
            self.wikipedia_page = BASE_URL + matches[0]
            print self.wikipedia_page
            
    @classmethod
    def update_all_wikipedia(cls, ids=[], force=False, **kwargs):
        """
        Attempts to guess the person's Wikipedia page.
        """
        BASE_URL = u'http://en.wikipedia.org'
        SEARCH_URL_TEMPLATE = u'http://en.wikipedia.org/w/index.php?title=Special%%3ASearch&profile=default&search=%(full_name)s&fulltext=Search'
        SEARCH_RESULT_URL = re.compile(u'<div\s+class=[\'"]mw-search-result-heading[\'"]>\s*<a\s+(?:title="[^"]+"\s+)?href="([^"]+)"', re.MULTILINE|re.DOTALL)
        q = cls.objects.get_real(check_slug=False).filter(Q(wikipedia_page__isnull=True)|Q(wikipedia_page__isnull=False, wikipedia_page=''))
        if not force:
            q = q.filter(wikipedia_checked=False)
        if ids:
            q = q.filter(id__in=ids)
        total = q.count()
        print 'Total:',total
        i = 0
        for person in q:
            i += 1
            print '%i of %i' % (i, total)
            
            url = SEARCH_URL_TEMPLATE % dict(full_name=person.display_name.replace(' ', '+'))
            #url = unicode(url, encoding='ascii', errors='ignore')
            url = url.encode("UTF-8")
            print 'URL:',url
            html = scrapper.get(url=url)
            #print html[:1000]
            html = unicode(html, encoding='ascii', errors='ignore')
            matches = SEARCH_RESULT_URL.findall(html)#[:top_n]
            print 'matches:',matches
            if matches:
                person.wikipedia_page = BASE_URL + matches[0]
                print person.wikipedia_page
            person.wikipedia_checked = True
            person.save()
    
    @classmethod
    def load_csv(cls, fn, real=False, dryrun=False, assume_missing=False, **kwargs):
        commit = True
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        
        get_slugs = [
            lambda row: ('%s-%s' % (row['nickname'],row['last_name'])).lower() if row['nickname'] else None,
            lambda row: ('%s-%s' % (row['first_name'],row['last_name'])).lower(),
            #lambda row: ('%s-%s-%s' % (row['first_name'],row['middle_name'],row['last_name'])).lower(),
            lambda row: ('%s-%s-%s' % (row['first_name'],row['last_name'],row['suffix_abbreviation'])).lower(),
        ]
#        print Person.objects.all().count()
#        return
        try:
            reader = csv.DictReader(open(fn))
            i = 0
            headers = [
                'slug','nickname','first_name','first_name_is_initial','middle_name',
                'middle_name_is_initial','last_name','suffix_abbreviation',
                'year_born','year_died','link'
            ]
            for row in reader:
                i += 1
                if i == 1:
                    assert set(row.keys()) == set(headers), 'Invalid headers: %s' % (set(row.keys()).difference(headers),)
                print i
                link_url = row['link'].strip() or None
                data = dict(
                    (k,v if v.strip() else None)
                    for k,v in row.iteritems()
                )
                data['first_name_is_initial'] = {'True':True, 'False':False}[data['first_name_is_initial']]
                data['middle_name_is_initial'] = {'True':True, 'False':False}[data['middle_name_is_initial']]
                data['real'] = real
                del data['link']
                data['wikipedia_page'] = link_url
                if assume_missing:
                    found = False
                    for slug_getter in get_slugs:
                        slug = (slug_getter(row) or '').strip()
                        slug = re.sub('[^a-z0-9]+$', '', slug)
                        slug = re.sub('^[^a-z0-9]+', '', slug)
                        if not slug:
                            continue
                        data['slug'] = slug
                        try:
                            obj = cls.objects.get(slug=slug, real=real)
                            continue
                        except cls.DoesNotExist:
                            obj = cls.objects.create(**data)
                            found = True
                            break
                    if not found:
                        continue
                    #break
                else:
                    try:
                        obj = cls.objects.get(slug=row['slug'], real=real)
                    except cls.DoesNotExist:
                        obj = cls.objects.create(**data)
                obj.wikipedia_page = link_url
                obj.save()
        except Exception, e:
            commit = False
            print e
            raise
        finally:
            settings.DEBUG = tmp_debug
            if commit and not dryrun:
                print 'Committing...'
                django.db.transaction.commit()
            else:
                print 'Rolling back...'
                django.db.transaction.rollback()
            django.db.transaction.leave_transaction_management()
        print 'Done.'
    
    @classmethod
    def load_govtrack(cls, dryrun=False, current=True, **kwargs):
        """
        Loads US federal senators and representatives via the Govtrack.us API.
        """
        from math import ceil
        
        usps_abbr = set(dict(USPS_CHOICES).keys())
        
        current_str = 'current=true' if current else ''
        
        print 'Loading previous govtrack_ids...'
        current_govtrack_ids = set(cls.objects.all().exclude(govtrack_id__isnull=True).values_list('govtrack_id', flat=True))
        print '%i govtrack_ids loaded.' % (len(current_govtrack_ids),)
        #raw_input()
        
        def get(url, user_agent = 'IssueBot9000'):
            req = urllib2.Request(url, None, {'user-agent':user_agent})
            opener = urllib2.build_opener()
            f = opener.open(req)
            return simplejson.load(f)
        
        def get_meta():
            json = get("http://www.govtrack.us/api/v2/role?" + current_str)
            meta = json['meta']
            limit = meta['limit']
            offset = meta['offset']
            total_count = meta['total_count']
            return limit, offset, total_count
        
        def iter_people():
            limit, offset, total_count = get_meta()
            pages = int(ceil(total_count/float(limit)))
            print limit, offset, total_count
            print pages
            i = 0
            for page in xrange(pages):
                offset = page*limit
                json = get(("http://www.govtrack.us/api/v2/role?"+current_str+"&offset=%i") % (offset,))
                objects = json['objects']
                for row in objects:
                    #print sorted(row.keys())
                    #yield row['person']['firstname'],row['person']['middlename'],row['person']['lastname']
                    i += 1
                    govtrack_id = int(row['person']['id'])
                    if govtrack_id in current_govtrack_ids:
                        print 'Skipping previously imported govtrack_id: %s' % (govtrack_id,)
                        continue
                    yield i, row
                #return
        
        def collect_data(row):
            data = dict((k1, row['person'][k0]) for k0,k1 in govtrack_to_native.iteritems())
            for k,v in data.items():
                if isinstance(v, basestring):
                    data[k] = unicode(v.strip())
            data['birthday'] = dateutil.parser.parse(data['birthday']) if data['birthday'] else None
            data['middle_name_is_initial'] = len(data['middle_name']) == 1 or data['middle_name'].strip().endswith('.')
            #data['middle_name'] = re.sub('[^a-zA-Z\s\-]+', '', data['middle_name'])
            #print data['middle_name']
            data['real'] = True
            return data
        
        def create_term(person):
            url = 'http://www.govtrack.us/api/v2/person/%i' % person.govtrack_id
            print url
            json = get(url)
            #print json
            roles = json['roles']
            #usps_abbr
            for role in roles:
                
                party = None
                if role['party']:
                    party, _ = Party.objects.get_or_create(
                        slug=slugify(unicode(role['party'])),
                        defaults=dict(name=role['party']))
                
                robj, _ = Role.objects.get_or_create(
                    slug=slugify(unicode(role['role_type'])),
                    defaults=dict(name=role['role_type_label']))
                
                start_date = role['startdate'].strip()
                assert start_date
                start_date = dateutil.parser.parse(start_date)
                end_date = role['enddate'].strip()
                assert end_date
                end_date = dateutil.parser.parse(end_date)
                
                state = role['state'].strip() or None
#                assert not state or state in usps_abbr, \
#                    'Invalid state abbreviation: %s' % (state,)
                if not state or state not in usps_abbr:
                    print 'Invalid state abbreviation: %s' % (state,)
                    continue
                
                term, _ = Term.objects.get_or_create(
                    person=person,
                    party=party,
                    role=robj,
                    start_date=start_date,
                    end_date=end_date,
                    defaults=dict(
                        senator_class=role['senator_class'],
                        district=role['district'],
                        state=state,
                        website=role['website'],
                    )
                )
        
        # These fields will be overwritten by Govtrack, no matter
        # what's there already.
        override_fields = (
            'govtrack_id',
            'cspan_id',
            'twitter_id',
            'youtube_id',
            'os_id',
            'pvs_id',
            'bioguide_id',
            'govtrack_page',
        )
        
        # These fields will be set by Govtrack only if they're currently blank.
        default_fields = set([
            'gender',
            'middle_name',
        ])
        
        # This translates Govtrack's field names to ours.
        govtrack_to_native = dict(
            firstname='first_name',
            middlename='middle_name',
            lastname='last_name',
            id='govtrack_id',
            link='govtrack_page',
            birthday='birthday',
            cspanid='cspan_id',
            twitterid='twitter_id',
            youtubeid='youtube_id',
            osid='os_id',
            pvsid='pvs_id',
            bioguideid='bioguide_id',
            gender='gender',
            nickname='nickname',
        )
        
        commit = True
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        new_people = 0
        old_people = 0
        ambiguous_people = 0
        try:
            for i, row in iter_people():
                print i, row['person']#['firstname'],row['person']['middlename'],row['person']['lastname']
                if not i % 10:
                    print 'Committing...'
                    django.db.transaction.commit()
                birthday = None
                if row['person']['birthday']:
                    birthday = dateutil.parser.parse(row['person']['birthday'])
                q = Person.objects.filter(
                    first_name=row['person']['firstname'],
                    last_name=row['person']['lastname'],
                    real=True,
                )
                if birthday:
                    q = q.filter(year_born=birthday.year)
                person = None
                if q.count():
                    person = q[0]
                do_update = False
                if q.count() == 0:
                    # Create new person record.
                    print 'Creating...'
                    new_people += 1
                    
                    data = collect_data(row)
                    person = Person(**data)
                    person.save()
                    if person.duplicate_of:
                        person = person.duplicate_of
                        do_update = True
                    print person.id
                    
                if do_update or q.count() == 1:
                    # Update existing person record.
                    print 'Updating...'
                    old_people += 1
                    
                    data = collect_data(row)
                    _priors = set()
                    while 1:
                        if person.duplicate_of and person not in _priors:
                            _priors.add(person)
                            person = person.duplicate_of
                        else:
                            break
                    for k,v in data.items():
                        if k in default_fields and getattr(person, k, None) is not None:
                            continue
                        setattr(person, k, v)
                    person.save()
                    
                else:
                    ambiguous_people += 0
                
                # Load term/role/party.
                if person:
                    create_term(person=person)
                    
        except Exception, e:
            commit = False
            print e
            raise
        finally:
            settings.DEBUG = tmp_debug
            if commit and not dryrun:
                print 'Committing...'
                django.db.transaction.commit()
            else:
                print 'Rolling back...'
                django.db.transaction.rollback()
            django.db.transaction.leave_transaction_management()
        print 'Done.'
        print '-'*80
        print 'new:',new_people
        print 'old:',old_people
        print 'ambiguous:',ambiguous_people
    
    @classmethod
    def load_openstates(cls, dryrun=False, **kwargs):
        """
        Loads US state senators and representatives via the Openstates.org API.
        """
        from countries.models import Country
        country = Country.objects.get(iso='US')

        def get(url, user_agent = 'IssueBot9000'):
            req = urllib2.Request(url, None, {'user-agent':user_agent})
            opener = urllib2.build_opener()
            f = opener.open(req, timeout=5)
            return simplejson.load(f)
        
        def get_legislator(id):
            url = 'http://openstates.org/api/v1/legislators/{id}/?apikey={apikey}'\
                .format(
                    id=id,
                    apikey=settings.SUNLIGHT_API_KEY,
                )
            data = get(url)
            return data
        
        def get_terms(id):
            data = get_legislator(id)
            roles = data['roles']
#            "term": "2011-2014",
#            "end_date": null,
#            "district": "1",
#            "chamber": "upper",
#            "state": "al",
#            "party": "Democratic",
#            "type": "member",
#            "start_date": null
            for role in roles:
                if role['type'] != 'member':
                    continue
                
                years = re.findall('([0-9]+)\-([0-9]+)', role['term'])
                start_date = role['start_date']
                end_date = role['end_date']
                if not start_date and years:
                    start_date = date(int(years[0][0]), 1, 1)
                    end_date = date(int(years[0][1]), 1, 1)
                
                role_obj = Role.objects.get(
                    slug=('senator' if role['chamber']=='upper' else 'representative'),
                    level=c.ROLE_LEVEL_STATE)
                
                party_obj = Party.objects.get(slug=role['party'].lower())
                
                yield dict(
                    start_date=start_date,
                    end_date=end_date,
                    district=role['district'],
                    party=party_obj,
                    role=role_obj,
                    url=data.get('url', ''),
                )
        
        def iter_people(state, chamber):
            assert len(state) == 2
            assert chamber in ('upper', 'lower')
            #http://openstates.org/api/v1/legislators/?state=dc&chamber=upper&apikey=5cbde0c917d34c6fa98e3aa31d129e42
            url = 'http://openstates.org/api/v1/legislators/?state={state}&chamber={chamber}&active=true&apikey={apikey}'\
                .format(
                    state=state.lower(),
                    chamber=chamber.lower(),
                    apikey=settings.SUNLIGHT_API_KEY,
                )
            i = 0
            for row in get(url=url):
                i += 1
                yield i, row
        
        total = len(USPS_CHOICES)*2
        current_i = 0
        for state_code, state_name in sorted(USPS_CHOICES):
            for chamber in ('upper', 'lower'):
                current_i += 1
                JobModel.update_progress(total_parts=total, total_parts_complete=current_i)
                print state_code, chamber
#                if state_code < 'WV':#TODO:remove
#                    continue
                for i, row in iter_people(state=state_code, chamber=chamber):
                    pprint(row, indent=4)
                    profile = get_legislator(row['id'])
                    pprint(profile, indent=4)
                    
                    #assert row['country'] == 'us', 'Unknown country: %s' % (row['country'],)
                    #assert row['level'] == 'state', 'Unknown level: %s' % (row['level'],)
                    assert row['active'], 'Person not active.'
                    
                    photo_url = row.get('photo_url', row.get('+photo_url', ''))
                    district = row.get('district', row.get('+district', ''))
                    openstate_id = row['id']
                    
                    person_data = dict(
                        first_name = row['first_name'].split(' ')[0].strip(),
                        middle_name = row['middle_name'].strip(),
                        last_name = row['last_name'].split(' ')[0].strip(),
                        nickname = profile.get('nickname', row.get('nickname', u'')).strip(),
                        pvs_id = row.get('votesmart_id', ''),
                        photo_thumbnail = get_thumbnail_from_url(photo_url) if photo_url else None,
                        openstate_id = openstate_id,
                        active=True,
                        public=True,
                        real=True,
                    )
                    person_data['photo_checked'] = bool(person_data['photo_thumbnail'])
                    for k, v in person_data.items():
                        if not isinstance(v, basestring):
                            continue
                        person_data[k] = force_text(person_data[k])
                    party = row.get('party', row.get('+party', ''))
                    pprint(person_data, indent=4)
                    party, _ = Party.objects.get_or_create(slug=party.strip().lower(), defaults=dict(name=party.strip().title()))
                    terms = list(get_terms(id=openstate_id))
                    
                    q = Person.objects.filter(openstate_id=openstate_id, real=True)
                    if q.count():
                        person = q[0]
                    else:
                        person = Person(**person_data)
                    for k,v in person_data.iteritems():
                        setattr(person, k, v)
                    person.save()
                    print 'Saved person %s.' % (person.id,)
                    
                    for term in terms:
                        print 'Term:'
                        pprint(term, indent=4)
                        term_obj, _ = Term.objects.get_or_create(
                            person=person,
                            start_date=term['start_date'],
                            end_date=term['end_date'],
                            state=state_code,
                            country=country,
                            district=district,
                            role=term['role'],
                            party=term['party'],
                        )
                        if term['url']:
                            term_obj.website = term['url']
                        term_obj.save()
                #return
    
    @classmethod
    def load_democracymap(cls, dryrun=False, **kwargs):
        """
        Loads current governors from the Democracy Map API.
        """
        #TODO:slow and missing party, don't use
        
        def get(url, user_agent = 'IssueBot9000'):
            req = urllib2.Request(url, None, {'user-agent':user_agent})
            opener = urllib2.build_opener()
            f = opener.open(req, timeout=60)
            return simplejson.load(f)
        
        def iter_people(state):
            assert len(state) > 2
            #http://openstates.org/api/v1/legislators/?state=dc&chamber=upper&apikey=5cbde0c917d34c6fa98e3aa31d129e42
            url = 'http://api.democracymap.org/context?location={location}&format=json'\
                .format(
                    location=state.lower(),
                )
            i = 0
            data = get(url=url)
            jurisdictions = data.get('jurisdictions', [])
            for person in jurisdictions:
                elected_office = person.get('elected_office', [])
                for office in elected_office:
                    office_type = office.get('type', '').lower().strip()
                    office_title = office.get('title', '').lower().strip()
                    if 'executive' not in office_type and 'governor' not in office_title:
                        continue
                    yield dict(
                        first_name = office['name_full'].split(' ')[0],
                        last_name = office['name_full'].split(' ')[-1],
                        photo_url=office['url_photo'],
                        website=office['url'],
                    )
        
        for state_code, state_name in sorted(USPS_CHOICES):
            pprint(iter_people(state=state_name), indent=4)
            return
        
    @classmethod
    def load_wikipedia_us_governors(cls, dryrun=False, **kwargs):
        """
        Loads current U.S. governors from Wikipedia.
        """
        from countries.models import Country
        country = Country.objects.get(iso='US')
        
        text="""
<tr>
<td><a href="/wiki/West_Virginia" title="West Virginia">West Virginia</a></td>
<td><a href="/wiki/File:Earl_Ray_Tomblin_2.jpg" class="image"><img alt="Earl Ray Tomblin 2.jpg" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/72/Earl_Ray_Tomblin_2.jpg/100px-Earl_Ray_Tomblin_2.jpg" width="100" height="125" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/72/Earl_Ray_Tomblin_2.jpg/150px-Earl_Ray_Tomblin_2.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/72/Earl_Ray_Tomblin_2.jpg/200px-Earl_Ray_Tomblin_2.jpg 2x" /></a></td>
<td><span style="display:none;">Tomblin, Earl Ray</span><span class="vcard"><span class="fn"><a href="/wiki/Earl_Ray_Tomblin" title="Earl Ray Tomblin">Earl Ray Tomblin</a></span></span></td>
<td style="background:#B0CEFF"><a href="/wiki/Democratic_Party_(United_States)" title="Democratic Party (United States)">Democratic</a></td>
<td><span style="display:none; speak:none">02010-11-15</span><span style="white-space:nowrap;">November 15, 2010</span></td>
<td>2017 (term limits)</td>
<td><a href="/wiki/List_of_Governors_of_West_Virginia" title="List of Governors of West Virginia">List</a></td>
</tr>

<tr>
<td><a href="/wiki/Wisconsin" title="Wisconsin">Wisconsin</a></td>
<td><a href="/wiki/File:Scott_Walker_by_Gage_Skidmore.jpg" class="image"><img alt="Scott Walker by Gage Skidmore.jpg" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Scott_Walker_by_Gage_Skidmore.jpg/100px-Scott_Walker_by_Gage_Skidmore.jpg" width="100" height="125" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Scott_Walker_by_Gage_Skidmore.jpg/150px-Scott_Walker_by_Gage_Skidmore.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/00/Scott_Walker_by_Gage_Skidmore.jpg/200px-Scott_Walker_by_Gage_Skidmore.jpg 2x" /></a></td>
<td><span style="display:none;">Walker, Scott</span><span class="vcard"><span class="fn"><a href="/wiki/Scott_Walker_(politician)" title="Scott Walker (politician)">Scott Walker</a></span></span></td>
<td style="background:#FFB6B6"><a href="/wiki/Republican_Party_(United_States)" title="Republican Party (United States)">Republican</a></td>
<td><span style="display:none; speak:none">02011-01-03</span><span style="white-space:nowrap;">January 3, 2011</span></td>
<td>2015</td>
<td><a href="/wiki/List_of_Governors_of_Wisconsin" title="List of Governors of Wisconsin">List</a></td>
</tr>

<tr>
<td><a href="/wiki/Wyoming" title="Wyoming">Wyoming</a></td>
<td><a href="/wiki/File:Matt_Mead.jpg" class="image"><img alt="Matt Mead.jpg" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Matt_Mead.jpg/100px-Matt_Mead.jpg" width="100" height="128" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Matt_Mead.jpg/150px-Matt_Mead.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/21/Matt_Mead.jpg/200px-Matt_Mead.jpg 2x" /></a></td>
<td><span style="display:none;">Mead, Matt</span><span class="vcard"><span class="fn"><a href="/wiki/Matt_Mead" title="Matt Mead">Matt Mead</a></span></span></td>
<td style="background:#FFB6B6"><a href="/wiki/Republican_Party_(United_States)" title="Republican Party (United States)">Republican</a></td>
<td><span style="display:none; speak:none">02011-01-03</span><span style="white-space:nowrap;">January 3, 2011</span></td>
<td>2015</td>
<td><a href="/wiki/List_of_Governors_of_Wyoming" title="List of Governors of Wyoming">List</a></td>
</tr>
</table>
        """
        pat_row = re.compile(
            '<tr>(.*?)</tr>',
            flags=re.IGNORECASE|re.DOTALL|re.MULTILINE)
        pat = re.compile(
            '<td><a[^>]+>(?P<state>[^<]+)</a></td>[\n\s]*'
            '<td><a[^>]+><img.*?src="(?P<photo_url>[^"]+)"[^>]+></a></td>[\n\s]*'
            '<td><span[^>]+>(?P<last_name>[^,]+),\s*(?P<first_name>[^<]+)</span><span[^>]+><span[^>]+><a href="(?P<wikipedial_url_part>[^"]+)"[^>]+>.*?</td>[\n\s]*'
            '<td[^>]+><a[^>]+>(?P<party>[^<]+)</a></td>[\n\s]*'
            '<td[^>]*><span[^>]+>(?P<term_start_date>[^<]+)</span><span[^>]+>[^<]*</span></td>[\n\s]*'
            '<td>(?P<term_end_year>[0-9]+)[^<]*</td>[\n\s]*',
            flags=re.IGNORECASE|re.DOTALL|re.MULTILINE)
        
#        if dryrun:
#            html = text
#        else:
        html = scrapper.get(url='http://en.wikipedia.org/wiki/List_of_current_United_States_governors')
        #html = text
        state_name_to_code = dict((v,k) for k,v in USPS_CHOICES)
        
        matches = pat.findall(html)
        person_i = 0
        for match in matches:
            person_i += 1
            print '-'*80
            print person_i
            if dryrun:
                print match
                continue
        
            state, raw_photo_url, last_name, raw_first_name, wikipedial_url_part, party, term_start_date, term_end_year = match
            wikipedia_url = None
            if wikipedial_url_part:
                wikipedia_url = 'http://en.wikipedia.org' + wikipedial_url_part
            image_src_parts = raw_photo_url.split('/')
            image_src = 'http:' + ('/'.join(image_src_parts[:-1]))
            image_url = image_src.replace('/thumb', '')
            raw_first_name = raw_first_name.split(' ')
            first_name = raw_first_name[0]
            middle_name = ''
            if len(raw_first_name) > 1:
                middle_name = raw_first_name[1]
            party, _ = Party.objects.get_or_create(slug=party.strip().lower(), defaults=dict(name=party.strip().title()))
            while term_start_date[0] == '0':
                term_start_date = term_start_date[1:]
            term_start_date = dateutil.parser.parse(term_start_date)
            term_end_date = date(int(term_end_year), term_start_date.month, term_start_date.day)
            state_code = state_name_to_code[state]
            role = Role.objects.get(slug='governor', level=c.ROLE_LEVEL_STATE)
            print state, state_code, last_name,  image_url, first_name, middle_name, wikipedia_url, last_name, party, term_start_date, term_end_date, role
            
            person_data = dict(
                first_name = first_name,
                middle_name = middle_name,
                last_name = last_name,
                photo_thumbnail = get_thumbnail_from_url(image_url) if image_url else None,
                active=True,
                public=True,
                real=True,
            )
            person_data['photo_checked'] = bool(person_data['photo_thumbnail'])
            for k, v in person_data.items():
                if not isinstance(v, basestring):
                    continue
                person_data[k] = force_text(person_data[k])
            
            person = None
            q = Person.objects.filter(first_name=first_name, last_name=last_name, real=True)
            if q.count():
                if q.count() == 1:
                    person = q[0]
                else:
                    print '!'*80
                    print 'Possible pre-existing person found: ', q
                print 'Skipping creation!!!'
            else:
                person = Person(**person_data)
            
            if person:
                
                if not person.photo_thumbnail and person_data['photo_thumbnail']:
                    person.photo_thumbnail = person_data['photo_thumbnail']
                    person.photo_checked = True
                
                person.active = True
                person.public = True
                person.real = True
                if wikipedia_url and not person.wikipedia_page:
                    person.wikipedia_page = wikipedia_url
                person.save()
                print 'Saved person %s.' % (person.id,)
                term_obj, _ = Term.objects.get_or_create(
                    person=person,
                    start_date=term_start_date,
                    end_date=term_end_date,
                    state=state_code,
                    country=country,
                    role=role,
                    party=party,
                )
                term_obj.save()
        
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            return slugify(slug)
    
    def _download_from_wikipedia(self):
        """
        Attempts to download certain data fields from the wikipedia page.
        """
        from django.contrib import messages
        request = middleware.get_current_request()
        #messages.add_message(request, messages.SUCCESS, 'Wikipedia URL deduced.')
        try:
            if not self.wikipedia_page:
                self.update_wikipedia_page()
                if self.wikipedia_page:
                    messages.add_message(request, messages.SUCCESS, 'Wikipedia URL deduced.')
                else:
                    messages.add_message(request, messages.WARNING, 'Unable to deduce Wikipedia URL.')
                    return
                
            if not self.wikipedia_page_confirmed:
                messages.add_message(request, messages.WARNING, 'Unable to read Wikipedia. URL set but not confirmed.')
                return
            
            self.load_wikipedia_photo()
            self.wikipedia_checked = True
        finally:
            self.download_from_wikipedia = False
    
    def save(self, *args, **kwargs):
        
        if self.download_from_wikipedia:
            self._download_from_wikipedia()
        
        request = middleware.get_current_request()
        self._generate_photo_thumbnail(show_messages=request and '/admin' in request.get_full_path())
        
        # DO NOT SAVE FULL-SIZED PHOTOS!
        self.photo = None
        
        if self.birthday:
            self.year_born = self.birthday.year
        
        if self.passed_date:
            self.year_died = self.passed_date.year
        
        self.first_name_is_initial = '.' in (self.first_name or '')
        self.middle_name_is_initial = '.' in (self.middle_name or '')
        
        if self.slug == 'None':
            self.slug = None
            
        if self.slug is None and self.real:
            if self.nickname:
                slug = '%s-%s' % (self.nickname, self.last_name)
            else:
                slug = '%s-%s' % (self.first_name, self.last_name)
            slug = slugify(slug.lower().strip())
            q = Person.objects.get_real().filter(slug=slug)
            if self.id:
                q = q.exclude(id=self.id)
            if q.count():
                other = q[0]
                print 'Person %s has identical slug as person %s.' % (self.id, other.id,)
                # Mark as duplicate if birthdays match.
                if self.birthday and other.birthday == self.birthday:
                    if self.id is not None or self.id > other.id:
                        self.duplicate_of = other
                elif self.middle_name:
                    # Try making a unique slug using the middle name.
                    slug = slugify('%s-%s-%s' % (self.first_name, self.middle_name, self.last_name)).lower().strip()
                    q = Person.objects.get_real().filter(slug=slug)
                    if self.id:
                        q = q.exclude(id=self.id)
                    if not q.count():
                        self.slug = slug
                    
            else:
                self.slug = slug
        
        if self.slug:
            self.slug = slugify(self.slug)

        self.total_karma = (
            self.link_karma +
            self.url_karma + 
            self.issue_karma + 
            self.comment_karma +
            self.extra_karma
        )
        
        if self.id and self.active:
            self.issue_link_count = self.issue_links.all().count()
            self.update_top_weight()
            
        if not self.active:
            self.top_weight = 0
        
        super(Person, self).save(*args, **kwargs)
        
        # Fake/virtual users cannot be real active users.
#        if not self.real and self.user:
#            self.user.is_active = False
#            self.user.save()

def user_post_create(sender, instance, created, **kwargs):
    user = instance
    if created:
        print 'Sending user created notification email to site admins...'
        send_mail(
            subject='New user %s created!' % user,
            message='%s%s' % (settings.BASE_SECURE_URL, get_admin_change_url(user)),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email for _, email in settings.ADMINS],
            fail_silently=True,
        )
        print 'Email sent!'
if settings.IM_NOTIFY_ADMINS_OF_USER_CREATION:
    signals.post_save.connect(user_post_create, sender=User)

class Role(BaseModel):
    
    slug = models.SlugField(
        blank=False,
        null=False,
        unique=False)
    
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False)
    
    level = models.CharField(
        max_length=50,
        choices=c.ROLE_LEVEL_CHOICES,
        default=c.ROLE_LEVEL_FEDERAL,
        blank=False,
        null=False)
    
    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('slug', 'level'),
        )
        
    def __unicode__(self):
        q = type(self).objects.filter(slug=self.slug)
        if q.count() > 1:
            return self.level.title() + ' ' + self.name
        else:
            return self.name
        
class Party(BaseModel):
    """
    Represents a political affiliation.
    """
    
    slug = models.SlugField(blank=False, null=False, unique=True)
    
    name = models.CharField(max_length=100, blank=False, null=False)
    
    description = models.TextField()
    
    website = models.URLField(blank=True, null=True)
    
    country = models.ForeignKey(
        'countries.Country',
        default=_get_default_country)
    
    class Meta:
        app_label = APP_LABEL
        verbose_name_plural = 'parties'

    def __unicode__(self):
        return self.name

class TagManager(models.Manager):
    
    def get_active(self):
        return self.filter(active=True)

class Tag(BaseModel):
    
    objects = TagManager()
    
    slug = models.SlugField(
        max_length=25,
        unique=True,
        db_index=True,
        blank=False,
        null=False)
    
    active = models.BooleanField(default=False)
    
    creator = models.ForeignKey(
        'Person',
        blank=True,
        null=True,
        related_name='tags')
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('slug',)
        
    def clean(self, *args, **kwargs):
        self.slug = self.slug.replace('_', '-')
        super(Tag, self).clean(*args, **kwargs)

class IssueTag(BaseModel):
    
    issue = models.ForeignKey('Issue', related_name='tags')
    
    tag = models.ForeignKey('Tag')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'tag'),
        )

class Term(BaseModel):
    """
    Represents a person's occupation of a role over a period of time.
    """
    
    person = models.ForeignKey(Person, related_name='terms')
    
    start_date = models.DateField(blank=True, null=True)
    
    end_date = models.DateField(blank=True, null=True)
    
    county = models.ForeignKey(
        'County',
        blank=True,
        null=True)
    
    state = USStateField(blank=True, null=True)
    
    country = models.ForeignKey(
        'countries.Country',
        default=_get_default_country)
    
    district = models.CharField(
        max_length=700,
        blank=True,
        null=True,
        help_text='The identifier for the district this person represents. '\
            'This should usually be a number or letter. Only enter a name '\
            'if a number is not available.<br/>e.g. MA only lists districts with names.')
    
    senator_class = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=c.SENATOR_CLASS_CHOICES,
        help_text='The US federal senator class. This defines which year the '\
            'senator\'s term ends. The different classes are used to ensure '\
            'there\'s always a mix of experienced and freshman in the Senate.',
    )
    
    role = models.ForeignKey(Role, related_name='terms')
    
    party = models.ForeignKey(Party, related_name='terms', blank=True, null=True)
    
    website = models.URLField(blank=True, null=True)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('person', 'start_date', 'state', 'country', 'district', 'role'),
        )
        ordering = ('person', '-end_date')

    def __unicode__(self):
        return u'%s %s from %s, %s (%s to %s)' % (self.country, self.role, self.state_name, self.person, self.start_date, self.end_date)
    
    @property
    def nameless_description(self):
        if self.state_name:
            return u'%s from %s (%s to %s)' % (self.role, self.state_name, self.start_date, self.end_date)
        return u'%s (%s to %s)' % (self.role, self.start_date, self.end_date)
    
    @property
    def state_name(self):
        return dict(USPS_CHOICES).get(self.state)
    
    @property
    def contexts(self):
        """
        Returns a list of contexts applicable for this term,
        starting with the most general first.
        """
        lst = []
        try:
            lst.append(Context.objects.get(
                country=self.country,
                state__isnull=True,
                county__isnull=True))
        except Context.DoesNotExist:
            pass
        try:
            lst.append(Context.objects.get(
                country=self.country,
                state__state=self.state,
                county__isnull=True))
        except Context.DoesNotExist:
            pass
        try:
            lst.append(Context.objects.get(
                country=self.country,
                state__state=self.state,
                county=self.county))
        except Context.DoesNotExist:
            pass
        return lst

class IssueManager(models.Manager):
    
    def get_by_natural_key(self, issue):
        return self.get(issue=issue)
    
    def get_active(self, q=None):
        if q is None:
            q = self
        return q.filter(active=True)
    
    def get_public(self, q=None):
        if q is None:
            q = self
        return q.filter(public=True)
    
    def get_active_public(self, q=None):
        if q is None:
            q = self
        return q.filter(public=True, active=True)
    
    def get_top(self):
        return self.get_active_public().filter(slug__isnull=False)\
            .order_by('-top_weight', 'rand')
    
    def get_positioned_by(self, user, person=None):
        """
        Returns all issues positioned by the user.
        """
        if not user.is_authenticated():
            return []
        q = self.get_public()
        if person:
            q = q.filter(
                positions__person=person,
                positions__creator__user=user,
                positions__polarity__isnull=False)
        else:
            q = q.filter(
                positions__person__user=user,
                positions__creator__user=user,
                positions__polarity__isnull=False)
        return q
    
    def get_positioned_by_with_updates(self, user, person=None):
        """
        Returns all issues with links added since the user last positioned,
        and the user is able to re-position.
        """
        if not user.is_authenticated():
            return self.get_public()
        days = settings.IM_WAIT_DAYS_BEFORE_REANSWER
        cutoff = timezone.now() - timedelta(days=days)
        q = self.get_public()
        if person:
            q = q.filter(
                Q(positions__creator__user=user,
                  positions__person=person,
                  positions__deleted__isnull=True,
                  positions__polarity__isnull=False),
                Q(positions__created__lt=F('last_link_datetime')),
                Q(positions__created__lt=cutoff)
            )
        else:
            q = q.filter(
                Q(positions__creator__user=user,
                  positions__person__user=user,
                  positions__deleted__isnull=True,
                  positions__polarity__isnull=False),
                Q(positions__created__lt=F('last_link_datetime')),
                Q(positions__created__lt=cutoff)
            )
        return q
    
    def get_unpositioned_by(self, user, person=None, rand=0):
        """
        Returns all issue not positioned by the user.
        """
        if not user.is_authenticated():
            return self.get_public()
        q = self.get_active_public()
        q = q.select_related('positions')
        if person:
            #positions = Position.objects.get_real_active()\
            positions = Position.objects.get_active()\
                .filter(person=person, creator__user=user)
            q = q.exclude(
                id__in=positions.values_list('issue', flat=True)
#                positions__creator__user=user,
#                positions__polarity__isnull=False,
#                positions__person=person
            )
        else:
            q = q.exclude(
                positions__creator__user=user,
                #TODO:delete or filter by old skipped?
#                Q(positions__polarity__isnull=False),
#                Q(
#                    Q(positions__polarity__isnull=False)|\
#                    Q(
#                        positions__polarity__isnull=True,
#                        positions__created__gt=timezone.now()-timedelta(days=7))),
                positions__person__user=user,
            )
        if random.random() < rand:
            q = q.order_by('?')
        return q

def normalize_issue(q):
    parts = q.split(' ')
    parts = [_ for _ in parts if _.strip()]
    if parts:
        if parts[0].lower() in ('should', 'would'):
            i = [
                i for i,_ in enumerate(parts) if _.lower().startswith('p:')
            ][0]
            parts.insert(i, parts[0].lower())
            parts.pop(0)
        elif parts[0].lower() in ('was', 'are'):
            i = [
                i for i,_ in enumerate(parts) if _.lower().startswith('o:')
            ][0]
            parts.insert(i, parts[0].lower())
            parts.pop(0)
    q = ' '.join(parts)
    if q.endswith('?'):
        q = q[:-1]
    if q[-1].isalpha():
        q = q + '.'
    if q[0].islower():
        q = q[0].upper() + q[1:]
    return q

def normalize_issue_simple(q):
    q = q.strip()
    q = q[0].upper() + q[1:]
    if q[-1].isalpha():
        q = q + '.'
    return q

class Issue(BaseModel):
    
    objects = IssueManager()
    
    issue = models.CharField(
        max_length=700,
        db_index=True,
        blank=False,
        null=False)
    
    issue_tagless = models.CharField(
        max_length=700,
        db_index=True,
        blank=True,
        null=True)
    
    slug = models.SlugField(
        max_length=700,
        unique=True,
        db_index=True,
        blank=False,
        null=False,
    )
    
    keywords = models.CharField(max_length=700, blank=True, null=True,
        help_text='Extra text that will be included in searches.')
    
#    approved = models.BooleanField(
#        default=True,
#        db_index=True,
#        help_text='If checked, requires moderation approval.')
    
    public = models.BooleanField(
        default=True,
        db_index=True,
        help_text='If checked, allows the public to see the issue.')
    
    active = models.BooleanField(
        default=False,
        db_index=True,
        help_text='If checked, allows users to position the issue.')
    
    creator = models.ForeignKey(Person, related_name='issues')
    
    position_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        editable=False,
        verbose_name='positions')
    
    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name='views')
    
    last_position_datetime = models.DateTimeField(
        db_index=True,
        blank=True,
        editable=False,
        null=True)
    
    last_view_datetime = models.DateTimeField(
        db_index=True,
        blank=True,
        editable=False,
        null=True)
    
    last_link_datetime = models.DateTimeField(
        db_index=True,
        editable=False,
        blank=True,
        null=True)
    
    cached_weight = models.FloatField(
        default=0,
        editable=False,
        verbose_name='weight',
        blank=False,
        null=False)
    
    needs_review = models.BooleanField(
        default=False,
        db_index=True)
    
    flip_polarity = models.BooleanField(
        default=False,
        db_index=True,
        help_text='If checked, indicates all positions on this issue '\
            'should be flipped. This should only be done if the wording '\
            'has been changed to denote the opposite implication.')
    
    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True)
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
    
    contexts = models.ManyToManyField('Context')
    
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'issue',
            'slug',
            'keywords',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('-top_weight', 'rand')
        
    def __unicode__(self):
        return self.friendly_text

    def natural_key(self):
        return (self.issue,)
    natural_key.dependencies = ['issue_mapper.person']

    @property
    def undeleted_positions(self):
        return self.positions.filter(deleted__isnull=True)

    @property
    def object(self):
        return self

    @property
    def current_user_position(self):
        """
        Returns the position record for this issue and the current user.
        """
        request = middleware.get_current_request()
        if not request.user.is_authenticated():
            return
        try:
            person = Person.objects.get(user=request.user)
        except Person.DoesNotExist:
            return
        q = Position.objects.filter(
            issue=self,
            person__user=request.user,
            creator__user=request.user,
            deleted__isnull=True,
            polarity__isnull=False,
        )
        if q.count():
            return q[0]

    @property
    def random_unpositioned_other_person(self):
        user = middleware.get_current_user()
        q = Person.objects.filter(real=True)
        if user.is_authenticated():
            q = q.exclude(id__in=Position.objects.filter(creator__user=user)\
                .values_list('id', flat=True))
        q = q.order_by('?')
        if q.count():
            return q[0]
    
    @property
    def position_choice_list(self):
        return c.POSITION_CHOICES
    
    @property
    def friendly_text(self):
        if settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING1:
            return re.sub('[a-zA-Z]+\:', '', self.issue).replace('^', '')
        elif settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING2:
            return re.sub('[a-zA-Z]+\:', '', self.issue).replace('^', '')+'?'
        elif settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING3:
            parts = re.findall('^(.*)(should|is)\s+(P:[a-zA-Z]+)(.*)$', self.issue)
            #re.sub('[a-zA-Z]+\:', '', self.issue).replace('^', '')
            #print 'parts:',parts
            if parts:
                # Rework "X should Y" to "should X Y"?
                first, pred_prefix, middle, last = parts[0]
                middle_verb = [_ for _ in middle.split(' ') if _.strip()][-1]
                if first[0].isupper():
                    first = first[0].lower() + first[1:]
                if not last[-1].isalpha():
                    last = last[:-1]
                issue = '%s %s %s %s?' % (pred_prefix.title(), first, middle_verb, last)
                issue = re.sub('[a-zA-Z]+\:', '', issue).replace('^', '')
                return issue
            else:
                return re.sub('[a-zA-Z]+\:', '', self.issue).replace('^', '')+'?'
    
    @property
    def friendly_text_no_punct(self):
        return re.sub('[^a-zA-Z0-9 ]+', ' ', self.friendly_text).strip()

    def friendly_text_wrt(self, person):
        issue = self.tagless
        if not person.real:
            return issue
        if settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING1:
            issue = person.display_name + ' currently believes ' + self.as_addendum + '.'
        elif settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING1:
            issue = person.display_name + ' currently believes ' + self.as_addendum + '?'
        elif settings.IM_DEFAULT_QUESTION_PHRASING == c.QUESTION_PHRASING3:
            # Does P currently believe X should be Y?
            part = re.sub('[a-zA-Z]+\:', '', self.issue).strip()
            if not part[-1].isalpha():
                part = part[:-1]
            if part[0].isalpha():
                part = part[0].lower() + part[1:]
            issue = 'Does %s currently believe %s?' % (person.display_name, part)
        issue = issue.replace('^', '')
        return issue
        
    @property
    def tagless(self):
        return re.sub('[a-zA-Z]+\:', '', self.issue)

    @property
    def as_addendum(self):
        issue = self.tagless
        if not re.findall('^[A-Z]{2,}\s', issue):
            # Only lowercase the first word if it's not
            # an all-caps abbreviation.
            issue = issue[0].lower() + issue[1:]
        if issue.endswith('.'):
            issue = issue[:-1]
        return issue

    def is_motionable(self, attr):
        if attr in ('activate',) and not self.active:
            return True
        if attr in ('deactivate',) and self.active:
            return True
        return False

    def get_motion_effect(self, attr, new_value=None):
        if attr == 'deactivate':
            return self.deactivate.short_description

    def deactivate(self):
        self.active = False
        self.save()
    deactivate.motionable = True
    deactivate.short_description = 'This would result in users no longer '\
        'being able to position themselves or others on the issue. The '\
        'issue would remain publically visible and '\
        'therefore accessible to further motions.'
    
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('issue', kwargs=dict(issue_id=self.slug))

    def get_last_position(self, person, creator):
        """
        Returns the last position the creator has on the given person.
        """
        person = person or creator
        if not creator:
            return
        if not creator.user or not creator.user.is_authenticated():
            return
        q = self.positions.filter(
            creator=creator,
            deleted__isnull=True)
        q = q.filter(person=person)
        if q.count():
            return q[0]

    def positionable(self, user):
        if not user.is_authenticated():
            return False
        
        prior_positions = Position.objects.get_real().filter(
            person__user=user,
            deleted__isnull=True,
            issue=self
        )
        if prior_positions:
            if (timezone.now() - prior_positions[0].created).days \
            < settings.IM_WAIT_DAYS_BEFORE_REANSWER:
                return False
            
        return True
    
    def last_position_of_current_user(self):
        user = middleware.get_current_user()
        if not user or not user.is_authenticated():
            return
        q = Position.objects.get_real().filter(
            issue=self,
            person__user=user,
            creator__user=user,
            deleted__isnull=True
        )
        if q.count():
            return q[0]
    
    def positioned(self, person, creator):
        if not creator:
            return False
        if not creator.user or not creator.user.is_authenticated():
            return False
        q = Position.objects.get_real().filter(
            issue=self,
            person=person,
            creator=creator,
        )
        return bool(q.count())
    
    def unread_links(self, person, creator):
        user = middleware.get_current_user()
        q = self.links.all().filter(url__spam=False)
        if user and user.is_authenticated():
            last_position = self.get_last_position(person, creator)
            if last_position:
                q = q.filter(created__gt=last_position.created)
        return q

    def read_links(self, person, creator):
        user = middleware.get_current_user()
        if user and user.is_authenticated():
            last_position = self.get_last_position(person, creator)
            if last_position:
                q = self.links.filter(
                    created__lte=last_position.created, url__spam=False)
                return q
        else:
            return

    def flagged(self):
        user = middleware.get_current_user()
        if not user.is_authenticated():
            return False
        person = user.person
        q = Flag.objects.filter(issue=self, flagger=person)
        return bool(q.count())
        
    def get_choice_counts(self):
        """
        Returns aggregated position counts for all responses to the issue.
        """
        counts = Position.objects.filter(issue=self, polarity__isnull=False)\
            .values('polarity')\
            .annotate(count=Count('polarity'))
        total = 0.
        agg = {}
        for data in counts:
            total += data['count']
        for data in sorted(counts, key=lambda x:x['count'], reverse=True):
            #ac = PositionChoice.objects.get(id=data['position_choice'])
            yield data['polarity'], data['count'], data['count']/total*100

    def get_position_count(self, polarity):
        counts = Position.objects.filter(issue=self, polarity=polarity)\
            .values('polarity')\
            .annotate(count=Count('polarity'))
        if not counts:
            return 0
        return counts[0]['count']
    
    def oppose_count(self):
        return self.get_position_count(c.OPPOSE)
    
    def undecided_count(self):
        return self.get_position_count(c.UNDECIDED)
    
    def favor_count(self):
        return self.get_position_count(c.FAVOR)
    
    @property
    def weight(self):
        """
        Calculates the heuristic value used to sort this issue
        among other issues.
        
        A higher weight increases chance of being shown on homepage.
        A lower weight decreases that chance.
        """
        
        # Being positioned by many people increases weight.
        max_position_count = Issue.objects.all()\
            .aggregate(Max('position_count'))['position_count__max'] or 0
        w1 = self.position_count/(max_position_count + 1)
        
        # Being created recently increases weight.
        w2days = 7.
        w2 = w2days/((timezone.now() - \
            (self.created or timezone.now())).days + w2days)
        
        weight = w1 + w2
        
        return weight

    @classmethod
    def flip_all(cls, *args, **options):
        """
        Flips polarity on positions linked to all issues with flip_polarity
        flag set.
        Modifies everything in a single transaction per-issue so data integrity
        is maintained.
        """
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        commit = True
        try:
            q = cls.objects.filter(flip_polarity=True)
            total = q.count()
            i = 0
            for issue in q.iterator():
                i += 1
                #print '%i of %i' % (i, total)
                
                #Note, inside a transaction, the updated progress won't be
                #seen until commit, unless the model is on a separate database.
                JobModel.update_progress(total_parts=total, total_parts_complete=i)
                
                positions = issue.positions.all()
                total_positions = positions.count()
                i_positions = 0
                for position in positions:
                    i_positions += 1
                    print_status(
                        top_percent=i/float(total)*100,
                        sub_percent=i_positions/float(total_positions)*100,
                        newline=False,
                        message='Flipping positions for issue %s...' % (issue,))
                    position.polarity = position.opposite_polarity
                    position.save()
                    
                issue.flip_polarity = False
                issue.save()
        
            print
            print 'Committing...'
            django.db.transaction.commit()
            print 'Committed!'
        except Exception, e:
            commit = False
            raise
        finally:
            settings.DEBUG = tmp_debug
            print
            if not commit:
                print 'Rolling back...'
                django.db.transaction.rollback()
                print 'Rolled back!'
            django.db.transaction.leave_transaction_management()
            django.db.connection.close()

    @classmethod
    def load_csv(cls, fn, user=None, **kwargs):
        commit = True
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        try:
            rows = csv.DictReader(open(fn))
            for row in rows:
                if not row['issue'].strip():
                    continue
                print 'Loading issue "%s"...' % (row['issue'],)
                
                user = User.objects.get(username=row['user'])
                person, _ = Person.objects.get_or_create(user=user)
                
                issue = normalize_issue(row['issue'].strip())
                issue, _ = Issue.objects.get_or_create(
                    issue=issue,
                    defaults=dict(
                        creator=person,
                    ))
                
                for related_url in row['urls'].strip().split(','):
                    if not related_url.strip():
                        continue
                    url, _ = URL.objects.get_or_create(
                        url=related_url,
                        defaults=dict(
                            creator=person
                        ))
                    link, _ = Link.objects.get_or_create(
                        issue=issue,
                        url=url,
                        defaults=dict(
                            creator=person
                        ))
                
        except Exception, e:
            commit = False
            raise
        finally:
            settings.DEBUG = tmp_debug
            if commit:
                print 'Committing...'
                django.db.transaction.commit()
            else:
                print 'Rolling back...'
                django.db.transaction.rollback()
            django.db.transaction.leave_transaction_management()
        print 'Done.'

    @classmethod
    def register_feeds(cls, **kwargs):
        """
        Attempts to creates a feed for every active issue
        """
        q = cls.objects.get_active_public()\
            .exclude(id__in=Feed.objects\
                .filter(issue__isnull=False, account__active=True)\
                .values_list('issue_id', flat=True))\
            .distinct()
        total = q.count()
        i = 0
#        print q.count()
#        return
        for issue in q:
            i += 1
            print '%i of %i: %s' % (i, total, issue)
            accounts = FeedAccount.objects.get_unfilled().order_by('?')
            if not accounts.count():
                print 'No unfilled accounts.'
                return
            account = accounts[0]
            query = account.get_query(issue=issue)
            Feed.objects.get_or_create(
                account=account,
                issue=issue,
                defaults=dict(query=query),
            )
            account.save()
            #time.sleep(random.randint(1,5))

    def save(self, *args, **kwargs):
        
        self.cached_weight = self.weight
        
        if not self.slug:
            self.slug = issue_to_slug(self.issue)
        
        self.issue_tagless = self.tagless
        
        super(Issue, self).save(*args, **kwargs)

def issue_to_slug(issue):
    slug = issue.strip().lower()
    slug = re.sub('[a-zA-Z]+\:', '', slug) # Remove POS tags.
    slug = re.sub('^[^a-z0-9\-]+', '', slug)
    slug = re.sub('[^a-z0-9\-]+$', '', slug)
    slug = re.sub('[^a-z0-9\-]+', '-', slug)
    slug = slugify(slug)
    return slug

class URLManager(models.Manager):
    
    def get_new(self):
        return self.filter(
            absolute_votes__lt=c.MIN_VOTE_NEW_THRESHOLD,
            created__gte=timezone.now() - timedelta(days=c.MIN_VOTE_NEW_DAYS)
        )
    
    def get_top(self):
        return self.all().order_by('-top_weight', 'rand')

class BaseContext(BaseModel, BaseVoteTarget):
    
    context = models.ForeignKey('Context', blank=False, null=False)
    
    votes_up = models.PositiveIntegerField(default=0)
    
    votes_down = models.PositiveIntegerField(default=0)
    
    absolute_votes = models.PositiveIntegerField(default=0)
    
    weight = models.IntegerField(
        default=0,
        help_text='Count of up votes minus count of down votes.')
    
    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True,
        help_text='The value that determines in what order this link '\
            'appears in queries.')
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
    
    class Meta:
        abstract = True

class URL(BaseModel, BaseVoteTarget):

    objects = URLManager()

    url = models.URLField(
        blank=True,
        null=True,
        db_index=True,
        max_length=700, # ~700 is maximum indexable length in MySQL
        unique=True)
    
    title = models.CharField(
        max_length=c.TITLE_LENGTH,
        blank=True,
        null=True)
    
    title_checked = models.BooleanField(
        default=False,
        db_index=True)
    
    text = models.TextField(blank=True, null=True)
    
    text_checked = models.BooleanField(
        default=False,
        db_index=True)
    
    creator = models.ForeignKey(
        Person,
        related_name='urls')
    
    spam = models.BooleanField(default=False)
    
    feed = models.ForeignKey(
        'Feed',
        on_delete=models.SET_NULL,
        related_name='urls',
        blank=True,
        null=True)
    
    og_image_thumbnail = models.ImageField(
        upload_to='uploads/url/og_image_thumbnail', blank=True, null=True)
    
    og_image_checked = models.BooleanField(
        default=False,
        verbose_name='image checked',
        db_index=True)
    
    #TODO:these are deprecated, use URLContext instead
    votes_up = models.PositiveIntegerField(default=0)
    votes_down = models.PositiveIntegerField(default=0)
    absolute_votes = models.PositiveIntegerField(default=0)
    weight = models.IntegerField(
        default=0,
        help_text='Count of up votes minus count of down votes.')
    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True,
        help_text='The value that determines in what order this link '\
            'appears in queries.')
    
    top_urlcontext = models.ForeignKey(
        'URLContext',
        related_name='top_urls',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    
    top_urlcontext_weight = models.FloatField(
        editable=False,
        blank=True,
        db_index=True,
        null=True)
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
        
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'title',
            'url',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('-top_weight', 'rand')
        
    @property
    def object(self):
        return self
    
    @property
    def taggable_object(self):
        return self
    
    @property
    def domain(self):
        from urlparse import urlparse
        return urlparse(self.url).netloc
    
    # 2013.7.28 Causes URL tags to up/down vote URLs.
    # After testing on URLs relevant to many people, we don't want this
    # because it skews the URL weight.
#    @property
#    def child_vote_targets(self):
#        return self.links.all()
    
    def get_absolute_url(self):
        return self.url
    
    @property
    def context(self):
        """
        Returns the effective context for this URL take from either the
        current request or the most top-weight URL context.
        """
        try:
            request = middleware.get_current_request()
            if request and hasattr(request, 'context') and request.context:
                return request.context
            elif self.top_urlcontext and self.top_urlcontext.context:
                return self.top_urlcontext.context
        except Exception, e:
            return str(e)
    
    @property
    def person_links(self):
        q = self.links.filter(
            person__isnull=False,
            issue__isnull=True,
            person__public=True,
            person__active=True,
        )
        person = middleware.get_current_person()
        if person:
            q = q.filter(Q(weight__gte=0)|Q(votes__voter=person)|Q(creator=person))
        return q
    
    @property
    def issue_links(self):
        q = self.links.filter(
            person__isnull=True,
            issue__isnull=False,
            issue__public=True,
            issue__active=True,
        )
        person = middleware.get_current_person()
        if person:
            q = q.filter(Q(weight__gte=0)|Q(votes__voter=person)|Q(creator=person))
        return q
    
    @property
    def feed_title(self):
        return self.better_display_text() or u''
    
    @property
    def feed_url(self):
        #return self.get_absolute_url()
        return settings.BASE_URL + reverse('link', args=(self.id,))
    
    @property
    def feed_teaser(self):
        return ''
            
    @classmethod
    def update_all(cls, url_ids=[], only=None, limit=None, **kwargs):
        """
        Updates the cached title, image and text for all pending URLs.
        """
        force = kwargs.get('force', False)
        url_ids = [int(_) for _ in url_ids]
        q = cls.objects.all()
        if not force:
            if only == 'title':
                q = q.filter(title_checked=False, title__isnull=True)
            elif only == 'text':
                q = q.filter(text_checked=False, text__isnull=True)
            elif only == 'image':
                q = q.filter(
                    Q(og_image_checked=False),
                    Q(og_image_thumbnail__isnull=True)|\
                    Q(og_image_thumbnail__isnull=False, og_image_thumbnail='')
                )
        if url_ids:
            print 'url_ids:',url_ids
            q = q.filter(id__in=url_ids)
#        if limit:
#            limit = int(limit)
#            q = q[:limit]
        total = q.count()
        print 'total:',total
        i = 0
        for o in q.iterator():
            i += 1
            save = False
            print '%i of %i' % (i, total)
            JobModel.update_progress(total_parts=total, total_parts_complete=i)
            
#            url = o.url
#            if url[0] == '[' and url[-1] == ']':#TODO:remove
#                o.url = eval(url)[0]
            
            print 'only:',only
            if (only is None or only == 'title') and (not o.title_checked or force):
                try:
                    o.update_title()
                except Exception, e:
                    #connection.close()
                    #django.db.transaction.rollback()
                    save = True
                    print>>sys.stderr, e
                    #continue
                    
            if (only is None or only == 'text') and (not o.text_checked or force):
                try:
                    o.update_text()
                except Exception, e:
                    #connection.close()
                    #django.db.transaction.rollback()
                    save = True
                    print>>sys.stderr, e
                    #continue
            
            if (only is None or only == 'image') and (not o.og_image_checked or force):
                try:
                    o.update_og_image()
                except Exception, e:
                    #raise
                    #connection.close()
                    #django.db.transaction.rollback()
                    save = True
                    print>>sys.stderr, e
                    #continue
                    
            if save:
                #connection.close()
                if only is None or only == 'title':
                    o.title_checked = True
                if only is None or only == 'text':
                    o.text_checked = True
                if only is None or only == 'image':
                    o.og_image_checked = True
                o.save()
    
    def display_text(self):
        if self.title:
            return self.title
        return self.url.url
    
    def better_display_text(self):
        if not self.title:
            return self.url
        title = (self.title or '').strip() or (self.url.title or '').strip()
        title = title.replace('<', '')
        parts = re.split(ur'(?: \| )|(?: \- )|(?: &raquo; )|(?: – )|(?: » )|(?: \u2013 )', title)
        url = self.url.lower()
        domain = self.domain
        possible = None
#        print 'domain:',domain
        for part in parts:
#            print 'part:',part
#            print 'domain parts:',[_.lower().strip() for _ in part.split(' ') if len(_.strip()) > 5]
            domainparts = [_ for _ in part.split(' ') if len(_.strip()) > 5 and _.lower().strip() in domain]
#            print 'domain parts2:',domainparts
            if domainparts:
                continue
            _part = re.sub('[a-z0-9\.]+', '', part.lower())
            if _part not in url and (possible is None or len(part) > len(possible)):
                possible = part
        return possible or self.url
    
    def update_title(self):
        self.title_checked = True
        html = scrapper.get(
            url=self.url,
            allow_cookies=True,
            timeout=10,
            verbose=True)
        if not html:
            return
        html = unicode(html, encoding='ascii', errors='ignore')
        matches = re.findall(
            '<title[^>]*>(.*?)</title[^>]*>',
            html,
            flags=re.IGNORECASE|re.DOTALL)
        if matches:
            print matches
            self.title = matches[0].strip()[:300]
        self.save()
        
    def update_text(self):
        self.text_checked = True
        print 'Updating text for %s...' % self.url
        import webarticle2text
        from django.utils.encoding import smart_text
        self.text = webarticle2text.extractFromURL(
            self.url,
            userAgent=random.choice(scrapper.USER_AGENTS))
        self.text = smart_text(self.text, encoding='utf-8', errors='replace')
        self.save()
        
    def update_og_image(self):
        #http://stackoverflow.com/questions/1386352/pil-thumbnail-and-end-up-with-a-square-image
        import opengraph
        from django.core import files
        
        self.og_image_checked = True
        print 'Updating og:image for %s...' % self.url
        
        data = opengraph.OpenGraph(url=self.url)
        print 'image:',data.image
        image_url = data.image
        if image_url:
            image_data = scrapper.get(url=image_url)
            image_file = files.temp.NamedTemporaryFile(
                dir=files.temp.gettempdir()
            )
            image_file.write(image_data)
            image_file.seek(0)
            #person.photo = files.File(image_file)
            
            from PIL import Image, ImageOps
            from cStringIO import StringIO
            PIL_TYPE = 'jpeg'
            THUMBNAIL_SIZE = (75, 75)
            image = Image.open(StringIO(image_data))
            #image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
            image = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
            temp_handle = StringIO()
            image.save(temp_handle, PIL_TYPE)
            temp_handle.seek(0)
            image_file = files.temp.NamedTemporaryFile(
                dir=files.temp.gettempdir()
            )
            image_file.write(temp_handle.getvalue())
            image_file.seek(0)
            self.og_image_thumbnail = files.File(image_file)
            print>>sys.stderr, 'Success!'
        self.save()
    
    @property
    def vote_type(self):
        return c.URL
    
    @classmethod
    def update_all_votes(cls):
        q = cls.objects.filter(Q(votes__id__isnull=False)|Q(links__votes__id__isnull=False)).distinct()
        total = q.count()
        i = 0
        for u in q.iterator():
            i += 1
            print '%i of %i' % (i, total)
            u.update_votes()
    
    @classmethod
    def update_weights(cls, *ids, **kwargs):
        """
        Bulk updates the top_weight value for all URLs.
        Note, this may take a long time.
        """
        #DEPRECATED? We don't track vote weight solely at the URL level.
        #Use update_top_urlcontext_weights() instead?
        top = kwargs.get('top')
        if ids:
            q = cls.objects.filter(id__in=map(int, ids))
        elif top:
            q = cls.objects.get_top()[:int(top)]
        else:
            q = cls.objects.all()
        total = q.count()
        i = 0
        for link in q.iterator():
            i += 1
            print_status(
                top_percent=(i/float(total)*100),
                sub_percent=None,
                message='%i of %i' % (i, total))
            link.save()
    
    @classmethod
    def update_top_urlcontext_weights(cls, *ids, **kwargs):
        """
        Bulk updates the top_weight value for all URLs.
        Note, this may take a long time.
        """
        context = kwargs.get('context')
        top = kwargs.get('top')
#        contexts = Context.objects.get_active_public()
#        if context:
#            contexts = contexts.filter(slug=context)
#        context_total = contexts.count()
#        context_i = 0
#        for context in contexts.iterator():
#            context_i += 1
        if ids:
            print 'Updating top_urlcontext_weight on specific IDs...'
            q = cls.objects.filter(id__in=map(int, ids))
        elif top:
            print 'Updating top_urlcontext_weight on top...'
            q = cls.objects.all().order_by('-top_urlcontext_weight')[:int(top)]
        else:
            print 'Updating top_urlcontext_weight on all missing...'
            q = cls.objects.all().filter(top_urlcontext_weight__isnull=True)
        #q = q.filter(top_urlcontext__context)
        total = q.count()
        i = 0
        for o in q.iterator():
            i += 1
            print_status(
#                top_percent=(context_i/float(context_total)*100),
#                sub_percent=(i/float(total)*100),
                top_percent=(i/float(total)*100),
                sub_percent=None,
                message='%i of %i' % (i, total))
            o.set_top_urlcontext()
            o.save()
            
        print
        print 'Done.'
    
    def set_top_urlcontext(self):
        """
        Updates cached reference to the most highly upvoted context.
        This allows the frontpage to show upvoted URLs from multiple contexts.
        """
        best = self.url_contexts.all().order_by('-top_weight')
        if best.count():
            best = best[0]
            self.top_urlcontext = best
            self.top_urlcontext_weight = best.top_weight
        else:
            self.top_urlcontext = None
            self.top_urlcontext_weight = None
    
    def save(self, *args, **kwargs):
        
        if self.title:
            self.title = re.sub('<[^>]*>', '', self.title).strip()
        
        if not (self.title or '').strip():
            self.title = None
            
        #TODO: 
        #TODO: better to do this kind of query in a separate periodic task?
        #self.o.set_top_urlcontext()
            
        super(URL, self).save(*args, **kwargs)

def get_default_creator():
    user = User.objects.get(username=settings.IM_DEFAULT_USERNAME)
    creator, _ = Person.objects.get_or_create(user=user)
    return creator

class URLContextManager(models.Manager):
    
    def get_top(self):
        return self.all().order_by('-top_weight', 'rand')

class URLContext(BaseContext):
    
    objects = URLContextManager()
    
    ## inherited
    # context
    
    url = models.ForeignKey(URL, related_name='url_contexts')
    
    creator = models.ForeignKey(
        'Person',
        blank=True,
        null=True,
        default=get_default_creator,
        related_name='url_contexts_created',
        help_text='The person who created this url context.')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('url', 'context'),
        )
        
    def __unicode__(self):
        return u'%s in %s' % (self.url, self.context)
    
    @property
    def vote_type(self):
        return c.URLCONTEXT
    
    @property
    def object(self):
        return self
    
    @property
    def taggable_object(self):
        return self.url
    
    @classmethod
    def update_all_votes(cls):
        q = cls.objects.filter(Q(votes__id__isnull=False)).distinct()
        total = q.count()
        i = 0
        for u in q.iterator():
            i += 1
            print '%i of %i' % (i, total)
            u.update_votes()
    
    @classmethod
    def update_weights(cls, top=None, only_null=False, context=None, **kwargs):
        """
        Bulk updates the top_weight value for all URL Contexts.
        Note, this may take a long time.
        """
        contexts = Context.objects.get_active_public()
        if context:
            contexts = contexts.filter(slug=context)
        context_total = contexts.count()
        context_i = 0
        for context in contexts.iterator():
            context_i += 1
            if top:
                q = cls.objects.get_top().filter(context=context)[:int(top)]
            else:
                q = cls.objects.all().filter(context=context)
            if only_null:
                q = q.filter(top_weight__isnull=True)
            total = q.count()
            i = 0
            for link in q:
                i += 1
                print_status(
                    top_percent=(context_i/float(context_total)*100),
                    sub_percent=(i/float(total)*100),
                    message='%i of %i: context %s' % (i, total, context.slug))
                link.save()
    
    def save(self, *args, **kwargs):
        
#        print 'votes_up:', self.votes_up
#        print 'votes_down:', self.votes_down
        
        self.update_vote_weight()
        
        #TODO:decrease over time
        #self.top_weight = self.weight
        #t = (timezone.now()-(self.created or timezone.now())).seconds/60./60. # hours since creation
        t = (timezone.now()-(self.created or timezone.now())).total_seconds()/60./60. # hours since creation
        p = self.weight # total vote summation
        self.top_weight = p / (t + 35.)**1.5
        #(lambda p,t: p / (t + 2)**1.5)(p=2,t=24)
        #(lambda p,t: p / (t + 2)**1.5)(p=1,t=1)
        #f=lambda p,t: p / (t + 2)**1.5; f(p=1,t=1); f(p=2,t=24);
        # One vote an hour ago is worth two votes 24 hours ago.
        ###f=lambda p,t: p / (t + 35.)**1.5; f(p=1,t=1); f(p=2,t=24);
        ###f=lambda p,t: p / (t + 35.)**1.5; f(p=1,t=1); f(p=3,t=7*24);
        
#        print 'id:',self.id
#        print 'absolute_votes:', self.absolute_votes
#        print 'weight:', self.weight
#        print 'top_weight:', self.top_weight
        
        super(URLContext, self).save(*args, **kwargs)
        
        url = self.url
        if not url.top_urlcontext_weight or self.top_weight > url.top_urlcontext_weight:
            url.top_urlcontext = self
            url.top_urlcontext_weight = self.top_weight
            url.save()

class URLVoteManager(models.Manager):
    def get_by_natural_key(self, link, voter):
        return self.get(link=link, voter=voter)
    
class URLVote(BaseVote):
    """
    Represents a person's support for or against a URL.
    """

    objects = URLVoteManager()
    
    voter = models.ForeignKey(Person, related_name='url_votes')
    
    url = models.ForeignKey(URL, related_name='votes')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('url', 'voter'),
        )
    
    @property
    def vote_object(self):
        return self.url
    
    @property
    def karma_field_name(self):
        return 'url_karma'
        
    def natural_key(self):
        return (self.link.natural_key(), self.voter.natural_key())
    natural_key.dependencies = ['issue_mapper.url', 'issue_mapper.person']
    
    def save(self, *args, **kwargs):
        super(URLVote, self).save(*args, **kwargs)
        voter = self.voter
        voter.last_url_vote = self.updated
        voter.save()
        
class URLContextVote(BaseVote):
    """
    Represents a person's support for or against a URL.
    """
    
    voter = models.ForeignKey(Person, related_name='url_context_votes')
    
    url_context = models.ForeignKey(URLContext, related_name='votes')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('url_context', 'voter'),
        )
        ordering = ('-created',)
    
    @property
    def vote_object(self):
        return self.url_context
    
    @property
    def karma_field_name(self):
        #return 'url_karma'
        return
        
#    def natural_key(self):
#        return (self.link.natural_key(), self.voter.natural_key())
#    natural_key.dependencies = ['issue_mapper.url', 'issue_mapper.person']
    
    def save(self, *args, **kwargs):
        super(URLContextVote, self).save(*args, **kwargs)
        voter = self.voter
        voter.last_url_vote = self.updated
        voter.save()

class LinkManager(models.Manager):
    def get_by_natural_key(self, issue, url):
        return self.get(issue=issue, url=url)
    
    def get_top(self):
        return self.all().order_by('-top_weight', 'rand')
    
    def active(self):
        return self.filter(deleted__isnull=True)
    
    def get_new(self):
        return self.active()\
            .filter(absolute_votes__lt=c.MIN_VOTE_NEW_THRESHOLD)\
            .filter(created__gte=timezone.now() - timedelta(days=c.MIN_VOTE_NEW_DAYS))
    
class Link(BaseModel, BaseVoteTarget):
    
    objects = LinkManager()
    
    issue = models.ForeignKey(
        Issue,
        blank=True,
        null=True,
        related_name='links')
    
    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name='issue_links')
    
    title = models.CharField(
        max_length=c.TITLE_LENGTH,
        db_index=True,
        blank=True,
        null=True)
    
    url = models.ForeignKey(
        URL,
        related_name='links')
    
    creator = models.ForeignKey(
        Person,
        related_name='links')
    
    votes_up = models.PositiveIntegerField(default=0, db_index=True,)
    
    votes_down = models.PositiveIntegerField(default=0, db_index=True,)
    
    absolute_votes = models.PositiveIntegerField(default=0, db_index=True,)
    
    weight = models.IntegerField(
        default=0,
        db_index=True,
        help_text='Count of up votes minus count of down votes.')
    
    feed = models.ForeignKey(
        'Feed',
        on_delete=models.SET_NULL,
        related_name='links',
        blank=True,
        null=True)
    
    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True,
        help_text='The value that determines in what order this link '\
            'appears in queries.')
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
    
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'title',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'person', 'url'),
        )
        ordering = ('-top_weight', '-created', 'rand')
    
    def __unicode__(self):
        return unicode(self.url)
    
    @property
    def has_negative_weight(self):
        return self.weight < 0
    
    @property
    def weight_above_zero(self):
        return max(self.weight, 0)
    
    @property
    def weight_non_zero(self):
        if not self.weight:
            return ''
        return '%+i' % self.weight
    
    @property
    def domain(self):
        from urlparse import urlparse
        return urlparse(self.url.url).netloc
    
    @property
    def object(self):
        return self
    
    @property
    def vote_type(self):
        return c.LINK
    
    @property
    def similar_person_links(self):
        """
        Returns links with the same URL with different people.
        """
        q = type(self).objects.active()
        q = q.exclude(id=self.id)
        q = q.filter(url=self.url)
        q = q.filter(
            person__isnull=False,
            person__real=True,
            person__duplicate_of__isnull=True,
            person__deleted__isnull=True
        )
        q = q.filter(issue__isnull=True)
        return q
    
    @property
    def similar_person_issue_links(self):
        """
        Returns links with the same URL with different people and issue.
        """
        q = type(self).objects.active()
        q = q.exclude(id=self.id)
        q = q.filter(url=self.url)
        q = q.filter(
            person__isnull=False,
            person__real=True,
            person__duplicate_of__isnull=True,
            person__deleted__isnull=True
        )
        q = q.filter(issue__isnull=False)
        return q
    
    @property
    def similar_issue_links(self):
        """
        Returns links with the same URL with different people.
        """
        q = type(self).objects.active()
        q = q.exclude(id=self.id)
        q = q.filter(url=self.url)
        q = q.filter(person__isnull=True)
        q = q.filter(issue__isnull=False)
        q = q.exclude(issue__deleted__isnull=False)
        q = q.filter(issue__active=True)
        return q
    
    @property
    def person_issue_links(self):
        """
        Returns person+issue links for all issues
        linked to the same URL as the current person.
        """
        if not self.person:
            return
        q = self.similar_issue_links
        return q
    
    @property
    def feed_title(self):
        return self.display_text() or u''
    
    @property
    def feed_url(self):
        return settings.BASE_URL + self.get_absolute_url()
    
    @property
    def feed_teaser(self):
        return ''
    
    def get_absolute_url(self):
        try:
            if self.person:
                return reverse('person_link', args=(self.person.slug, self.id))
            elif self.issue:
                return reverse('issue_link', args=(self.issue.slug, self.id))
        except Exception, e:
            return str(e)
    
    def is_motionable(self, attr):
#        if attr in (,):
#            return True
        return False
    
    def display_text(self):
        if self.title:
            return self.title
        elif self.url.title:
            return self.url.title
        return self.url.url
    
    def better_display_text(self):
        if not self.title and not self.url.title:
            return self.url.url
        title = (self.title or '').strip() or (self.url.title or '').strip()
        title = title.replace('<', '')
        parts = re.split(ur'(?: \| )|(?: \- )|(?: – )|(?: \u2013 )', title)
        #print 'parts:',parts
        url = self.url.url.lower()
        for part in parts:
            _part = re.sub('[a-z0-9\.]+', '', part.lower())
            if _part not in url:
                return part
    
    def better_display_text_with_ref(self):
        bd = self.better_display_text()
        if self.issue:
            other = self.issue.friendly_text
        else:
            other = unicode(self.person.display_name)
        return mark_safe('%s &rarr; %s' % (bd, other))
    
    def some_title(self):
        if self.title:
            return self.title
        elif self.url.title:
            return self.url.title
    some_title.short_description = 'title'
    
    def natural_key(self):
        return (self.issue.natural_key(), self.url)
    natural_key.dependencies = ['issue_mapper.issue']
    
    def flagged(self):
        user = middleware.get_current_user()
        if not user.is_authenticated():
            return False
        person = user.person
        q = Flag.objects.filter(link=self, flagger=person)
        return bool(q.count())
    
    def by_current_user(self):
        return self.creator.user == middleware.get_current_user()
    
    @classmethod
    def update_weights(cls, top=None, **kwargs):
        if top:
            q = cls.objects.get_top()[:int(top)]
        else:
            q = cls.objects.all()
        total = q.count()
        i = 0
        for link in q:
            i += 1
            print '%i of %i' % (i, total)
            #print 'top_weight0:',link.top_weight
            link.save()
            link = Link.objects.get(id=link.id)
            #print 'top_weight1:',link.top_weight
            
    def clean(self, *args, **kwargs):
        super(Link, self).clean(*args, **kwargs)
        if not self.issue and not self.person:
            raise ValidationError, 'Either an issue or person must be set.'
    
    def save(self, *args, **kwargs):
        
        if self.url.title and not self.title:
            self.title = self.url.title
        
        self.update_vote_weight()
        
        #TODO:decrease over time
        #self.top_weight = self.weight
        t = (timezone.now()-(self.created or timezone.now())).seconds/60./60.
        p = self.weight
        self.top_weight = p / (t + 2)**1.5
        
        if self.issue:
            if self.issue.last_link_datetime:
                self.issue.last_link_datetime = max(
                    self.issue.last_link_datetime or timezone.now(),
                    self.created or timezone.now())
            else:
                self.issue.last_link_datetime = self.created or timezone.now()
            self.issue.save()
        
        super(Link, self).save(*args, **kwargs)

class LinkVoteManager(models.Manager):
    def get_by_natural_key(self, link, voter):
        return self.get(link=link, voter=voter)
    
class LinkVote(BaseVote):
    """
    Represents a person's support for or against a link.
    """

    objects = LinkVoteManager()
    
    voter = models.ForeignKey(Person, related_name='link_votes')
    
    link = models.ForeignKey(Link, related_name='votes')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('link', 'voter'),
        )
    
    @property
    def vote_object(self):
        return self.link
    
    # 2013.7.28 CKS This and child_targets cause URL to get skewed
    # by many tags.
#    @property
#    def parent_target(self):
#        return self.link.url
    
    @property
    def karma_field_name(self):
        return 'link_karma'
        
    def natural_key(self):
        return (self.link.natural_key(), self.voter.natural_key())
    natural_key.dependencies = ['issue_mapper.link', 'issue_mapper.person']
    
class CommentVoteManager(models.Manager):
    def get_by_natural_key(self, comment, voter):
        return self.get(comment=comment, voter=voter)
    
class CommentVote(BaseVote):
    """
    Represents a person's support for or against a comment.
    """

    objects = CommentVoteManager()
    
    voter = models.ForeignKey(Person, related_name='comment_votes')
    
    comment = models.ForeignKey('Comment', related_name='votes')
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('comment', 'voter'),
        )
    
    @property
    def vote_object(self):
        return self.comment
    
    @property
    def karma_field_name(self):
        return 'comment_karma'
        
    def natural_key(self):
        return (self.comment.natural_key(), self.voter.natural_key())
    natural_key.dependencies = ['issue_mapper.comment', 'issue_mapper.person']

class PositionManager(models.Manager):
    
    def get_real(self, q=None):
        """
        Returns all non-skipped positions with a real answer.
        """
        if q is None:
            q = self
        return q.exclude(polarity__isnull=True).exclude(polarity='')
    
    def get_active(self, q=None):
        """
        Returns all non-deleted positions.
        """
        if q is None:
            q = self
        return q.filter(deleted__isnull=True)
    
    def get_self(self, q=None):
        """
        Returns all positions made by the user of the user.
        """
        if q is None:
            q = self
        return q.filter(person=F('creator'))
    
    def get_real_active(self):
        return self.get_active(self.get_real())
    
    def get_real_active_self(self):
        """
        Returns all non-skipped non-deleted positions answered for themselves.
        """
        return self.get_self(self.get_active(self.get_real()))

class Position(BaseModel):
    """
    Represents a user's stated opinion or their belief of another's opinion
    towards a specific issue.
    """
    
    objects = PositionManager()
    
    issue = models.ForeignKey(
        Issue,
        related_name='positions')
    
    polarity = models.CharField(
        max_length=20,
        choices=c.POSITION_CHOICES,
        blank=True,
        null=True)
    
    importance = models.PositiveIntegerField(
        choices=c.IMPORTANCE_CHOICES,
        default=c.SOMEWHAT,
        blank=False,
        null=False
    )
    
    person = models.ForeignKey(
        Person,
        blank=False,
        null=False,
        related_name='positions',
        help_text='The person that the position applies to.')
    
    creator = models.ForeignKey(
        Person,
        blank=False,
        null=False,
        related_name='positions_created',
        help_text='''The person who created this position. Note, if this
            does not match the person field, that indicates a second-hand
            belief.''')
    
    comment = models.CharField(
        max_length=700,
        blank=True,
        null=True)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'person', 'deleted'),
        )
    
    def __unicode__(self):
        return self.display_text()
        
    @property
    def normalized_polarity(self):
        if self.polarity is None:
            return
        return dict(c.POSITION_SCORES)[self.polarity]
    
    @property
    def opposite_polarity(self):
        if self.polarity == c.OPPOSE:
            return c.FAVOR
        if self.polarity == c.FAVOR:
            return c.OPPOSE
        assert self.polarity in (None, c.UNDECIDED), \
            'Invalid polarity: %s' % (self.polarity,)
        return self.polarity
        
    def display_text(self, links=False):
        user = middleware.get_current_user()
        person_str = ''
        
        if self.person != self.creator:
            if user and self.creator.user == user:
                creator_str = u'You'
                verb = self.polarity_infinitive
            else:
                creator_str = unicode(self.creator).title()
                verb = self.polarity_3rd_singular_present
            
            person_str = self.person
            if links:
                person_str = '<a href="%s">%s</a>' % (
                    reverse('person', args=(self.person.slug,)), self.person)
                
            template = '%(creator_str)s %(verb_str)s that %(person_str)s ' \
                'thinks %(addendum)s.'
        else:
            if user and self.person.user == user:
                creator_str = u'You'
                verb = self.polarity_infinitive
            else:
                creator_str = unicode(self.person).title()
                verb = self.polarity_3rd_singular_present
            template = '%(creator_str)s %(verb_str)s that %(addendum)s.'
        
        verb_str = verb
        if links:
            if self.person != self.creator:
                verb_str = '<a href="%s">%s</a>' % (
                    reverse('issue_wrt_person',
                        args=(self.person.slug, self.issue.slug,)), verb)
            else:
                verb_str = '<a href="%s">%s</a>' % (
                    reverse('issue', args=(self.issue.slug,)), verb)
        
        return template % dict(
            creator_str=creator_str,
            verb_str=verb_str,
            person_str=person_str,
            addendum=self.issue.as_addendum,
        )
    
    def display_text_with_links(self):
        return self.display_text(links=True)
        
    @property
    def polarity_infinitive(self):
        return c.POSITION_TO_VERB_INFINITIVE.get(self.polarity, self.polarity)
    
    @property
    def polarity_3rd_singular_present(self):
        return c.POSITION_TO_VERB.get(self.polarity, self.polarity)
    
    @classmethod
    def create(cls, issue, polarity, person, creator, force=False):
        if not creator.user.is_authenticated():
            print 'User not authenticated.'
            return None, None
        assert polarity in c.ALLOWED_POSITION_VALUES, \
            'Invalid polarity value: %s' % (polarity,)
        prior_positions = cls.objects.filter(
            person=person,
            creator=creator,
            deleted__isnull=True,
            issue=issue,
        ).exclude(
            polarity=polarity
        )
        # Disallow creating a new position if the user recently created
        # a non-skip position for this issue.
        if prior_positions:
            if prior_positions[0].polarity and not force \
            and (timezone.now() - prior_positions[0].created).days \
            < settings.IM_WAIT_DAYS_BEFORE_REANSWER:
                return prior_positions[0], False
            for a in prior_positions:
                a.deleted = timezone.now()
                a.save()
        position, _ = cls.objects.get_or_create(
            issue=issue,
            polarity=polarity,
            person=person,
            creator=creator,
            deleted=None,
        )
        return position, _
    
    def get_position_count(self, polarity):
        if self.person == self.creator:
            q = type(self).objects.filter(id=self.id, polarity=polarity)
            #print 'q:',q
        else:
            q = Position.objects.get_real_active()
            q = q.filter(issue=self.issue, polarity=polarity)
            q = q.filter(person=self.person)
        counts = q\
            .values('polarity')\
            .annotate(count=Count('polarity'))
        if not counts:
            return 0
        return counts[0]['count']
    
    def oppose_count(self):
        return self.get_position_count(c.OPPOSE)
    
    def undecided_count(self):
        return self.get_position_count(c.UNDECIDED)
    
    def favor_count(self):
        return self.get_position_count(c.FAVOR)
    
    def reaffirm(self):
        self.created = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        
        if not self.id:
            self.issue.position_count += 1
            self.issue.last_position_datetime = timezone.now()
            self.issue.save()
            
            self.person.position_count += 1
            self.person.save()
        
        if self.person != self.creator:
            agg, _ = PositionAggregate.objects.get_or_create(
                issue=self.issue, person=self.person, date=None
            )
            agg.fresh = False
            agg.save()
            agg, _ = PositionAggregate.objects.get_or_create(
                issue=self.issue,
                person=self.person,
                date=date(self.created.year, self.created.month, 1)
            )
            agg.fresh = False
            agg.save()
        
        super(Position, self).save(*args, **kwargs)

class MotionManager(models.Manager):
    pass

class Motion(BaseModel, BaseVoteTarget):
    """
    Represents a proposed action.
    """

    objects = MotionManager()

    issue = models.ForeignKey(
        Issue,
        blank=True,
        null=True,
        related_name='motions')
    
    link = models.ForeignKey(
        Link,
        blank=True,
        null=True,
        related_name='motions')
    
    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name='motions')
    
    creator = models.ForeignKey(
        Person,
        blank=False,
        null=False,
        related_name='motions_created')
    
    attribute = models.CharField(
        max_length=700,
        db_index=True,
        blank=False,
        null=False)
    
    new_value = models.CharField(
        max_length=700,
        db_index=True,
        blank=True,
        null=True)
    
    pending = models.NullBooleanField(
        default=True)
    
    votes_up = models.PositiveIntegerField(default=0, editable=False)
    
    votes_down = models.PositiveIntegerField(default=0, editable=False)
    
    weight = models.IntegerField(default=0, editable=False)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            # A person can only propose one change to an item at a time.
            ('issue', 'link', 'person', 'attribute', 'new_value', 'pending'),
        )
    
    def get_absolute_url(self):
        return reverse('motion', args=(self.id,))
    
    @property
    def status(self):
        if self.pending:
            return 'pending'
        return 'closed' #TODO
    
    @property
    def object(self):
        return self.issue or self.person or self.link
        
    @property
    def object_model(self):
        return type(self.object)
    
    @property
    def action(self):
        if not (self.new_value or '').strip():
            return self.attribute.title()
        else:
            return 'Change %s to %s.' % (self.attribute, self.new_value)
    
    def __unicode__(self):
        if not (self.new_value or '').strip():
            return u'%s %s "%s"' % (
                self.attribute.title(),
                self.object_model.__name__.lower(),
                self.object
            )
        else:
            return u'Change %s on %s "%s" to %s' % (
                self.attribute,
                self.object_model.__name__.lower(),
                self.object,
                self.new_value,
            )
    
    @property
    def description_short(self):
        s = '%s %s "%s"' % (self.attribute, self.object_model.__name__.lower(), self.object)
        s = s[0].upper() + s[1:]
        return s
    
    @property
    def effect_friendly_text(self):
        s = self.object.get_motion_effect(self.attribute, self.new_value)
        s = (s or '').strip()
        s = 'If passed, ' + s[0].lower() + s[1:]
        if s[-1].isalpha():
            s = s + '.'
        return s
    
    @property
    def forecast_str(self):
        total = self.votes_up + self.votes_down
        if total <= 1:
            return 'uncertain'
        elif self.weight > 0:
            return 'likely to pass'
        else:
            return 'likely to fail'
    
    def update_votes(self):
        self.votes_up = self.votes.filter(vote=c.UPVOTE).count()
        self.votes_down = self.votes.filter(vote=c.DOWNVOTE).count()
        self.save()
        
    def clean(self, *args, **kwargs):
        items = [_ for _ in (self.issue, self.link, self.person) if _]
        if not items:
            raise ValidationError(
                'Either an issue, link, or person must be specified.')
        elif len(items) > 1:
            raise ValidationError(
                'Only a single issue, link, or person may be specified.')
            
        self.weight = self.votes_up - self.votes_down
        
        return super(Motion, self).clean(*args, **kwargs)
    
#    def clean(self, *args, **kwargs):
#        self.vote_toal = self.votes_up - self.votes_down
#        return super(Motion, self).save(*args, **kwargs)

class MotionVote(BaseModel):
    """
    Represents a person's support for or against a link.
    """

    objects = LinkVoteManager()

    motion = models.ForeignKey(Motion, related_name='votes')
    
    voter = models.ForeignKey(Person, related_name='motion_votes')
    
    vote = models.IntegerField(
        choices=c.VOTE_CHOICES,
        blank=False,
        null=False
    )
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('motion', 'voter'),
        )
    
    def is_up(self):
        return self.vote == c.UPVOTE
    
    def flip(self):
        if self.is_up():
            self.vote = c.DOWNVOTE
        else:
            self.vote = c.UPVOTE
    
    @property
    def description(self):
        try:
            if self.is_up():
                return ("You voted to {attribute}. "\
                    "Click to reverse your vote.")\
                    .format(attribute=self.motion.attribute, vote_created=self.created)
            else:
                return ("You voted to un-{attribute}. "\
                    "Click to reverse your vote.")\
                    .format(attribute=self.motion.attribute, vote_created=self.created)
        except Exception, e:
            return str(e)
    
    def save(self, *args, **kwargs):
        
#        assert self.voter != self.motion.creator, \
#            'A person may not vote on their own link.'
        
        old_vote = None
        if self.id:
            old_vote = MotionVote.objects.get(id=self.id)
            
        super(MotionVote, self).save(*args, **kwargs)
        
        # Update cached link vote totals.
        obj = self.motion
        if old_vote:
            if old_vote.vote != self.vote:
                if old_vote.vote == c.UPVOTE:
                    obj.votes_up = max(0, obj.votes_up - 1)
                    obj.votes_down += 1
                else:
                    obj.votes_up += 1
                    obj.votes_down = max(0, obj.votes_down - 1)
                obj.save()
        else:
            # Record just created.
            if self.vote == c.UPVOTE:
                obj.votes_up += 1
            else:
                obj.votes_down += 1
            obj.save()

class FlagManager(models.Manager):
    
    def get_by_natural_key(self, issue, link, person, type):
        return self.get(
            issue=issue,
            link=link,
            person=person,
            type=type)

class Flag(BaseModel):

    objects = FlagManager()

    issue = models.ForeignKey(
        Issue,
        blank=True,
        null=True,
        related_name='flags')
    
    link = models.ForeignKey(
        Link,
        blank=True,
        null=True,
        related_name='flags')
    
    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name='flags')
    
    flagger = models.ForeignKey(
        Person,
        related_name='flags_created')
    
    type = models.CharField(
        choices=c.FLAG_CHOICES,
        default=c.SPAM,
        max_length=10,
        db_index=True,
        editable=False,
        blank=False,
        null=False)
    
    comment = models.CharField(
        max_length=700,
        blank=False,
        null=False)
    
    judged = models.BooleanField(default=False)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'link', 'person', 'flagger'),
        )
    
    def __unicode__(self):
        if self.issue:
            obj = self.issue
        elif self.link:
            obj = self.link
        else:
            obj = self.person
        return u'%s flagged by %s' % (obj, self.flagger)
    
    def natural_key(self):
        return (
            self.issue.natural_key() if self.issue else None,
            self.link.natural_key() if self.link else None,
            self.person.natural_key() if self.person else None,
            self.flagger.natural_key(),
            self.type,
        )
    natural_key.dependencies = [
        'issue_mapper.issue',
        'issue_mapper.link',
        'issue_mapper.person',
    ]
    #TODO:aggregate counts in issue/link, expose in admin
    #TODO:score hit/miss of flagger

class FlagJudgement(BaseModel):
    
    flag = models.ForeignKey(
        Flag,
        related_name='judgements')
    
    judge = models.ForeignKey(
        Person,
        related_name='judgements')
    
    judgement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        db_index=True,
        choices=c.FLAG_JUDGEMENT_CHOICES,
    )
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('flag', 'judge'),
        )

class PositionAggregateManager(models.Manager):
    
    def current(self):
        return self.filter(date__isnull=True)

class PositionAggregate(BaseModel):
    
    objects = PositionAggregateManager()
    
    issue = models.ForeignKey(
        Issue,
        editable=False,
        related_name='position_aggregates')
    
    person = models.ForeignKey(
        Person,
        editable=False,
        related_name='position_aggregates')
    
    date = models.DateField(
        blank=True,
        editable=False,
        null=True)
    
    fresh = models.BooleanField(
        default=False,
        editable=False,
        db_index=True)
    
    oppose_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        db_index=True)
    
    undecided_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        db_index=True)
    
    favor_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        db_index=True)
    
    total_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        db_index=True)
    
    total_bots = models.PositiveIntegerField(
        default=0,
        editable=False,
        db_index=True)
    
    entropy = models.FloatField(
        blank=True,
        null=True,
        editable=False,
        db_index=True)
    
    polarity_estimate = models.FloatField(
        blank=True,
        null=True,
        editable=False,
        db_index=True)
    
    polarity = models.CharField(
        max_length=20,
        choices=c.POSITION_CHOICES,
        blank=True,
        null=True)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'person', 'date'),
        )
        
    def __unicode__(self):
        dt = self.date or date.today()
        return u'%i: as of <%s> concerning <%s> person <%s> believes <%s>' % (
            self.id, dt, self.issue, self.person, self.counts
        )
    
    @property
    def normalized_polarity(self):
        """
        Returns the position polarity as a floating point
        value between [-1:+1].
        """
        if not self.total_count:
            return
        return sum([-1*self.oppose_count, self.favor_count])/self.total_count
    
    @property
    def normalized_classification(self):
        """
        Returns the position polarity rounded to the nearest integer
        in [-1:+1].
        """
        if not self.total_count:
            return
        position = sum([-1*self.oppose_count, self.favor_count])/self.total_count
        position = int(round(position))
        return position
    
    @property
    def normalized_classification_name(self):
        """
        Returns the name of the normalized classification.
        """
        return max([
            (self.oppose_count, c.OPPOSE),
            (self.undecided_count, c.UNDECIDED),
            (self.favor_count, c.FAVOR)
        ])[1]
    
    @property
    def counts(self):
        return [self.oppose_count, self.undecided_count, self.favor_count]
    
    @classmethod
    def update_all(cls, force=False, **kwargs):
        q = cls.objects.all()
        if not force:
            q = q.filter(fresh=False)
        total = q.count()
        i = 0
        for pa in q:
            i += 1
            if not i % 10 or i == 1:
                print '%i of %i (%.0f%%)' % (i, total, i/float(total)*100)
                JobModel.update_progress(total_parts=total, total_parts_complete=i)
            pa.update()
        if total:
            print '%i of %i (%.0f%%)' % (i, total, i/float(total)*100)
            JobModel.update_progress(total_parts=total, total_parts_complete=total)
    
    def update(self):
        q = Position.objects.get_real_active()
        q = q.filter(issue=self.issue, person=self.person)
        self.oppose_count = q.filter(polarity=c.OPPOSE).count()
        self.undecided_count = q.filter(polarity=c.UNDECIDED).count()
        self.favor_count = q.filter(polarity=c.FAVOR).count()
        self.total_bots = q.filter(creator__bot=True).count()
        counts = self.counts
        self.total_count = sum(counts)
        if self.total_count:
            self.entropy = abs(entropy_histogram(counts))
        else:
            self.entropy = None
        
        self.polarity_estimate = self.normalized_polarity
        self.polarity = self.normalized_classification_name
        
        self.fresh = True
        self.updated = timezone.now()
        self.save()

class MatchPending(models.Model):
    
    id = models.CharField(
        max_length=100,
        primary_key=True,
        blank=False,
        null=False)
    
    matcher = models.ForeignKey(
        Person,
        related_name='pending_matches_for',
        on_delete=models.DO_NOTHING,
        db_column='matcher_id')
    
    matchee = models.ForeignKey(
        Person,
        related_name='pending_matches_with',
        on_delete=models.DO_NOTHING,
        db_column='matchee_id')
    
    class Meta:
        app_label = APP_LABEL
        managed = False
        db_table = 'issue_mapper_matchpending'

    @classmethod
    def update_all(cls, force=False, **kwargs):
        if force:
            q = Match.objects.all()
        else:
            q = cls.objects.all()
        total = q.count()
        i = 0
        for r in q:
            i += 1
            print '%i of %i' % (i, total)
            JobModel.update_progress(total_parts=total, total_parts_complete=i)
            if isinstance(r, Match):
                obj = r
            else:
                obj, _ = Match.objects.get_or_create(
                    matcher=r.matcher, matchee=r.matchee)
            obj.update()
        
class Match(BaseModel):
    
    matcher = models.ForeignKey(
        Person,
        editable=False,
        related_name='matches_for',
        help_text='The person the match is for. This is usually the user.')
    
    matchee = models.ForeignKey(
        Person,
        editable=False,
        related_name='matched_with',
        help_text='''The person being matched to. This is usually the
            elected official.''')
    
    fresh = models.BooleanField(
        db_index=True,
        default=False,
        editable=False,
        help_text='If checked, indicates the match value needs to be recalculated.')
    
    value = models.FloatField(
        db_index=True,
        blank=True,
        editable=False,
        null=True)
    
    issue_count = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False)
    
    class Meta:
        app_label = APP_LABEL
        verbose_name_plural = 'matches'
        unique_together = (
            ('matcher', 'matchee'),
        )
    
    @property
    def value_percent(self):
        if self.value is None:
            return
        return self.value * 100
    
    def update(self):
        """
        Calculates the match ratio between two people based upon their
        positions on issues.
        """
        matcher_positions = self.matcher.positions\
            .filter(deleted__isnull=True, polarity__isnull=False)
        matcher_issues = matcher_positions.values_list('issue', flat=True)
        common_positions = self.matchee.position_aggregates\
            .filter(
                date__isnull=True,
                issue__in=matcher_issues,
                total_count__gt=0)\
            .order_by('issue__id')
        numerator = 0.
        denominator = 0.
        self.issue_count = common_positions.count()
        for pos_agg in common_positions:
            print 'issue:',pos_agg.issue
            #print 'A',pos_agg.id,pos_agg.normalized_polarity, pos_agg.person #pos_agg
            matchee_pos = (pos_agg.normalized_polarity+1)/2.
            #print 'AA'
            
            q = self.matcher.positions_created.get_real_active_self()\
                .filter(issue=pos_agg.issue)
            assert q.count() == 1, ('Expected user to have one position on '
                'the issue, but found %i.') % (q.count(),)
            position = q[0]
            #print 'B',position.normalized_polarity, position
            matcher_pos = (position.normalized_polarity+1)/2.
            
            pos_diff = (1-abs(matcher_pos - matchee_pos))*position.importance
            #print 'C',self.matcher, self.matchee, pos_agg.issue.id, matcher_pos, matchee_pos, pos_diff, position.importance
            
            numerator += pos_diff
            denominator += position.importance
            
        score = numerator/denominator
        #print numerator, denominator, score
        self.value = score
        self.fresh = True
        self.updated = timezone.now()
        self.save()

class Priviledge(BaseModel):

    site = models.OneToOneField(Site, related_name='priviledge_threshold')
    
    # Issues.
    
    single_submit_issue = models.PositiveIntegerField(default=10)
    
    single_submit_issue_unthrottled = models.PositiveIntegerField(default=20)
    
    submit_issue_throttle_minutes = models.PositiveIntegerField(default=1)
    
    many_approve_issue = models.PositiveIntegerField(default=1000)
    
    single_answer_issue_for_themself = models.PositiveIntegerField(default=50)
    
    single_answer_issue_for_other = models.PositiveIntegerField(default=100)
    
#    edit_issue = models.PositiveIntegerField(default=500)
    
    single_flag_issue = models.PositiveIntegerField(default=10)
    
#    vote_issue_action = models.PositiveIntegerField(default=0)
    
    # Tags (the Link model).
    
    single_submit_tag = models.PositiveIntegerField(default=200)
    
    many_approve_tag = models.PositiveIntegerField(default=1000)
    
    single_tag_issue = models.PositiveIntegerField(default=100)
    
    single_vote_tag = models.PositiveIntegerField(default=5)
    
    many_approve_tag_issue = models.PositiveIntegerField(default=500)
    
    # Quotes.
    
    single_submit_quote = models.PositiveIntegerField(default=5)
    
    single_vote_quote = models.PositiveIntegerField(default=5)
    
    single_flag_quote = models.PositiveIntegerField(default=0)
    
    # Links (the URLs/URL Contexts models)
    
    single_submit_link = models.PositiveIntegerField(default=50)
    
    single_submit_link_unthrottled = models.PositiveIntegerField(default=20)
    
    submit_link_throttle_minutes = models.PositiveIntegerField(default=1)
    
    single_vote_link = models.PositiveIntegerField(default=50)
    
    #single_comment_link = models.PositiveIntegerField(default=0)
#    
    single_flag_link = models.PositiveIntegerField(default=10)
#    
#    vote_link_action = models.PositiveIntegerField(default=0)
    
    # Person.
    
    single_submit_person = models.PositiveIntegerField(default=100)
    
    single_quote_person = models.PositiveIntegerField(default=5)
    
    many_approve_person = models.PositiveIntegerField(default=1000)
    
    single_flag_person = models.PositiveIntegerField(default=10)
#    
#    vote_person_action = models.PositiveIntegerField(default=0)
#    
#    edit_person = models.PositiveIntegerField(default=0)
    
    # Moderation.
    
    moderate_flags = models.PositiveIntegerField(default=1000)
    
    # Points.
    
    points_from_upvoted_link = models.IntegerField(default=1)
    
    points_from_downvoted_link = models.IntegerField(default=-1)
    
    points_from_downvoting_link = models.IntegerField(default=-1)
    
    points_from_answered_issue = models.IntegerField(default=1)
    
    points_from_trashed_issue = models.IntegerField(default=-100)
    
    points_from_trashed_link = models.IntegerField(default=-100)
    
    # General site access.
    
    allow_registration = models.BooleanField(default=True)
    
    @classmethod
    def get_current(cls):
        from django.contrib.sites.models import get_current_site
        request = middleware.get_current_request()
        return cls.objects.get_or_create(site=get_current_site(request))[0]
    
    @property
    def can(self):
        
        class Perm(object):
            
            def __init__(self, threshold, user):
                self.threshold = threshold
                self.person = None
                if user and user.is_authenticated():
                    self.person = user.person
            
            def __getattr__(self, key):
                if not self.person:
                    return False
                key0 = key
                key = 'single_' + key
                assert hasattr(self.threshold, key), 'Invalid permission name: %s' % (key,)
                threshold = getattr(self.threshold, key, 1e999999999)
                #print 'key:',key, 'threshold:',threshold,'self.person.total_karma:',self.person.total_karma
                return threshold <= self.person.total_karma
        
        return Perm(threshold=self, user=middleware.get_current_user())

class FeedAccountManager(models.Manager):

    def get_unfilled(self):
        return self.filter(active=True, total_feeds__lt=F('max_feeds'))

class FeedAccount(BaseModel):
    
    objects = FeedAccountManager()
    
    type =  models.CharField(
        max_length=100,
        choices=c.FEED_TYPES,
        blank=False,
        null=False)
    
    url = models.URLField(
        max_length=100,
        blank=True,
        null=True)
    
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True)
    
    password = models.CharField(
        max_length=100,
        blank=True,
        null=True)
    
    total_feeds = models.PositiveIntegerField(
        default=0,
        db_index=True,
        editable=False,
        blank=False,
        null=False)
    
    max_feeds = models.PositiveIntegerField(
        default=1000,
        db_index=True,
        blank=False,
        null=False)
    
    active = models.BooleanField(default=True)
    
    min_check_hours = models.PositiveIntegerField(
        default=23,
        db_index=True,
        blank=False,
        null=False,
        help_text='The minimum time allowed between subsequent feed checks.')
    
    #https://pypi.python.org/pypi/galerts
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('url', 'username'),
        )

    @property
    def free_slots(self):
        return max(self.max_feeds - self.total_feeds, 0)

    def __unicode__(self):
        return dict(c.FEED_TYPES).get(self.type)
        #return '%s@%s' % (self.username, self.url)
    
    def clean(self, *args, **kwargs):
        result = super(FeedAccount, self).clean(*args, **kwargs)
        self.total_feeds = self.feeds.all().count()
        return result

    def get_query(self, person=None, issue=None):
        #TODO:support non-Google query formats?
        #e.g. types that don't support AND or parens?
        if person:
            query = '"%s"' % person.display_name
            terms = ' OR '.join(set(person.terms.all()\
                .values_list('role__name', flat=True)))
            if terms:
                query = '%s AND (%s)' % (query, terms)
        elif issue:
            query = issue.friendly_text
        else:
            raise Exception, 'Either a person or issue must be specified.'
        return query

class FeedManager(models.Manager):
    
    def get_pending(self):
        return self.filter(
            account__active=True,
            account__deleted__isnull=True,
            active=True,
            deleted__isnull=True,
        ).filter(
            Q(next_check__isnull=True)|\
            Q(next_check__isnull=False, next_check__lte=timezone.now())
        ).filter(
            Q(issue__isnull=False, issue__public=True, issue__active=True)|\
            Q(person__isnull=False, person__public=True, person__active=True)
        )

class Feed(BaseModel):
    
    objects = FeedManager()
    
    account = models.ForeignKey(FeedAccount, related_name='feeds')
    
    query = models.CharField(
        max_length=700,
        blank=False,
        null=False)
    
    issue = models.ForeignKey(
        Issue,
        blank=True,
        null=True,
        related_name='feeds')
    
    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name='feeds')
    
    active = models.BooleanField(default=True)
    
    last_checked = models.DateTimeField(blank=True, null=True)
    
    next_check = models.DateTimeField(blank=True, null=True)
    
    uid = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text='Vendor-specific unique identifier.')
    
    url = models.URLField(
        blank=True,
        null=True,
        help_text='RSS feed URL.')
    
    link_count = models.PositiveIntegerField(default=0, editable=False)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('account', 'person'),
        )

    def __unicode__(self):
        return '<search for %s for %s from %s>' % (self.query, self.person, self.account)
    
    @property
    def fresh(self):
        if not self.last_checked:
            return False
        cutoff = timezone.now() - timedelta(days=self.account.min_check_hours/24.)
        return self.last_checked < cutoff
    
    def clean(self, *args, **kwargs):
        result = super(Feed, self).clean(*args, **kwargs)
        if not self.id and self.account.total_feeds >= self.account.max_feeds:
            raise ValidationError, \
                'Unable to create new feed. Account has reached the maximum '\
                'allowed number of feeds.'
        elif not self.issue and not self.person:
            raise ValidationError, \
                'Either an issue or a person must be specified.'
        elif self.issue and self.person:
            raise ValidationError, \
                'An issue and a person cannot both be specified.'
        
        # Register or unregister feed based on active flag.
        if not self.active and self.url:
            self.unregister(save=False)
        elif self.active and not self.url:
            self.register(save=False)
        
        self.link_count = self.links.all().count()
        
        if self.account.type == c.FEED_GOOGLE_NEWS:
            params = dict(
                hl='en',
                gl='us',
                authuser=0,
                q=unicode(self.query).encode('utf-8'),
                um=1,
                ie='UTF-8',
                output='rss',
            )
            self.url = 'http://news.google.com/news?' + urllib.urlencode(params)
        
        return result
    
    @classmethod
    def update_all(cls, **kwargs):
        q = cls.objects.get_pending()
        total = q.count()
        i = 0
        for feed in q:
            i += 1
            print '%i of %i' % (i, total)
            JobModel.update_progress(total_parts=total, total_parts_complete=i)
            feed.update()
            #time.sleep(random.randint(1, 3))
    
    def _lookup_galerts_manager(self):
        return galerts.GAlertsManager(
            self.account.username,
            self.account.password
        )
    
    def _lookup_galerts_object(self):
        gam = self._lookup_galerts_manager()
        for alert in list(gam.alerts):
            if alert.query != self.query:
                continue
            q = Feed.objects.filter(url=alert.feedurl).exclude(id=self.id)
            if q.count():
                continue
            return alert
    
    def unregister(self, save=True):
        if not self.url:
            return
        elif self.account.type == c.FEED_GALERTS:
            pass
#            gam = self._lookup_galerts_manager()
#            alert = self._lookup_galerts_object()
#            if alert:
#                gam.delete(alert)
#                self.url = None
        elif self.account.type == c.FEED_GOOGLE_NEWS:
            pass
        else:
            raise NotImplemented
        if save:
            self.save()
        
    def register(self, save=True):
        if self.url:
            return
        elif self.account.type == c.FEED_GALERTS:
            pass
#            gam = self._lookup_galerts_manager()
#            gam.create(
#                query=self.query,
#                type=galerts.TYPE_EVERYTHING,
#                feed=True)
#            alert = self._lookup_galerts_object()
#            if alert:
#                self.url = alert.feedurl
        elif self.account.type == c.FEED_GOOGLE_NEWS:
            pass
        else:
            raise NotImplemented
        if save:
            self.save()
    
    def delete(self, *args, **kwargs):
        self.unregister(save=False)
        super(Feed, self).delete(*args, **kwargs)
    
    def update(self):
        
        user = User.objects.get(username=settings.IM_DEFAULT_USERNAME)
        creator, _ = Person.objects.get_or_create(user=user)
        
        if self.account.type in (c.FEED_GALERTS, c.FEED_GOOGLE_NEWS):
            self.register()
            # Query feed.
            if self.url:
                d = feedparser.parse(self.url)
                i = 0
                for entry in d.entries:
                    if 'google' in entry.title.lower():
                        continue
                    i += 1
                    title = re.sub('<[^>]+>', '', entry.title).strip()
                    if '...' in title:
                        title = None
                    url = urlparse.urlparse(entry.link)
                    qs = urlparse.parse_qs(url.query)
                    #print 'qs:',qs
                    if not qs:
                        print '!'*80
                        print 'Skipping invalid url: %s' % (url,)
                        print '!'*80
                        continue
                    if 'q' in qs:
                        url = qs['q'][0].strip()
                    elif 'url' in qs:
                        url = qs['url'][0]
                    else:
                        raise Exception, 'No URL found in feed item: %s' % (str(qs),)
                    print i, title, url
                    if 'https' in url.lower():
                        continue
                    url, _ = URL.objects.get_or_create(
                        url=url,
                        defaults=dict(
                            title=title,
                            creator=creator,
                            feed=self
                        ))
                    try:
                        if not url.title:
                            url.update_title()
                            url.save()
                    except Exception, e:
                        print 'Unable to update URL title: %s' % (e,)
                    link, _ = Link.objects.get_or_create(
                        issue=self.issue,
                        person=self.person,
                        url=url,
                        defaults=dict(
                            creator=creator,
                            feed=self
                        ))
                    
                    # Add URL to appropriate contexts.
                    contexts = []
                    if self.issue:
                        contexts.extend(self.issue.contexts.all())
                    elif self.person:
                        
                        # Lookup federal context.
                        terms = self.person.terms.filter(role__level=c.ROLE_LEVEL_FEDERAL)
                        if terms.count():
                            contexts.append(Context.objects.get(country=terms[0].country, state=None, county=None))
                        terms = self.person.terms.filter(role__level=c.ROLE_LEVEL_FEDERAL, state__isnull=False)
                        if terms.count():
                            state = State.objects.get(state=terms[0].state)
                            contexts.append(Context.objects.get(country=terms[0].country, state=state, county=None))
                        
                        # Lookup state context.
                        terms = self.person.terms.filter(role__level=c.ROLE_LEVEL_STATE)
                        if terms.count():
                            state = State.objects.get(state=terms[0].state)
                            contexts.append(Context.objects.get(country=terms[0].country, state=state, county=None))
                            
                        #TODO:Lookup county context?
                        
                    for context in contexts:
                        URLContext.objects.get_or_create(
                            context=context,
                            url=url,
                            defaults=dict(creator=creator))
                    
                    if _:
                        print '\tNEW'
                    else:
                        print '\tOLD'
            #TODO:self.last_checked = timezone.now(); self.save()
        else:
            raise NotImplemented
        self.last_checked = timezone.now()
        self.next_check = timezone.now() + timedelta(days=self.account.min_check_hours/24.)
        self.save()

def feed_pre_delete(sender, instance, **kwargs):
    instance.unregister(save=False)
signals.pre_delete.connect(feed_pre_delete, sender=Feed)

class CommentManager(models.Manager):
    
    def get_undeleted(self):
        return self.filter(deleted__isnull=True)
    
    def get_to_person(self, person):
        return self.filter(
            person__isnull=False,
            person__real=False)

    def get_read_to_person(self, person):
        return self.get_to_person(person=person).filter(read=True)
    
    def get_unread_to_person(self, person):
        return self.get_to_person(person=person).filter(read=False)
    
def get_client_ip(request=None):
    request = request or middleware.get_current_request()
    if not request:
        return
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class Comment(BaseModel, BaseVoteTarget):
    
    objects = CommentManager()
    
    issue = models.ForeignKey(
        'Issue',
        related_name='comments',
        blank=True, null=True)
    
    link = models.ForeignKey(
        'Link',
        related_name='comments',
        blank=True, null=True)
    
    person = models.ForeignKey(
        'Person',
        related_name='comments',
        blank=True, null=True)
    
    motion = models.ForeignKey(
        'Motion',
        related_name='comments',
        blank=True, null=True)
    
    comment = models.ForeignKey(
        'self',
        related_name='comments',
        blank=True, null=True)
    
    creator = models.ForeignKey(
        'Person',
        blank=False,
        null=False,
        related_name='comments_created')
    
    depth = models.PositiveIntegerField(
        default=0,
        editable=False,
        blank=False,
        null=False,
        db_index=True)
    
    reply_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        blank=False,
        null=False,
        db_index=True)
    
    votes_up = models.PositiveIntegerField(default=0)
    
    votes_down = models.PositiveIntegerField(default=0)
    
    absolute_votes = models.PositiveIntegerField(default=0)
    
    weight = models.IntegerField(
        default=0,
        help_text='Count of up votes minus count of down votes.')
    
    text = models.CharField(
        max_length=700,
        blank=False,
        null=False)
    
    address = models.GenericIPAddressField(
        db_index=True,
        default=get_client_ip,
        editable=False,
        blank=True,
        null=True)
    
    read = models.BooleanField(
        default=False,
        db_index=True,
        help_text='If checked, and this is a comment to a user, indicates ' \
            'that that user has read the comment.')
    
    top_weight = models.FloatField(
        editable=False,
        blank=True,
        null=True)
    
    rand = models.FloatField(
        editable=False,
        default=random.random,
        blank=False,
        null=False)
    
    class Meta:
        app_label = APP_LABEL
        unique_together = (
            ('issue', 'link', 'person', 'motion', 'comment', 'creator'),
        )
    
    @property
    def unread(self):
        request = middleware.get_current_request()
        if not request.user.is_authenticated():
            return
        if self.comment and self.comment.creator.user == request.user:
            return not self.read
    
    def mark_read(self):
        self.read = True
        self.save()
        return ''
    
    def replies(self):
        return self.comments.all().order_by('-top_weight', 'created')
    
    def undeleted_replies(self):
        return self.comments.filter(deleted__isnull=True).order_by('-top_weight', 'created')
    
    @property
    def target(self):
        """
        Returns the object that the comment is directly referring to.
        """
        if self.issue:
            return self.issue
        elif self.person:
            return self.person
        elif self.link:
            return self.link
        elif self.motion:
            return self.motion
        elif self.comment:
            return self.comment
    
    @property
    def top_target(self):
        """
        Returns the top-most record referred by the comment that is not also
        a comment.
        """
        target = self.target
        if isinstance(target, Comment):
            return target.top_target
        else:
            return target
        
    @property
    def top_target_name(self):
        target = self.top_target
        if isinstance(target, Link):
            return target.better_display_text
        elif isinstance(target, Comment):
            return unicode(target)
        elif isinstance(target, Issue):
            return target.friendly_text
        elif isinstance(target, Person):
            return unicode(target)
        elif isinstance(target, Motion):
            return unicode(target)
    
    def get_absolute_url(self):
        top_target = self.top_target
        return top_target.get_absolute_url() + '?comment=' + str(self.id)
    
    @property
    def object(self):
        return self

    @property
    def vote_type(self):
        return c.COMMENT
    
    def update_reply_count(self):
        self.reply_count = self.comments.all().count()

    def clean(self, *args, **kwargs):
        result = super(Comment, self).clean(*args, **kwargs)
        items = [_ for _ in [
            self.issue, self.link, self.person, self.motion, #self.comment
        ] if _]
        if len(items) > 1:
            raise ValidationError, \
                'Only one type may be specified.'
        if self.comment:
            self.depth = self.comment.depth + 1
            self.issue = self.comment.issue
            self.link = self.comment.link
            self.person = self.comment.person
            self.motion = self.comment.motion
        self.update_reply_count()
        return result
    
    def save(self, *args, **kwargs):
        self.update_vote_weight()
        super(Comment, self).save(*args, **kwargs)
        if self.comment:
            self.comment.save()

class PositionAgreement(models.Model):
    """
    Lists all matches that need to be created or updated.
    """
    
    id = models.CharField(
        max_length=100,
        primary_key=True,
        blank=False,
        null=False)
    
    issue = models.ForeignKey(
        Issue,
        related_name='issue_agreements',
        on_delete=models.DO_NOTHING,
        db_column='issue_id')
    
    your_person = models.ForeignKey(
        Person,
        related_name='your_agreements',
        on_delete=models.DO_NOTHING,
        db_column='your_person_id')
    
    your_polarity = models.CharField(
        max_length=20,
        choices=c.POSITION_CHOICES,
        blank=True,
        null=True)
    
    their_person = models.ForeignKey(
        Person,
        related_name='their_agreements',
        on_delete=models.DO_NOTHING,
        db_column='their_person_id')
    
    their_polarity = models.CharField(
        max_length=20,
        choices=c.POSITION_CHOICES,
        blank=True,
        null=True)
    
    agree = models.NullBooleanField()
    
    unknown = models.BooleanField()
    
    class Meta:
        app_label = APP_LABEL
        managed = False
        db_table = 'issue_mapper_positionagreement'

class Quote(BaseModel):
    
    person = models.ForeignKey(
        Person,
        related_name='quotes')
    
    url = models.ForeignKey(
        URL,
        related_name='quotes',
        help_text='The URL documenting the context in which the person said the quote.')
    
    said_date = models.DateField(
        blank=False,
        null=False,
        help_text='The date when the person said or wrote the quoted text.')
    
    text = models.TextField(blank=False, null=False)
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('url', 'person__last_name', 'said_date')
        unique_together = (
            ('person', 'url', 'said_date', 'text'),
        )
        
        permissions = (
            (c.PERM_QUOTE_SUBMIT, u'Publically submit a quote for a person.'),
            (c.PERM_QUOTE_FLAG, u'Flag a quote for moderation.'),
            (c.PERM_QUOTE_VOTE, u'Vote on the importance of a quote.'),
        )

class ElectionManager(models.Manager):
    
    def get_public(self, q=None):
        if q is None:
            q = self
        return q.filter(public=True)
    
    def get_active(self, q=None):
        if q is None:
            q = self
        return self.get_public(q=q).filter(election_date__gte=date.today())
    
class Election(BaseModel):
    
    objects = ElectionManager()
    
    name = models.CharField(max_length=500, blank=False, null=False)
    
    slug = models.SlugField(max_length=500, blank=True, null=True, unique=True)
    
    google_civic_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        help_text='The ID for this election in the <a href="https://developers.google.com/civic-information/">Google Civic Information database</a>.')
    
    election_date = models.DateField(
        blank=False,
        null=False,
        db_index=True,
        help_text='The final drop-dead date when this election will be held.')
    
    public = models.BooleanField(
        default=True,
        help_text='If checked, this record will be publically viewable to normal users.')
    
    context = models.ForeignKey('Context', blank=True, null=True)
    
    wikipedia_page = models.URLField(blank=True, null=True)
    
    keywords = models.TextField(blank=True, null=True)
    
    generate_keywords = models.BooleanField(
        default=False,
        help_text='''If checked, the keywords field will be populated from
            candidates.''')
    
    search_index = VectorField()

    search_objects = SearchManager(
        fields = (
            'name',
            'wikipedia_page',
            'keywords',
        ),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('-election_date',)
    
    def __unicode__(self):
        return self.name
    
    def useful_links(self):
        lst = []
        if self.wikipedia_page:
            lst.append((self.wikipedia_page, 'Wikipedia'))
        return lst
    
    def get_absolute_url(self):
        slug = self.slug or self.id
        return reverse('election', args=(slug,))
    
    def save(self, *args, **kwargs):
        
        if self.generate_keywords:
            self.generate_keywords = False
            keywords = []
            for candidate in self.candidates.all():
                keywords.append(candidate.person.first_name or '')
                keywords.append(candidate.person.middle_name or '')
                keywords.append(candidate.person.last_name or '')
                keywords.append(candidate.person.nickname or '')
            self.keywords = ' '.join(_ for _ in keywords if _.strip())
        
        super(Election, self).save(*args, **kwargs)
    
    def object(self):
        return self
    
    def active(self):
        return self.public and self.election_date >= date.today()
    active.boolean = True
    
    @classmethod
    def import_google(cls, *args, **kwargs):
        """
        Loads election data from the Google Civic Information database.
        https://developers.google.com/civic-information/
        """
        
        ids = args or []
        
        def get(url, post_values=None):
            data = urllib.urlencode(post_values) if post_values else None
            print 'data:',data
            req = urllib2.Request(url, data)#, {'user-agent':settings.OFFICIAL_BOT_USERAGENT})
            opener = urllib2.build_opener()
            f = opener.open(req)
            return simplejson.load(f)
        
        url = 'https://www.googleapis.com/civicinfo/us_v1/elections?key={APIKEY}'\
            .format(APIKEY=settings.GOOGLE_CIVIC_INFORMATION_APIKEY)
        
        data = get(url)
        for election in data.get('elections', []):
            google_civic_id=election['id'].strip()
            if ids and google_civic_id not in ids:
                continue
            print election
            
            electionObj, _ = Election.objects.get_or_create(
                google_civic_id=google_civic_id,
                defaults=dict(
                    name=election['name'],
                    election_date=dateutil.parser.parse(election['electionDay']),
                ),
            )
            
            #TODO:must pass "address" in body via POST?
#            url = 'https://www.googleapis.com/civicinfo/us_v1/voterinfo/{election_id}/lookup?key={APIKEY}'\
#                .format(
#                    APIKEY=settings.GOOGLE_CIVIC_INFORMATION_APIKEY,
#                    election_id=electionObj.google_civic_id)
#            print url
            #candidates = get(url, post_values=dict(address='244 5th Ave # 2, New York, NY 10001',))
            
#            h = httplib.HTTPSConnection('www.googleapis.com')
#            h.request(
#                'POST',
#                '/civicinfo/us_v1/voterinfo/{election_id}/lookup?key={APIKEY}'\
#                    .format(
#                        APIKEY=settings.GOOGLE_CIVIC_INFORMATION_APIKEY,
#                        election_id=electionObj.google_civic_id),
#                urllib.urlencode(dict(address='244 5th Ave # 2, New York, NY 10001')),
#                {
#                 #"Content-type": "application/x-www-form-urlencoded",
#                 "Accept": "text/plain"
#                 }
#            )
#            r = h.getresponse()
#            print 'r:',r
#            candidates = simplejson.load(r)

            #TODO:api requires an address of the voter, which we don't have, so just bulk load everything?
#            response = commands.getoutput(('curl -s -H "Content-Type: application/json" -'
#                'd "{ \'address\': \'%(address)s\' }" '
#                '"https://www.googleapis.com/civicinfo/us_v1/voterinfo/%(election_id)s/lookup?key=%(APIKEY)s"')\
#                % dict(
#                    APIKEY=settings.GOOGLE_CIVIC_INFORMATION_APIKEY,
#                    address='244 5th Ave # 2, New York, NY 10001',
#                    election_id=electionObj.google_civic_id,
#                ),
#            )
#            #print 'response:',response
#            candidates = simplejson.loads(response)
#            
#            print candidates
#            contests = candidates.get('contests', [])
#            if contests:
#                todo
#            else:
#                print 'No contests found!?'
            

class Candidate(BaseModel):
    
    election = models.ForeignKey(Election, related_name='candidates')
    
    person = models.ForeignKey(Person, related_name='candidates')
    
    role = models.ForeignKey(Role)
    
    party = models.ForeignKey(Party)
    
    won = models.NullBooleanField(default=None, db_index=True)
    
    class Meta:
        app_label = APP_LABEL
        ordering = ('election',)
        unique_together = (
            'election',
            'person',
            'role',
        )
    
    def __unicode__(self):
        return '%s running for %s in %s' \
            % (self.person, self.role, self.election)
            