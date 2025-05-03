
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

from enum import Enum

class Status(Enum):
    pass

class ProgressStatus(Status):

    # Skipped statuses
    DISABLED = 10
    INTENTIONALLY_SKIPPED = 20

    # Success statuses
    DONE= 200
    DONE_WITH_NOTICES = 205
    DONE_WITH_WARNINGS = 210

    # Pending statuses
    NOT_STARTED = 300
    STARTED=350
    IN_PROGRESS = 360
    IN_PROGRESS_WITH_NOTICES = 363
    IN_PROGRESS_WITH_WARNINGS = 364
    IN_PROGRESS_WITH_ISSUES = 365
    PAUSED = 370
    BLOCKED_BY_UNRESOLVED_DEPENDENCY = 380
    
    UNKNOWN = 400

    FINISHED_WITH_ISSUES= 510
    UNFINISHED = 610
    FAILED = 620

    def __str__(self):
        return self.name
    

    @classmethod
    def pending_statuses(cls):
        return frozenset({
            cls.UNKNOWN,
            cls.NOT_STARTED,
            cls.STARTED,
            cls.IN_PROGRESS,
            cls.IN_PROGRESS_WITH_ISSUES,
            cls.IN_PROGRESS_WITH_WARNINGS,
            cls.IN_PROGRESS_WITH_NOTICES,
            cls.PAUSED,
        })
    
    @classmethod
    def pending_or_blocked_statuses(cls):
        return frozenset.union(
            cls.pending_statuses(),
            {cls.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
        )
    


    @classmethod
    def skipped_statuses(cls):
        return frozenset({
            cls.INTENTIONALLY_SKIPPED,
            cls.DISABLED,
        })

    @classmethod
    def success_statuses(cls):
        return frozenset({
            cls.DONE,
            cls.DONE_WITH_NOTICES,
            cls.DONE_WITH_WARNINGS,
        })

    @classmethod
    def failure_statuses(cls):
        return frozenset({
            cls.FINISHED_WITH_ISSUES,
            cls.UNFINISHED,
            cls.FAILED,
        })
    
    @classmethod
    def issue_statuses(cls):
        return frozenset.union(
            cls.failure_statuses(),
            {cls.IN_PROGRESS_WITH_ISSUES,
            cls.UNKNOWN,
            cls.BLOCKED_BY_UNRESOLVED_DEPENDENCY}
        )

    @classmethod
    def closed_statuses(cls):
        return frozenset.union(
            cls.success_statuses(),
            cls.failure_statuses()
        )

    @classmethod
    def closed_or_skipped_statuses(cls):
        return frozenset.union(
            cls.closed_statuses(),
            cls.skipped_statuses()
        )
    
    @classmethod
    def at_least_started_statuses(cls):
        return frozenset.union({
            cls.STARTED,
            cls.IN_PROGRESS,
            cls.IN_PROGRESS_WITH_ISSUES,
            cls.IN_PROGRESS_WITH_WARNINGS,
            cls.IN_PROGRESS_WITH_NOTICES,
            cls.PAUSED,
        },
        cls.closed_statuses()
        )

class ReviewStatus(Status):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    CANCELLED = "cancelled"
    CLOSED = "closed"

    def __str__(self):
        return self.name
    

class ObjectOverallStatus(Status):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    PENDING = "pending"
    PAUSED = "paused"
    ARCHIVED = "archived"
    def __str__(self):
        return self.name
    
class TradingStatus(Status):
    TRADED_ON_PUBLIC_EXCHANGE = "traded_on_public_exchange"
    TRADED_OTC = "traded_otc"
    TRADED_ON_PUBLIC_SITE_OR_APP = "traded_on_public_site_or_app"
    NOT_FOR_SALE = "not_for_sale"
    TRADED_VIA_BROKER = "traded_via_broker"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    DELISTED = "delisted"
    SUSPENDED = "suspended"
    LIQUIDATED = "liquidated"
    DELIVERED = "delivered"
    BANKRUPT = "bankrupt"
    MERGED = "merged"
    ACQUIRED = "acquired"
    EXPIRED = "expired"
    EXERCISED = "exercised"
    REDEEMED = "redeemed"
    CALLED = "called"
    UNKNOWN = "unknown"
    def __str__(self):
        return self.name


class WorkScheduleStatus(Status):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    MAINTENANCE = "maintenance"
    BREAK="break"
    HOLIDAY="holiday"
    UNREACHABLE = "unreachable"
    PERMANENTLY_CLOSED="permanently_closed"
    TEMPORARILY_CLOSED="temporarily_closed"
    UNKNOWN="unknown"

    def __str__(self):
        return self.name


class SubscriptionStatus(Status):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL = "trial"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.name

