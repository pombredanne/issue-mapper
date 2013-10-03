from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = ''
    help = 'Registers feeds for people and issues.'
    option_list = BaseCommand.option_list + (
        make_option('--force', default=False, action='store_true'),
    )

    def handle(self, **options):
        models.Person.register_feeds(**options)
        models.Issue.register_feeds(**options)
        