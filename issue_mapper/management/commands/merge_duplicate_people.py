from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from django.core.mail import send_mail

from issue_mapper import models

class Command(BaseCommand):
    args = ''
    help = 'Merges records of duplicate people.'
    option_list = BaseCommand.option_list + (
    )

    def handle(self, *args, **options):
        models.Person.merge_all(**options)