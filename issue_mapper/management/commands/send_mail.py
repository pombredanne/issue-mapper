from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from django.core.mail import send_mail

class Command(BaseCommand):
    args = '<message>'
    help = 'Send an email.'
    option_list = BaseCommand.option_list + (
        #make_option('--user', default=1),
        make_option('--subject', default='test subject'),
        make_option('--to', default=''),
    )

    def handle(self, *args, **options):
        from_email = settings.EMAIL_HOST_USER
        recipient_list = options['to'].split(',')
        print 'Attempting to send email to %s from %s...' % (' ,'.join(recipient_list), from_email)
        print 'EMAIL_HOST:',settings.EMAIL_HOST
        print 'EMAIL_HOST_USER:',settings.EMAIL_HOST_USER
        print 'EMAIL_PORT:',settings.EMAIL_PORT
        print 'EMAIL_USE_TLS:',settings.EMAIL_USE_TLS
        send_mail(
            subject=options['subject'],
            message=' '.join(args)+'\n\n',
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
#            auth_user=settings.EMAIL_HOST_USER,
#            auth_password=settings.EMAIL_HOST_PASSWORD,
            #connection=None
        )
        print 'Sent email to %s.' % (' ,'.join(recipient_list),)
        