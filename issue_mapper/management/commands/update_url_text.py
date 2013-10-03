from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<url ids>'
    help = 'Updates url text.'
    option_list = BaseCommand.option_list + (
        make_option('--force', default=False, action='store_true'),
        make_option('--limit', default=500),
    )

    def handle(self, *args, **options):
        models.URL.update_all(url_ids=args, only='text', **options)