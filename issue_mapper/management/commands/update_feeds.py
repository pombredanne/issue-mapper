from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<ids>'
    help = 'Updates feeds.'
    option_list = BaseCommand.option_list + (
        make_option('--force', default=False, action='store_true'),
    )

    def handle(self, *ids, **options):
        models.Feed.update_all(*ids, **options)