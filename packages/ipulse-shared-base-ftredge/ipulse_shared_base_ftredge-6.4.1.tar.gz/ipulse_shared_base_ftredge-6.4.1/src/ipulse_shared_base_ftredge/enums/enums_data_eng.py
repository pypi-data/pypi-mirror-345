# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum

class PipelineTrigger(Enum):
    MANUAL = "manual"
    SCHEDULER = "scheduler"
    SCHEDULER_MAIN = "scheduler_main"
    SCHEDULER_FALLBACK = "scheduler_fallback"
    SCHEDULER_RETRY = "scheduler_retry"
    SCHEDULER_VERIFICATION = "scheduler_verification"
    EVENT_GCS_UPLOAD= "event_gcs_upload"
    EVENT_PUBSUB= "event_pubsub"
    ANOTHER_PIPELINE = "another_pipeline"

    def __str__(self):
        return self.name


class DataPrimaryCategory(Enum):
    HISTORIC = "historic" # Historical data, usually accurate and complete
    LIVE="live" # Real-time data, not always certain, can have error. Live and Historic can intersect, depending if
    ARCHIVE="archive" # Archived data,usually not used for refernce but for long term storage and compliance. Yes some commonality with Historic but not the same
    REFERENCE = "reference" # Reference data, used for reference and mapping, for example dimensional tables
    ANALYTICS="analytics" # Analytical data and modelling, derived from historical and prediction data. Normally shall be making Human readable sense. vs. Features
    FEATURES="features" # Feature data, used for training models
    PREDICTIONS="predictions" # Predictive data, based on models and simulations
    SIMULATION="simulation" # Simulation data, based on models and simulations
    SHARED="shared" # Shared data, used for sharing data between systems

    def __str__(self):
        return self.name

class DataSecondaryCategory(Enum): # Data about the Data
    DATA= "data"
    CATALOGS="catalogs"
    MONITORING="monitoring"
    METADATA= "metadata"
    CHANGELOG = "changelog"
    PIPELOGS= "pipelogs"
    GENERALLOGS= "generallogs"
    TAGS = "tags"
    COMMENTS = "comments"


class Lineage(Enum):
    SOURCE_OF_TRUTH = "sot"
    COPY= "cpy"
    DERIVED_DATA = "ded"
    BACKUP = "bcp"
    TEMPORARY = "tmp"
    UNKNOWN = "unk"

    def __str__(self):
        return self.name

class DatasetScope(Enum):
    FULL = "full_dataset"
    LATEST= "latest_record"
    INCREMENTAL = "incremental_dataset"
    BACKFILLING = "backfilling_dataset"
    PARTIAL = "partial_dataset"
    FILTERED = "filtered_dataset"
    METADATA= "metadata"
    SOURCING_METADATA = "sourcing_metadata"
    DATASET_METADATA = "dataset_metadata"
    CHANGE_METADATA = "change_metadata"
    UNKNOWN = "unknown_dataset_scope"

    def __str__(self):
        return self.name



class CloudProvider(Enum):
    GCP = "cloud_gcp"
    AWS = "cloud_aws"
    AZURE = "cloud_azure"
    IBM = "cloud_ibm"
    ALIBABA = "cloud_alibaba"
    NO_CLOUD = "no_cloud"
    CLOUD_AGNOSTIC = "cloud_agnostic"
    OTHER = "other"
    UNKNWON = "unknown"

    def __str__(self):
        return self.value


class Attribute(Enum):
    RECENT_DATE = "recent_date"
    RECENT_TIMESTAMP = "recent_timestamp"
    RECENT_DATETIME = "recent_datetime"
    OLDEST_DATE = "oldest_date"
    OLDEST_TIMESTAMP = "oldest_timestamp"
    OLDEST_DATETIME = "oldest_datetime"
    MAX_VALUE = "max_value"
    MIN_VALUE = "min_value"
    TOTAL_COUNT = "total_count"
    TOTAL_SUM = "total_sum"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    STANDARD_DEVIATION = "standard_deviation"
    NB_FIELDS_PER_RECORDS = "nb_fields_per_records"

    def __str__(self):
        return self.name

class MatchCondition(Enum):
    EXACT = "exact"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    CONTAINS = "contains"
    REGEX = "regex"
    IN_RANGE = "in_range"
    NOT_IN_RANGE = "not_in_range"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    ON_FIELD_MATCH = "on_field_match"
    ON_FIELD_EQUAL = "on_field_equal"
    ON_FIELDS_EQUAL_TO = "on_fields_equal_to"
    ON_FIELDS_COMBINATION = "on_fields_combination"
    NOT_APPLICABLE = "not_applicable"

    def __str__(self):
        return self.name


class DuplicationHandling(Enum):
    RAISE_ERROR = "raise_error"
    OVERWRITE = "overwrite"
    INCREMENT = "increment"
    SKIP = "skip"
    SYSTEM_DEFAULT = "system_default"
    ALLOW = "allow" ## applicable for databases allowing this operation i.e. BigQuery 
    MERGE_DEFAULT = "merge_default"
    MERGE_PRESERVE_SOURCE_ON_DUPLICATES = "merge_preserve_source_on_dups"
    MERGE_PRESERVE_TARGET_ON_DUPLICATES = "merge_preserve_target_on_dups"
    MERGE_PRESERVE_BOTH_ON_DUPLICATES = "merge_preserve_both_on_dups"
    MERGE_RAISE_ERROR_ON_DUPLICATES = "merge_raise_error_on_dups"
    MERGE_CUSTOM = "merge_custom"

    def __str__(self):
        return self.name


class DuplicationHandlingStatus(Enum):
    ALLOWED = "allowed"
    RAISED_ERROR = "raised_error"
    SYSTEM_DEFAULT = "system_default"
    OVERWRITTEN = "overwritten"
    SKIPPED = "skipped"
    INCREMENTED = "incremented"
    OPERATION_CANCELLED = "operation_cancelled"
    MERGED = "merged"
    MERGED_PRESERVED_SOURCE = "merged_preserved_source"
    MERGED_PRESERVED_TARGET = "merged_preserved_target"
    MERGED_PRESERVED_BOTH = "merged_preserved_both"
    MERGED_RAISED_ERROR = "merged_raised_error"
    MERGED_CUSTOM = "merged_custom"
    NO_DUPLICATES = "no_duplicates"
    UNKNOWN = "unknown"
    UNEXPECTED_ERROR= "unexpected_error"
    CONDITIONAL_ERROR = "conditional_error"
    NOT_APPLICABLE = "not_applicable"

    def __str__(self):
        return self.name

class CodingLanguage(Enum):
    PYTHON = "python"
    NODEJS = "nodejs"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACTJS = "reactjs"

    def __str__(self):
        return self.name

