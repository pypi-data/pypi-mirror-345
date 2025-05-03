from enum import Enum


# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

class Resource(Enum):
    pass


class DataResource(Resource):

    UNKNOWN= "unknown"
    NOTSET= "notset"

    # --- Generic Reference ---
    DATA = "data"
    IN_MEMORY_DATA = "in_memory_data"
    METADATA= "metadata"
    IN_MEMORY_METADATA = "in_memory_metadata"
    CONFIG = "config"
    # --- COMMUNICATION  ---
    API = "api"
    API_INTERNAL = "api_internal"
    API_EXTERNAL = "api_external"
    WEBSITE = "website"
    INTERNET = "internet"
    RPC = "rpc"
    GRPC = "grpc"

    # --- Messaging ---
    MESSAGING_KAFKA = "messaging_kafka"
    MESSAGING_SQS = "messaging_sqs"
    MESSAGING_PUBSUB_TOPIC = "messaging_pubsub_topic"
    # --- Real-time Communication ---
    REALTIME_WEBSOCKET = "websocket"
     # --- Notifications ---
    NOTIFICATION_WEBHOOK = "webhook"

    #-----------------
    #------ DBs ------
    #-----------------

    # --Generic Reference --
    DB= "db"
    DB_TABLE = "db_table"
    DB_RECORD = "db_record"
    DB_COLLECTION = "db_collection"
    DB_DOCUMENT = "db_document"
    DB_VIEW = "db_view"

    # --SQL Databases--
    DB_ORACLE = "db_oracle"
    DB_POSTGRESQL = "db_postgresql"
    DB_SQLSERVER = "db_sqlserver"
    DB_MYSQL = "db_mysql"
    DB_BIGQUERY = "db_bigquery"
    DB_BIGQUERY_TABLE = "db_bigquery_table"
    DB_SNOWFLAKE = "db_snowflake"
    DB_REDSHIFT = "db_redshift"
    DB_ATHENA = "db_athena"
    # --NOSQL Databases--
    DB_MONGO = "db_mongo"
    DB_REDIS = "db_redis"
    DB_CASSANDRA = "db_cassandra"
    DB_NEO4J = "db_neo4j"
    DB_FIRESTORE = "db_firestore"
    DB_FIRESTORE_DOC = "db_firestore_doc"
    DB_FIRESTORE_COLLECTION = "db_firestore_collection"
    DB_DYNAMODB = "db_dynamodb"
    # --NEWSQL Databases--  
    DB_COCKROACHDB = "db_cockroachdb"
    DB_SPANNER = "db_spanner"
    
    # --- Storage and DATA ---
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    LOCAL_STORAGE = "local_storage"
    GCS = "gcs"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    HDFS = "hdfs"
    NFS = "nfs"
    FTP = "ftp"
    SFTP = "sftp"
    # --- Files ---
    FILE = "file"
    FILE_JSON = ".json"
    FILE_CSV = ".csv"
    FILE_EXCEL = ".xlsx"
    FILE_TXT = ".txt"
    FILE_PDF = ".pdf"
    FILE_PARQUET = ".parquet"
    FILE_AVRO = ".avro"
    FILE_WORD = ".docx"
    FILE_PPT = ".pptx"
    FILE_HTML = ".html"
    FILE_MARKDOWN = ".md"
    FILE_XML = ".xml"
    FILE_YAML = ".yaml"
    FILE_TOML = ".toml"
    FILE_JPG = ".jpg"
    FILE_JPEG = ".jpeg"
    FILE_PNG = ".png"
    FILE_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
    FILE_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"]
    FILE_AUDIO_EXTENSIONS = [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma"]
    
    def __str__(self):
        return self.name
    



class ComputeResource(Resource):

    # --- Compute ---
    CLOUD_FUNCTION = "cloud_function"
    CLOUD_RUN= "cloud_run"
    CLOUD_RUN_SERVICE = "cloud_run_service"
    CLOUD_RUN_JOB = "cloud_run_job"
    CLOUD_COMPUTE_ENGINE = "cloud_compute_engine"
    CLOUD_DATAPROC = "cloud_dataproc"
    CLOUD_DATAFLOW = "cloud_dataflow"
    CLOUD_BIGQUERY = "cloud_bigquery"
    CLOUD_LAMBDA = "cloud_lambda"
    CLOUD_EC2 = "cloud_ec2"
    CLOUD_EMR = "cloud_emr"
    CLOUD_GLUE = "cloud_glue"
    CLOUD_ATHENA = "cloud_athena"
    CLOUD_REDSHIFT = "cloud_redshift"
    CLOUD_SYNAPSE_ANALYTICS = "cloud_synapse_analytics"
    CLOUD_DATA_FACTORY = "cloud_data_factory"
    CLOUD_VIRTUAL_MACHINES = "cloud_virtual_machines"
    CLOUD_COMPUTE = "cloud_compute"
    CLOUD_DOCKER = "cloud_docker"
    CLOUD_KUBERNETES = "cloud_kubernetes"
    CLOUD_GKE = "cloud_gke"
    CLOUD_AKS = "cloud_aks"
    CLOUD_EKS = "cloud_eks"
    CLOUD_AZURE_FUNCTIONS = "cloud_azure_functions"
    CLOUD_AZURE_VIRTUAL_MACHINES = "cloud_azure_virtual_machines"
    CLOUD_AZURE_SYNAPSE_ANALYTICS = "cloud_azure_synapse_analytics"
    CLOUD_AZURE_DATA_FACTORY = "cloud_azure_data_factory"
    CLOUD_AZURE_DATABRICKS = "cloud_azure_databricks"
    CLOUD_AZURE_ANALYTICS = "cloud_azure_analytics"
    CLOUD_AZURE_SQL = "cloud_azure_sql"
    CLOUD_AZURE_COSMOSDB = "cloud_azure_cosmosdb"
    CLOUD_AZURE_TABLE = "cloud_azure_table"
    CLOUD_AZURE_BLOB = "cloud_azure_blob"
    CLOUD_AZURE_FILE = "cloud_azure_file"
    CLOUD_AZURE_QUEUE = "cloud_azure_queue"
    CLOUD_AZURE_EVENTHUB = "cloud_azure_eventhub"
    CLOUD_AZURE_NOTIFICATIONHUB = "cloud_azure_notificationhub"
    CLOUD_AZURE_CACHE = "cloud_azure_cache"
    CLOUD_AZURE_REDIS = "cloud_azure_redis"
    CLOUD_AZURE_SEARCH = "cloud_azure_search"
    LOCAL_COMPUTE = "local_compute"
    LOCAL_JUPYTER_NOTEBOOK = "local_jupyter_notebook"
    LOCAL_SCRIPT = "local_script"
    LOCAL_SERVER = "local_server"
    LOCAL_DOCKER = "local_docker"
    LOCAL_KUBERNETES = "local_kubernetes"
    LOCAL_GCP_CLOUD_FUNCTION = "local_gcp_cloud_function"

    def __str__(self):
        return self.name
    

class ProcessorResource(Resource):

    CPU_INTEL = "cpu_intel"
    CPU_AMD = "cpu_amd"
    CPU_ARM = "cpu_arm"
    GPU_NVIDIA = "gpu_nvidia"
    GPU_AMD = "gpu_amd"
    GPU_INTEL = "gpu_intel"
    TPU_GOOGLE = "tpu_google"
    TPU_INTEL = "tpu_intel"
    TPU_AMD = "tpu_amd"

    def __str__(self):
        return self.name


class AbstractResource(Resource):
    SERVICE = "service"
    SERVICEMON = "servicemon"
    
    PIPELINE= "pipeline"
    PIPELINEFLOW= "pipelineflow"
    PIPELINEMON= "pipelinemon"
    PIPELINE_STEP= "pipeline_step"
    PIPELINE_TASK = "pipeline_task"
    PIPELINE_OPERATION = "pipeline_operation"
    PIPELINE_TASK_SEQUENCE = "pipeline_task_sequence"
    PIPELINE_GROUP= "pipeline_group"
    PIPELINE_DYNAMIC_ITERATOR = "pipeline_dynamic_iterator"
    PIPELINE_ITERATION = "pipeline_iteration"
    PIPELINE_SUBJECT="pipeline_subject"
    PIPELINE_SUBJECT_SEQUENCE="pipeline_subject_sequence"

    RECORD= "record"
    SCRIPT = "script"
    JOB= "job"

    

    def __str__(self):
        return self.name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring


class Action(Enum):

   # NO ACTION (0)
    UNKNOWN=0
    NOTSET = 1
    NO_ACTION = 2
    
    # READ ACTIONS (1000-1999)
    READ = 1000
    READ_STREAM = 1001
    READ_QUERY = 1010
    READ_FILE = 1020
    READ_HTTP_GET = 1030
    READ_SECRET = 1040
    READ_SCHEMA = 1045
    READ_PULL_MESSAGE = 1050
    READ_PUSH_MESSAGE = 1070
    READ_PUBLISHED_MESSAGE = 1075
    READ_LIST_SUBSCRIPTIONS = 1080
    READ_LIST_TOPICS = 1090
    READ_LIST_MESSAGES = 1100
    READ_LIST_FILES = 1110
    READ_LIST_TABLES = 1120
    READ_LIST_COLLECTIONS = 1130
    READ_LIST_DOCUMENTS = 1140
    READ_AUTHZ = 1170
    READ_AUTHZ_LIST_PERMISSIONS = 1171
    READ_AUTH_LIST_USERS = 1180
    READ_AUTH_GET_USER = 1181
    READ_AUTH_LIST_GROUPS = 1185

    # VALIDATE AND AUTHORIZATION ACTIONS (2000-2999)
    VALIDATE = 2000
    VALIDATE_AGAINST_SCHEMA= 2021
    VALIDATE_ATTRIBUTES = 2025


    VALIDATE_AUTHZ_ALLOWED = 2210
    VALIDATE_AUTHZ_DENIED = 2220
    VALIDATE_AUTH_PASSWORD_CORRECT = 2300
    VALIDATE_AUTH_USER_TOKEN = 2310

    # CALCULATE ACTIONS (3000-3999)
    CALCULATE = 3000
    CALCULATE_STATISTICS = 3050
    CALCULATE_METRICS = 3060
    CALCULATE_FEATURES = 3070
    CALCULATE_TRAIN = 3080
    CALCULATE_EVALUATE = 3090
    CALCULATE_DERIVED_FIELDS = 3100
    CALCULATE_CLASSIFICATION = 3110
    CALCULATE_CLUSTERING = 3120
    CALCULATE_PREDICTION = 3130
    CALCULATE_ANOMALY_DETECTION = 3140
    CALCULATE_SIMULATION = 3150
    
   # TRANSFORM ACTIONS (4000-4999)
    TRANSFORM = 4000
    TRANSFORM_JSON_LOADS = 4005
    TRANSFORM_JSON_DUMPS = 4006
    TRANSFORM_JSON_LOAD = 4007
    TRANSFORM_JSON_DUMP = 4008
    TRANSFORM_PREPROCESS = 4010
    TRANSFORM_FILTER = 4020
    TRANSFORM_SORT = 4030
    TRANSFORM_UNION = 4040
    TRANSFORM_JOIN = 4050
    TRANSFORM_MERGE = 4060
    TRANSFORM_SPLIT = 4070
    TRANSFORM_GROUP = 4080
    TRANSFORM_GROUP_BY = 4090
    TRANSFORM_AGGREGATE = 4100
    TRANSFORM_NORMALIZE = 4110
    TRANSFORM_DENORMALIZE = 4120
    TRANSFORM_DEDUPLICATE = 4130
    TRANSFORM_DECRYPT = 4140
    TRANSFORM_ENCRYPT = 4150
    TRANSFORM_MASK = 4160
    TRANSFORM_SYNC = 4170
    TRANSFORM_ADD_VALUES = 4180
    TRANSFORM_FILL_MISSING_VALUES = 4190
    TRANSFORM_REPLACE_VALUES = 4200
    TRANSFORM_REPLACE = 4210
    TRANSFORM_RENAME = 4220
    TRANSFORM_INCREMENT = 4230
    TRANSFORM_ANONYMIZE = 4240

    # PERSIST ACTIONS (5000-5999)
    PERSIST = 5000
    PERSIST_BATCH=5001
    # HTTP Persist
    PERSIST_HTTP_POST = 5010
    PERSIST_HTTP_PUT = 5020
    PERSIST_HTTP_PATCH = 5030
    PERSIST_HTTP_DELETE = 5040
    PERSIST_HTTP_OPTIONS = 5050
    
    # Generic Persist for Files, Tables, Collections, Databases
    PERSIST_WRITE = 5060
    PERSIST_WRITE_BATCH = 5061
    PERSIST_WRITE_QUERY = 5062
    PERSIST_WRITE_STREAM = 5063
    PERSIST_WRITE_FILE = 5064
    PERSIST_EXPORT_FILE_QUERY = 5064
    PERSIST_CREATE = 5070
    PERSIST_CREATE_BATCH = 5071
    PERSIST_CREATE_TABLE = 5072
    PERSIST_CREATE_TABLE_TEMP = 5073
    PERSIST_CREATE_OR_REPLACE_TABLE = 5074
    PERSIST_CREATE_OR_REPLACE_TABLE_TEMP = 5074
    PERSIST_CREATE_OR_LOAD_TABLE_FROM_JSON = 5075
    PERSIST_CREATE_OR_LOAD_TABLE_FROM_JSON_TEMP = 5076
    PERSIST_CREATE_DATABASE = 5080
    PERSIST_CREATE_COLLECTION = 5081
    PERSIST_UPDATE = 5090
    PERSIST_UPDATE_BATCH = 5091
    
    PERSIST_INSERT = 5100
    PERSIST_INSERT_BATCH = 5101
    PERSIST_MERGE = 5110
    PERSIST_MERGE_BATCH = 5113
    PERSIST_MERGE_QUERY = 5115
    PERSIST_MERGE_UPDATE_AND_INSERT_NEW_QUERY = 5116
    PERSIST_MERGE_UPDATE_DONT_INSERT_NEW_QUERY = 5117
    PERSIST_MERGE_INSERT_NEW_AND_DONT_UPDATE_QUERY = 5118
    PERSIST_MERGE_DOCUMENT = 5121
    PERSIST_RENAME = 5125
    PERSIST_RENAME_BATCH = 5126
    PERSIST_MOVE = 5130
    PERSIST_MOVE_BATCH = 5131
    PERSIST_COPY = 5140
    PERSIST_COPY_BATCH = 5141
    PERSIST_APPEND = 5150
    PERSIST_APPEND_BATCH = 5151
    PERSIST_UPSERT = 5160
    PERSIST_UPSERT_BATCH = 5161
    PERSIST_BACKUP = 5170
    PERSIST_RESTORE = 5175

    PERSIST_DELETE = 5200
    PERSIST_DELETE_BATCH = 5210
    PERSIST_DELETE_TABLE = 5220
    PERSIST_DELETE_TABLE_TEMP = 5225
    PERSIST_DELETE_DATABASE = 5230
    PERSIST_DELETE_COLLECTION = 5235
    PERSIST_DELETE_FILE= 5240
    PERSIST_ARCHIVE = 5270

    #Messaging Actions (5300-5399)
    PERSIST_PUBLISH_MESSAGE = 5400
    PERSIST_ACK_MESSAGE = 5405
    PERSIST_CREATE_TOPIC = 5410
    PERSIST_DELETE_TOPIC = 5415
    PERSIST_CREATE_SUBSCRIPTION = 5420
    PERSIST_DELETE_SUBSCRIPTION = 5425


    # IAM Actions (5400-5565)
    PERSIST_AUTHZ_SET_PERMISSIONS = 5500
    PERSIST_AUTHZ_SET_USER_PERMISSIONS = 5505
    PERSIST_AUTHZ_SET_GROUP_PERMISSIONS = 5510
    PERSIST_AUTHZ_SET_ROLE_PERMISSIONS = 5515
    PERSIST_AUTH_REGISTER_USER = 5520
    PERSIST_AUTH_DELETE_USER = 5525
    PERSIST_AUTH_RESET_PASSWORD = 5530
    PERSIST_AUTH_CHANGE_PASSWORD = 5535
    PERSIST_AUTH_UPDATE_USER = 5540
    PERSIST_AUTH_CREATE_GROUP = 5545
    PERSIST_AUTH_DELETE_GROUP = 5550
    PERSIST_AUTH_UPDATE_GROUP = 5555

    # EXECUTE ACTIONS (7000-7999)
    EXECUTE = 7000

    def __str__(self):
        return self.name

class ControlAction(Enum):

 # --- CONTROL ACTIONS ---
    CONTROL_START = "control_start"
    CONTROL_BOOT = "control_boot"
    CONTROL_STOP = "control_stop"
    CONTROL_PAUSE = "control_pause"
    CONTROL_RESUME = "control_resume"
    CONTROL_RESTART = "control_restart"
    CONTROL_RELOAD = "control_reload"
    CONTROL_SHUTDOWN = "control_shutdown"
    CONTROL_REBOOT = "control_reboot"
    CONTROL_VERIFY = "control_verify"
    CONTROL_RECOVER = "control_recover"
    CONTROL_SKIP= "control_skip"
    CONTROL_CANCEL = "control_cancel"

    def __str__(self):
        return self.name

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring



class Alert(Enum):

    UNKNOWN = 0
    # NOTICE ALERTS (1000-1999)
    # Authentication/Authorization (1000-1099)
    AUTHZ_PERMISSION_GRANTED = 1000
    AUTHZ_PERMISSION_DENIED = 1005
    AUTHZ_PERMISSION_REVOKED = 1010
    AUTHZ_ACTION_ALLOWED = 1015
    AUTHZ_ACTION_DENIED = 1020
    AUTHZ_RESOURCE_ALLOWED = 1025
    AUTHZ_RESOURCE_DENIED = 1030
    AUTH_SUCCESS = 1035
    AUTH_FAILURE = 1040

    # Data Existence (1100-1199)
    ALREADY_EXISTS = 1100
    RESOURCE_ALREADY_EXISTS = 1102
    FILE_ALREADY_EXISTS = 1105
    USER_ALREADY_EXISTS = 1107
    DATA_ALREADY_EXISTS = 1110
    DATA_PARTIALLY_EXISTS = 1115
    RECORD_ALREADY_EXISTS = 1120
    RECORDS_ALREADY_EXIST = 1125
    RECORDS_PARTIALLY_EXIST = 1130
    DOCUMENT_ALREADY_EXISTS = 1135

    # NOTICE OR WARNING ALERTS (2000-2299)
    # Data Availability (2200-2299)
    NOT_FOUND=2200
    RESOURCE_NOT_FOUND = 2202
    TABLE_NOT_FOUND = 2205
    TABLES_NOT_FOUND = 2206
    TABLE_EMPTY = 2210
    DB_NOT_FOUND = 2215
    COLLECTION_NOT_FOUND = 2220
    COLLECTION_EMPTY = 2225
    DOCUMENT_NOT_FOUND = 2230
    FILE_NOT_FOUND = 2235
    FILES_NOT_FOUND = 2240
    FILE_EMPTY = 2245

    # WARNING ALERTS (3000-3999)
    # System Performance
    SYSTEM_MEMORY_USAGE_HIGH = 3100
    SYSTEM_CPU_USAGE_HIGH = 3110
    SYSTEM_NETWORK_SPEED_SLOW = 3120
    SYSTEM_DISK_SPACE_LOW = 3130
    SYSTEM_THROUGHPUT_LOW = 3140

    # WARNING OR ERROR ALERTS (4000-4999)
    SYSTEM_CONCURRENCY_LIMIT = 4100
    SYSTEM_CONNECTIONS_LIMIT = 4110
    SERVICE_RESPONSE_TIME_LIMIT = 4130

    # ERROR ALERTS (5000-5999)

    # System Errors (5000-5099)
    SERVICE_UNRESPONSIVE = 5000
    SERVICE_TIMEOUT = 5005
    SERVICE_ISSUES_THRESHOLD_REACHED = 5010
    SYSTEM_ISSUES_THRESHOLD_LIMIT = 5015
    SYSTEM_EARLY_TERMINATION = 5020

    # CONTENT ISSUES (5100-5199)
    DATA_VALIDATION_ISSUES = 5100
    VALIDATION_ISSUE = 5105
    SCHEMA_VALIDATION_ISSUES = 5110
    SCHEMA_ISSUE = 5115
    DATA_ISSUE = 5120
    DATA_ISSUES = 5125
    METADATA_ISSUE = 5130
    METADATA_ISSUES = 5135
    ALLOWED_ISSUES_THRESHOLD_REACHED = 5140

    # CRITICAL ALERTS (4000-6999)
    # System Critical (6000-6099)
    SYSTEM_OUT_OF_MEMORY = 6000
    SYSTEM_CPU_LIMIT_REACHED = 6005
    SYSTEM_DISK_SPACE_FULL = 6010
    SYSTEM_NETWORK_UNAVAILABLE = 6015

    # System Crashes (6100-6199)
    SYSTEM_PROCESSOR_CRASH = 6100
    SYSTEM_CRASH = 6105
    SYSTEM_CONTAINER_CRASH = 6110
    SYSTEM_SERVICE_CRASH = 6115

    def __str__(self):
        return self.name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

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

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring


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
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

class FinCoreCategory(Enum):
    MARKET="market" # Market prices data
    CORPORATE="corp" # Corporate data such as financial statements and earnings, similar to fundamental data
    FUNDAMENTAL="fundam"
    ECONOMY="economy"
    NEWS="news"
    SENTIMENT="sntmnt"
    SOCIAL="social"
    POLITICS="poltcs"
    OTHER="other"

    def __str__(self):
        return self.name

class FincCoreSubCategory(Enum):
    STOCK = "stock"
    BOND = "bond"
    COMMODITY = "commodt"
    CURRENCY = "currncy"
    CRYPTO = "crypto"
    REAL_ESTATE = "realest"
    EQUITY_INDICE = "eqtindx"
    OPTION = "option"
    FUTURE = "futures"
    ETF = "etf"
    ECONOMIC_INDICATOR = "ecoindctr"
    FUNDAMENTAL = "fundamental"
    OTHER = "other"

    def __str__(self):
        return self.name

class FinCoreRecordsCategory(Enum):
    PRICE="pric"
    SPOT= "spot"
    OHLCVA="ohlcva"
    OHLCV="ohlcv"
    OPEN="open"
    HIGH="high"
    LOW="low"
    CLOSE="close"
    VOLUME="volume"
    ADJC="adjc"
    FUNDAMENTAL="fundam" # treat this differently
    EARNINGS="earnings"
    CASH_FLOW="cashflw"
    BALANCE_SHEET="blnce_sht"
    INTERNAL_TRANSACTIONS="internaltrans"
    INDICATORS="indic"
    ARTICLE="article"
    INSTA_POST="isntapost"
    TWEET="tweet"
    OTHER="othr"

    def __str__(self):
        return self.name

class FinancialExchangeOrPublisher(Enum):
    CC="CC"
    US="US" # mix of all major US exchanges incl NASDAQ, NYSE, etc.
    NASDAQ="NASDAQ"
    NYSE="NYSE"
    SHG="SHG"
    LSE="LSE"
    

    def __str__(self):
        return self.name
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

class LogLevel(Enum):
    NOTSET=0
    DEBUG =10
    INFO = 20
    NOTICE= 25
    WARNING=30
    ERROR=40
    CRITICAL=50

    def __str__(self):
        return self.name

class LoggingHandler(Enum):

    """
    Standardized remote logging handlers for data engineering pipelines,
    designed for easy analysis and identification of remote logging
    requirements
    """
    
    NONE = "none"  # No remote handler
    LOCAL_STREAM = "local_stream"  # Local stream handler
    GCP_CLOUD_LOGGING = "gcp_cloud_logging"
    GCP_ERROR_REPORTING = "gcp_error_reporting"
    GCP_FIREBASE = "gcp_firebase"
    AWS_CLOUD_WATCH = "aws_cloud_watch"
    AZURE_MONITOR = "azure_monitor"
    AZURE_APPLICATION_INSIGHTS = "azure_application_insights"
    IBM_LOG_ANALYTICS = "ibm_log_analytics"
    ALIBABA_LOG_SERVICE = "alibaba_log_service"
    LOGGLY = "loggly"
    DATADOG = "datadog"
    NEW_RELIC = "new_relic"
    SENTRY = "sentry"
    SUMOLOGIC = "sumologic"
    # --- Other ---
    SYSLOG = "syslog" # For system logs
    CUSTOM = "custom" # For a user-defined remote handler
    OTHER = "other"

    def __str__(self):
        return self.name


class LogLevelPro(Enum):
    """
    Standardized notice levels for data engineering pipelines,
    designed for easy analysis and identification of manual 
    intervention needs.
    """
    ##############################
    # DEBUG (1000 - 9990) --> LOGGED AT DEBUG LEVEL
    ##############################
    DEBUG = 1000

    ##############################
    # INFO (10000 - 19990)
    ##############################
    INFO = 10000
    # Task Info (11100 - 11190)
    INFO_TASK_STARTED = 11100
    INFO_TASK_COMPLETE = 11110
    INFO_TASK_COMPLETE_WITH_NOTICES = 11120
    INFO_TASK_COMPLETE_WITH_WARNINGS = 11130
    INFO_TASK_PAUSED = 11140
    INFO_TASK_RESUMED = 11150
    INFO_TASK_CANCELLED = 11160
    INFO_TASK_STOPPED = 11170
    INFO_TASK_SKIPPED = 11180

    # Subject Info (12100 - 12190)
    INFO_SUBJECT_STARTED = 12100

    # Subject Group Info (12200 - 12290)
    INFO_SUBJECT_GROUP_STARTED = 12200

    # Iteration Info (13100 - 13190)
    INFO_ITERATION_STARTED = 13100
    INFO_ITERATION_PAUSED = 13110
    INFO_ITERATION_RESUMED = 13120
    INFO_ITERATION_CANCELLED = 13130
    INFO_ITERATION_STOPPED = 13140
    INFO_ITERATION_SKIPPED = 13150

    # Pipeline Info (14100 - 14190)
    INFO_PIPELINE_STARTED = 14100
    INFO_PIPELINE_PAUSED = 14110
    INFO_PIPELINE_RESUMED = 14120
    INFO_PIPELINE_CANCELLED = 14130
    INFO_PIPELINE_STOPPED = 14140

    ##############################
    # READS (20000 - 29990)
    ##############################
    READ = 20000
    READ_COMPLETE = 20010
    READ_DB_COMPLETE = 20020
    READ_DOCUMENT_COMPLETE = 20030
    READ_FILE_FROM_CLOUD_STORAGE_COMPLETE = 20040
    READ_FILE_FROM_LOCAL_STORAGE_COMPLETE = 20050
    READ_HTTP_GET_COMPLETE = 20060
    READ_SECRET_FROM_SECRET_MANAGER_COMPLETE = 20070

    # PubSub Reads (20200 - 20290)
    READ_PUBSUB_PULL_MESSAGE_COMPLETE = 20200
    READ_PUBSUB_PUSH_MESSAGE_COMPLETE = 20210
    READ_PUBSUB_LIST_SUBSCRIPTIONS_COMPLETE = 20220
    READ_PUBSUB_LIST_TOPICS_COMPLETE = 20230
    READ_PUBSUB_LIST_SUBSCRIPTIONS_FOR_TOPIC_COMPLETE = 20240

    ##############################
    # IN-MEMORY TASKS (30000 - 39990)
    ##############################
    IN_MEMORY_TASK = 30000
    # Validation (30100 - 30990)
    IN_MEMORY_VALIDATE_SCHEMA_COMPLETE = 30100
    IN_MEMORY_VALIDATE_COMPLETE = 30110

    # Sorting/Grouping/Joining (31000 - 31990)
    IN_MEMORY_SORT_COMPLETE = 31000
    IN_MEMORY_GROUP_BY_COMPLETE = 31010
    IN_MEMORY_JOIN_COMPLETE = 31020
    IN_MEMORY_MERGE_COMPLETE = 31030
    IN_MEMORY_SPLIT_COMPLETE = 31040
    IN_MEMORY_UNION_COMPLETE = 31050

    # Transformation (32000 - 32990)
    IN_MEMORY_TRANSFORM_COMPLETE = 32000
    IN_MEMORY_FILTER_COMPLETE = 32010
    IN_MEMORY_AGGREGATE_COMPLETE = 32020
    IN_MEMORY_NORMALIZE_COMPLETE = 32030
    IN_MEMORY_DENORMALIZE_COMPLETE = 32040
    IN_MEMORY_DEDUPLICATE_COMPLETE = 32050
    IN_MEMORY_ENRICH_COMPLETE = 32060
    IN_MEMORY_DECRYPT_COMPLETE = 32070
    IN_MEMORY_ENCRYPT_COMPLETE = 32080
    IN_MEMORY_MASK_COMPLETE = 32090
    IN_MEMORY_FILL_MISSING_VALUES_COMPLETE = 32100
    IN_MEMORY_REPLACE_VALUES_COMPLETE = 32110

    ##############################
    # PERSIST (40000 - 49990) --> ALSO LOGGED AT INFO LEVEL
    ##############################
    PERSIST = 40000  # General PERSIST, no immediate PERSIST required

    # General PERSIST Completions (41000 - 41990)
    PERSIST_COMPLETE = 41000  # General PERSIST, no immediate PERSIST required
    PERSIST_CREATE_COMPLETE = 41010
    PERSIST_WRITE_COMPLETE = 41020
    PERSIST_UPDATE_COMPLETE = 41030
    PERSIST_DELETE_COMPLETE = 41040
    PERSIST_MERGE_COMPLETE = 41050

    # BATCH PERSIST Completions (42000 - 42990)
    PERSIST_BATCH_COMPLETE = 42000
    PERSIST_CREATE_BATCH_COMPLETE = 42010
    PERSIST_WRITE_BATCH_COMPLETE = 42020
    PERSIST_UPDATE_BATCH_COMPLETE = 42030
    PERSIST_DELETE_BATCH_COMPLETE = 42040

    # Cloud Storage PERSISTs (43000 - 43990)
    PERSIST_WRITE_IN_CLOUD_STORAGE_COMPLETE = 43000
    PERSIST_UPDATE_IN_CLOUD_STORAGE_COMPLETE = 43010
    PERSIST_DELETE_IN_CLOUD_STORAGE_COMPLETE = 43020
    PERSIST_WRITE_BATCH_IN_CLOUD_STORAGE_COMPLETE = 43100
    PERSIST_UPDATE_BATCH_IN_CLOUD_STORAGE_COMPLETE = 43110
    PERSIST_DELETE_BATCH_IN_CLOUD_STORAGE_COMPLETE = 43120

    # Local Storage PERSISTs (44000 - 44990)
    PERSIST_WRITE_IN_LOCAL_STORAGE_COMPLETE = 44000
    PERSIST_UPDATE_IN_LOCAL_STORAGE_COMPLETE = 44010
    PERSIST_DELETE_IN_LOCAL_STORAGE_COMPLETE = 44020
    PERSIST_WRITE_BATCH_IN_LOCAL_STORAGE_COMPLETE = 44100
    PERSIST_UPDATE_BATCH_IN_LOCAL_STORAGE_COMPLETE = 44110
    PERSIST_DELETE_BATCH_IN_LOCAL_STORAGE_COMPLETE = 44120

    # Cloud DB PERSISTs (45000 - 45990)
    PERSIST_WRITE_IN_DB_COMPLETE = 45000
    PERSIST_UPDATE_IN_DB_COMPLETE = 45010
    PERSIST_DELETE_IN_DB_COMPLETE = 45020
    PERSIST_MERGE_IN_DB_COMPLETE = 45030

    # BATCH Cloud DB PERSISTs (45100 - 45990)
    PERSIST_WRITE_BATCH_IN_DB_COMPLETE = 45100
    PERSIST_UPDATE_BATCH_IN_DB_COMPLETE = 45110
    PERSIST_DELETE_BATCH_IN_DB_COMPLETE = 45120
    PERSIST_MERGE_BATCH_IN_DB_COMPLETE = 45130

    # Cloud Create PERSISTs (45500 - 45690)
    PERSIST_CREATE_DB_TABLE_COMPLETE = 45500
    PERSIST_CREATE_OR_REPLACE_DB_TABLE_COMPLETE = 45510
    PERSIST_CREATE_AND_LOAD_DB_TABLE_COMPLETE = 45520
    PERSIST_DELETE_DB_TABLE_COMPLETE = 45530

    # Cloud Collection PERSISTs (45700 - 45990)
    PERSIST_CREATE_DB_COLLECTION_COMPLETE = 45700
    PERSIST_DELETE_DB_COLLECTION_COMPLETE = 45710

    # HTTP PERSISTs (47000 - 47990)
    PERSIST_WRITE_HTTP_POST_COMPLETE = 47000
    PERSIST_WRITE_HTTP_PUT_COMPLETE = 47010
    PERSIST_WRITE_HTTP_PATCH_COMPLETE = 47020
    PERSIST_WRITE_HTTP_DELETE_COMPLETE = 47030

    # PubSub PERSISTs (48000 - 48990)
    PERSIST_PUBSUB_PUBLISH_MESSAGE_COMPLETE = 48000
    PERSIST_PUBSUB_ACK_MESSAGE_COMPLETE = 48010
    PERSIST_PUBSUB_CREATE_TOPIC_COMPLETE = 48100
    PERSIST_PUBSUB_DELETE_TOPIC_COMPLETE = 48110
    PERSIST_PUBSUB_CREATE_SUBSCRIPTION_COMPLETE = 48200
    PERSIST_PUBSUB_DELETE_SUBSCRIPTION_COMPLETE = 48210


    ##############################
    # SUCCESSES (50000 - 54990) --> LOGGED AT INFO LEVEL
    ##############################
    SUCCESS = 50000
    # # Task Successes (5100 - 5199) ---> TASK SUCCESSES ARE INFO LEVEL, HENCE ARE IN INFO
    # Subject Successes (52000 - 52990)
    SUCCESS_SUBJECT_COMPLETE = 52000
    SUCCESS_SUBJECT_COMPLETE_WITH_NOTICES = 52010
    SUCCESS_SUBJECT_COMPLETE_WITH_WARNINGS = 52020

    SUCCESS_SUBJECT_GROUP_COMPLETE = 52030
    SUCCESS_SUBJECT_GROUP_COMPLETE_WITH_NOTICES = 52040
    SUCCESS_SUBJECT_GROUP_COMPLETE_WITH_WARNINGS = 52050

    # Iteration Successes (53000 - 53990)
    SUCCESS_ITERATION_COMPLETE = 53000
    SUCCESS_ITERATION_COMPLETE_WITH_NOTICES = 53010
    SUCCESS_ITERATION_COMPLETE_WITH_WARNINGS = 53020

    # Pipeline Successes (54000 - 54990)
    SUCCESS_PIPELINE_COMPLETE = 54000
    SUCCESS_PIPELINE_COMPLETE_WITH_NOTICES = 54010
    SUCCESS_PIPELINE_COMPLETE_WITH_WARNINGS = 54020

    ##############################
    # NOTICES (60000 - 61990) --> LOGGED AT INFO LEVEL
    ##############################
    NOTICE = 60000

    NOTICE_ALREADY_EXISTS = 61000
    NOTICE_PARTIAL_EXISTS = 61010

    NOTICE_FILE_IN_CLOUD_STORAGE_ALREADY_EXISTS = 61100
    NOTICE_DATA_IN_DB_ALREADY_EXISTS = 61110
    NOTICE_DATA_IN_DB_PARTIALLY_EXISTS = 61120
    NOTICE_TABLE_DOESNT_EXIST = 61130
    NOTICE_COLLECTION_DOESNT_EXIST = 61140
    NOTICE_DOCUMENT_DOESNT_EXIST = 61150

    ##############################
    # WARNINGS (70000 - 72990) --> LOGGED AT WARNING LEVEL
    ##############################
    WARNING = 70000

    WARNING_REVIEW_RECOMMENDED = 71000
    WARNING_DATA_SCHEMA_ISSUE = 72000
    WARNING_METADATA_SCHEMA_ISSUE = 72010
    WARNING_VALIDATION_ISSUES = 72020

    ##############################
    # ERRORS (80000 - 89990) --> LOGGED AT ERROR LEVEL
    ##############################
    ERROR = 80000
    ERROR_EXCEPTION = 80010
    ERROR_CUSTOM = 80020

    ERROR_DATA_QUALITY_ISSUE = 80030
    ERROR_VALIDATION_ISSUE = 80040
    ERROR_SCHEMA_ISSUE = 80050
    ERROR_SCHEMA_VALIDATION_ISSUE = 80060

    # Read Errors (82000 - 82990)
    ERROR_READ = 82010
    ERROR_READ_DB = 82100

    ERROR_READ_FILE_FROM_CLOUD_STORAGE = 82300
    ERROR_READ_FILE_FROM_LOCAL_STORAGE = 82310
    ERROR_READ_FILE_FROM_CLOUD_STORAGE_WITH_ERRORS = 82320
    ERROR_READ_FILE_FROM_LOCAL_STORAGE_WITH_ERRORS = 82330

    ERROR_READ_HTTP_GET = 82500
    ERROR_READ_SECRET_FROM_SECRET_MANAGER = 82600

    ERROR_READ_PUBSUB_PULL = 82710
    ERROR_READ_PUBSUB_PUSH = 82720

    # In-Memory Task Errors (83000 - 83990)
    ERROR_IN_MEMORY_TASK = 83100
    ERROR_IN_MEMORY_TRANSFORMATION = 83120

    ERROR_IN_MEMORY_VALIDATE = 83510
    ERROR_IN_MEMORY_VALIDATE_SCHEMA = 83520

    # PERSIST Errors (84000 - 84990)
    ERROR_PERSIST_PARTIALLY_FAILED = 84000
    ERROR_PERSIST_FAILED = 84010
    ERROR_PERSIST_WITH_ERRORS = 84020
    ERROR_PERSIST_WITH_WARNINGS_OR_ERRORS = 84030

    # General Data Persistence Errors (84100 - 84290)
    ERROR_PERSIST_CREATE = 84210
    ERROR_PERSIST_WRITE = 84220
    ERROR_PERSIST_UPDATE = 84230
    ERROR_PERSIST_DELETE = 84240
    ERROR_PERSIST_MERGE = 84250

    # Data Persistence Errors with Warnings (84400 - 84490)
    ERROR_PERSIST_CREATE_WITH_ERRORS = 84410
    ERROR_PERSIST_WRITE_WITH_ERRORS = 84420
    ERROR_PERSIST_UPDATE_WITH_ERRORS = 84430
    ERROR_PERSIST_DELETE_WITH_ERRORS = 84440
    ERROR_PERSIST_MERGE_WITH_ERRORS = 84450

    # Cloud Storage Errors (84500 - 84590)
    ERROR_PERSIST_WRITE_IN_CLOUD_STORAGE_FAILED = 84500
    ERROR_PERSIST_UPDATE_IN_CLOUD_STORAGE_FAILED = 84510
    ERROR_PERSIST_DELETE_IN_CLOUD_STORAGE_FAILED = 84520
    ERROR_PERSIST_MERGE_IN_CLOUD_STORAGE_FAILED = 84530

    # Cloud Storage Errors with Warnings (84600 - 84690)
    ERROR_PERSIST_WRITE_IN_CLOUD_STORAGE_WITH_ERRORS = 84550
    ERROR_PERSIST_UPDATE_IN_CLOUD_STORAGE_WITH_ERRORS = 84560
    ERROR_PERSIST_DELETE_IN_CLOUD_STORAGE_WITH_ERRORS = 84580
    ERROR_PERSIST_MERGE_IN_CLOUD_STORAGE_WITH_ERRORS = 84590

    # Local Storage Persistence Errors (84600 - 84690)
    ERROR_PERSIST_WRITE_IN_LOCAL_STORAGE_FAILED = 84600
    ERROR_PERSIST_UPDATE_IN_LOCAL_STORAGE_FAILED = 84610
    ERROR_PERSIST_DELETE_IN_LOCAL_STORAGE_FAILED = 84620
    ERROR_PERSIST_MERGE_IN_LOCAL_STORAGE_FAILED = 84630

    # Local Storage Errors with Warnings (84700 - 84790)
    ERROR_PERSIST_WRITE_IN_LOCAL_STORAGE_WITH_ERRORS = 84650
    ERROR_PERSIST_UPDATE_IN_LOCAL_STORAGE_WITH_ERRORS = 84660
    ERROR_PERSIST_DELETE_IN_LOCAL_STORAGE_WITH_ERRORS = 84670
    ERROR_PERSIST_MERGE_IN_LOCAL_STORAGE_WITH_ERRORS = 84680

    # Database Persistence Errors (84800 - 84890)
    ERROR_PERSIST_WRITE_IN_DB_FAILED = 84800
    ERROR_PERSIST_UPDATE_IN_DB_FAILED = 84810
    ERROR_PERSIST_DELETE_IN_DB_FAILED = 84820
    ERROR_PERSIST_MERGE_IN_DB_FAILED = 84830

    # Database Errors with Warnings (84850 - 84890)
    ERROR_PERSIST_WRITE_IN_DB_WITH_ERRORS = 84850
    ERROR_PERSIST_UPDATE_IN_DB_WITH_ERRORS = 84860
    ERROR_PERSIST_DELETE_IN_DB_WITH_ERRORS = 84870
    ERROR_PERSIST_MERGE_IN_DB_WITH_ERRORS = 84880

    # Cloud Create Persistence Errors (86000 - 86290)
    ERROR_PERSIST_CREATE_DB_TABLE_FAILED = 86000
    ERROR_PERSIST_CREATE_OR_REPLACE_DB_TABLE_FAILED = 86010
    ERROR_PERSIST_CREATE_AND_LOAD_DB_TABLE_FAILED = 86020
    ERROR_PERSIST_DELETE_DB_TABLE_FAILED = 86030

    ERROR_PERSIST_CREATE_DB_TABLE_WITH_ERRORS = 86200
    ERROR_PERSIST_CREATE_OR_REPLACE_DB_TABLE_WITH_ERRORS = 86210
    ERROR_PERSIST_CREATE_AND_LOAD_DB_TABLE_WITH_ERRORS = 86220
    ERROR_PERSIST_DELETE_DB_TABLE_WITH_ERRORS = 86230

    # Cloud Collection Persistence Errors (86400 - 86590)
    ERROR_PERSIST_CREATE_DB_COLLECTION_FAILED = 86400
    ERROR_PERSIST_DELETE_DB_COLLECTION_FAILED = 86410

    ERROR_PERSIST_CREATE_DB_COLLECTION_WITH_ERRORS = 86500
    ERROR_PERSIST_DELETE_DB_COLLECTION_WITH_ERRORS = 86510

    # HTTP Persistence Errors (87000 - 87299)
    ERROR_PERSIST_WRITE_HTTP_POST_FAILED = 87000
    ERROR_PERSIST_WRITE_HTTP_PUT_FAILED = 87010
    ERROR_PERSIST_WRITE_HTTP_PATCH_FAILED = 87020
    ERROR_PERSIST_WRITE_HTTP_DELETE_FAILED = 87030

    ERROR_PERSIST_WRITE_HTTP_POST_WITH_ERRORS = 87200
    ERROR_PERSIST_WRITE_HTTP_PUT_WITH_ERRORS = 87210
    ERROR_PERSIST_WRITE_HTTP_PATCH_WITH_ERRORS = 87220
    ERROR_PERSIST_WRITE_HTTP_DELETE_WITH_ERRORS = 87230

    # PubSub Persistence Errors (87500 - 87799)
    ERROR_PERSIST_PUBSUB_PUBLISH_MESSAGE_FAILED = 87500
    ERROR_PERSIST_PUBSUB_ACK_MESSAGE_FAILED = 87510
    ERROR_PERSIST_PUBSUB_CREATE_TOPIC_FAILED = 87520
    ERROR_PERSIST_PUBSUB_DELETE_TOPIC_FAILED = 87530
    ERROR_PERSIST_PUBSUB_CREATE_SUBSCRIPTION_FAILED = 87540
    ERROR_PERSIST_PUBSUB_DELETE_SUBSCRIPTION_FAILED = 87550

    ERROR_PERSIST_PUBSUB_PUBLISH_MESSAGE_WITH_ERRORS = 87700
    ERROR_PERSIST_PUBSUB_ACK_MESSAGE_WITH_ERRORS = 87710
    ERROR_PERSIST_PUBSUB_CREATE_TOPIC_WITH_ERRORS = 87720
    ERROR_PERSIST_PUBSUB_DELETE_TOPIC_WITH_ERRORS = 87730
    ERROR_PERSIST_PUBSUB_CREATE_SUBSCRIPTION_WITH_ERRORS = 87740
    ERROR_PERSIST_PUBSUB_DELETE_SUBSCRIPTION_WITH_ERRORS = 87750

    # Threshold Errors (88000 - 89999)
    ERROR_TASK_ALLOWED_THRESHOLD_REACHED = 88000
    ERROR_DATA_QUALITY_ALLOWED_THRESHOLD_REACHED = 88010
    ERROR_METADATA_QUALITY_ALLOWED_THRESHOLD_REACHED = 88020

    ERROR_SUBJECT_ALLOWED_THRESHOLD_REACHED = 88110
    ERROR_ITERATION_ALLOWED_THRESHOLD_REACHED = 88120
    ERROR_PIPELINE_ALLOWED_THRESHOLD_REACHED = 88130

    ##############################
    # FAILURES (90000 - 99990) --> LOGGED AT ERROR LEVEL
    ##############################
    FAILED = 90000

    # Task Failures (91000 - 91990)
    FAILED_TASK = 91000
    FAILED_TASK_COMPLETE_WITH_ERRORS = 91010

    # Subject Failures (92000 - 92990)
    FAILED_SUBJECT = 92000
    FAILED_SUBJECT_COMPLETE_WITH_ERRORS = 92010
    FAILED_SUBJECT_GROUP = 92020
    FAILED_SUBJECT_GROUP_COMPLETE_WITH_ERRORS = 92030

    # Iteration Failures (93000 - 93499)
    FAILED_ITERATION = 93000
    FAILED_ITERATION_COMPLETE_WITH_ERRORS = 93010

    # Pipeline Failures (94000 - 94999)
    FAILED_PIPELINE_COMPLETE_WITH_ERRORS = 94000
    FAILED_PIPELINE_EARLY_EXITED = 94010

    # Critical System Failures (98000 - 99999)
    FAILED_CRITICAL_SYSTEM_FAILURE = 98000

    def __str__(self):
        return self.name

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

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
    SUBSCRIPTION_PLAN="subscription_plan"
    CATALOG="catalog"
    PAYMENT="payment"
    ACTION="action"
    RESOURCE="resource"
    SERVICE="service"
    ROLE="role"

    def __str__(self):
        return self.value

class SubscriptionPlan(Enum):
    FREE="free"
    BASIC="basic"
    PREMIUM="premium"
    ADVANCED="advanced"
    PROFESSIONAL="professional"
    ENTERPRISE="enterprise"

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
    



# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long


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



