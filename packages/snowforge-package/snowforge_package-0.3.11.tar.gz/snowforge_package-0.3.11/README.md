
# 🚀 Snowforge - Powerful Data Integration

**Snowforge** is a Python package designed to streamline data integration and transfer between **AWS**, **Snowflake**, and various **on-premise database systems**. It provides efficient data extraction, logging, configuration management, and AWS utilities to support robust data engineering workflows.

---

## ✨ Features

- **AWS Integration**: Manage AWS S3 and Secrets Manager operations.
- **Snowflake Connection**: Establish and manage Snowflake connections with key-pair authentication.
- **Advanced Logging**: Centralized logging system with colored output for better visibility.
- **Snowflake Logging**: Structured task logging directly to Snowflake using stored procedures (**requires setup**).
- **Configuration Management**: Load and manage credentials from a TOML configuration file.
- **Data Mover Engine**: Parallel data processing and extraction strategies for efficiency.
- **Extensible Database Extraction**: Uses a **strategy pattern** to support multiple **on-prem database systems** (e.g., Netezza, Oracle, PostgreSQL, etc.).

---

## 📥 Installation

Install Snowforge using pip:

```sh
pip install snowforge-package
```

---

## ⚙️ Configuration

Snowforge uses a `snowforge_config.toml` file to manage profiles and credentials for AWS and Snowflake. The package searches for this file in the following order:

1. Path specified in the `SNOWFORGE_CONFIG_PATH` environment variable.
2. Current working directory.
3. `~/.config/snowforge_config.toml`
4. Package directory.

### ✅ Example `snowforge_config.toml`

```toml
[AWS.default]
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
REGION = "us-east-1"

[SNOWFLAKE.default]
USERNAME = "your-username"
ACCOUNT = "your-account"
ROLE = "optional-role"

[SNOWFLAKE.svc_key_based_profile]
USERNAME = "svc_user"
ACCOUNT = "your-account"
KEY_FILE_PATH = "/absolute/path/to/your/private_key.p8"
KEY_FILE_PASSWORD = "your_key_password"

[SNOWFLAKE.snowforge]
USERNAME = "svc_user"
ACCOUNT = "your-account"
KEY_FILE_PATH = "/absolute/path/to/your/private_key.p8"
KEY_FILE_PASSWORD = "your_key_password"
SNOWFLAKE_DATABASE = "YOUR_DB"
SNOWFLAKE_SCHEMA = "YOUR_SCHEMA"
```

> ⚠️ **Note:** The `snowforge` profile is **required** for SnowflakeLogging.
> You **must** execute the provided `.sql` scripts located in `Snowforge/resources/sql/` on your Snowflake account beforehand.
> These scripts define the required `TASK_LOGS` table and the `LOG_TASK_EXECUTION_START` and `LOG_TASK_EXECUTION_END` procedures.

---

## 🚀 Quick Start

### 🔹 Initialize AWS

```python
from Snowforge.AWSIntegration import AWSIntegration

AWSIntegration.initialize(profile="default", verbose=True)
```

### 🔹 Connect to Snowflake

```python
from Snowforge.SnowflakeIntegration import SnowflakeIntegration

# Connect using TOML profile:
conn = SnowflakeIntegration.connect(profile="svc_key_based_profile", verbose=True)

# Or fall back to username + account only:
conn = SnowflakeIntegration.connect(user_name="your-user", account="your-account")
```

### 🔹 Use Logging

```python
from Snowforge.Logging import Debug

Debug.log("This is an info message", level='INFO')
Debug.log("This is an error message", level='ERROR')
```

### 🔹 Log to Snowflake

```python
from Snowforge.SnowflakeLogging import SnowflakeLogging
from datetime import datetime

# Show required Snowflake SQL setup
SnowflakeLogging.show_requirements(print_to_console=True)

# Log task start
execution_id = SnowflakeLogging.log_start(
    task_id=42, process_id=1001, starttime=datetime.now()
)

# Log task end
SnowflakeLogging.log_end(
    execution_id=execution_id,
    status="SUCCESS",
    log_path="/logs/job.log",
    endtime=datetime.now(),
    next_execution_time=datetime.now()
)
```

### 🔹 Extract Data Using Strategy Pattern

```python
from Snowforge.DataMover import Engine
from Snowforge.DataMover.Extractors.NetezzaExtractor import NetezzaExtractor

extractor = NetezzaExtractor()

header, output_file = Engine.export_to_file(
    extractor=extractor,
    output_path="/tmp/exported_data",
    fully_qualified_table_name="MY_DB.MY_SCHEMA.MY_TABLE",
    filter_column="date_column",
    filter_value="01.01.2023",
    verbose=True
)
```

---

## 🧩 Extending the System

Implement a new database extractor by inheriting from `ExtractorStrategy` and implementing:

- `extract_table_query(...)`
- `list_all_tables(...)`
- `export_external_table(...)`

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👥 Kontakt og samarbeid

Vi oppfordrer til å ta kontakt dersom du har forslag til forbedringer, spørsmål om bruken av Snowforge, eller ønsker samarbeid. Ditt bidrag er alltid velkommen!
