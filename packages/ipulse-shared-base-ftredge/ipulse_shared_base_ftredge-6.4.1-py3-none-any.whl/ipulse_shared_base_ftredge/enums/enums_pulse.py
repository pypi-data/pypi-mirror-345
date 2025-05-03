
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
from enum import Enum

class Layer(Enum):
    PULSE_APP="papp"
    PULSE_MSG="pmsg"
    DATA_PLATFORM="dp"

    def __str__(self):
        return self.value
    
class Module(Enum):
    SHARED="shared"
    CORE="core"
    ORACLE="oracle"
    PORTFOLIO="portfolio"
    RISK="risk"
    RESEARCH="research"
    TRADING="trading"
    SIMULATION="simulation"

    def __str__(self):
        return self.value


class Subject(Enum):
    USER="user"
    ORGANIZATION="organization"
    DEPARTMENT = "department"
    WORKSPACE = "workspace"
    GROUP="group"
    SUBSCRIPTION="subscription"
    CATALOG="catalog"
    PAYMENT="payment"
    ACTION="action"
    RESOURCE="resource"
    SERVICE="service"
    ROLE="role"

    def __str__(self):
        return self.value

class SubscriptionPlan(Enum):
    NO_SUBSCRIPTION="no_subscription"
    FREE="free_subscription"
    BASE="base_subscription"
    PREMIUM="premium_subscription"
    ADVANCED="advanced_subscription"
    PROFESSIONAL="professional_subscription"
    ENTERPRISE="enterprise_subscription"

    def __str__(self):
        return self.value

class Sector(Enum):
    FINCORE="fincore"
    HEALTHCORE="healthcore"
    ENVICORE="envicore"
    SPORTSCORE="sportscore"
    POLITCORE="politcore"
    NEWSCORE="newscore"
    PORTFOLIO="portfolio"
    RISK="risk"
    RESEARCH="research"
    TRADING="trading"
    CUSTOM="custom"

    def __str__(self):
        return self.value
    


