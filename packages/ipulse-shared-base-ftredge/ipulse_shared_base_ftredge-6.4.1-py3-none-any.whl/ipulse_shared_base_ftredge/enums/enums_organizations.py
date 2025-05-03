from enum import Enum

class OrganizationRelation(str, Enum):
    """Organization relationship types"""
    
    RETAIL_CUSTOMER = "retail_customer"
    CORPORATE_CUSTOMER = "corporate_customer"
    PARENT = "parent"
    SISTER = "sister"
    SELF = "self"
    PARTNER = "partner"
    SUPPLIER = "supplier"
    SPONSOR = "sponsor"
    INVESTOR = "investor"
    REGULATOR = "regulator"
    OTHER = "other"
    def __str__(self):
        return self.name

class OrganizationIndustry(str, Enum):
    """Organization industry types"""
    DATA = "data"
    GOVERNMENT = "government"
    MEDIA = "media"
    ACADEMIC = "academic"
    COMMERCIAL = "commercial"
    FUND = "fund"
    FINANCE = "finance"
    ADVISORY = "advisory"
    HEDGE_FUND = "hedgefund"
    BANK = "bank"
    VC = "vc"
    PE = "pe"
    CONSTRUCTION = "construction"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    CONSULTING = "consulting"
    RETAIL = "retail"
    NON_PROFIT = "non_profit"
    INDIVIDUAL = "individual"
    FREELANCER = "freelancer"
    OTHER = "other"

    def __str__(self):
        return self.name