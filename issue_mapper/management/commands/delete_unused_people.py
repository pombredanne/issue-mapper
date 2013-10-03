from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = ''
    help = 'Deletes person records created and unused by anonymous users.'
    option_list = BaseCommand.option_list + (
        make_option('--dryrun', default=False, action='store_true'),
        make_option('--days', default=None),
    )

    def handle(self, *args, **options):
        models.Person.delete_unused(*args, **options)
        