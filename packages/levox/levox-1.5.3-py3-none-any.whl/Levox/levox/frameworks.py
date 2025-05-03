"""
Framework-specific detection patterns for common web frameworks and platforms.
"""
from typing import Dict, List, Any

# Django specific patterns
DJANGO_PATTERNS = {
    "data_transfer": [
        r"(?i)requests\.(?:get|post|put|delete|patch|head)\(",  # Django requests
        r"(?i)urllib\.request\.urlopen\(",  # urllib usage
        r"(?i)http\.client\.HTTPConnection\(",  # http client
        r"(?i)django\.core\.mail\.send",  # Email sending
        r"(?i)requests_oauthlib",  # OAuth integration
        r"(?i)boto3\.client\(['\"](?:s3|sns|sqs|ses)",  # AWS integrations
        r"(?i)CrossDomainXhr",  # Cross-domain XHR
        r"(?i)cors_headers",  # CORS headers indicating cross-origin access
        r"(?i)JsonResponse\(.*?to=['\"].*?@",  # API responses with possible email
    ],
    "pii_collection": [
        r"(?i)models\.(?:Char|Text|Email|Integer|Float|Decimal|Boolean|Date|DateTime|Time|Phone|File|Image|JSON)Field\(",  # Django model fields
        r"(?i)request\.POST\.get\(['\"](?:email|name|address|phone|user|password|birth|gender|age|passport|license|nationality|tax|ssn|social|health|religion|political|account|payment|card)",  # POST data
        r"(?i)request\.user\.",  # User data access
        r"(?i)User\.objects\.(?:create|get|filter)",  # User model operations
        r"(?i)Profile\.objects\.",  # User profile
        r"(?i)request\.META\[['\"](HTTP_X_FORWARDED_FOR|REMOTE_ADDR)",  # IP address collection
        r"(?i)request\.GET\.get\(['\"](?:email|name|address|phone|user|birth|id|age)",  # GET parameters with PII
        r"(?i)geolocator",  # Geolocation services
    ],
    "consent_issues": [
        r"(?i)request\.session\[['\"]",  # Session data without consent check
        r"(?i)set_cookie\(",  # Setting cookies
        r"(?i)response\.set_cookie\(",  # Django response cookies
        r"(?i)django\.contrib\.auth\.(?:login|authenticate)",  # Authentication without explicit consent
        r"(?i)request\.COOKIES\[",  # Reading cookies
        r"(?i)request\.session\[",  # Using session storage
        r"(?i)cache\.set\(",  # Setting cache
    ],
    "data_deletion": [
        r"(?i)def delete\(",  # Delete views
        r"(?i)\.delete\(\)",  # Model delete method
        r"(?i)DeleteView",  # Django delete view
        r"(?i)\.objects\.filter\(.*\)\.delete\(\)",  # Batch deletion
        r"(?i)request\.session\.flush\(\)",  # Session deletion
        r"(?i)request\.session\.clear\(\)",  # Session clearing
    ],
    "security_measures": [
        r"(?i)verify_ssl\s*=\s*False",  # Disabled SSL verification
        r"(?i)DEBUG\s*=\s*True",  # Debug mode in production context
        r"(?i)ALLOWED_HOSTS\s*=\s*\['*[*]'*\]",  # Overly permissive hosts
        r"(?i)password\s*=.*['\"]",  # Hardcoded passwords
        r"(?i)django\.middleware\.security",  # Security middleware (positive)
        r"(?i)SECRET_KEY\s*=\s*['\"]",  # Hardcoded secret keys
    ],
}

# Flask specific patterns
FLASK_PATTERNS = {
    "data_transfer": [
        r"(?i)requests\.(?:get|post|put|delete|patch|head)\(",  # Flask with requests
        r"(?i)flask_(?:mail|api)",  # Flask extensions for external comms
        r"(?i)app\.route\(['\"]\/api",  # API endpoints
        r"(?i)jsonify\(",  # JSON responses to API requests
        r"(?i)flask_cors",  # CORS handling
        r"(?i)response\s*=\s*make_response\(",  # Response creation
        r"(?i)redirect\(.*?['\"]https?://",  # Redirects to external sites
        r"(?i)send_file\(",  # File transfers
        r"(?i)urllib\.parse\.urljoin\(",  # URL construction
    ],
    "pii_collection": [
        r"(?i)request\.(?:form|args|values|json)\.get\(['\"](?:email|name|address|phone|user|birth|passport|tax|ssn|health|gender|religion)",  # Form data
        r"(?i)db\.(?:session|Column)\(",  # Database operations
        r"(?i)current_user\.",  # User data access
        r"(?i)Model\(.*?=.*?request\.",  # Model creation with request data
        r"(?i)request\.headers\.get\(['\"](?:X-Forwarded-For|CF-Connecting-IP)",  # IP collection
        r"(?i)request\.cookies\.get\(",  # Cookie access
        r"(?i)request\.files",  # File uploads which might contain PII
        r"(?i)(?:String|Integer|Float|Boolean|Date|DateTime|PickleType)\(",  # SQLAlchemy field types
    ],
    "consent_issues": [
        r"(?i)session\[['\"]",  # Session data without consent check
        r"(?i)response\.set_cookie\(",  # Setting cookies
        r"(?i)make_response\(.*set_cookie",  # Setting cookies in response
        r"(?i)flask_login",  # Flask login (might need consent checks)
        r"(?i)remember_me",  # Remember me functionality
        r"(?i)request\.cookies",  # Reading cookies
        r"(?i)get_cookie\(",  # Getting cookies without consent check
    ],
    "data_deletion": [
        r"(?i)db\.session\.delete\(",  # Database deletion
        r"(?i)@app\.route\(['\"]\/.*\/delete",  # Delete routes
        r"(?i)\.query\.filter_by\(.*\)\.delete\(\)",  # Batch deletion
        r"(?i)session\.pop\(",  # Session data removal
        r"(?i)session\.clear\(\)",  # Session clearing
    ],
    "security_measures": [
        r"(?i)verify\s*=\s*False",  # Disabled SSL verification
        r"(?i)debug\s*=\s*True",  # Debug mode in production context
        r"(?i)SECRET_KEY\s*=\s*['\"]",  # Hardcoded secrets
        r"(?i)app\.config\[['\"]SECRET_KEY['\"]\]\s*=\s*['\"]",  # Hardcoded secrets
        r"(?i)flask\_talisman",  # Security headers (positive)
        r"(?i)werkzeug\.security\.generate_password_hash",  # Password hashing (positive)
    ],
}

# Node.js/Express patterns
NODE_PATTERNS = {
    "data_transfer": [
        r"(?i)axios\.(?:get|post|put|delete|patch|head)\(",  # Axios HTTP client
        r"(?i)fetch\(['\"]https?://",  # Fetch API
        r"(?i)http\.(?:get|request)\(",  # Node HTTP module
        r"(?i)\.send\(",  # Express response
        r"(?i)request\(['\"]https?://",  # Request library
        r"(?i)https\.request\(",  # HTTPS module
        r"(?i)nodemailer",  # Email sending
        r"(?i)aws-sdk",  # AWS SDK
        r"(?i)\.createConnection\(",  # Database connections
        r"(?i)cors\(",  # CORS middleware
    ],
    "pii_collection": [
        r"(?i)req\.body\.(?:email|name|address|phone|user|birth|passport|ssn|gender|religion|nationality)",  # Request body
        r"(?i)req\.params\.(?:id|user|email)",  # URL parameters
        r"(?i)mongoose\.model\(",  # MongoDB models
        r"(?i)\.findOne\(",  # Database queries
        r"(?i)req\.session\.user",  # User data in session
        r"(?i)req\.ip",  # IP address collection
        r"(?i)req\.headers\[['\"](x-forwarded-for|cf-connecting-ip)",  # IP collection headers
        r"(?i)req\.cookies",  # Cookie access
        r"(?i)(?:String|Number|Date|Buffer|Boolean|ObjectId)\(",  # Schema types
    ],
    "consent_issues": [
        r"(?i)req\.session",  # Session data without consent check
        r"(?i)res\.cookie\(",  # Setting cookies
        r"(?i)localStorage\.",  # Browser localStorage
        r"(?i)sessionStorage\.",  # Session storage
        r"(?i)document\.cookie",  # Browser cookies
        r"(?i)jwt\.sign\(",  # JWT token creation
        r"(?i)passport\.authenticate\(",  # Authentication without explicit consent check
        r"(?i)cookie-parser",  # Cookie parsing
    ],
    "data_deletion": [
        r"(?i)\.findByIdAndDelete\(",  # MongoDB deletion
        r"(?i)\.deleteOne\(",  # MongoDB deletion
        r"(?i)app\.delete\(",  # Express delete routes
        r"(?i)req\.session\.destroy\(",  # Session destruction
        r"(?i)\.remove\(",  # MongoDB remove method
        r"(?i)\.truncate\(",  # SQL table truncation
    ],
    "security_measures": [
        r"(?i)rejectUnauthorized:\s*false",  # Disabled SSL verification
        r"(?i)process\.env\.",  # Environment variables (positive)
        r"(?i)bcrypt\.(?:hash|compare)",  # Password hashing (positive)
        r"(?i)helmet\(",  # Security middleware (positive)
        r"(?i)eval\(",  # Eval usage (negative)
        r"(?i)\.innerHTML\s*=",  # Potential XSS
    ],
}

# React patterns
REACT_PATTERNS = {
    "data_transfer": [
        r"(?i)useEffect\(.*fetch\(",  # Fetch in useEffect
        r"(?i)axios\.(?:get|post|put|delete|patch|head)\(",  # Axios HTTP client
        r"(?i)\.json\(\)",  # Parsing JSON responses
        r"(?i)new FormData\(\)",  # Form data submission
        r"(?i)headers:\s*{",  # Setting HTTP headers
        r"(?i)window\.location\s*=",  # Browser redirects
        r"(?i)navigate\(",  # React Router navigation
        r"(?i)POST|GET|PUT|DELETE|PATCH",  # HTTP methods
    ],
    "pii_collection": [
        r"(?i)useState\(\[?['\"]?(?:user|profile|account|customer|name|email|phone|address)",  # User state
        r"(?i)\.(?:email|name|address|phone|user|birth|ssn|passport|gender|nationality|religion)",  # Properties that might be PII
        r"(?i)value=\{(?:email|name|address|phone|birth|passport|nationality)",  # Form values
        r"(?i)useContext\(.*?User",  # User context
        r"(?i)localStorage\.(?:get|set)Item\(['\"]user",  # User storage
        r"(?i)onChange=\{.*?\}",  # Form input changes
        r"(?i)type=['\"](?:text|email|tel|password)",  # Form input types
        r"(?i)<input\s[^>]*name=['\"](?:email|name|address|phone|birth)",  # Form input names
    ],
    "consent_issues": [
        r"(?i)localStorage\.",  # Browser localStorage
        r"(?i)sessionStorage\.",  # Browser sessionStorage
        r"(?i)document\.cookie",  # Browser cookies
        r"(?i)useCookies\(",  # React Cookie usage
        r"(?i)Cookies\.set\(",  # JS-Cookie library
        r"(?i)accept(?:Cookies|Terms|Privacy)",  # Acceptance functions
        r"(?i)gdpr|ccpa|consent|opt[_-]?in",  # GDPR/consent terms
    ],
    "security_measures": [
        r"(?i)dangerouslySetInnerHTML",  # Potential XSS
        r"(?i)eval\(",  # Eval usage
        r"(?i)Math\.random\(\)",  # Weak randomness
        r"(?i)HttpOnly:\s*false",  # Insecure cookies
        r"(?i)process\.env\.",  # Environment variables (positive)
        r"(?i)iframe\s+src=",  # iframes (potential risk)
    ],
}

# AWS specific patterns
AWS_PATTERNS = {
    "data_transfer": [
        r"(?i)s3\.(?:put_object|upload_file)\(",  # S3 uploads
        r"(?i)dynamodb\.(?:put_item|update_item)\(",  # DynamoDB writes
        r"(?i)sns\.publish\(",  # SNS publishing
        r"(?i)sqs\.send_message\(",  # SQS messaging
        r"(?i)lambda\.invoke\(",  # Lambda invocation
        r"(?i)ses\.send_email\(",  # SES email sending
        r"(?i)cloudwatch\.put_metric_data\(",  # CloudWatch metrics
        r"(?i)cognito-idp\..*\.amazonaws\.com",  # Cognito endpoint
        r"(?i)apigateway\..*\.amazonaws\.com",  # API Gateway endpoint
        r"(?i)kinesis\.put_record",  # Kinesis data streams
    ],
    "pii_collection": [
        r"(?i)cognito\.",  # Cognito user management
        r"(?i)secrets_manager\.get_secret_value\(",  # Secrets that might contain PII
        r"(?i)dynamodb\.scan\(",  # Scanning DynamoDB tables
        r"(?i)s3\.get_object\(",  # Getting S3 objects
        r"(?i)cognito-identity\..*\.amazonaws\.com",  # Cognito Identity endpoint
        r"(?i)personal_id_number",  # Parameter names in AWS docs for PII
        r"(?i)(?:email|name|address|phone|birth|ssn|passport)['\"]:\s*{",  # DynamoDB attribute definitions
    ],
    "data_deletion": [
        r"(?i)s3\.delete_object\(",  # S3 deletion
        r"(?i)dynamodb\.delete_item\(",  # DynamoDB deletion
        r"(?i)cognito\.(?:admin_delete_user|admin_disable_user)\(",  # Cognito user deletion
        r"(?i)rds\.delete_db_instance\(",  # RDS instance deletion
        r"(?i)lambda\.delete_function\(",  # Lambda function deletion
        r"(?i)cloudformation\.delete_stack\(",  # CloudFormation stack deletion
    ],
    "security_measures": [
        r"(?i)aws_secret_access_key\s*=\s*['\"]",  # Hardcoded AWS credentials
        r"(?i)KMS\.(?:encrypt|decrypt)\(",  # KMS encryption (positive)
        r"(?i)SSECustomerKey",  # S3 server-side encryption
        r"(?i)verify_ssl\s*=\s*False",  # Disabled SSL verification
        r"(?i)IAM\.create_policy\(",  # IAM policy creation
        r"(?i)cognito\.initiate_auth\(",  # Cognito authentication (positive)
    ],
}

# Azure specific patterns
AZURE_PATTERNS = {
    "data_transfer": [
        r"(?i)blob_service_client\.upload_blob\(",  # Azure Blob Storage
        r"(?i)table_service\.create_entity\(",  # Azure Table Storage
        r"(?i)service_bus_client\.send\(",  # Azure Service Bus
    ],
    "pii_collection": [
        r"(?i)msal\.(?:PublicClientApplication|ConfidentialClientApplication)\(",  # MSAL authentication
        r"(?i)key_vault_client\.set_secret\(",  # Key Vault operations
    ],
    "data_deletion": [
        r"(?i)blob_service_client\.delete_blob\(",  # Blob deletion
        r"(?i)table_service\.delete_entity\(",  # Table entity deletion
    ],
}

# Google Cloud specific patterns
GCP_PATTERNS = {
    "data_transfer": [
        r"(?i)storage_client\.(?:bucket|blob)\(",  # GCS operations
        r"(?i)firestore\.collection\(",  # Firestore operations
        r"(?i)pubsub\.(?:publish|publish_messages)\(",  # Pub/Sub publishing
    ],
    "pii_collection": [
        r"(?i)auth\.(?:verify_id_token|get_user)\(",  # Firebase auth
        r"(?i)secret_manager\.access_secret_version\(",  # Secret Manager
    ],
    "data_deletion": [
        r"(?i)blob\.delete\(",  # GCS deletion
        r"(?i)firestore\.(?:delete|remove)\(",  # Firestore deletion
    ],
}

# All framework patterns combined
FRAMEWORK_PATTERNS = {
    "django": DJANGO_PATTERNS,
    "flask": FLASK_PATTERNS,
    "node": NODE_PATTERNS,
    "react": REACT_PATTERNS,
    "aws": AWS_PATTERNS,
    "azure": AZURE_PATTERNS,
    "gcp": GCP_PATTERNS,
}

def detect_frameworks(file_content: str) -> List[str]:
    """Detect which frameworks a file is using based on imports and patterns."""
    detected = []
    
    # Django detection
    if any(pattern in file_content.lower() for pattern in [
        "from django", "import django", "django.db", "django.contrib", 
        "django.http", "django.template"
    ]):
        detected.append("django")
        
    # Flask detection
    if any(pattern in file_content.lower() for pattern in [
        "from flask", "import flask", "Flask(__name__", "@app.route"
    ]):
        detected.append("flask")
        
    # Node.js/Express detection
    if any(pattern in file_content.lower() for pattern in [
        "require('express')", "import express", "app.get(", "app.use(",
        "module.exports", "npm", "package.json", "node_modules"
    ]):
        detected.append("node")
        
    # React detection
    if any(pattern in file_content.lower() for pattern in [
        "import react", "from 'react'", "useState", "useEffect", "component",
        "jsx", "props", "react-dom"
    ]):
        detected.append("react")
        
    # AWS detection
    if any(pattern in file_content.lower() for pattern in [
        "import boto3", "aws-sdk", "new AWS.", "aws-lambda", "aws-cdk",
        "dynamodb", "s3client", "ec2client", "lambda", "aws.config"
    ]):
        detected.append("aws")
        
    # Azure detection
    if any(pattern in file_content.lower() for pattern in [
        "azure.storage", "azure.cosmos", "azure.identity", "from azure", 
        "Microsoft.Azure", "AzureClient", "BlobServiceClient"
    ]):
        detected.append("azure")
        
    # GCP detection
    if any(pattern in file_content.lower() for pattern in [
        "google.cloud", "from google", "gcloud", "firebase",
        "GCP", "GoogleCredential", "StorageClient", "Firestore"
    ]):
        detected.append("gcp")
        
    return detected

def get_framework_patterns(file_content: str) -> Dict[str, List[str]]:
    """Get relevant detection patterns based on detected frameworks."""
    frameworks = detect_frameworks(file_content)
    
    # If no frameworks detected, return empty patterns
    if not frameworks:
        return {}
        
    # Combine patterns from all detected frameworks
    combined_patterns = {}
    for framework in frameworks:
        framework_patterns = FRAMEWORK_PATTERNS.get(framework, {})
        
        for issue_type, patterns in framework_patterns.items():
            if issue_type not in combined_patterns:
                combined_patterns[issue_type] = []
            combined_patterns[issue_type].extend(patterns)
            
    return combined_patterns 

# New categories to add to all framework patterns
CROSS_FRAMEWORK_PATTERNS = {
    "data_minimization": [
        r"(?i)select\s*\*\s*from",  # Selecting all columns
        r"(?i)find\(\{\}\)",  # Finding all documents
        r"(?i)limit\(",  # Using limits (positive)
        r"(?i)projection\(",  # Using projections (positive)
        r"(?i)filter\(",  # Using filters (positive)
        r"(?i)select\s+(?:id|specific|columns)",  # Selecting specific columns (positive)
    ],
    "children_data": [
        r"(?i)(?:child|children|minor|age|kid|birth|born)",  # Child-related terms
        r"(?i)verify_age\(",  # Age verification (positive)
        r"(?i)parental_consent\(",  # Parental consent (positive)
        r"(?i)guardian",  # Guardian references
        r"(?i)under_13|under_16|under_18",  # Age restrictions
    ],
    "data_portability": [
        r"(?i)export_data|data_export|json_export|download_data",  # Export functions
        r"(?i)\.to_(?:json|csv|xml)",  # Data conversion
        r"(?i)serializer\.|serialize\(",  # Serialization
        r"(?i)portable_format|structured_format",  # Format references
    ],
    "breach_notification": [
        r"(?i)notify_breach|security_incident|data_breach|breach_report",  # Breach terms
        r"(?i)incident_response|report_breach|alert_users",  # Response terms
        r"(?i)72_hours|notification_deadline",  # Notification deadline
    ],
    "automated_decision": [
        r"(?i)algorithm\.(?:decide|score|calculate|predict|classify)",  # Algorithm terms
        r"(?i)automated_decision|auto_approval|auto_reject|score_calculation",  # Automated terms
        r"(?i)human_review|manual_override|appeal_process",  # Human intervention (positive)
        r"(?i)ml_model|machine_learning|ai\.|artificial_intelligence",  # ML/AI terms
    ],
}

# Update all framework patterns with the cross-framework patterns
for framework_patterns in [DJANGO_PATTERNS, FLASK_PATTERNS, NODE_PATTERNS, REACT_PATTERNS, AWS_PATTERNS, AZURE_PATTERNS, GCP_PATTERNS]:
    for category, patterns in CROSS_FRAMEWORK_PATTERNS.items():
        if category not in framework_patterns:
            framework_patterns[category] = []
        framework_patterns[category].extend(patterns) 