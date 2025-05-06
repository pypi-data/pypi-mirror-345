# **Dkr Resource**

> This Python library is designed to monitor and log system resource usage (CPU and RAM) during the execution of a routine. It collects data periodically and stores it in a database, allowing users to track the resource consumption of their applications.

## **Installation**

```plaintext
pip install dkrresource
```

## **Configuration**

To use ResourceManager, configure the following parameters:

- **routine_name**: Name of the routine being monitored.
- **start_date**: Start time of the routine.
- **routine_path**: Path where the routine is running.
- **db_str**: Database connection string.
- **t_channel**: Teams channel for error reporting.
- **t_url**: Teams webhook URL for reporting errors.

## **Usage**

```python
from datetime import datetime as dt
from resourcemanager import ResourceManager


routine_name = "DataPipeline"
start_date = dt.now()
routine_path = "/path/to/routine"
db_str = "postgresql://user:password@localhost/dbname"
t_channel = "resource-alerts"
t_url = "https://teams.webhook.url"


# Initialize the ResourceManager
rm = ResourceManager(
    routine_name,
    start_date,
    routine_path,
    db_str,
    t_channel,
    t_url
)

# Start resource monitoring
rm.start_collection()

# Execute some processing...

# Stop collecting and log final data
rm.finish_collection()
```
## **Database Logging**

The library logs the following resource metrics in a database:

- **Maximum CPU usage**
- **Average CPU usage**
- **Maximum RAM usage**
- **Average RAM usage**

## **Error Reporting**

If an issue occurs during execution, **ResourceManager** sends an error notification to a Microsoft Teams channel using the provided webhook.


## **License**

This project is licensed under the MIT License.