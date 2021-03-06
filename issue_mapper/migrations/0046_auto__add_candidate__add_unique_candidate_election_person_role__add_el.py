# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Candidate'
        db.create_table(u'issue_mapper_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Election'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Person'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Role'])),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue_mapper.Party'])),
        ))
        db.send_create_signal('issue_mapper', ['Candidate'])

        # Adding unique constraint on 'Candidate', fields ['election', 'person', 'role']
        db.create_unique(u'issue_mapper_candidate', ['election_id', 'person_id', 'role_id'])

        # Adding model 'Election'
        db.create_table(u'issue_mapper_election', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('google_civic_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, unique=True, null=True, blank=True)),
            ('election_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('issue_mapper', ['Election'])

        # Adding field 'Quote.created'
        db.add_column(u'issue_mapper_quote', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, db_index=True, blank=True),
                      keep_default=False)

        # Adding field 'Quote.updated'
        db.add_column(u'issue_mapper_quote', 'updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True, auto_now_add=True, null=True, db_index=True),
                      keep_default=False)

        # Adding field 'Quote.deleted'
        db.add_column(u'issue_mapper_quote', 'deleted',
                      self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'Candidate', fields ['election', 'person', 'role']
        db.delete_unique(u'issue_mapper_candidate', ['election_id', 'person_id', 'role_id'])

        # Deleting model 'Candidate'
        db.delete_table(u'issue_mapper_candidate')

        # Deleting model 'Election'
        db.delete_table(u'issue_mapper_election')

        # Deleting field 'Quote.created'
        db.delete_column(u'issue_mapper_quote', 'created')

        # Deleting field 'Quote.updated'
        db.delete_column(u'issue_mapper_quote', 'updated')

        # Deleting field 'Quote.deleted'
        db.delete_column(u'issue_mapper_quote', 'deleted')


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
        'issue_mapper.candidate': {
            'Meta': {'ordering': "('election',)", 'unique_together': "(('election', 'person', 'role'),)", 'object_name': 'Candidate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Election']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Party']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Role']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.comment': {
            'Meta': {'unique_together': "(('issue', 'link', 'person', 'motion', 'comment', 'creator'),)", 'object_name': 'Comment'},
            'absolute_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
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
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.40984632907466556'}),
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
            'vote': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.context': {
            'Meta': {'ordering': "('name', 'country', 'state', 'county')", 'unique_together': "(('name', 'country', 'state', 'county'),)", 'object_name': 'Context'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['countries.Country']", 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.County']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '700', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.State']", 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.county': {
            'Meta': {'ordering': "('state', 'name')", 'unique_together': "(('state', 'name'),)", 'object_name': 'County'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.State']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.election': {
            'Meta': {'ordering': "('-election_date',)", 'object_name': 'Election'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'election_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'google_civic_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
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
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'total_feeds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
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
            'contexts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['issue_mapper.Context']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issues'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'flip_polarity': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.CharField', [], {'max_length': '700', 'db_index': 'True'}),
            'issue_tagless': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'last_link_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_position_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_view_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'needs_review': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'position_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.45752589797422716'}),
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
            'Meta': {'ordering': "('-top_weight', '-created', 'rand')", 'unique_together': "(('issue', 'person', 'url'),)", 'object_name': 'Link'},
            'absolute_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'to': "orm['issue_mapper.Issue']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issue_links'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.9152225506508788'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['issue_mapper.URL']"}),
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
            'vote': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'bot': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'comment_karma': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'people_created'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'cspan_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'default_notification_method': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'duplicate_merged': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'duplicates'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.Person']"}),
            'extra_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'first_name_is_initial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '10', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'govtrack_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'govtrack_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'issue_link_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'last_url_vote': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'link_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'middle_name_is_initial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'needs_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'openstate_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'os_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'passed_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'photo_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'photo_thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'position_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'pvs_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.10647370752782881'}),
            'real': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'suffix_abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url_karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'562ce1fe2173416b8d924095fa3572c3'", 'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
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
            'polarity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'polarity_estimate': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'total_bots': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'total_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'undecided_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.positionagreement': {
            'Meta': {'object_name': 'PositionAgreement', 'managed': 'False'},
            'agree': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_agreements'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'issue_id'", 'to': "orm['issue_mapper.Issue']"}),
            'their_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'their_agreements'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'their_person_id'", 'to': "orm['issue_mapper.Person']"}),
            'their_polarity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'unknown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'your_person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'your_agreements'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'your_person_id'", 'to': "orm['issue_mapper.Person']"}),
            'your_polarity': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
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
            'single_flag_quote': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'single_quote_person': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'single_submit_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'single_submit_issue_unthrottled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '20'}),
            'single_submit_link': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'single_submit_link_unthrottled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '20'}),
            'single_submit_person': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'single_submit_quote': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'single_submit_tag': ('django.db.models.fields.PositiveIntegerField', [], {'default': '200'}),
            'single_tag_issue': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'single_vote_link': ('django.db.models.fields.PositiveIntegerField', [], {'default': '50'}),
            'single_vote_quote': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'single_vote_tag': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'priviledge_threshold'", 'unique': 'True', 'to': u"orm['sites.Site']"}),
            'submit_issue_throttle_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'submit_link_throttle_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'})
        },
        'issue_mapper.quote': {
            'Meta': {'ordering': "('url', 'person__last_name', 'said_date')", 'unique_together': "(('person', 'url', 'said_date', 'text'),)", 'object_name': 'Quote'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotes'", 'to': "orm['issue_mapper.Person']"}),
            'said_date': ('django.db.models.fields.DateField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotes'", 'to': "orm['issue_mapper.URL']"})
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
        'issue_mapper.state': {
            'Meta': {'ordering': "('country', 'state')", 'unique_together': "(('country', 'state'),)", 'object_name': 'State'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['countries.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django_localflavor_us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
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
            'county': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.County']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '700', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'terms'", 'null': 'True', 'to': "orm['issue_mapper.Party']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'terms'", 'to': "orm['issue_mapper.Person']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'terms'", 'to': "orm['issue_mapper.Role']"}),
            'senator_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django_localflavor_us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'issue_mapper.url': {
            'Meta': {'ordering': "('-top_weight', 'rand')", 'object_name': 'URL'},
            'absolute_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urls'", 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'urls'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'og_image_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'og_image_thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.46163561977698997'}),
            'search_index': ('djorm_pgfulltext.fields.VectorField', [], {'default': "''", 'null': 'True', 'db_index': 'True'}),
            'spam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'title_checked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'top_urlcontext': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'top_urls'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['issue_mapper.URLContext']"}),
            'top_urlcontext_weight': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '700', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'votes_down': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'votes_up': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue_mapper.urlcontext': {
            'Meta': {'unique_together': "(('url', 'context'),)", 'object_name': 'URLContext'},
            'absolute_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'context': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue_mapper.Context']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'url_contexts_created'", 'null': 'True', 'to': "orm['issue_mapper.Person']"}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rand': ('django.db.models.fields.FloatField', [], {'default': '0.5787779369471776'}),
            'top_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'url_contexts'", 'to': "orm['issue_mapper.URL']"}),
            'votes_down': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'votes_up': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue_mapper.urlcontextvote': {
            'Meta': {'ordering': "('-created',)", 'unique_together': "(('url_context', 'voter'),)", 'object_name': 'URLContextVote'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url_context': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['issue_mapper.URLContext']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'url_context_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        'issue_mapper.urlvote': {
            'Meta': {'unique_together': "(('url', 'voter'),)", 'object_name': 'URLVote'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['issue_mapper.URL']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'url_votes'", 'to': "orm['issue_mapper.Person']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['issue_mapper']