from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationFormUniqueEmail

import constants as c

settings.IM_WAIT_DAYS_BEFORE_REANSWER = getattr(settings, 'IM_WAIT_DAYS_BEFORE_REANSWER', 1)

settings.IM_URL_PREFIX = getattr(settings, 'IM_URL_PREFIX', '')

settings.IM_TITLE = getattr(settings, 'IM_TITLE', 'Issue Mapper')

settings.IM_SHOW_TITLE = getattr(settings, 'IM_SHOW_TITLE', True)

settings.IM_SUBTITLE = getattr(settings, 'IM_SUBTITLE', 'Home')

settings.IM_DEFAULT_USERNAME = getattr(settings, 'IM_DEFAULT_USERNAME', 'IssueBot9000')

settings.IM_USE_CMS = getattr(settings, 'IM_USE_CMS', False)

settings.IM_USE_CMS = getattr(settings, 'IM_USE_CMS', False)

settings.IM_LOGIN_FORM = getattr(settings, 'IM_LOGIN_FORM', AuthenticationForm)

settings.IM_REGISTRATION_FORM = getattr(settings, 'IM_REGISTRATION_FORM', RegistrationFormUniqueEmail)

settings.IM_ALLOW_SELF_VOTE = getattr(settings, 'IM_ALLOW_SELF_VOTE', False)

settings.IM_DEFAULT_QUESTION_PHRASING = getattr(settings, 'IM_DEFAULT_QUESTION_PHRASING', c.QUESTION_PHRASING3)

settings.IM_NOTIFY_ADMINS_OF_USER_CREATION = getattr(settings, 'IM_NOTIFY_ADMINS_OF_USER_CREATION', True)
