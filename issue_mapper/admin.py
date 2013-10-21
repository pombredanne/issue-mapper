from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

import reversion

import admin_steroids
from admin_steroids import formatters as f
from admin_steroids.filters import NullListFilter

import models

from django.contrib.admin.sites import AdminSite as _AdminSite

#class AdminSite(_AdminSite):
#    
#    def app_index(self, request, app_label, extra_context=None):
#        #extra_context['']
#        super(AdminSite, self).app_index(request, app_label, extra_context)

#site = AdminSite()
site = admin.site

terms_field = f.OneToManyLink('terms',
        title='Terms',
        url_param='admin:issue_mapper_term',
        id_param='person__id')

class PersonAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    prepopulated_fields = {
    }
#    fields = (
#        'user',
#        'nickname',
#    )
    list_display = (
        'id',
        f.ReadonlyFormat(
            'user__username',
            title='username'),
        'slug',
        'first_name',
        'middle_name',
        'last_name',
        'nickname',
        'year_born',
        'year_died',
        'link_karma',
        'issue_karma',
        'comment_karma',
        'real',
        'public',
        'active',
        'is_duplicate',
        'photo_checked',
        'issue_link_count',
        'position_count',
        'top_weight',
    )
    list_filter = (
        'real',
        'active',
        'public',
        'bot',
        'gender',
        'photo_checked',
        ('slug', NullListFilter),
        ('photo', NullListFilter),
        ('wikipedia_page', NullListFilter),
        ('ontheissues_page', NullListFilter),
        'ontheissues_page_confirmed',
        ('deleted', NullListFilter),
        ('duplicate_of', NullListFilter),
    )
    exclude = (
        #'search_index',
    )
    search_fields = (
        'slug',
        'first_name',
        'middle_name',
        'last_name',
        'year_born',
        'year_died',
        'user__username',
        'user__email',
    )
    raw_id_fields = (
        'user',
        'duplicate_of',
        'creator',
    )
    
    base_readonly_fields = (
    #readonly_fields = (
        'id',
        'thumbnail',
        'uuid',
        'created',
        'updated',
        'last_seen',
        #'gender',
        'last_url_vote',
        'total_karma',
        'top_weight',
        'rand',
        'search_index',
        'urls_submitted',
        'urls_voted_on',
        'issue_tags_created',
        'issue_tags_voted_on',
        'person_tags_created',
        'person_tags_voted_on',
        'flags_created_count',
        terms_field,
        'add_term_link',
    )
#    )
    inlines = (
    )
    
#    def id(self, obj=None):
#        if obj is None:
#            return ''
#        return obj.id
    
    def get_fieldsets(self, request, obj=None):
        fields = ['id', 'thumbnail']
        fields += [_.name for _ in self.model._meta.fields if _.name not in fields]
        
        self.base_readonly_fields = list(self.base_readonly_fields)
        self.base_readonly_fields.append(terms_field)
        fields.append(terms_field)
        
        #print 'fields:',fields
        return (
            (None, {
            'fields': (
                'thumbnail',
                'id',
                'slug',
                'uuid',
                'user',
                'creator',
                terms_field,
                'add_term_link',
            ),
            }),
            ('Names', {
                'classes': (),
                'fields': (
                    'nickname',
                    'first_name',
                    'first_name_is_initial',
                    'middle_name',
                    'middle_name_is_initial',
                    'last_name',
                    'suffix_abbreviation',
                ),
            }),
            ('Flags', {
                'classes': (),
                'fields': (
                    'bot',
                    'public',
                    'active',
                    'real',
                    'needs_review',
                ),
            }),
            ('Photo', {
                'classes': (),
                'fields': (
                    'photo',
                    'photo_thumbnail',
                    'photo_checked',
                ),
            }),
            ('Dates', {
                'classes': (),
                'fields': (
                    'birthday',
                    'passed_date',
                    'year_born',
                    'year_died',
                    'last_seen',
                ),
            }),
            ('Karma', {
                'classes': (),
                'fields': (
                    'link_karma',
                    'url_karma',
                    'issue_karma',
                    'comment_karma',
                    'extra_karma',
                    'total_karma',
                ),
            }),
            ('Remote IDs', {
                'classes': (),
                'fields': (
                    'govtrack_id',
                    'cspan_id',
                    'twitter_id',
                    'youtube_id',
                    'os_id',
                    'pvs_id',
                    'bioguide_id',
                    'openstate_id',
                ),
            }),
            ('URLs', {
                'classes': (),
                'fields': (
                    'wikipedia_page',
                    'wikipedia_page_confirmed',
                    'wikipedia_checked',
                    'download_from_wikipedia',
                    
                    'govtrack_page',
                    'ontheissues_page',
                    'ontheissues_page_confirmed',
                ),
            }),
            ('Site Contributions', {
                'classes': (),
                'fields': (
                    'urls_submitted',
                    'urls_voted_on',
                    'issue_tags_created',
                    'issue_tags_voted_on',
                    'person_tags_created',
                    'person_tags_voted_on',
                    'flags_created_count',
                ),
            }),
            ('Details', {
                'classes': (),
                'fields': (
                    'duplicate_of',
                    'duplicate_merged',
                    'gender',
                    'issue_link_count',
                    'position_count',
                    'default_notification_method',
                    'top_weight',
                    'rand',
                    'search_index',
                ),
            }),
        )
    
    def lookup_allowed(self, key, value=None):
        return True
    
    def thumbnail(self, obj):
        try:
            if obj.photo_thumbnail:
                return '<img src="%s" />' % (obj.photo_thumbnail.url,)
        except Exception, e:
            return str(e)
    thumbnail.allow_tags = True
    
    def add_term_link(self, obj):
        if not obj or not obj.id:
            return ''
        url = admin_steroids.utils.get_admin_changelist_url(models.Term)
        url += 'add/?person=%i' % (obj.id,)
        return '<a href="%s" target="_blank">Add</a>' % (url,)
    add_term_link.short_description = 'Term'
    add_term_link.allow_tags = True
    
    def toggle_active(self, request, qs=None):
        for r in qs:
            r.active = not r.active
            r.save()
    toggle_active.short_description = \
        'Toggle active flag for selected %(verbose_name_plural)s records'
    
    def toggle_public(self, request, qs=None):
        for r in qs:
            r.public = not r.public
            r.save()
    toggle_public.short_description = \
        'Toggle public flag for selected %(verbose_name_plural)s records'
    
    def get_actions(self, request):
        actions = self.actions if hasattr(self, 'actions') else []
        actions.append('toggle_active')
        actions.append('toggle_public')
        actions = super(PersonAdmin, self).get_actions(request)
        return actions
    
site.register(models.Person, PersonAdmin)

#class PositionChoiceInline(admin_steroids.BetterRawIdFieldsTabularInline):
#    model = models.PositionChoice

class LinkInline(admin_steroids.BetterRawIdFieldsTabularInline):
    model = models.Link
    
    raw_id_fields = (
        'creator',
        'url',
        'person',
        'feed',
    )
    
    base_readonly_fields = (
        'created',
    )

links_field = f.OneToManyLink('links',
    title='Links',
    url_param='admin:issue_mapper_link',
    id_param='issue')

class IssueAdmin(admin_steroids.BetterRawIdFieldsModelAdmin):
    prepopulated_fields = {
        "slug": ("issue",)
    }
    list_display = (
        'id',
        'issue',
        'slug',
        'position_count',
        'view_count',
        'created',
        'creator',
        'cached_weight',
        'flip_polarity',
        'public',
        'active',
    )
    list_editable = (
        'issue',
        'slug',
        'flip_polarity',
    )
    list_filter = (
        'public',
        'active',
    )
    search_fields = (
        'issue',
        'slug',
    )
    raw_id_fields = (
        'creator',
        'contexts',
        #'url',
    )
    fields = (
        'issue',
        'slug',
        'keywords',
        'public',
        'active',
        'creator',
        'position_count',
        'view_count',
        'cached_weight',
        'contexts',
        links_field,
    )
    readonly_fields = (
        'position_count',
        'view_count',
        'last_position_datetime',
        'last_view_datetime',
        'last_link_datetime',
        'cached_weight',
        links_field,
    )
    inlines = (
        #LinkInline,
    )
    
    def toggle_active(self, request, qs=None):
        for r in qs:
            r.active = not r.active
            r.save()
    toggle_active.short_description = \
        'Toggle active flag for selected %(verbose_name_plural)s records'
    
    def toggle_public(self, request, qs=None):
        for r in qs:
            r.public = not r.public
            r.save()
    toggle_public.short_description = \
        'Toggle public flag for selected %(verbose_name_plural)s records'
    
    def get_actions(self, request):
        actions = self.actions if hasattr(self, 'actions') else []
        actions.append('toggle_active')
        actions.append('toggle_public')
        actions = super(IssueAdmin, self).get_actions(request)
        return actions
        
site.register(models.Issue, IssueAdmin)

#from django import forms
#
#class PositionModelForm(forms.ModelForm):
#    class Meta:
#        model = models.Position
#        
#    def __init__(self, *args, **kwargs):
#        inst = kwargs.get('instance')
#        print '!'*80
#        print 'inst:',inst
#        super(PositionModelForm, self).__init__(*args, **kwargs)
#        if inst:
#            self.fields['position_choices'].queryset = inst.issue.position_choices.all()

class PositionAdmin(
    #admin.ModelAdmin
    admin_steroids.BetterRawIdFieldsModelAdmin):
    #form = PositionModelForm
    
    list_display = (
        'id',
        'issue',
        'polarity',
        'importance',
        'person',
        'creator',
        'created',
    )
    search_fields = (
        'issue__issue',
    )
    raw_id_fields = (
        'issue',
#        'position_choice',
        'person',
        'creator',
    )
    readonly_fields = (
        'created',
        'updated',
    )
    list_filter = (
        ('polarity', NullListFilter),
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.Position, PositionAdmin)

class LinkAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'url',
        'some_title',
        'creator',
        'issue',
        'person',
        'top_weight',
        'absolute_votes',
        'rand',
        'created',
    )
    
    list_filter = (
        ('top_weight', NullListFilter),
        ('issue', NullListFilter),
        ('person', NullListFilter),
        ('feed', NullListFilter),
    )
    
    raw_id_fields = (
        'url',
        'feed',
        'issue',
        'person',
        'creator',
    )
    
    base_readonly_fields = (
        'some_title',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.Link, LinkAdmin)

class TagAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'slug',
        'created',
        'creator',
    )
    fields = (
        'slug',
        'deleted',
        #'created',
        #'updated',
    )
    search_fields = (
        'slug',
    )
site.register(models.Tag, TagAdmin)

class URLAdmin(
    #admin_steroids.BetterRawIdFieldsModelAdmin,
    #admin_steroids.FormatterModelAdmin
    admin.ModelAdmin
    ):
    
    list_display = (
        'id',
        'url',
        'title',
        'title_checked',
        'text_checked',
        'og_image_checked',
        'absolute_votes',
        'top_weight',
        'top_urlcontext_weight',
        'creator',
        'created',
    )
    
    list_filter = (
        'title_checked',
        'text_checked',
        'og_image_checked',
        ('feed', NullListFilter),
        ('title', NullListFilter),
        ('text', NullListFilter),
        ('og_image_thumbnail', NullListFilter),
        ('top_weight', NullListFilter),
        ('top_urlcontext_weight', NullListFilter),
    )
    
    search_fields = (
        'url',
        'title',
    )
    
    raw_id_fields = (
        'creator',
        'feed',
        'top_urlcontext',
    )
    
    readonly_fields = (
        'id',
        'thumbnail',
        'created',
        'updated',
        'deleted',
        'top_weight',
        'top_urlcontext_weight',
        'rand',
        'search_index',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
    def get_fieldsets(self, request, obj=None):
        fields = ['id', 'thumbnail']
        fields += [_.name for _ in self.model._meta.fields if _.name not in fields]
        
#        self.base_readonly_fields = list(self.base_readonly_fields)
#        self.base_readonly_fields.append(terms_field)
        #fields.append(terms_field)
        
        #print 'fields:',fields
        return (
            (None, {
            'fields': fields,
            }),
        )
    
    def thumbnail(self, obj):
        try:
            if obj.og_image_thumbnail:
                return '<img src="%s" />' % (obj.og_image_thumbnail.url,)
        except Exception, e:
            return str(e)
    thumbnail.allow_tags = True
    
site.register(models.URL, URLAdmin)

class URLContextAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    #admin.ModelAdmin
    ):
    
    list_display = (
        'id',
        'url_id',
        'context',
        'url',
        'absolute_votes',
        'weight',
        'creator',
        'top_weight',
        'rand',
        'created',
    )
    
    list_filter = (
        ('top_weight', NullListFilter),
    )
    
    search_fields = (
        'url__url',
        'url__text',
    )
    
    raw_id_fields = (
        'context',
        'url',
        'creator',
    )
    
    readonly_fields = (
        'id',
        #'creator',
        'top_weight',
        'weight',
        'absolute_votes',
        'votes_up',
        'votes_down',
        'created',
        'updated',
        'deleted',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
    def url_id(self, obj):
        if not obj:
            return ''
        return obj.url.id
    
site.register(models.URLContext, URLContextAdmin)

class URLVoteAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'url',
        'voter',
        'vote',
        'created',
    )
    
    raw_id_fields = (
        'url',
        'voter',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.URLVote, URLVoteAdmin)

class URLContextVoteAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'url_id',
        'url_context',
        'voter',
        'vote',
        'created',
        'url_context__created',
    )
    
    list_filter = (
        'vote',
        'voter__bot',
    )
    
    raw_id_fields = (
        'url_context',
        'voter',
    )
    
    def url_id(self, obj):
        if not obj:
            return ''
        return obj.url_context.url.id
    
    def url_context__created(self, obj):
        return obj.url_context.created
    url_context__created.admin_order_field = 'url_context__created'
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.URLContextVote, URLContextVoteAdmin)


class LinkVoteAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'link',
        'voter',
        'vote',
        'created',
    )
    
    raw_id_fields = (
        'link',
        'voter',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.LinkVote, LinkVoteAdmin)

class FlagJudgementInline(admin_steroids.BetterRawIdFieldsTabularInline):
    model = models.FlagJudgement

    extra = 0

    raw_id_fields = (
        'judge',
    )
    
class FlagAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'issue',
        'link',
        'person',
        'flagger',
        'created',
        'judged',
    )
    list_filter = (
        'judged',
    )
    
    raw_id_fields = (
        'issue',
        'link',
        'person',
        'flagger',
    )
    
    base_readonly_fields = (
        'type',
        'created',
        'comment',
    )
    
    inlines = (
        FlagJudgementInline,
    )
    
    def lookup_allowed(self, key, value=None):
        return True

site.register(models.Flag, FlagAdmin)

class MotionAdmin(
    #admin.ModelAdmin
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'id',
        'issue',
        'link',
        'person',
        'creator',
        'attribute',
        'new_value',
        'pending',
        'weight',
    )
    list_filter = (
        'pending',
    )
    
    raw_id_fields = (
        'issue',
        'link',
        'person',
        'creator',
    )
    
    readonly_fields = (
        'created',
        'votes_up',
        'votes_down',
        'weight',
    )
    
#    inlines = (
#        FlagJudgementInline,
#    )
    
    def lookup_allowed(self, key, value=None):
        return True

site.register(models.Motion, MotionAdmin)


class PositionAggregateAdmin(
    #admin.ModelAdmin
    admin_steroids.BetterRawIdFieldsModelAdmin):
    
    list_display = (
        'id',
        'issue',
        'person',
        'date',
        'oppose_count',
        'undecided_count',
        'favor_count',
        'total_count',
        'total_bots',
        f.FloatFormat('entropy'),
        'polarity',
        'created',
        'updated',
    )
    list_filter = (
        'fresh',
    )
    
    readonly_fields = (
        'id',
        'issue',
        'person',
        'date',
        'oppose_count',
        'undecided_count',
        'favor_count',
        'total_count',
        'total_bots',
        f.FloatFormat('entropy'),
        'polarity',
        'created',
        'updated',
    )
    
    raw_id_fields = (
        'issue',
        'person',
    )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.PositionAggregate, PositionAggregateAdmin)

class MatchAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin):
    
    list_display = (
        'matcher',
        'matchee',
        'value',
        'created',
        'updated',
    )
    
    search_fields = (
        'matcher__user__username',
        'matchee__first_name',
        'matchee__last_name',
    )
    
site.register(models.Match, MatchAdmin)

class TermAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin):
    
    list_display = (
        'id',
        'person',
        'role',
        'party',
        'start_date',
        'end_date',
        'state',
        'country',
    )
    
    list_filter = (
        'role',
        'party',
        'state',
        'country',
    )
    
    search_fields = (
        'person__first_name',
        'person__last_name',
    )
    
    raw_id_fields = (
        'person',
        'role',
        'party',
        'country',
        'county',
    )
    
site.register(models.Term, TermAdmin)

class RoleAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin):
    
    list_display = (
        'id',
        'name',
        'slug',
        'level',
    )
    
    list_filter = (
        'level',
    )
    
    search_fields = (
        'name',
        'slug',
    )
    
site.register(models.Role, RoleAdmin)

class PartyAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin):
    
    list_display = (
        'id',
        'name',
        'slug'
    )
    
    search_fields = (
        'name',
        'slug'
    )
    
site.register(models.Party, PartyAdmin)

class FeedAccountAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'type',
        'url',
        'username',
        'active',
    )
    list_filter = (
        'active',
    )
    base_readonly_fields = (
        'id',
        #'total_feeds',
        'created',
        'updated',
        #'deleted',
    )
    fields = (
        'id',
        'type',
        'url',
        'username',
        'password',
        #'total_feeds',
        'max_feeds',
        'active',
        'min_check_hours',
        'deleted',
        f.OneToManyLink(
            'feeds',
            title='feeds',
            url_param='admin:issue_mapper_feed',
            id_param='account'
        ),
    )
    
#    def get_fieldsets(self, request, obj=None):
#        fields = ['id',]
#        fields += [_f.name for _f in self.model._meta.fields if _f.name not in fields]
##        total_feeds = f.OneToManyLink(
##            'feeds',
##            title='feeds',
##            url_param='admin:issue_mapper_feed',
##            id_param='account'
##        )
##        fields.append(total_feeds)
##        self.base_readonly_fields = list(self.base_readonly_fields)
##        self.base_readonly_fields.append(total_feeds)
#        print 'fields:',fields
#        return (
#            (None, {
#            'fields':fields
#            }),
#        )
    
    def lookup_allowed(self, key, value=None):
        return True
    
site.register(models.FeedAccount, FeedAccountAdmin)

class CommentAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'text',
        'creator',
        'address',
        'reply_count',
        'top_weight',
        'rand',
        'deleted',
    )
    list_filter = (
        ('deleted', NullListFilter),
    )
    search_fields = (
        'text',
    )
    raw_id_fields = (
        'issue',
        'link',
        'person',
        'motion',
        'comment',
        'creator',
    )
site.register(models.Comment, CommentAdmin)
    
class FeedAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'account',
        'issue',
        'person',
        'query',
        'last_checked',
        'active',
        'link_count',
    )
    list_filter = (
        ('issue', NullListFilter),
        ('person', NullListFilter),
        'active',
        'account',
        ('last_checked', NullListFilter),
    )
    raw_id_fields = (
        'account',
        'person',
        'issue',
    )
    search_fields = (
        'query',
    )
    readonly_fields = (
        'link_count',
    )
    
site.register(models.Feed, FeedAdmin)

class PriviledgeAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        #'id',
        'site',
    )
    
site.register(models.Priviledge, PriviledgeAdmin)

class QuoteAdmin(
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin):
    
    list_display = (
        'id',
        'person',
        'url',
        'text',
        'said_date',
    )
    
    raw_id_fields = (
        'person',
        'url',
    )
    
site.register(models.Quote, QuoteAdmin)

class StateAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'id',
        'country',
        'state',
        #'state_name',
    )
    
    search_fields = (
        'state',
        '_state_name',
    )
    
    raw_id_fields = (
        'country',
    )
    
    base_readonly_fields = (
        '_state_name',
    )
    
    pass

site.register(models.State, StateAdmin)

class CountyAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    raw_id_fields = (
        'state',
    )
    
    pass

site.register(models.County, CountyAdmin)

class ContextAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'id',
        'name',
        'country',
        'state_name',
        'county',
        'active',
        'public',
    )
    
    list_filter = (
        'active',
        'public',
        'country',
        'state',
    )
    
    search_fields = (
        'name',
        'country__printable_name',
        'state__state',
        'state___state_name',
        'county__name',
    )
    
    raw_id_fields = (
        'country',
        'state',
        'county',
    )
    
    base_readonly_fields = (
        'state_name',
        'search_index',
        'deleted',
        'updated',
        'created',
    )
    
    def state_name(self, obj):
        if not obj.state:
            return '(None)'
        return obj.state.state_name
    state_name.short_description = 'state'
    state_name.admin_order_field = 'state'
    
    pass

site.register(models.Context, ContextAdmin)

class ElectionCandidateInline(admin_steroids.BetterRawIdFieldsTabularInline):
    model = models.Candidate
    
    fields = (
        'person',
        'role',
        'party',
        'won',
    )
    
    raw_id_fields = (
        'person',
        'role',
        'party',
    )

class ElectionAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'id',
        'name',
        'context',
        'election_date',
        'public',
        'active',
    )
    
    list_filter = (
        'public',
        ('context', NullListFilter),
    )
    
    search_fields = (
        'name',
        'google_civic_id',
        'keywords',
        'wikipedia_page',
    )
    
    raw_id_fields = (
        'context',
    )
    
    base_readonly_fields = (
        'active',
        'deleted',
        'updated',
        'created',
        'keywords',
        'search_index',
    )
    
    inlines = (
        ElectionCandidateInline,
    )

site.register(models.Election, ElectionAdmin)

class CandidateAdmin(
    reversion.VersionAdmin,
    admin_steroids.BetterRawIdFieldsModelAdmin,
    admin_steroids.FormatterModelAdmin
    ):
    
    list_display = (
        'id',
        'election',
        'person',
        'role',
        'party',
    )
    
    list_filter = (
    )
    
    search_fields = (
        'election__name',
        'election__google_civic_id',
    )
    
    raw_id_fields = (
        'election',
        'person',
        'role',
        'party',
    )
    
    base_readonly_fields = (
        'deleted',
        'updated',
        'created',
    )

site.register(models.Candidate, CandidateAdmin)
