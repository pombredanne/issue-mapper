from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<object ids>'
    help = 'Updates model weights used for sorting.'
    option_list = BaseCommand.option_list + (
        make_option('--force', default=False, action='store_true'),
        make_option('--only', default=None),
        make_option('--only_null', default=False, action='store_true'),
        make_option('--top', default=None),
        make_option('--context', default=None),
    )

    def handle(self, *ids, **options):
        if not options['only'] or options['only'] == 'person':
            models.Person.update_weights(*ids, **options)
        if not options['only'] or options['only'] == 'urlcontext':
            models.URLContext.update_weights(*ids, **options)
        if not options['only'] or options['only'] == 'url':
            #models.URL.update_weights(*ids, **options)
            models.URL.update_top_urlcontext_weights(*ids, **options)
        if not options['only'] or options['only'] == 'issue':
            models.Issue.update_weights(*ids, **options)
        