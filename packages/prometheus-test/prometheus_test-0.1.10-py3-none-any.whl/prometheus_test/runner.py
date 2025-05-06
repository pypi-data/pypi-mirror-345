from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypedDict
import json
from pymongo import MongoClient
from .workers import TestEnvironment
import yaml
import os


class MongoCollectionConfig(TypedDict, total=False):
    data_file: str  # Optional, not all collections need data files
    required_count: int


class MongoConfig(TypedDict, total=False):
    database: str
    collections: Dict[str, MongoCollectionConfig]


@dataclass
class TestConfig:
    """Configuration for the test runner"""

    # Core configuration with defaults
    base_dir: Path = Path.cwd()
    data_dir: Optional[Path] = None
    workers_config: str = "workers.json"
    task_id: str = "test-task-123"
    base_port: int = 5000
    middle_server_url: Optional[str] = None
    server_entrypoint: Optional[Path] = None
    max_rounds: Optional[int] = (
        None  # Will be calculated from collection if not specified
    )
    rounds_collection: Optional[str] = (
        "todos"  # Collection to use for calculating max_rounds
    )
    post_load_callback: Optional[Callable[[Any], None]] = (
        None  # Callback for post-JSON data processing
    )

    # Default MongoDB configuration
    mongodb: MongoConfig = field(
        default_factory=lambda: {
            "database": "builder247",
            "collections": {},  # No default collections, use only what's in config.yaml
        }
    )

    # Store arbitrary config values
    _extra_config: Dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        """Allow access to arbitrary config values"""
        if name in self._extra_config:
            return self._extra_config[name]
        raise AttributeError(f"'TestConfig' object has no attribute '{name}'")

    @classmethod
    def from_yaml(
        cls, yaml_path: Path, base_dir: Optional[Path] = None
    ) -> "TestConfig":
        """Create TestConfig from a YAML file"""
        # Load YAML config
        with open(yaml_path) as f:
            config = yaml.safe_load(f) or {}

        # Use base_dir from argument or yaml_path's parent
        base_dir = base_dir or yaml_path.parent
        config["base_dir"] = base_dir

        # Convert relative paths to absolute
        if "data_dir" in config and not config["data_dir"].startswith("/"):
            config["data_dir"] = base_dir / config["data_dir"]
        if "server_entrypoint" in config and not config["server_entrypoint"].startswith(
            "/"
        ):
            config["server_entrypoint"] = base_dir.parent / config["server_entrypoint"]

        # Merge MongoDB config with defaults
        if "mongodb" in config:
            default_mongodb = cls().mongodb
            mongodb_config = config["mongodb"]

            # Use default database if not specified
            if "database" not in mongodb_config:
                mongodb_config["database"] = default_mongodb["database"]

            # Merge collection configs with defaults
            if "collections" in mongodb_config:
                for coll_name, default_coll in default_mongodb["collections"].items():
                    if coll_name not in mongodb_config["collections"]:
                        mongodb_config["collections"][coll_name] = default_coll
                    else:
                        # Merge with default collection config
                        mongodb_config["collections"][coll_name] = {
                            **default_coll,
                            **mongodb_config["collections"][coll_name],
                        }

        # Separate known fields from extra config
        known_fields = {}
        extra_fields = {}

        for k, v in config.items():
            if k in cls.__dataclass_fields__:
                known_fields[k] = v
            else:
                extra_fields[k] = v

        # Create instance with known fields
        instance = cls(**known_fields)

        # Store extra fields
        instance._extra_config = extra_fields

        return instance

    def __post_init__(self):
        # Convert string paths to Path objects
        self.base_dir = Path(self.base_dir)
        if self.data_dir:
            self.data_dir = Path(self.data_dir)
        else:
            self.data_dir = self.base_dir / "data"

        if self.server_entrypoint:
            self.server_entrypoint = Path(self.server_entrypoint)


@dataclass
class TestStep:
    """Represents a single step in a task test sequence"""

    name: str
    description: str
    worker: str
    prepare: Callable[[], Dict[str, Any]]  # Returns data needed for the step
    execute: Callable[Dict[str, Any], Any]  # Takes prepared data and executes step
    validate: Optional[Callable[[Any, Any], None]] = (
        None  # Optional validation function
    )


class TestRunner:
    """Main test runner that executes a sequence of test steps"""

    def __init__(
        self,
        steps: List[TestStep],
        config_file: Optional[Path] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ):
        """Initialize test runner with steps and optional config"""
        self.steps = steps
        self._config_file = config_file
        self._config_overrides = config_overrides

        # These will be initialized when needed
        self._test_env = None
        self._mongo_client = None
        self._max_rounds = None
        self.state = None

    def clear_data(self):
        """Clear all existing data - databases and state"""
        print("\nClearing existing data...")

        # Initialize MongoDB client and clear collections
        db = self.mongo_client[self._config.mongodb["database"]]
        for collection in self._config.mongodb["collections"]:
            print(f"Clearing collection: {collection}")
            db[collection].delete_many({})

        # Delete all SQLite database files in data_dir
        print("\nClearing database files...")
        if self.data_dir.exists():
            for db_file in self.data_dir.glob("*.db"):
                print(f"Deleting database file: {db_file}")
                db_file.unlink()

        # Initialize empty state
        self.state = {
            "rounds": {},
            "global": {},
            "current_round": 1,
            "last_completed_step": None,
        }

    def load_data(self):
        """Initialize state with config values and load any external data"""

        # Store config values in global state (except callables)
        for f in self._config.__dataclass_fields__:
            if f == "_extra_config":  # Skip the internal extra config field
                continue
            value = getattr(self._config, f)
            # Skip storing callables in state, but don't skip the field entirely
            if callable(value):
                self.state["global"][f] = None
                continue
            # Convert Path objects to strings for JSON serialization
            if isinstance(value, Path):
                value = str(value)
            self.state["global"][f] = value
            if f == "base_dir":
                print(f"Stored base_dir in state: {value}")

        # Store extra config values
        for k, v in self._config._extra_config.items():
            self.state["global"][k] = v

        # Load and store worker config
        workers_config = Path(self._config.workers_config)
        if not workers_config.is_absolute():
            workers_config = self._config.base_dir / workers_config

        with open(workers_config) as f:
            config = json.load(f)
            self.state["global"]["workers"] = config

        # Import MongoDB data
        print("\nImporting MongoDB data...")
        db = self.mongo_client[self._config.mongodb["database"]]
        for coll_name, coll_config in self._config.mongodb["collections"].items():
            if "data_file" not in coll_config:
                continue

            data_file = self.data_dir / coll_config["data_file"]
            if not data_file.exists():
                if coll_config.get("required_count", 0) > 0:
                    raise FileNotFoundError(
                        f"Required data file not found: {data_file}"
                    )
                continue

            print(f"Importing data for {coll_name} from {data_file}")
            with open(data_file) as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]

                # Add task_id to all documents
                for item in data:
                    item["taskId"] = self._config.task_id

                # Insert data into collection
                db[coll_name].insert_many(data)

        # Run post-load callback if provided
        if self._config.post_load_callback:
            print("\nRunning post-load data processing...")
            self._config.post_load_callback(db)

        # Save state
        self.save_state()

    def _init_config(self):
        """Initialize config from YAML file"""
        if not hasattr(self, "_config"):
            # Create base config from YAML or defaults
            self._config = (
                TestConfig.from_yaml(self._config_file)
                if self._config_file
                else TestConfig()
            )

            # Apply any config overrides directly to the config object
            if self._config_overrides:
                for key, value in self._config_overrides.items():
                    if hasattr(self._config, key):
                        setattr(self._config, key, value)

    @property
    def data_dir(self) -> Path:
        """Get the data directory path from config or state"""
        # Initialize config if needed
        if not hasattr(self, "_config"):
            self._init_config()

        # Try to get from state first
        if self.state is not None:
            data_dir = self.get("data_dir")
            if data_dir is not None:
                return Path(data_dir)

        # Fall back to config
        return self._config.data_dir

    @property
    def mongo_client(self) -> MongoClient:
        """Get MongoDB client, initializing if needed"""
        if self._mongo_client is None:
            # Get MongoDB URI from environment variable
            mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            self._mongo_client = MongoClient(mongodb_uri)
        return self._mongo_client

    @property
    def max_rounds(self) -> int:
        """Get maximum number of rounds, calculating from the specified collection if not set explicitly"""
        if self._max_rounds is None:
            if self._config.max_rounds is not None:
                self._max_rounds = self._config.max_rounds
            else:
                # Count documents in the specified collection and add 1
                if not self._config.rounds_collection:
                    raise ValueError(
                        "No collection specified for calculating max_rounds"
                    )

                db = self.mongo_client[self._config.mongodb["database"]]
                if self._config.rounds_collection not in db.list_collection_names():
                    raise ValueError(
                        f"Collection {self._config.rounds_collection} does not exist"
                    )

                self._max_rounds = (
                    db[self._config.rounds_collection].count_documents(
                        {"taskId": self._config.task_id}
                    )
                    + 1
                )
                print(
                    f"\nCalculated {self._max_rounds} rounds from {self._config.rounds_collection} collection"
                )
        return self._max_rounds

    @property
    def test_env(self) -> TestEnvironment:
        """Get the test environment, initializing if needed"""
        if self._test_env is None:
            if self.state is None:
                raise RuntimeError(
                    "Cannot initialize test environment - state not loaded"
                )

            # Initialize test environment
            base_dir = self.get("base_dir")
            if base_dir is None:
                raise RuntimeError(
                    "Cannot initialize test environment - base_dir not set"
                )

            self._test_env = TestEnvironment(
                worker_configs=self.get("workers"),
                base_dir=Path(base_dir),
                base_port=self.get("base_port"),
                data_dir=self.data_dir,  # Pass data_dir to TestEnvironment
            )
        return self._test_env

    def get_worker(self, name: str):
        """Get a worker by name"""
        return self.test_env.get_worker(name)

    def save_state(self):
        """Save current test state to file"""
        state_file = self.data_dir / "test_state.json"
        with open(state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_state(self):
        """Load test state from file if it exists"""
        state_file = self.data_dir / "test_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                self.state = json.load(f)
            return True
        return False

    def log_step(self, step: TestStep):
        """Log test step execution"""
        print("\n" + "#" * 80)
        print(f"STEP {step.name}: {step.description}")
        print("#" * 80)

    def next_round(self):
        """Move to next round"""
        self.set("current_round", self.state["current_round"] + 1, scope="execution")
        self.set("last_completed_step", None, scope="execution")

    def get_round_state(self):
        """Get the state for the current round"""
        return self.state["rounds"].get(str(self.state["current_round"]), {})

    def get(self, key: str) -> Optional[Any]:
        """
        Unified data access method. Automatically checks all data stores in priority order:
        1. Execution state (current_round, last_completed_step)
        2. Current round state
        3. Global state

        Args:
            key: The key to look up. Can use dot notation for nested access.

        Returns:
            The value if found, None if the key doesn't exist at any level or if the value is None
        """
        # Support nested key access with dot notation
        parts = key.split(".")

        # Check execution state first
        if key in ["current_round", "last_completed_step"]:
            return self.state.get(key)

        # For simple keys, check each state level directly
        if len(parts) == 1:
            # Check current round state first
            round_state = self.get_round_state()
            if key in round_state:
                return round_state[key]
            # Then check global state
            return self.state["global"].get(key)

        # For nested keys, traverse the state
        # Check current round state
        round_state = self.get_round_state()
        try:
            value = round_state
            for part in parts:
                if not isinstance(value, dict):
                    return None
                if part not in value:
                    return None
                value = value[part]
            return value
        except (TypeError, AttributeError):
            pass

        # Check global state
        try:
            value = self.state["global"]
            for part in parts:
                if not isinstance(value, dict):
                    return None
                if part not in value:
                    return None
                value = value[part]
            return value
        except (TypeError, AttributeError):
            pass

        return None

    def set(self, key: str, value: Any, scope: str = "round") -> None:
        """
        Unified data setter. Stores data in the appropriate location based on scope.
        Automatically creates any necessary nested dictionary structures.

        Args:
            key: The key to store. Can use dot notation for nested access (e.g. "pr_urls.worker1")
            value: The value to store
            scope: Where to store the data. Options:
                - "round": Store in current round state (default)
                - "global": Store in global state
                - "execution": Store in execution state (only for specific variables)
        """
        # Handle nested keys with dot notation
        parts = key.split(".")

        if scope == "round":
            # Ensure round state exists
            round_key = str(self.state["current_round"])
            if round_key not in self.state["rounds"]:
                self.state["rounds"][round_key] = {}

            # Navigate to the correct nested location
            current = self.state["rounds"][round_key]
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value

        elif scope == "global":
            # Navigate to the correct nested location
            current = self.state["global"]
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = value

        elif scope == "execution":
            if key in ["current_round", "last_completed_step"]:
                self.state[key] = value
            else:
                raise ValueError(f"Cannot set execution variable: {key}")
        else:
            raise ValueError(f"Invalid scope: {scope}")

        # Save state after any modification
        self.save_state()

    def run(self, force_reset=False):
        """Run the test sequence."""
        # Always initialize config first
        self._init_config()
        state_file = self.data_dir / "test_state.json"

        # Either load existing state or create fresh state
        if force_reset or not state_file.exists():
            print("\nStarting fresh test run...")
            self.clear_data()  # Initialize empty state
            self.load_data()  # Populate state with config values and load external data
        else:
            print("\nLoading existing state...")
            if not self.load_state():
                raise RuntimeError("Failed to load existing state")
            print(
                f"Resuming from step {self.state['last_completed_step']} in round {self.state['current_round']}..."
            )

        try:
            # Set up test environment
            with self.test_env:
                while self.state["current_round"] <= self.max_rounds:
                    round_steps = [s for s in self.steps]

                    # Find the index to start from based on last completed step
                    start_index = 0
                    last_step = self.state["last_completed_step"]
                    if last_step:
                        for i, step in enumerate(round_steps):
                            if step.name == last_step:
                                start_index = i + 1
                                break

                    # Skip already completed steps
                    for step in round_steps[start_index:]:
                        self.log_step(step)

                        worker = self.get_worker(step.worker)
                        # Prepare step data
                        data = step.prepare(self, worker)

                        # Execute step
                        result = step.execute(self, worker, data)

                        # Check for errors
                        if not result.get("success"):
                            error_msg = result.get("error", "Unknown error")
                            raise RuntimeError(f"Step {step.name} failed: {error_msg}")

                        # Save state after successful step
                        self.state["last_completed_step"] = step.name
                        self.save_state()

                    # Move to next round after completing all steps
                    if self.state["current_round"] < self.max_rounds:
                        self.next_round()
                    else:
                        print("\nAll rounds completed successfully!")
                        break

        except Exception as e:
            print(f"\nTest run failed: {str(e)}")
            raise
        finally:
            # Ensure we always clean up, even if there's an error
            if hasattr(self, "_test_env") and self._test_env:
                print("\nCleaning up test environment...")
                self._test_env._cleanup()

        print("\nTest run completed.")
