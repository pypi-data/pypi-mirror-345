from enum import StrEnum


class AuthenticationRealms(StrEnum):
    production = "production"
    sandbox = "sandbox"


class ApiPaths(StrEnum):
    token_issue = "/auth/token"
    token_refresh = "/auth/token/refresh"
    token_revoke = "/auth/token/revoke"
    token_validate = "/auth/token/validate"
    invoices_payin = "/deals/payin"
    invoices_payout = "/deals/payout"
    invoices_payout_tlv = "/deals/tlv"
    invoices_info = "/deals/:id"
    invoices_credentials = "/deals/:id/credentials"
    assets_list = "/wallet"
    assets_deposit = "/wallet/deposit"
    banks_list = "/banks/find"
    appel_create = "/support/create"
    appel_list = "/support/list"
    appel_stat = "/support/statistic"
    fx_quote = "/fx/calculatenew"
    fx_quote_tlv = "/fx/tlv"


class Currencies(StrEnum):
    USDT = "USDT"
    EUR = "EUR"
    USD = "USD"
    TRY = "TRY"
    CNY = "CNY"
    JPY = "JPY"
    GEL = "GEL"
    AZN = "AZN"
    INR = "INR"
    AED = "AED"
    KZT = "KZT"
    UZS = "UZS"
    TJS = "TJS"
    EGP = "EGP"
    PKR = "PKR"
    IDR = "IDR"
    BDT = "BDT"
    GBP = "GBP"
    RUB = "RUB"
    THB = "THB"
    KGS = "KGS"
    PHP = "PHP"
    ZAR = "ZAR"
    ARS = "ARS"
    GHS = "GHS"
    KES = "KES"
    NGN = "NGN"
    AMD = "AMD"


class Languages(StrEnum):
    EN = ("EN",)
    AZ = ("AZ",)
    UZ = ("UZ",)
    GE = ("GE",)
    TR = ("TR",)
    AE = ("AE",)
    RU = ("RU",)
    IN = ("IN",)
    AR = ("AR",)
    KG = "KG"


class Statuses(StrEnum):
    queued = "queued"
    new = "new"
    pending = "pending"
    paid = "paid"
    completed = "completed"
    disputed = "disputed"
    canceled = "canceled"


class CurrencyTypes(StrEnum):
    fiat = "FIAT"
    crypto = "CRYPTO"


class InvoiceTypes(StrEnum):
    p2p = "p2p"
    ecom = "ecom"
    c2c = "c2c"
    m10 = "m10"
    mpay = "mpay"
    sbp = "sbp"
    sbpqr = "sbpqr"
    iban = "iban"
    upi = "upi"
    imps = "imps"
    spei = "spei"
    pix = "pix"
    rps = "rps"
    ibps = "ibps"
    bizum = "bizum"
    rkgs = "rkgs"
    kgsphone = "kgsphone"
    krungthainext = "krungthainext"
    sber = "sber"
    kztphone = "kztphone"
    accountbdt = "accountbdt"
    alipay = "alipay"
    accountegp = "accountegp"
    accountphp = "accountphp"
    sberqr = "sberqr"
    maya = "maya"
    gcash = "gcash"
    banktransferphp = "banktransferphp"
    banktransferars = "banktransferars"
    phonepe = "phonepe"
    freecharge = "freecharge"
    instapay = "instapay"
    vodafonecash = "vodafonecash"
    razn = "razn"
    rtjs = "rtjs"
    sberpay = ("sberpay",)
    tpay = ("tpay",)
    opay = ("opay",)
    moniepoint = ("moniepoint",)
    palmpay = ("palmpay",)
    wave = ("wave",)
    orangemoney = ("orangemoney",)
    moovmoney = ("moovmoney",)
    rtjscard = ("rtjscard",)
    ruzs = ("ruzs",)
    amobile = ("amobile",)
    payid = ("payid",)
    baridi = ("baridi",)
    multiwidget = ("multiwidget",)
    attijari = ("attijari",)
    cih = ("cih",)
    cashplus = ("cashplus",)
    elqr = ("elqr",)
    odengi = "odengi"


class EELQRBankALias(StrEnum):
    bakai = ("bakai",)
    mbank = ("mbank",)
    optima = ("optima",)
    kicb = ("kicb",)
    odengi = ("odengi",)
    demir = ("demir",)
    megapay = ("megapay",)


class CredentialsTypes(StrEnum):
    iban = ("iban",)
    phone = ("phone",)
    card = ("card",)
    fps = ("fps",)
    qr = ("qr",)
    account = ("account",)
    custom = "custom"


class RiskScoreLevels(StrEnum):
    unclassified = "unclassified"
    hr = "hr"  # highest risk
    ftd = "ftd"  # high risk
    trusted = "trusted"  # low risk


class CancellationReason(StrEnum):
    NO_MONEY = ("NO_MONEY",)
    CREDENTIALS_INVALID = ("CREDENTIALS_INVALID",)
    EXPIRED = ("EXPIRED",)
    PRECHARGE_GAP_UPPER_LIMIT = ("PRECHARGE_GAP_UPPER_LIMIT",)
    CROSS_BANK_TFF_LESS_THAN_3K = ("CROSS_BANK_TFF_LESS_THAN_3K",)
    CROSS_BANK_UNSUPPORTED = ("CROSS_BANK_UNSUPPORTED",)
    ACCOUNT_NUMBER_BLACKLISTED = "ACCOUNT_NUMBER_BLACKLISTED"


class FeesStrategy(StrEnum):
    add = "add"
    sub = "sub"


class InvoiceDirection(StrEnum):
    F2C = ("F2C",)
    C2F = ("C2F",)
    FIAT_IN = ("FIAT_IN",)
    FIAT_OUT = "FIAT_OUT"


class TTLUnits(StrEnum):
    sec = "sec"
    min = "min"
    hour = "hour"
