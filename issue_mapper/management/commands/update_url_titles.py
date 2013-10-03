from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<url ids>'
    help = 'Updates url titles.'
    option_list = BaseCommand.option_list + (
        make_option('--force', default=False, action='store_true'),
    )

    def handle(self, *args, **options):
        models.URL.update_all(url_ids=args, only='title', **options)