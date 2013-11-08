import re

# Cookie.
COOKIE_NAME = 'im_uuid'
COOKIE_QUESTION_TYPE = 'qt'
COOKIE_KEYWORDS = 'keywords'
COOKIE_BUTTONS_FLOAT = 'buttons_float'
MAX_COOKIE_DAYS = 3

# Issue.
SINGLE = 'single'
MULTIPLE = 'multiple'
ANSWER_TYPE_CHOICES = (
    (SINGLE, 'single'),
    (MULTIPLE, 'multiple'),
)
ANSWERED = 'answered'
UNANSWERED = 'unanswered'
UPDATED = 'updated'
COMMENT = 'comment'
COMMENTS = 'comments'
REPLY = 'reply'
REPLIES = 'replies'
ISSUE = 'issue'
ISSUES = 'issues'
QUOTE = 'quote'
QUOTES = 'quotes'
CONTEXT = 'context'
CONTEXTS = 'contexts'
RATIONALE = 'rationale'
PERSON = 'person'
PEOPLE = 'people'
URL = 'url'
URLS = 'urls'
LINK = 'link'
LINKS = 'links'
ELECTION = 'election'
ELECTIONS = 'elections'
URLCONTEXT = 'urlcontext'
URLCONTEXTS = 'urlcontexts'
MATCHES = 'matches'
QUESTION_TYPES = (
    ANSWERED,
    UNANSWERED,
    UPDATED,
    PEOPLE,
    QUOTE,
    LINK,
    URL,
    MATCHES,
    RATIONALE,
)

TO_PLURAL = {
    COMMENT: COMMENTS,
    REPLY: REPLIES,
    ISSUE: ISSUES,
    QUOTE: QUOTES,
    CONTEXT: CONTEXTS,
    RATIONALE: RATIONALE,
    PERSON: PEOPLE,
    URL: URLS,
    LINK: LINKS,
    ELECTION: ELECTIONS,
}

# Vote.
UPVOTE = +1
DOWNVOTE = -1
VOTE_CHOICES = (
    (UPVOTE, 'up'),
    (DOWNVOTE, 'down'),
)
UPVOTE_NAME = 'up'
DOWNVOTE_NAME = 'down'
SUPPORTS_NO_NAME = 'supports-no'
SUPPORTS_YES_NAME = 'supports-yes'
VOTE_NAME_TO_VALUE = {
    UPVOTE_NAME: UPVOTE,
    DOWNVOTE_NAME: DOWNVOTE,
    SUPPORTS_NO_NAME: 0,
    SUPPORTS_YES_NAME: 0,
}

# Http.
JSON = 'json'
HTML = 'html'

# Flag.
SPAM = 'spam'
ABUSIVE = 'abusive'
DUPLICATE = 'duplicate'
FLAG_CHOICES = (
    (SPAM, 'Spam'),
    (ABUSIVE, 'Abusive'),
    (DUPLICATE, 'Duplicate'),
)
SUSTAINED = 'sustained'
OVERRULED = 'overruled'
FLAG_JUDGEMENT_CHOICES = (
    (SUSTAINED, 'Sustained: the moderator agrees with the flagger'),
    (OVERRULED, 'Overruled: the moderator disagrees with the flagger'),
)

# Position.
STRONGLY_OPPOSE = 'strongly-oppose' # strongly disagree
OPPOSE = 'oppose' # disagree
UNDECIDED = 'undecided'
FAVOR = 'favor' # agree
STRONGLY_FAVOR = 'strongly-favor' # strongly agree
POSITION_CHOICES = (
    #(STRONGLY_OPPOSE, 'Strongly Oppose'),
    (OPPOSE, 'Oppose'),
    (UNDECIDED, 'Undecided/No-opinion'),
    (FAVOR, 'Favor'),
    #(STRONGLY_FAVOR, 'Strongly Favor'),
)
POSITION_CHOICES3 = (
    (OPPOSE, 'No'),
    (UNDECIDED, 'Unsure'),
    (FAVOR, 'Yes'),
)
POSITION_CHOICES3_WRT = (
    (OPPOSE, 'No'),
    (UNDECIDED, 'Unsure'),
    (FAVOR, 'Yes'),
)
POSITIONS = (OPPOSE, UNDECIDED, FAVOR)
POSITION_SCORES = (
    (OPPOSE, -1),
    (UNDECIDED, 0),
    (FAVOR, +1),
)
POSITION_SCORE_TO_NAME = dict((v, k) for k,v in POSITION_SCORES)
ALLOWED_POSITION_VALUES = POSITIONS + (None,)
POSITION_CHOICES_PAST = (
    #(STRONGLY_OPPOSE, 'Strongly Disagree'),
    (OPPOSE, 'Disagree'),
    (UNDECIDED, 'Undecided/No-opinion'),
    (FAVOR, 'Agree'),
    #(STRONGLY_FAVOR, 'Strongly Agree'),
)
POSITION_TO_VERB = {
    STRONGLY_OPPOSE: 'strongly disagrees',
    OPPOSE: 'disagrees',
    UNDECIDED: 'is undecided',
    FAVOR: 'agrees',
    STRONGLY_FAVOR: 'strongly agrees',
}
POSITION_TO_VERB_INFINITIVE = {
    STRONGLY_OPPOSE: 'strongly disagree',
    OPPOSE: 'disagree',
    UNDECIDED: 'are undecided',
    FAVOR: 'agree',
    STRONGLY_FAVOR: 'strongly agree',
}
POSITION_TO_BOOL = {
    STRONGLY_OPPOSE: 'no',
    OPPOSE: 'no',
    UNDECIDED: 'unsure',
    FAVOR: 'yes',
    STRONGLY_FAVOR: 'yes',
}

# Person.
SUFFIX_SR = 'Sr.'
SUFFIX_JR = 'Jr.'
SUFFIX_I = 'I'
SUFFIX_II = 'II'
SUFFIX_III = 'III'
SUFFIX_IV = 'IV'
SUFFIX_ABBREVIATION_CHOICES = (
    (SUFFIX_SR, 'Sr.'),
    (SUFFIX_JR, 'Jr.'),
    (SUFFIX_II, 'II'),
    (SUFFIX_III, 'III'),
    (SUFFIX_IV, 'IV'),
)
SUFFIX_UP = dict(
    I='II',
    II='III',
    III='IV',
    IV='V',
    V='VI',
    VI='VII',
)
SUFFIX_UP[SUFFIX_SR] = SUFFIX_JR
SUFFIX_UP[SUFFIX_JR] = SUFFIX_III
SUFFIX_DOWN = dict(
    II='I',
    III='II',
    IV='III',
    V='IV',
    VI='V',
    VII='VI',
)
SUFFIX_DOWN[SUFFIX_JR] = SUFFIX_SR

LINK_REGEX = re.compile('link:([^\s\t\n]+)')

NEXT = 'next'
SKIP = 'skip'

IRRELEVANT = 0
LITTLE = 1
SOMEWHAT = 10
VERY = 50
MANDATORY = 250
IMPORTANCE_CHOICES = (
    (IRRELEVANT, 0),
    (LITTLE, 1),
    (SOMEWHAT, 10),
    (VERY, 50),
    (MANDATORY, 250),
)
IMPORTANCES = (
    IRRELEVANT,
    LITTLE,
    SOMEWHAT,
    VERY,
    MANDATORY,
)
IMPORTANCE_CHOICES_FRIENDLY = (
    (MANDATORY, 'Super important'),
    (VERY, 'Very important'),
    (SOMEWHAT, 'Somewhat important'),
    (LITTLE, 'A little important'),
    (IRRELEVANT, 'Irrelevent'),
)

UNKNOWN = 'unknown'
MALE = 'male'
FEMALE = 'female'
GENDER_CHOICES = (
    (MALE, 'male'),
    (FEMALE, 'female'),
    (UNKNOWN, 'unknown'),
)

SENATOR_CLASS_CHOICES = (
    ('class1', 'Class 1'),
    ('class2', 'Class 2'),
    ('class3', 'Class 3'),
)

FEED_GALERTS = 'galerts'
FEED_GOOGLE_NEWS = 'google-news'
FEED_GENERIC_RSS = 'generic-rss'
FEED_SOCIALMENTION = 'socialmention'
FEED_FAROO = 'faroo'
FEED_TYPES = (
    (FEED_GALERTS, 'Google Alerts'),
    (FEED_GOOGLE_NEWS, 'Google News'),
    (FEED_GENERIC_RSS, 'Generic RSS'),
    #(FEED_SOCIALMENTION, 'Social Mention'),
)

NO_NOTIFICATION = None
EMAIL_NOTIFICATION = 'email'
NOTIFICATION_CHOICES = (
    (NO_NOTIFICATION, 'None'),
    (EMAIL_NOTIFICATION, 'Email'),
)

FILTER_LINKS_BY_ISSUE_AND_PERSON = 'issue-and-person'
FILTER_LINKS_BY_ISSUE = 'issue'
FILTER_LINKS_BY_ISSUE_WITHOUT_PERSON = 'issue-without-person'
FILTER_LINKS_BY_PERSON_WITHOUT_ISSUE = 'person-without-issue'

FLB = 'flb'

TITLE_LENGTH = 300

SORT_BY_MATCH_ASC = 'sort_by_match_asc'
SORT_BY_MATCH_DSC = 'sort_by_match_dsc'
SORT_BY_MAGIC_ASC = 'sort_by_magic_asc'
SORT_BY_MAGIC_DSC = 'sort_by_magic_dsc'
SORT_BY_COVERAGE_ASC = 'sort_by_coverage_asc'
SORT_BY_COVERAGE_DSC = 'sort_by_coverage_dsc'
SORT_BY_TOP_ASC = 'sort_by_top_asc'
SORT_BY_TOP_DSC = 'sort_by_top_dsc'
SORT_BY_CREATED_ASC = 'sort_by_created_asc'
SORT_BY_CREATED_DSC = 'sort_by_created_dsc'
SORT_BY_LINKS_DSC = 'sort_by_links_dsc'
SORT_BY_LINKS_ASC = 'sort_by_links_asc'
SORT_BY_SUPPORT_YES_DSC = 'sort_by_support_yes_dsc'
SORT_BY_SUPPORT_YES_ASC = 'sort_by_support_yes_asc'
SORT_BY_SUPPORT_NO_DSC = 'sort_by_support_no_dsc'
SORT_BY_SUPPORT_NO_ASC = 'sort_by_support_no_asc'

ROLE_LEVEL_FEDERAL = 'federal'
ROLE_LEVEL_STATE = 'state'
ROLE_LEVEL_COUNTY = 'county'
ROLE_LEVEL_CITY = 'city'
ROLE_LEVEL_CHOICES = (
    (ROLE_LEVEL_FEDERAL, 'Federal'),
    (ROLE_LEVEL_STATE, 'State'),
    (ROLE_LEVEL_COUNTY, 'County'),
    (ROLE_LEVEL_CITY, 'City'),
)

# The threshold over which a votable object is no longer new.
MIN_VOTE_NEW_THRESHOLD = 5

# The number of days a votable object can go without any votes
# and still be considered new.
MIN_VOTE_NEW_DAYS = 7

VOTED_YES = 'voted-yes'
VOTED_YES_UP = 'voted-yes-up'
VOTED_YES_DOWN = 'voted-yes-down'
VOTED_NO = 'voted-no'

RSS = 'rss'
HTML = 'html'

AGREE = 'agree'
DISAGREE = 'disagree'

UNREVIEWED_BY_YOU = 'unreviewed-by-you'

FALSE = 'false'
TRUE = 'true'

YES = 'yes'
NO = 'no'

UNKNOWN = 'unknown'

QUESTION_PHRASING1 = 'phrasing1' # Joe believes X.
QUESTION_PHRASING2 = 'phrasing2' # Joe believes X?
QUESTION_PHRASING3 = 'phrasing3' # Does Joe believe X?

PERM_PERSON_SUBMIT = 'perm_submit_person'
PERM_PERSON_FLAG = 'perm_flag_person'

PERM_ISSUE_SUBMIT = 'perm_submit_issue'
PERM_ISSUE_FLAG = 'perm_flag_issue'
PERM_ISSUE_ANSWER_FOR_YOU = 'perm_answer_issue_for_themself'
PERM_ISSUE_ANSWER_FOR_OTHER = 'perm_answer_issue_for_other'

PERM_URL_SUBMIT = 'perm_submit_link'
PERM_URL_VOTE = 'perm_vote_link'
PERM_URL_FLAG = 'perm_flag_link'

PERM_TAG_SUBMIT = 'perm_submit_tag'
PERM_TAG_VOTE = 'perm_vote_tag'

PERM_QUOTE_SUBMIT = 'perm_submit_quote'
PERM_QUOTE_FLAG = 'perm_flag_quote'
PERM_QUOTE_VOTE = 'perm_vote_quote'

SUPPORTS = 'supports'
SUPPORTS_YES = 'supports yes'
SUPPORTS_NO = 'supports no'
SUPPORTED_YES_BY = 'supported yes by'
SUPPORTED_NO_BY = 'supported no by'
BECAUSE = 'because'

VIEW_DEFAULT = ''
VIEW_TABLE = 'table'

RESULT_LIMIT_CHOICES = (
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (100, '100'),
)