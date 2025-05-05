from enum import Enum


class BulkOperationEnumClickHouse(Enum):
    Tag = 0
    Retag = 1
    Close = 2
    Delete = 3
    TagChildren = 4
    DeleteChildren = 5
    UpdateInfluencer = 6
    UpdateCampaign = 7
    UserInfo = 8
    MarkSeenBulk = 10
    MarkSeenSelectBulk = 11
    MarkChildAsSeen = 12


class SentimentEnum(Enum):
    Neutral = 0
    Positive = 1
    Negative = 2
    PassivePositive = 3
    Multiple = 4


class SocialMedia(Enum):
    Twitter = 1
    Facebook = 2
    Instagram = 3
    YouTube = 4
    LinkedIn = 5
    GooglePlus = 6
    GooglePlayStore = 7
    AutomotiveIndia = 8
    Blogs = 9
    BookingCom = 10
    ComplaintWebsites = 11
    CustomerCare = 12
    DiscussionForums = 13
    ECommerceWebsites = 14
    ExpediaCom = 15
    HolidayIQ = 16
    MakeMyTrip = 17
    MyGov = 18
    News = 19
    ReviewWebsites = 20
    TeamBHP = 21
    TripAdvisor = 22
    Videos = 23
    Zomato = 24
    Email = 25
    GMB = 26
    ExternalMedia = 27
    WhatsApp = 28
    ChatBot = 29
    AppStore = 30
    Discourse = 31
    VOIP = 32
    Glassdoor = 33
    Quora = 36
    Tiktok = 37
    GBM = 38


class ColumnsType(Enum):
    Simple = 0
    Complex = 1
    SimpleRawQuery = 3


class PrimaryColumnNameEnum(Enum):
    tagid = 0
    u_authorid = 1
    channelgroupid = 2
    authorsocialid = 3
    authorchannelgroupid = 4
    accountid = 5
    uniqueid = 6
    createddate = 7


class StatusEnum(Enum):
    initiated = 1
    picked = 2
    in_progress = 3
    completed = 4
    error = 5
    parent_failed = 6


class TableName(Enum):
    mentiondetails = 0
    mstuserinformation = 1
    audiencegrowthdetails = 2
    page_stats = 3


class MediaEnum(Enum):
    TEXT = 1
    IMAGE = 2
    VIDEO = 3
    URL = 4
    POLL = 5
    OTHER = 6
    ANIMATEDGIF = 7
    PDF = 8
    DOC = 9
    EXCEL = 10
    AUDIO = 11
    CONTACT = 12
    SYSTEM = 13
    LOCATIONS = 14
    HTML = 15
    CARD = 16
    QUICKREPLY = 17
    BUTTON = 18
    FILE = 19
    QUICKREPLYLOCATION = 20
    PAYLOADBUTTONS = 21
    PAYLOADBUTTONSWITHICONS = 22
    IMAGEWITHSUBTITLE = 23
    SLIDERBUTTONS = 24
    SLIDERNOBUTTONS = 25
    STICKER = 26
    IMAGEANDVIDEOGROUP = 27
    PING = 28
    ALBUM = 29


class EnumUtils:
    @classmethod
    def get_key(cls, enum_class, value):
        for key, val in enum_class.__members__.items():
            if val.value == value:
                return key
        raise ValueError("Invalid enum value")

    @classmethod
    def get_value(cls, enum_class, key):
        return enum_class[key].value
