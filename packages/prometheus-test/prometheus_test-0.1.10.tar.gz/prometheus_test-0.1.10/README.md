# Prometheus Test Framework Usage Guide

## Getting Started

### Installation

```bash
pip install prometheus_test
```

### Basic Structure

A test implementation consists of three main components:

1. Configuration Files
2. Test Steps Definition
3. Test Runner Script

## Creating a Test

### 1. Configuration

#### Directory Structure

Below is the recommended file structure for creating your test. See the `example` folder for sample file contents.

```
orca-container
  ├── .env
  ├──src/
  ├──tests/
    ├── .env
    ├── data/
    │    ├── collection1.json
    │    └── collection2.json
    ├── config.yaml
    ├── workers.json
    ├── e2e.py
    ├── steps.py
    └── stages/
      ├── task.py
      ├── submission.py
      └── audit.py
```

#### Test Configuration (config.yaml)

```yaml
# Test Configuration
task_id: "your_task_id" # Task identifier, should match the middle server
base_port: 5000 # Base port for worker servers, optional
max_rounds: 3 # Maximum test rounds, optional.
rounds_collection: "documentations" # By default number of rounds the task will run for equals the number of documents in this collection

# Paths
data_dir: data # Test data directory, optional. defaults to the /data dir within your tests folder
workers_config: workers.json # Worker configuration, relative to tests directory, optional. defaults to workers.json in your tests folder

# MongoDB Configuration (if needed)
mongodb:
  database: your_database_name
  collections:
    tasks: # collection name
      data_file: tasks.json # file containing data for this collection, relative to the data_dir you specified
      required_count: 1 # minimum number of documents the collection must have
    audits:
      required_count: 0 # No data file, just needs to exist
```

#### Worker Configuration (workers.json)

```json
{
  "worker1": {
    "port": 5001, // optional, will be automatically determined if not specified
    "server_entrypoint": "/path/to/entrypoint.py" // The file used to start your server. Defaults to container_folder/main.py. Either an absolute path or relative to container_folder

    // this maps the env variable used by the server to the actual env variable defined in your .env file
    // for example, if every worker needs its own github token, the server variable will be just `GITHUB_TOKEN`
    // but we need to differentiate which token belongs to which worker, so we map the server variable to the specific worker variable
    "env_vars": {
      "GITHUB_TOKEN": "WORKER1_GITHUB_TOKEN",
      "GITHUB_USERNAME": "WORKER1_GITHUB_USERNAME"
    },

    // Workers need keypairs to simulate the signatures generated in the node
    // Depending on your task, you may need only one of these two. By default, namespaceWrapper.payloadSigning uses the public key.
    // These do not need to be real staking and public keypairs from the node as they're only used for signing; any valid wallets will do
    // Specify the keypair paths in your .env file using the variable names you specify here.
    "keypairs": {
      "staking": "WORKER1_STAKING_KEYPAIR",
      "main": "WORKER1_PUBLIC_KEYPAIR"
    }
  },
  "worker2": {
    "port": 5002,
    "env": {
      "WORKER_ID": "worker2"
    }
  }
      "keypairs": {
      "staking": "WORKER2_STAKING_KEYPAIR",
      "main": "WORKER2_PUBLIC_KEYPAIR"
    }
}
```

### 2. Defining Test Steps

#### Defining Step Sequence

Orca tasks are fundamentally a series of API calls, either to the middle server or to your Orca container. In order to simulate the running of a task, we have the test runner execute a series of steps each round, with each step corresponding to an API call.

Create a `steps.py` file to define your test sequence:

```python
from prometheus_test import TestStep
from stages.step_name import your_prepare_function, your_execute_function

steps = [
    TestStep(
        name="step_name",                    # Unique step identifier
        description="Step description",       # Human-readable description
        prepare=your_prepare_function,        # Setup function
        execute=your_execute_function,        # Main execution function
        worker="worker_name",                # Worker that executes this step. Matches the worker names defined in workers.json
    ),
    # Add more steps...
]
```

If you need to add extra parameters when calling prepare or execute functions you can `partial` from `functools`

```py
from functools import partial

...
    TestStep(
        name="step_name",
        description="Step description",
        prepare=your_prepare_function,
        execute=partial(your_execute_function, extra_parameter=value),
        worker="worker_name",
    ),
...

```

#### Create Steps

As each step corresponds to an API call, most of which are POST requests with a payload, each step has two stages: preparing the data to send, and making the call.

Each function will have access to the test runner as well as the specific worker executing the step.

These two steps are by convention named `prepare` and `execute`.

Runner variables can be set and accessed using runner.set("name", "value") and runner.get("name"). The set function additionally has an optional scope parameter that can be set to "global" (values that will not change throughout the test) and "round" (values that change from round to round). As most data you will store in the runner will be round-specific, the default scope is "round".

Worker variables cannot be set at runtime, but anything you define in workers.json will be available via get_env("ENV_VAR_NAME"), get_key() (options are "staking_public", "staking_signing", "main_public", and "main_signing"), and get() for all other variables.

1. Prepare Function:

```python
from prometheus_test.utils import create_signature

def prepare(runner, worker):
    """Setup before step execution"""
    # Any configuration values set in config.yaml will be available on the runner
    #
    task_id = runner.get("task_id")
    twitter_username = worker.get("twitter_id")
    twitter_password = worker.get_env("TWITTER_PASSWORD")

    payload = {
      "some_data": "I want to sign this"
    }

    # Setup prerequisites
    return {
        "task_id": task_id,
        "twitter_username": twitter_username
        "twitter_password": twitter_password
        # the create_signature utility function will generate signatures that match
        # the output of namespaceWrapper.payloadSigning
        # https://www.koii.network/docs/develop/write-a-koii-task/namespace-wrapper/wallet-signatures
        "signature": create_signature(worker.get_key("main_signing"), payload)
    }
```

2. Execute Function:

```python
def execute(runner, worker, data):
    """Execute the test step"""
    response = requests.post(f"{worker.get('url')}/endpoint", json=data)
    result = response.json()

    # Sometimes you'll have steps that don't always run, add skip conditions to keep the test running

      if response.status_code == 409:
          print("Skipping step")
          return
      elif not result.get("success"):
          raise Exception(
              f"Failed to execute step: {result.get('message')}"
          )
      # you can use dot notation to store and retrieve nested values
      runner.set(f"post_urls.{worker.get('name')}", result["post_url"])
```

### 3. Test Runner Script

Create a main test script (e.g., `e2e.py`) that sets up and runs your test sequence:

```python
from pathlib import Path
from prometheus_test import TestRunner
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Import your test steps
from .steps import steps

def main():
    # Create test runner with config from YAML
    base_dir = Path(__file__).parent
    runner = TestRunner(
        steps=steps,
        config_file=base_dir / "config.yaml",
        config_overrides={
            "post_load_callback": your_callback_function  # Optional
        }
    )

    # Run test sequence
    runner.run(force_reset=False)

if __name__ == "__main__":
    main()
```

This is mostly boilerplate and can usually be used as-is.

### 4. Post Load Callback

If you're loading data from JSON files into MongoDB, you may need to do additional post processing (e.g. adding UUIDs or a task ID). You can define a post load callback in `e2e.py` which will be automatically executed after the MongoDB collections have been populated.

```python
def post_load_callback(db):
    """Modify database after initial load"""
    for doc in db.collection.find():
        # Modify documents as needed
        db.collection.update_one({"_id": doc["_id"]}, {"$set": {"field": "value"}})
```

### 5. ENV Variables

If you have an .env file in your agent's top level folder (for API keys, etc), those environment variables will be automatically loaded into your test script. If you want to add testing specific ENV variables or you need to override any values from you main .env, you can add a second .env in your tests/ directory, which will also be automatically loaded and overrides will be applied.

## Running Tests

Execute your test script:

```bash
cd <container_folder>
python -m tests.e2e [--reset]
```

Options:

- `--reset`: Force reset of all databases before running tests. Deleting the state file (data_dir/test_state.json) will also force a reset.

## Resuming a Previous Test

Test state is saved in data_dir/test_state.json. If you run the test without the `--reset` flag, this state file will be used to resume your progress. You can also manually edit the file to alter the point at which you resume, but do note you may have to also edit the local SQLite DB and/or the remote MongoDB instance (if using) in order to keep the state in sync.

## TODO

- automatically generate wallets for signing
- More information about MongoDB setup
