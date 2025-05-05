SYMBOLS = {
    "en": ("point", "negative", "percent"),
    "hi": ("दशमलव", "ऋणात्मक", "प्रतिशत"),
    "de": ("Komma", "minus", "Prozent"),
    "fr": ("virgule", "moins", "pourcent")
}

SUFFIXES = {
    'en': [(3, "K"), (6, "M"), (9, "B"), (12, "T"), (15, "Q"), (18, "Qn"), (21, "Sxt"), (24, "Spt"), (27, "Oct"),
           (30, "Non"), (33, "Dec"), (36, "Undec"), (39, "Duodec")],
    'hi': [(3, " हजार"), (5, " लाख"), (7, " करोड़"), (9, " अरब"), (11, " खरब"), (13, " नील"), (15, " पद्म"),
           (17, " शंख"), (19, " अंत"), (21, " मध्य"), (23, " परार्ध"), (25, " धुन"), (27, " अशोहिनी")],
    'en-hi': [(3, "K"), (5, "L"), (7, "Cr"), (9, "Ar"), (11, "Kharab"), (13, "Nil"), (15, "Padm"), (17, "Shankh"),
              (19, "Ant"), (21, "Madh"), (23, "Parardh"), (25, "Dhun"), (27, "Ashohini")],
    'de': [(3, "tausend"), (6, "Million"), (9, "Milliarde"), (12, "Billion"), (15, "Billiarde"), (18, "Trillion"),
           (21, "Trilliarde"), (24, "Quadrillion"), (27, "Quadrilliarde"), (30, "Quintillion"),
           (33, "Quintilliarde"), (36, "Sextillion"), (39, "Sextilliarde")],
    'fr': [(3, "mille"), (6, "million"), (9, "milliard"), (12, "billion"), (15, "billiard"), (18, "trillion"),
           (21, "trilliard"), (24, "quadrillion"), (27, "quadrilliard"), (30, "quintillion"),
           (33, "quintilliard"), (36, "sextillion"), (39, "sextilliard")]
}

CURRENCY_SYMBOLS = {
    "AFN": "؋", "ALL": "L", "DZD": "د.ج", "EUR": "€", "AOA": "Kz", "ARS": "$",
    "AMD": "֏", "AUD": "A$", "AZN": "₼", "BHD": ".د.ب", "BDT": "৳", "BYN": "Br",
    "BZD": "BZ$", "XOF": "CFA", "BTN": "Nu.", "BOB": "Bs.", "BAM": "KM",
    "BWP": "P", "BRL": "R$", "BND": "B$", "BGN": "лв", "BIF": "FBu", "KHR": "៛",
    "XAF": "CFA", "CAD": "C$", "CDF": "FC", "CLP": "$", "CNY": "¥", "COP": "$",
    "KMF": "CF", "CRC": "₡", "HRK": "kn", "CUP": "$", "CZK": "Kč", "DKK": "kr",
    "DJF": "Fdj", "XCD": "$", "DOP": "RD$", "USD": "$", "EGP": "E£", "ERN": "Nfk",
    "ETB": "Br", "FJD": "$", "GMD": "D", "GEL": "₾", "GHS": "₵", "GTQ": "Q",
    "GNF": "FG", "GYD": "$", "HTG": "G", "HNL": "L", "HKD": "HK$", "HUF": "Ft",
    "ISK": "kr", "INR": "₹", "IDR": "Rp", "IRR": "﷼", "IQD": "ع.د", "ILS": "₪",
    "JMD": "$", "JPY": "¥", "JOD": "JD", "KZT": "₸", "KES": "KSh", "KWD": "KD",
    "KGS": "лв", "LAK": "₭", "LBP": "ل.ل", "LSL": "L", "LRD": "$", "LYD": "LD",
    "MGA": "Ar", "MWK": "MK", "MYR": "RM", "MVR": "Rf", "MRU": "UM", "MUR": "₨",
    "MXN": "$", "MDL": "L", "MNT": "₮", "MAD": "د.م.", "MZN": "MT", "MMK": "K",
    "NAD": "$", "NPR": "₨", "NZD": "NZ$", "NIO": "C$", "NGN": "₦", "NOK": "kr",
    "OMR": "﷼", "PKR": "₨", "PAB": "B/.", "PGK": "K", "PYG": "₲", "PEN": "S/",
    "PHP": "₱", "PLN": "zł", "QAR": "﷼", "RON": "lei", "RUB": "₽", "RWF": "FRw",
    "SAR": "﷼", "RSD": "дин.", "SCR": "₨", "SLL": "Le", "SGD": "S$", "SBD": "$",
    "SOS": "Sh", "ZAR": "R", "KRW": "₩", "SSP": "£", "LKR": "Rs", "SDG": "ج.س.",
    "SEK": "kr", "CHF": "CHF", "SYP": "£", "TWD": "NT$", "TZS": "TSh", "THB": "฿",
    "TOP": "T$", "TTD": "TT$", "TND": "د.ت", "TRY": "₺", "TMT": "m", "UGX": "USh",
    "UAH": "₴", "AED": "د.إ", "GBP": "£", "UYU": "$U", "UZS": "лв", "VUV": "VT",
    "VES": "Bs.", "VND": "₫", "YER": "﷼", "ZMW": "ZK", "ZWL": "$"
}
