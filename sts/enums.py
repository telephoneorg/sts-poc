import enum


class CreditTransactionType(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class PaymentProcessor(enum.Enum):
    STRIPE = "stripe"


class IdentityProvider(enum.Enum):
    CUP = "cup"


class LicenseType(enum.Enum):
    TBD = "tbd"


class OrderStatus(enum.Enum):
    CREATED = "created"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class ProductType(enum.Enum):
    PACK = "pack"
    PLAN = "plan"


class BasicStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class ProductStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class TimePeriod(enum.Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UserContextType(enum.Enum):
    BASE = "base"
    PARTICIPANT = "participant"
    FACILITATOR = "facilitator"
    EMPLOYEE = "employee"
    COMPANY = "company"


class UserContextStatus(enum.Enum):
    CREATED = "created"
    DELETED = "deleted"
    VERIFIED = "verified"


class UsState(enum.Enum):
    AL = "al"
    AK = "ak"
    AS = "as"
    AZ = "az"
    AR = "ar"
    CA = "ca"
    CO = "co"
    CT = "ct"
    DE = "de"
    DC = "dc"
    FM = "fm"
    FL = "fl"
    GA = "ga"
    GU = "gu"
    HI = "hi"
    ID = "id"
    IL = "il"
    IN = "in"
    IA = "ia"
    KS = "ks"
    KY = "ky"
    LA = "la"
    ME = "me"
    MH = "mh"
    MD = "md"
    MA = "ma"
    MI = "mi"
    MN = "mn"
    MS = "ms"
    MO = "mo"
    MT = "mt"
    NE = "ne"
    NV = "nv"
    NH = "nh"
    NJ = "nj"
    NM = "nm"
    NY = "ny"
    NC = "nc"
    ND = "nd"
    MP = "mp"
    OH = "oh"
    OK = "ok"
    OR = "or"
    PW = "pw"
    PA = "pa"
    PR = "pr"
    RI = "ri"
    SC = "sc"
    SD = "sd"
    TN = "tn"
    TX = "tx"
    UT = "ut"
    VT = "vt"
    VI = "vi"
    VA = "va"
    WA = "wa"
    WV = "wv"
    WI = "wi"
    WY = "wy"


def print_values(item):
    print("enum" + str([i.value for i in item]).replace("[", "(").replace("]", ")"))
