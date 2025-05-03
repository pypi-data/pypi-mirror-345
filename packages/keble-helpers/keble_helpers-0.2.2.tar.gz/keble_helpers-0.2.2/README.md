# Keble helpers

Just a collection of helper functions used by keble project.

## Aliyun

The Aliyun module provides helpers for interacting with Alibaba Cloud (Aliyun) services.

### Base Classes

#### `Aliyun`
- `__init__(*, access_key: str, secret: str)`: Initialize with Aliyun credentials

### OSS (Object Storage Service)

#### `AliyunOss`
- `__init__(oss_endpoint: AnyHttpUrl, bucket: str, **kwargs)`: Initialize OSS client
- `get_bucket() -> oss2.Bucket`: Get OSS bucket instance
- `get_bucket_with_sts(sts_token: str)`: Get bucket with STS token
- `get_object_meta(key: str) -> AliyunOssMeta`: Get object metadata
- `save_object_to_local(key: str, local_path: str, *args, **kwargs)`: Download file from OSS
- `save_local_to_cloud(key: str, local_path: str, *args, **kwargs)`: Upload file to OSS
- `save_snapshot_to_local(key: str, local_path: str, seconds: int)`: Get video snapshot
- `cold_archive_object(key: str)`: Convert object to cold archive storage class
- `get_sts_signed_url(sts_token: str, key: str, *, expire_seconds: int = 60, content_type: Optional[str] = None, oss_storage_class: Optional[str] = None) -> str`: Generate signed URL with STS

### STS (Security Token Service)

#### `AliyunSts`
- `__init__(region, **kwargs)`: Initialize STS client
- `get_sts(session_name: str, role_arn: str) -> AliyunStsToken`: Get STS token

### Schemas

#### `AliyunOssPutObjectResponse`
- `status: int`: Response status
- `request_id: str`: Request ID
- `etag: str`: ETag
- `headers: dict`: Response headers

#### `AliyunStsToken`
- `access_key_secret: str`: Access key secret
- `security_token: str`: Security token
- `access_key_id: str`: Access key ID

#### `AliyunOssMeta`
- `etag: Optional[str]`: OSS ETag
- `content_length: Optional[int]`: File size in bytes
- `last_modified: Optional[int]`: Last modified timestamp
- `content_type: Optional[str]`: MIME type of the file

### Usage Examples

```python
# Initialize Aliyun OSS
oss_client = AliyunOss(
    oss_endpoint="https://oss-cn-beijing.aliyuncs.com",
    bucket="your-bucket-name",
    access_key="your-access-key-id",
    secret="your-access-key-secret"
)

# Upload file to OSS
response = oss_client.save_local_to_cloud(
    key="path/in/oss/file.txt",
    local_path="/local/path/to/file.txt"
)

# Get file metadata
meta = oss_client.get_object_meta("path/in/oss/file.txt")

# Download file from OSS
oss_client.save_object_to_local(
    key="path/in/oss/file.txt",
    local_path="/local/path/to/download.txt"
)

# Get STS token
sts_client = AliyunSts(
    region="cn-beijing",
    access_key="your-access-key-id", 
    secret="your-access-key-secret"
)
sts_token = sts_client.get_sts(
    session_name="session-name",
    role_arn="acs:ram::your-account-id:role/your-role-name"
)

# Generate signed URL with STS token
signed_url = oss_client.get_sts_signed_url(
    sts_token=sts_token.security_token,
    key="path/in/oss/file.txt",
    expire_seconds=3600
)
```

## Progress

The Progress module provides a Redis-based task tracking system to monitor the progress of multi-stage operations.

### Base Classes

#### `ProgressHandler`
- `__init__(redis: Redis)`: Initialize with Redis connection
- `new(*, key: str, model_key: str | None = None) -> ProgressTask`: Create a new progress task
- `get(*, key: str) -> ProgressReport | None`: Retrieve progress report by key

#### `ProgressTask`
- `__init__(redis: Optional[Redis] = None, key: Optional[str] = None, model_key: Optional[str] = None, root: Optional["ProgressTask"] = None)`: Initialize a progress task
- `new_subtask() -> ProgressTask`: Create a subtask under this task
- `success()`: Mark task as successful
- `failure(error: Optional[str] = None)`: Mark task as failed
- `set_message(message: Optional[str])`: Set a message for the task
- `get_from_redis(redis: Redis, *, key: str) -> Optional["ProgressTask"]`: Class method to retrieve a task from Redis
- `get_prebuilt_subtasks_model(root: "ProgressTask", redis: Redis, *, model_key: str) -> List["ProgressTask"]`: Class method to get prebuilt subtasks

### Schemas

#### `ProgressTaskStage`
Enum with the following values:
- `PENDING`: Task is in progress
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed

#### `ProgressReport`
- `progress_key: Optional[str]`: Key used to store progress in Redis
- `progress: float`: Completion percentage (0.0 to 1.0)
- `is_root_success: bool`: Whether the root task is successful
- `success: int`: Number of successful tasks
- `failure: int`: Number of failed tasks
- `pending: int`: Number of pending tasks
- `assigned: int`: Number of assigned tasks
- `total: int`: Total number of tasks
- `message: Optional[str]`: Optional message
- `errors: List[str]`: List of error messages

### Usage Examples

```python
import uuid
from redis import Redis
from keble_helpers import ProgressHandler

# Initialize Redis connection
redis = Redis(host='localhost', port=6379, db=0)

# Create a progress handler
handler = ProgressHandler(redis=redis)

# Create a new progress task
task_key = str(uuid.uuid4())
task = handler.new(key=task_key)

# Create subtasks
subtask1 = task.new_subtask()
subtask2 = task.new_subtask()
subtask3 = task.new_subtask()

# Mark tasks as complete or failed
subtask1.success()
subtask2.failure(error="Something went wrong")
subtask3.success()
task.success()

# Get progress report
report = handler.get(key=task_key)
print(f"Progress: {report.progress * 100}%")
print(f"Success: {report.success}, Failure: {report.failure}, Pending: {report.pending}")

# Using model_key for prebuilt subtasks
model_key = str(uuid.uuid4())
root_task = handler.new(key=str(uuid.uuid4()), model_key=model_key)

# When you create a new task with the same model_key,
# it will have the same number of subtasks
new_task = handler.new(key=str(uuid.uuid4()), model_key=model_key)
```

## Pydantic

The Pydantic module provides helpers and utilities for working with Pydantic models.

### Functions

- `is_http_url(url: Any) -> bool`: Validates if a string is a valid HTTP or HTTPS URL

### Base Classes

#### `PydanticModelConfig`
- `default_dict(**kwargs) -> dict`: Returns a dictionary with default configuration
- `default(**kwargs) -> ConfigDict`: Returns a ConfigDict with default configuration

#### `CloudStorageBase`
- Base model for cloud storage objects with standardized fields

### Enums

#### `CloudStorageType`
- `AWS_S3`: Amazon S3 storage
- `ALIYUN_OSS`: Alibaba Cloud OSS storage

#### `CloudStorageObjectType`
- `IMAGE`: Image files
- `VIDEO`: Video files
- `EXCEL`: Excel spreadsheets
- `CSV`: CSV files
- `OTHER`: Other file types
- `determine_type(*, mime: str) -> CloudStorageObjectType`: Determine type from MIME

### Usage Examples

```python
from keble_helpers.pydantic import CloudStorageBase, CloudStorageObjectType, CloudStorageType
from keble_helpers.pydantic.schemas import is_http_url
from pydantic import BaseModel

# Check if a URL is valid HTTP/HTTPS
valid = is_http_url("https://example.com")  # True
valid = is_http_url("ftp://example.com")    # False

# Create a custom model with Pydantic configuration
class MyModel(BaseModel):
    model_config = PydanticModelConfig.default()
    # Fields go here

# Create a cloud storage object
storage = CloudStorageBase(
    key="path/to/file.jpg",
    base_url="https://example.com/storage",
    type=CloudStorageType.AWS_S3,
    object_type=CloudStorageObjectType.IMAGE,
    original_file_name="photo.jpg"
)

# Determine object type from MIME
object_type = CloudStorageObjectType.determine_type(mime="image/jpeg")
```

## Common

The Common module provides general utility functions for common tasks.

### Functions

#### String and ID Utilities
- `id_generator() -> str`: Generate a UUID4 string
- `generate_random_string(length: int = 32, *, lower: bool = True, upper: bool = True, digit: bool = True) -> str`: Generate a random string
- `hash_string(arg: str) -> str`: Generate MD5 hash of a string
- `inline_string(string: str, max_len: int = 30)`: Format a string for inline display

#### Pydantic Helpers
- `is_pydantic_field_empty(obj: BaseModel, field: str) -> bool`: Check if a field is empty in a Pydantic model

#### Date and Time
- `date_to_datetime(d: date) -> datetime`: Convert a date to datetime
- `datetime_to_date(d: datetime) -> date`: Convert a datetime to date

#### List and Collection Operations
- `slice_to_list(items: List[Any], slice_size: int) -> List[List[Any]]`: Split a list into chunks
- `get_first_match(items: list, key_fn, value)`: Find first item in a list matching a criterion

#### File System Operations
- `ensure_has_folder(path: str) -> str`: Create a directory if it doesn't exist
- `yield_files(folder: str) -> Iterator[str | Path]`: Recursively yield files in a directory
- `get_files(folder: str) -> List[str | Path]`: Get a list of all files in a directory
- `zip_dir(folder: Path | str, zip_filepath: Path | str)`: Zip a directory
- `remove_dir(dir: Path | str)`: Remove a directory

#### MIME Type Checking
- `is_mime_prefix_in(mime, mime_start: List[str])`: Check if a MIME type has a specific prefix
- `is_mime_image(mime: str)`: Check if a MIME type is an image
- `is_mime_video(mime: str)`: Check if a MIME type is a video
- `is_mime_audio(mime: str)`: Check if a MIME type is audio
- `is_mime_media(mime: str)`: Check if a MIME type is any media (image, video, audio)
- `is_mime_ms_excel(mime: str)`: Check if a MIME type is MS Excel
- `is_mime_csv(mime: str)`: Check if a MIME type is CSV

### Usage Examples

```python
from keble_helpers.common import (
    id_generator, hash_string, ensure_has_folder, get_files, 
    is_mime_image, slice_to_list
)

# Generate a unique ID
unique_id = id_generator()

# Generate a hash of a string
file_hash = hash_string("content to hash")

# Ensure a directory exists
path = ensure_has_folder("/path/to/directory")

# Get all files in a directory
files = get_files("/path/to/directory")

# Check if a MIME type is an image
is_image = is_mime_image("image/jpeg")  # True

# Split a list into chunks of size 3
chunks = slice_to_list([1, 2, 3, 4, 5, 6, 7], 3)  # [[1, 2, 3], [4, 5, 6], [7]]
```

## DateTime

The DateTime module provides utilities for working with dates and times.

### Functions

- `days_in_month(year, month)`: Get the number of days in a specific month

### Usage Examples

```python
from keble_helpers.datetime import days_in_month

# Get days in February 2024 (leap year)
days = days_in_month(2024, 2)  # 29

# Get days in February 2023 (non-leap year)
days = days_in_month(2023, 2)  # 28
```

## Enum

The Enum module provides predefined enumerations.

### Enums

#### `Environment`
- `development`: Development environment
- `test`: Test environment
- `production`: Production environment

### Usage Examples

```python
from keble_helpers.enum import Environment

# Use environment enum
current_env = Environment.development

# Check environment
if current_env == Environment.production:
    # Production-specific code
    pass
```

## FastAPI

The FastAPI module provides helpers for working with FastAPI applications, focusing on JSON encoding compatible with Pydantic v2.

### Functions

- `jsonable_encoder(obj: Any, include: Optional[IncEx] = None, exclude: Optional[IncEx] = None, by_alias: bool = True, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, custom_encoder: Optional[Dict[Any, Callable[[Any], Any]]] = None, sqlalchemy_safe: bool = True) -> Any`: Convert a Python object to a JSON-compatible object

### Constants

- `PYDANTIC_V2`: Boolean indicating if Pydantic v2 is in use
- `ENCODERS_BY_TYPE`: Dictionary mapping Python types to encoder functions

### Usage Examples

```python
from keble_helpers.fastapi import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime | None = None

user = User(id=1, name="John Doe", created_at=datetime.now())

# Convert to JSON-compatible dict
json_data = jsonable_encoder(user)

# Convert excluding some fields
json_data = jsonable_encoder(user, exclude={"created_at"})

# Convert with custom encoders
json_data = jsonable_encoder(
    user, 
    custom_encoder={datetime: lambda dt: dt.strftime("%Y-%m-%d")}
)
```

## File

The File module provides utilities for file operations, particularly for downloading files.

### Functions

- `adownload_file(*, url: str, folder: Path, filename: str) -> Path`: Asynchronously download a file from a URL

### Usage Examples

```python
import asyncio
from pathlib import Path
from keble_helpers.file import adownload_file

async def download_example():
    # Download a file
    file_path = await adownload_file(
        url="https://example.com/file.pdf",
        folder=Path("/path/to/downloads"),
        filename="document.pdf"
    )
    
    print(f"Downloaded to: {file_path}")

# Run the async function
asyncio.run(download_example())
```

## Multithread (Deprecated)

> **Note**: This module is deprecated. The project now uses async-based approaches instead of multithreading.

The Multithread module provides utilities for thread management and parallel execution.

### Classes

#### `ThreadController`
- `__init__(thread_size: int)`: Initialize with a maximum number of threads
- `create_thread(target: Callable, *, args: Optional[tuple] = None, kwargs: Optional[Dict[str, Any]] = None, thread_owner: Optional[str | int] = None, disable_sema: Optional[bool] = False, join: Optional[bool] = False)`: Create and start a new thread
- `acquire(*, thread_owner: Optional[str | int] = None)`: Acquire a semaphore
- `release(*, thread_owner: Optional[str | int] = None)`: Release a semaphore
- `wait_all_to_finish()`: Wait for all threads to complete
- `wait_owner_to_finish(thread_owner: str | int)`: Wait for all threads by a specific owner to complete

### Decorators

- `threaded(*, sema: Optional[Semaphore] = None, join: Optional[bool] = False)`: Decorator to run a function in a separate thread

### Usage Examples

```python
from keble_helpers import ThreadController, threaded
from threading import Semaphore

# Using ThreadController
controller = ThreadController(thread_size=5)

def task(results):
    # Perform task
    results.append("Task completed")
    controller.release()

results = []
for _ in range(10):
    controller.create_thread(target=task, args=(results,))

controller.wait_all_to_finish()

# Using threaded decorator
sema = Semaphore(3)

@threaded(sema=sema)
def background_task(results):
    results.append("Background task completed")
    sema.release()

threads = []
results = []
for _ in range(5):
    threads.append(background_task(results))

for thread in threads:
    thread.join()
```

## NumPy Utils

The NumPy Utils module provides helper functions for working with NumPy arrays and handling numerical values.

### Functions

- `is_invalid_float(value: Optional[float]) -> bool`: Check if a float value is NaN or infinity
- `guard_invalid_float(value: float | None | np.floating) -> float | None`: Replace invalid float values (NaN, inf) with None

### Usage Examples

```python
import numpy as np
from keble_helpers.np_utils import is_invalid_float, guard_invalid_float

# Check if a value is an invalid float
invalid = is_invalid_float(float('nan'))  # True
invalid = is_invalid_float(float('inf'))  # True
invalid = is_invalid_float(42.0)  # False

# Guard against invalid floats
safe_value = guard_invalid_float(np.nan)  # None
safe_value = guard_invalid_float(np.inf)  # None
safe_value = guard_invalid_float(42.0)  # 42.0
safe_value = guard_invalid_float(np.float32(3.14))  # 3.14
```