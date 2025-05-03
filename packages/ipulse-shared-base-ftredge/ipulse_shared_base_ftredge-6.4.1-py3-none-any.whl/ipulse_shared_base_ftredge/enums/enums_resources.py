
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum

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