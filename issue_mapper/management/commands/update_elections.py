from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = ''
    help = 'Loads election data from external resources such as Google.'
    option_list = BaseCommand.option_list + (
        #make_option('--force', default=False, action='store_true'),
    )

    def handle(self, *args, **options):
        models.Election.import_google(*args, **options)
        