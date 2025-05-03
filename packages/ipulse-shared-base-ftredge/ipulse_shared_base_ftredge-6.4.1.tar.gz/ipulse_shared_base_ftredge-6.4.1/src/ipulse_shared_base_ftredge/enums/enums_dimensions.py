# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum


class Dimension(Enum):
    pass

class Unit(Dimension):
    MIX="MIX"
    # Currency and Financial Values
    USD = "USD"  # United States Dollar
    EUR = "EUR"  # Euro
    JPY = "JPY"  # Japanese Yen
    GBP = "GBP"  # British Pound Sterling
    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan Renminbi
    SEK = "SEK"  # Swedish Krona
    NZD = "NZD"  # New Zealand Dollar
    MXN = "MXN"  # Mexican Peso
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    NOK = "NOK"  # Norwegian Krone
    KRW = "KRW"  # South Korean Won
    RUB = "RUB"  # Russian Ruble
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    ZAR = "ZAR"  # South African Rand
    CURRENCY = "currency"    # General currency, when specific currency is not needed

    BYTES="bytes"
    KILOBYTES="kb"
    MEGABYTES="mb"
    GIGABYTES="gb"
    TERABYTES="tb"
    PETABYTES="pb"
    EXABYTES="eb"


    # Stock Market and Investments
    SHARE = "share"        # Number of shares
    BPS = "bps"              # Basis points, often used for interest rates and financial ratios

    # Volume and Quantitative Measurements
    VOLUME = "volume"        # Trading volume in units
    MILLION = "mill"    # Millions, used for large quantities or sums
    BILLION = "bill"    # Billions, used for very large quantities or sums


    # Mass and Weight Measurements
    BARREL = "barrel"      # Barrels, specifically for oil and similar liquids
    GRAM="gram"
    KILOGRAM="kg"
    TONNE="tonne"
    LITRE="litre"
    GALLON="gallon"
    POUND="pound"
    OUNCE="ounce"
    TROY_OUNCE = "troy_oz" # Troy ounces, specifically for precious metalss

    #Distance and Length Measurements
    SQUARE_FEET = "sq_ft"    # Square feet, for area measurement in real estate
    METER_SQUARE = "m2"      # Square meters, for area measurement in real estate
    ACRE = "acre"          # Acres, used for measuring large plots of land

    # Miscellaneous and Other Measures
    PERCENT = "prcnt"      # Percentage, used for rates and ratios
    UNIT = "unit"          # Generic units, applicable when other specific units are not suitable
    COUNT = "count"          # Count, used for tallying items or events
    INDEX_POINT = "index_pnt"  # Index points, used in measuring indices like stock market indices
    RATIO = "ratio"          # Ratio, for various financial ratios
    RECORD="record"
    ROW="row"
    COLUMN="column"
    FIELD="field"
    ITEM="item"
    
    



    def __str__(self):
        return self.name

class Frequency(Dimension):
    ONE_MIN = "1min"
    FIVE_MIN="5min"
    FIFTEEN_MIN="15min"
    THIRTY_MIN = "30min"
    ONE_H = "1h"
    TWO_H = "2h"
    SIX_H = "6h"
    TWELVE_H = "12h"
    FOUR_H = "4h"
    EOD="eod"
    ONE_D = "1d"
    TWO_D = "2d"
    THREE_D = "3d"
    ONE_W = "1w"
    ONE_M = "1m"
    TWO_M="2m"
    THREE_M="3m"
    SIX_M="6m"
    ONE_Y="1y"
    THREE_Y="3y"

    def __str__(self):
        return self.name


class Days(Dimension):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    MON_THUR=14
    MON_TO_FRI = 15
    ALL_DAYS = 17
    MON_TO_SAT = 16
    WEEKEND = 67
    SUN_TO_THUR = 74

    def __str__(self):
        return self.name