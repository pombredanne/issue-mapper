from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from issue_mapper import models

class Command(BaseCommand):
    args = ''
    help = 'Imports people.'
    option_list = BaseCommand.option_list + (
        make_option('--real', default=False, action='store_true'),
        make_option('--dryrun', default=False, action='store_true'),
        make_option('--assume_missing', default=False, action='store_true'),
        make_option('--filename', default=None),
        make_option('--source', default=None),
    )

    def handle(self, **options):
        source = options['source']
        if source == 'csv':
            models.Person.load_csv(options['filename'], **options)
        elif source == 'govtrack':
            models.Person.load_govtrack(**options)
        elif source == 'openstates':
            models.Person.load_openstates(**options)
#        elif source == 'democracymap':
#            models.Person.load_democracymap(**options)
        elif source == 'wikipedia_us_governors':
            models.Person.load_wikipedia_us_governors(**options)
        else:
            raise NotImplementedError
        