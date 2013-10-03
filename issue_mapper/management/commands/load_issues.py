from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<filename>'
    help = 'Imports issues.'
    option_list = BaseCommand.option_list + (
        make_option('--user', default=None),
    )

    def handle(self, fn, **options):
        models.Issue.load_csv(fn)
        