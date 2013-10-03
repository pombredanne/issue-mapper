# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'issue_mapper_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='people_created', null=True, to=orm['issue_mapper.Person'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='10a84f55f00a486e956eda9bd46bbe15', unique=True, max_length=32, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('real', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('link_karma', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('issue_karma', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('comment_karma', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('extra_karma', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('total_karma', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('photo_thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('photo_checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=1000, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('first_name_is_initial', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('middle_name_is_initial', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('suffix_abbreviation', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('year_born', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('year_died', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('passed_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('wikipedia_page', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('wikipedia_checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gender', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=10, null=True, blank=True)),
            ('govtrack_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
            ('cspan_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True, null=True, blank=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('youtube_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('os_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('pvs_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('bioguide_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('govtrack_page', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('duplicate_of', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Person'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('duplicate_merged', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue_link_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('position_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('needs_review', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_notification_method', self.gf('django.db.models.fields.CharField')(default='email', max_length=25, null=True, blank=True)),
            ('top_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('rand', self.gf('django.db.models.fields.FloatField')(default=0.7843802000440665)),
            ('search_index', self.gf('djorm_pgfulltext.fields.VectorField')(default='', null=True, db_index=True)),
        ))
        db.send_create_signal('issue_mapper', ['Person'])

        # Adding unique constraint on 'Person', fields ['slug', 'real', 'deleted']
        db.create_unique(u'issue_mapper_person', ['slug', 'real', 'deleted'])

        # Adding model 'Role'
        db.create_table(u'issue_mapper_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('level', self.gf('django.db.models.fields.CharField')(default='federal', max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('issue_mapper', ['Role'])

        # Adding unique constraint on 'Role', fields ['slug', 'level']
        db.create_unique(u'issue_mapper_role', ['slug', 'level'])

        # Adding model 'Party'
        db.create_table(u'issue_mapper_party', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countries.Country'])),
        ))
        db.send_create_signal('issue_mapper', ['Party'])

        # Adding model 'Tag'
        db.create_table(u'issue_mapper_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=25)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tags', null=True, to=orm['issue_mapper.Person'])),
        ))
        db.send_create_signal('issue_mapper', ['Tag'])

        # Adding model 'IssueTag'
        db.create_table(u'issue_mapper_issuetag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', to=orm['issue_mapper.Issue'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Tag'])),
        ))
        db.send_create_signal('issue_mapper', ['IssueTag'])

        # Adding unique constraint on 'IssueTag', fields ['issue', 'tag']
        db.create_unique(u'issue_mapper_issuetag', ['issue_id', 'tag_id'])

        # Adding model 'Term'
        db.create_table(u'issue_mapper_term', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='terms', to=orm['issue_mapper.Person'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('state', self.gf('django_localflavor_us.models.USStateField')(max_length=2, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countries.Country'])),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('senator_class', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Role'])),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Party'], null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('issue_mapper', ['Term'])

        # Adding unique constraint on 'Term', fields ['person', 'start_date', 'state', 'country', 'district', 'role']
        db.create_unique(u'issue_mapper_term', ['person_id', 'start_date', 'state', 'country_id', 'district', 'role_id'])

        # Adding model 'Issue'
        db.create_table(u'issue_mapper_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.CharField')(max_length=700, db_index=True)),
            ('issue_tagless', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=700, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=700)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issues', to=orm['issue_mapper.Person'])),
            ('position_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('view_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('last_position_datetime', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('last_view_datetime', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('last_link_datetime', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('cached_weight', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('needs_review', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('top_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('rand', self.gf('django.db.models.fields.FloatField')(default=0.32173309268623684)),
            ('search_index', self.gf('djorm_pgfulltext.fields.VectorField')(default='', null=True, db_index=True)),
        ))
        db.send_create_signal('issue_mapper', ['Issue'])

        # Adding model 'URL'
        db.create_table(u'issue_mapper_url', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=700, unique=True, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('title_checked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='urls', to=orm['issue_mapper.Person'])),
            ('spam', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='urls', null=True, on_delete=models.SET_NULL, to=orm['issue_mapper.Feed'])),
        ))
        db.send_create_signal(u'issue_mapper', ['URL'])

        # Adding model 'Link'
        db.create_table(u'issue_mapper_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='links', null=True, to=orm['issue_mapper.Issue'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issue_links', null=True, to=orm['issue_mapper.Person'])),
            ('title', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=300, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['issue_mapper.URL'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['issue_mapper.Person'])),
            ('votes_up', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('votes_down', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='links', null=True, on_delete=models.SET_NULL, to=orm['issue_mapper.Feed'])),
            ('top_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('rand', self.gf('django.db.models.fields.FloatField')(default=0.8433642391924211)),
            ('search_index', self.gf('djorm_pgfulltext.fields.VectorField')(default='', null=True, db_index=True)),
        ))
        db.send_create_signal('issue_mapper', ['Link'])

        # Adding unique constraint on 'Link', fields ['issue', 'person', 'url']
        db.create_unique(u'issue_mapper_link', ['issue_id', 'person_id', 'url_id'])

        # Adding model 'LinkVote'
        db.create_table(u'issue_mapper_linkvote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='link_votes', to=orm['issue_mapper.Person'])),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['issue_mapper.Link'])),
        ))
        db.send_create_signal('issue_mapper', ['LinkVote'])

        # Adding unique constraint on 'LinkVote', fields ['link', 'voter']
        db.create_unique(u'issue_mapper_linkvote', ['link_id', 'voter_id'])

        # Adding model 'CommentVote'
        db.create_table(u'issue_mapper_commentvote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comment_votes', to=orm['issue_mapper.Person'])),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['issue_mapper.Comment'])),
        ))
        db.send_create_signal('issue_mapper', ['CommentVote'])

        # Adding unique constraint on 'CommentVote', fields ['comment', 'voter']
        db.create_unique(u'issue_mapper_commentvote', ['comment_id', 'voter_id'])

        # Adding model 'Position'
        db.create_table(u'issue_mapper_position', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='positions', to=orm['issue_mapper.Issue'])),
            ('polarity', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('importance', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='positions', to=orm['issue_mapper.Person'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='positions_created', to=orm['issue_mapper.Person'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=700, null=True, blank=True)),
        ))
        db.send_create_signal('issue_mapper', ['Position'])

        # Adding unique constraint on 'Position', fields ['issue', 'person', 'deleted']
        db.create_unique(u'issue_mapper_position', ['issue_id', 'person_id', 'deleted'])

        # Adding model 'Motion'
        db.create_table(u'issue_mapper_motion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='motions', null=True, to=orm['issue_mapper.Issue'])),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='motions', null=True, to=orm['issue_mapper.Link'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='motions', null=True, to=orm['issue_mapper.Person'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='motions_created', to=orm['issue_mapper.Person'])),
            ('attribute', self.gf('django.db.models.fields.CharField')(max_length=700, db_index=True)),
            ('new_value', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=700, null=True, blank=True)),
            ('pending', self.gf('django.db.models.fields.NullBooleanField')(default=True, null=True, blank=True)),
            ('votes_up', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('votes_down', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('issue_mapper', ['Motion'])

        # Adding unique constraint on 'Motion', fields ['issue', 'link', 'person', 'attribute', 'new_value', 'pending']
        db.create_unique(u'issue_mapper_motion', ['issue_id', 'link_id', 'person_id', 'attribute', 'new_value', 'pending'])

        # Adding model 'MotionVote'
        db.create_table(u'issue_mapper_motionvote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('motion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['issue_mapper.Motion'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='motion_votes', to=orm['issue_mapper.Person'])),
            ('vote', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('issue_mapper', ['MotionVote'])

        # Adding unique constraint on 'MotionVote', fields ['motion', 'voter']
        db.create_unique(u'issue_mapper_motionvote', ['motion_id', 'voter_id'])

        # Adding model 'Flag'
        db.create_table(u'issue_mapper_flag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='flags', null=True, to=orm['issue_mapper.Issue'])),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='flags', null=True, to=orm['issue_mapper.Link'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='flags', null=True, to=orm['issue_mapper.Person'])),
            ('flagger', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flags_created', to=orm['issue_mapper.Person'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='spam', max_length=10, db_index=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('judged', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('issue_mapper', ['Flag'])

        # Adding unique constraint on 'Flag', fields ['issue', 'link', 'person', 'flagger']
        db.create_unique(u'issue_mapper_flag', ['issue_id', 'link_id', 'person_id', 'flagger_id'])

        # Adding model 'FlagJudgement'
        db.create_table(u'issue_mapper_flagjudgement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('flag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='judgements', to=orm['issue_mapper.Flag'])),
            ('judge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='judgements', to=orm['issue_mapper.Person'])),
            ('judgement', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('issue_mapper', ['FlagJudgement'])

        # Adding unique constraint on 'FlagJudgement', fields ['flag', 'judge']
        db.create_unique(u'issue_mapper_flagjudgement', ['flag_id', 'judge_id'])

        # Adding model 'PositionAggregate'
        db.create_table(u'issue_mapper_positionaggregate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='position_aggregates', to=orm['issue_mapper.Issue'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='position_aggregates', to=orm['issue_mapper.Person'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('fresh', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('oppose_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('undecided_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('favor_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('total_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('entropy', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('issue_mapper', ['PositionAggregate'])

        # Adding unique constraint on 'PositionAggregate', fields ['issue', 'person', 'date']
        db.create_unique(u'issue_mapper_positionaggregate', ['issue_id', 'person_id', 'date'])

        # Adding model 'Match'
        db.create_table(u'issue_mapper_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('matcher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='matches_for', to=orm['issue_mapper.Person'])),
            ('matchee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='matched_with', to=orm['issue_mapper.Person'])),
            ('fresh', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(db_index=True, null=True, blank=True)),
            ('issue_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('issue_mapper', ['Match'])

        # Adding unique constraint on 'Match', fields ['matcher', 'matchee']
        db.create_unique(u'issue_mapper_match', ['matcher_id', 'matchee_id'])

        # Adding model 'Priviledge'
        db.create_table(u'issue_mapper_priviledge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(related_name='priviledge_threshold', unique=True, to=orm['sites.Site'])),
            ('single_submit_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('single_submit_issue_unthrottled', self.gf('django.db.models.fields.PositiveIntegerField')(default=20)),
            ('submit_issue_throttle_minutes', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('many_approve_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
            ('single_answer_issue_for_themself', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('single_answer_issue_for_other', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('single_flag_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('single_submit_tag', self.gf('django.db.models.fields.PositiveIntegerField')(default=200)),
            ('many_approve_tag', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
            ('single_tag_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('many_approve_tag_issue', self.gf('django.db.models.fields.PositiveIntegerField')(default=500)),
            ('single_submit_link', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('single_submit_link_unthrottled', self.gf('django.db.models.fields.PositiveIntegerField')(default=20)),
            ('submit_link_throttle_minutes', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('single_vote_link', self.gf('django.db.models.fields.PositiveIntegerField')(default=50)),
            ('single_flag_link', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('single_submit_person', self.gf('django.db.models.fields.PositiveIntegerField')(default=100)),
            ('many_approve_person', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
            ('single_flag_person', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('moderate_flags', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000)),
            ('points_from_upvoted_link', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('points_from_downvoted_link', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('points_from_downvoting_link', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('points_from_answered_issue', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('points_from_trashed_issue', self.gf('django.db.models.fields.IntegerField')(default=-100)),
            ('points_from_trashed_link', self.gf('django.db.models.fields.IntegerField')(default=-100)),
            ('allow_registration', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'issue_mapper', ['Priviledge'])

        # Adding model 'FeedAccount'
        db.create_table(u'issue_mapper_feedaccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=100)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('total_feeds', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('max_feeds', self.gf('django.db.models.fields.PositiveIntegerField')(default=1000, db_index=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('min_check_hours', self.gf('django.db.models.fields.PositiveIntegerField')(default=23, db_index=True)),
        ))
        db.send_create_signal('issue_mapper', ['FeedAccount'])

        # Adding unique constraint on 'FeedAccount', fields ['url', 'username']
        db.create_unique(u'issue_mapper_feedaccount', ['url', 'username'])

        # Adding model 'Feed'
        db.create_table(u'issue_mapper_feed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='feeds', to=orm['issue_mapper.FeedAccount'])),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='feeds', null=True, to=orm['issue_mapper.Issue'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='feeds', null=True, to=orm['issue_mapper.Person'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_checked', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('next_check', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('link_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('issue_mapper', ['Feed'])

        # Adding unique constraint on 'Feed', fields ['account', 'person']
        db.create_unique(u'issue_mapper_feed', ['account_id', 'person_id'])

        # Adding model 'Comment'
        db.create_table(u'issue_mapper_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issue_mapper.Issue'])),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issue_mapper.Link'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issue_mapper.Person'])),
            ('motion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issue_mapper.Motion'])),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='comments', null=True, to=orm['issue_mapper.Comment'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments_created', to=orm['issue_mapper.Person'])),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('reply_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True)),
            ('votes_up', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('votes_down', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('address', self.gf('django.db.models.fields.GenericIPAddressField')(default=None, max_length=39, null=True, db_index=True, blank=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('top_weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('rand', self.gf('django.db.models.fields.FloatField')(default=0.12309288920533934)),
        ))
        db.send_create_signal('issue_mapper', ['Comment'])

        # Adding unique constraint on 'Comment', fields ['issue', 'link', 'person', 'motion', 'comment', 'creator']
        db.create_unique(u'issue_mapper_comment', ['issue_id', 'link_id', 'person_id', 'motion_id', 'comment_id', 'creator_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Comment', fields ['issue', 'link', 'person', 'motion', 'comment', 'creator']
        db.delete_unique(u'issue_mapper_comment', ['issue_id', 'link_id', 'person_id', 'motion_id', 'comment_id', 'creator_id'])

        # Removing unique constraint on 'Feed', fields ['account', 'person']
        db.delete_unique(u'issue_mapper_feed', ['account_id', 'person_id'])

        # Removing unique constraint on 'FeedAccount', fields ['url', 'username']
        db.delete_unique(u'issue_mapper_feedaccount', ['url', 'username'])

        # Removing unique constraint on 'Match', fields ['matcher', 'matchee']
        db.delete_unique(u'issue_mapper_match', ['matcher_id', 'matchee_id'])

        # Removing unique constraint on 'PositionAggregate', fields ['issue', 'person', 'date']
        db.delete_unique(u'issue_mapper_positionaggregate', ['issue_id', 'person_id', 'date'])

        # Removing unique constraint on 'FlagJudgement', fields ['flag', 'judge']
        db.delete_unique(u'issue_mapper_flagjudgement', ['flag_id', 'judge_id'])

        # Removing unique constraint on 'Flag', fields ['issue', 'link', 'person', 'flagger']
        db.delete_unique(u'issue_mapper_flag', ['issue_id', 'link_id', 'person_id', 'flagger_id'])

        # Removing unique constraint on 'MotionVote', fields ['motion', 'voter']
        db.delete_unique(u'issue_mapper_motionvote', ['motion_id', 'voter_id'])

        # Removing unique constraint on 'Motion', fields ['issue', 'link', 'person', 'attribute', 'new_value', 'pending']
        db.delete_unique(u'issue_mapper_motion', ['issue_id', 'link_id', 'person_id', 'attribute', 'new_value', 'pending'])

        # Removing unique constraint on 'Position', fields ['issue', 'person', 'deleted']
        db.delete_unique(u'issue_mapper_position', ['issue_id', 'person_id', 'deleted'])

        # Removing unique constraint on 'CommentVote', fields ['comment', 'voter']
        db.delete_unique(u'issue_mapper_commentvote', ['comment_id', 'voter_id'])

        # Removing unique constraint on 'LinkVote', fields ['link', 'voter']
        db.delete_unique(u'issue_mapper_linkvote', ['link_id', 'voter_id'])

        # Removing unique constraint on 'Link', fields ['issue', 'person', 'url']
        db.delete_unique(u'issue_mapper_link', ['issue_id', 'person_id', 'url_id'])

        # Removing unique constraint on 'Term', fields ['person', 'start_date', 'state', 'country', 'district', 'role']
        db.delete_unique(u'issue_mapper_term', ['person_id', 'start_date', 'state', 'country_id', 'district', 'role_id'])

        # Removing unique constraint on 'IssueTag', fields ['issue', 'tag']
        db.delete_unique(u'issue_mapper_issuetag', ['issue_id', 'tag_id'])

        # Removing unique constraint on 'Role', fields ['slug', 'level']
        db.delete_unique(u'issue_mapper_role', ['slug', 'level'])

        # Removing unique constraint on 'Person', fields ['slug', 'real', 'deleted']
        db.delete_unique(u'issue_mapper_person', ['slug', 'real', 'deleted'])

        # Deleting model 'Person'
        db.delete_table(u'issue_mapper_person')

        # Deleting model 'Role'
        db.delete_table(u'issue_mapper_role')

        # Deleting model 'Party'
        db.delete_table(u'issue_mapper_party')

        # Deleting model 'Tag'
        db.delete_table(u'issue_mapper_tag')

        # Deleting model 'IssueTag'
        db.delete_table(u'issue_mapper_issuetag')

        # Deleting model 'Term'
        db.delete_table(u'issue_mapper_term')

        # Deleting model 'Issue'
        db.delete_table(u'issue_mapper_issue')

        # Deleting model 'URL'
        db.delete_table(u'issue_mapper_url')

        # Deleting model 'Link'
        db.delete_table(u'issue_mapper_link')

        # Deleting model 'LinkVote'
        db.delete_table(u'issue_mapper_linkvote')

        # Deleting model 'CommentVote'
        db.delete_table(u'issue_mapper_commentvote')

        # Deleting model 'Position'
        db.delete_table(u'issue_mapper_position')

        # Deleting model 'Motion'
        db.delete_table(u'issue_mapper_motion')

        # Deleting model 'MotionVote'
        db.delete_table(u'issue_mapper_motionvote')

        # Deleting model 'Flag'
        db.delete_table(u'issue_mapper_flag')

        # Deleting model 'FlagJudgement'
        db.delete_table(u'issue_mapper_flagjudgement')

        # Deleting model 'PositionAggregate'
        db.delete_table(u'issue_mapper_positionaggregate')

        # Deleting model 'Match'
        db.delete_table(u'issue_mapper_match')

        # Deleting model 'Priviledge'
        db.delete_table(u'issue_mapper_priviledge')

        # Deleting model 'FeedAccount'
        db.delete_table(u'issue_mapper_feedaccount')

        # Deleting model 'Feed'
        db.delete_table(u'issue_mapper_feed')

        # Deleting model 'Comment'
        db.delete_table(u'issue_mapper_comment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'countries.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'issue_mapper.comment': {
            'Meta': {'unique_together': "(('issue', 'link', 'person', 'motion', 'comment', 'creator'),)", 'object_name': 'Comment'},
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'default': 'None', 'max_length': '39', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['issue_mapper.Comment']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments_created'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['issue_mapper.Link']"}),
            'motion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['issue_mapper.Motion']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.4424761686522062'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'reply_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'votes_down': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'votes_up': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue_mapper.commentvote': {
            'Meta': {'unique_together': "(('comment', 'voter'),)", 'object_name': 'CommentVote'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['issue_mapper.Comment']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'vote': ('django.db.models.fields.IntegerField', [], {}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.feed': {
            'Meta': {'unique_together': "(('account', 'person'),)", 'object_name': 'Feed'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feeds'", 'to': "orm['issue_mapper.FeedAccount']"}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'feeds'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'last_checked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'link_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'next_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'feeds'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'issue_mapper.feedaccount': {
            'Meta': {'unique_together': "(('url', 'username'),)", 'object_name': 'FeedAccount'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_feeds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000', 'db_index': 'True'}),
            'min_check_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '23', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'total_feeds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'issue_mapper.flag': {
            'Meta': {'unique_together': "(('issue', 'link', 'person', 'flagger'),)", 'object_name': 'Flag'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'flagger': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flags_created'", 'to': "orm['issue_mapper.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'flags'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'judged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'flags'", 'null': 'True', 'to': "orm['issue_mapper.Link']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'flags'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'spam'", 'max_length': '10', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.flagjudgement': {
            'Meta': {'unique_together': "(('flag', 'judge'),)", 'object_name': 'FlagJudgement'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'flag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'judgements'", 'to': "orm['issue_mapper.Flag']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'judge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'judgements'", 'to': "orm['issue_mapper.Person']"}),
            'judgement': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.issue': {
            'Meta': {'ordering': "('-top_weight', 'rand')", 'object_name': 'Issue'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'cached_weight': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issues'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.CharField', [], {'max_length': '700', 'db_index': 'True'}),
            'issue_tagless': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'last_link_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_position_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_view_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'needs_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'position_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.3224454591828332'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '700'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'issue_mapper.issuetag': {
            'Meta': {'unique_together': "(('issue', 'tag'),)", 'object_name': 'IssueTag'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'to': "orm['issue_mapper.Issue']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Tag']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.link': {
            'Meta': {'ordering': "('-top_weight', 'rand')", 'unique_together': "(('issue', 'person', 'url'),)", 'object_name': 'Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_links'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.0358831798383904'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': u"orm['issue_mapper.URL']"}),
            'votes_down': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'votes_up': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue_mapper.linkvote': {
            'Meta': {'unique_together': "(('link', 'voter'),)", 'object_name': 'LinkVote'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['issue_mapper.Link']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'vote': ('django.db.models.fields.IntegerField', [], {}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'link_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.match': {
            'Meta': {'unique_together': "(('matcher', 'matchee'),)", 'object_name': 'Match'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'fresh': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'matchee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'matched_with'", 'to': "orm['issue_mapper.Person']"}),
            'matcher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'matches_for'", 'to': "orm['issue_mapper.Person']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'issue_mapper.matchpending': {
            'Meta': {'object_name': 'MatchPending', 'managed': 'False'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'matchee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pending_matches_with'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'matchee_id'", 'to': "orm['issue_mapper.Person']"}),
            'matcher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pending_matches_for'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'matcher_id'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.motion': {
            'Meta': {'unique_together': "(('issue', 'link', 'person', 'attribute', 'new_value', 'pending'),)", 'object_name': 'Motion'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '700', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'motions_created'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'motions'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'motions'", 'null': 'True', 'to': "orm['issue_mapper.Link']"}),
            'new_value': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'pending': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'motions'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'votes_down': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'votes_up': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue_mapper.motionvote': {
            'Meta': {'unique_together': "(('motion', 'voter'),)", 'object_name': 'MotionVote'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'motion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['issue_mapper.Motion']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'vote': ('django.db.models.fields.IntegerField', [], {}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'motion_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.party': {
            'Meta': {'object_name': 'Party'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['countries.Country']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'issue_mapper.person': {
            'Meta': {'ordering': "('-top_weight', 'rand')", 'unique_together': "(('slug', 'real', 'deleted'),)", 'object_name': 'Person'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'bioguide_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'comment_karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'people_created'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'cspan_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'default_notification_method': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'duplicate_merged': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Person']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'extra_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'first_name_is_initial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'govtrack_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'govtrack_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'issue_link_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'link_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'middle_name_is_initial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'needs_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'os_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'passed_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'photo_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'photo_thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'position_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'pvs_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.4701149334407615'}),
            'real': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'suffix_abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'e1176c668c894ccbae964559edb350f5'", 'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'wikipedia_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wikipedia_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year_born': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'year_died': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'youtube_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'issue_mapper.position': {
            'Meta': {'unique_together': "(('issue', 'person', 'deleted'),)", 'object_name': 'Position'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'positions_created'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'positions'", 'to': "orm['issue_mapper.Issue']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'positions'", 'to': "orm['issue_mapper.Person']"}),
            'polarity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.positionaggregate': {
            'Meta': {'unique_together': "(('issue', 'person', 'date'),)", 'object_name': 'PositionAggregate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'entropy': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'favor_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'fresh': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'position_aggregates'", 'to': "orm['issue_mapper.Issue']"}),
            'oppose_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'position_aggregates'", 'to': "orm['issue_mapper.Person']"}),
            'total_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'undecided_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        u'issue_mapper.priviledge': {
            'Meta': {'object_name': 'Priviledge'},
            'allow_registration': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'many_approve_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'many_approve_person': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'many_approve_tag': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'many_approve_tag_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '500'}),
            'moderate_flags': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'points_from_answered_issue': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'points_from_downvoted_link': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'points_from_downvoting_link': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'points_from_trashed_issue': ('django.db.models.fields.IntegerField', [], {'default': '-100'}),
            'points_from_trashed_link': ('django.db.models.fields.IntegerField', [], {'default': '-100'}),
            'points_from_upvoted_link': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'single_answer_issue_for_other': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'single_answer_issue_for_themself': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'single_flag_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'single_flag_link': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'single_flag_person': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'single_submit_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'single_submit_issue_unthrottled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '20'}),
            'single_submit_link': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'single_submit_link_unthrottled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '20'}),
            'single_submit_person': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'single_submit_tag': ('django.db.models.fields.PositiveIntegerField', [], {'default': '200'}),
            'single_tag_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'single_vote_link': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'priviledge_threshold'", 'unique': 'True', 'to': u"orm['sites.Site']"}),
            'submit_issue_throttle_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'submit_link_throttle_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.role': {
            'Meta': {'unique_together': "(('slug', 'level'),)", 'object_name': 'Role'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'default': "'federal'", 'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.tag': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'Tag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tags'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.term': {
            'Meta': {'ordering': "('person', 'start_date', 'end_date')", 'unique_together': "(('person', 'start_date', 'state', 'country', 'district', 'role'),)", 'object_name': 'Term'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['countries.Country']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Party']", 'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'terms'", 'to': "orm['issue_mapper.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Role']"}),
            'senator_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'state': ('django_localflavor_us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'issue_mapper.url': {
            'Meta': {'object_name': 'URL'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urls'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'urls'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'title_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '700', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['issue_mapper']