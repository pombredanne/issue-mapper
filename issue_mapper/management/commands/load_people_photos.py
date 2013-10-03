from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = '<filename>'
    help = 'Imports photos for people.'
    option_list = BaseCommand.option_list + (
        #make_option('--real', default=False, action='store_true'),
        #make_option('--dryrun', default=False, action='store_true'),
    )

    def handle(self, *args, **options):
        models.Person.load_photo(person_ids=args, **options)
        