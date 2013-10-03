import datetime

from django.db.models import Max

from issue_mapper import models

#class BaseIndex(indexes.SearchIndex):
#    
#    text = indexes.CharField(document=True, use_template=True)
#    object_id = indexes.IntegerField()
#    top_weight = indexes.FloatField(default=0)
#    rand = indexes.FloatField()
#    
#    def get_updated_field(self):
#        return "updated"
#    
#    def prepare_top_weight(self, obj):
#        return obj.top_weight
#    
#    def prepare_rand(self, obj):
#        return obj.rand
#    
#    def prepare_object_id(self, obj):
#        return obj.id
#    
#    class Meta:
#        abstract = True
#
#class PersonIndex(BaseIndex, indexes.Indexable):
#    nickname = indexes.CharField()
#    first_name = indexes.CharField()
#    middle_name = indexes.CharField()
#    last_name = indexes.CharField()
#    slug = indexes.CharField()
#    term_role_name = indexes.CharField()
#    term_state = indexes.CharField()
#    term_latest_start_date = indexes.DateField()
#    term_latest_end_date = indexes.DateField()
#    term_latest_party = indexes.CharField()
#    has_photo = indexes.BooleanField(default='false')
#
#    def get_model(self):
#        return models.Person
#
#    def index_queryset(self, using=None):
#        """Used when the entire index for model is updated."""
#        return self.get_model().objects.get_real().filter(public=True, slug__isnull=False)
#    
#    def prepare_has_photo(self, person):
#        return bool(person.photo)
#    
#    def prepare_term_role_name(self, person):
#        return ' '.join(term.role.name for term in person.terms.all())
#    
#    def prepare_term_state(self, person):
#        return ' '.join((term.state or '') for term in person.terms.all())
#    
#    def prepare_term_latest_start_date(self, person):
#        q = person.terms.all().aggregate(Max('start_date'))
#        if not q:
#            return
#        return q['start_date__max']
#    
#    def prepare_term_latest_end_date(self, person):
#        q = person.terms.all().aggregate(Max('end_date'))
#        if not q:
#            return
#        return q['end_date__max']
#
#    def prepare_term_latest_party(self, person):
#        q = person.terms.all().order_by('-end_date')
#        if not q or not q[0].party:
#            return
#        return q[0].party.slug
#
#class LinkIndex(BaseIndex, indexes.Indexable):
#    person = indexes.IntegerField()
#    issue = indexes.IntegerField()
#    link_title = indexes.CharField()
#    url_title = indexes.CharField()
#    url = indexes.CharField()
#    person_name = indexes.CharField()
#
#    def get_model(self):
#        return models.Link
#
#    def index_queryset(self, using=None):
#        """Used when the entire index for model is updated."""
#        return self.get_model().objects.all()
#    
#    def prepare_issue(self, link):
#        if not link.issue:
#            return 0
#        return link.issue.id
#    
#    def prepare_person(self, link):
#        if not link.person:
#            return 0
#        return link.person.id
#    
#    def prepare_person_name(self, link):
#        if not link.person:
#            return
#        person = link.person
#        return '%s %s %s %s' % (
#            person.nickname or '',
#            person.first_name or '',
#            person.middle_name or '',
#            person.last_name or '',
#        )
#    
#    def prepare_link_title(self, link):
#        return link.title
#    
#    def prepare_url_title(self, link):
#        return link.url.title
#    
#    def prepare_url(self, link):
#        return link.url.url
#    
#class IssueIndex(BaseIndex, indexes.Indexable):
#    issue = indexes.CharField()
#    slug = indexes.CharField()
#    public = indexes.BooleanField(default='false')
#
#    def get_model(self):
#        return models.Issue
#
#    def index_queryset(self, using=None):
#        """Used when the entire index for model is updated."""
#        return self.get_model().objects.all()
#    
#    def prepare_public(self, issue):
#        return bool(issue.public)
#    