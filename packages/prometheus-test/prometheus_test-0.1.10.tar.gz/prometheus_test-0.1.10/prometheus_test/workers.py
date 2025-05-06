import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import threading
from .utils import load_keypair

load_dotenv()


class Worker:
    """Represents a worker in the test environment"""

    def __init__(
        self,
        name: str,
        base_dir: Path,
        default_port: int,
        config: Dict[str, Any],
        data_dir: Optional[Path] = None,
    ):
        # Initialize process attribute
        self.process = None

        # Keep env_vars and keypairs as properties
        self.env_vars = config.get("env_vars", {})
        self.keypairs = config.get("keypairs", {})

        # Initialize data storage with defaults
        self._data = {
            "name": name,
            "base_dir": str(base_dir),
            "port": default_port,
            "url": f"http://localhost:{default_port}",
            "database_path": str(data_dir / f"database_{name}.db"),
            "server_entrypoint": str(base_dir.parent / "main.py"),
        }

        # Add all config fields except env_vars and keypairs
        self._data.update(
            {k: v for k, v in config.items() if k not in ["env_vars", "keypairs"]}
        )

        server_path = Path(self.get("server_entrypoint"))
        if not server_path.is_absolute():
            server_path = Path(self.get("base_dir")).parent / server_path
        if not server_path.exists():
            raise ValueError(f"Server entrypoint not found at {server_path}")

        # Load environment variables
        base_env = Path(self.get("base_dir")) / ".env"
        if base_env.exists():
            load_dotenv(base_env, override=True)

        # Validate environment variables
        missing_env_vars = []
        for key, value in self.env_vars.items():
            # Skip DATA_DIR as it's handled specially
            if key == "DATA_DIR":
                continue
            # If value doesn't exist as an env var, it's missing
            if not os.getenv(value):
                missing_env_vars.append(f"{key} ({value})")
        if missing_env_vars:
            raise ValueError(
                f"Missing required environment variables for {name}: {', '.join(missing_env_vars)}"
            )

        # Load and validate keypairs
        staking_keypair_env = self.keypairs.get("staking")
        main_keypair_env = self.keypairs.get("main")

        # Initialize keypair attributes as None
        self.staking_signing_key = None
        self.staking_public_key = None
        self.main_signing_key = None
        self.main_public_key = None

        # Ensure at least one keypair is loaded if any were configured
        if not staking_keypair_env and not main_keypair_env:
            raise ValueError("At least one keypair must be provided")

        # Load staking keypair if configured
        if staking_keypair_env:
            staking_keypair_path = os.getenv(staking_keypair_env)
            if not staking_keypair_path:
                raise ValueError(
                    f"Missing staking keypair path - env var {staking_keypair_env} not set"
                )
            if not Path(staking_keypair_path).exists():
                raise ValueError(
                    f"Staking keypair file not found at {staking_keypair_path}"
                )
            try:
                self.staking_signing_key, self.staking_public_key = load_keypair(
                    staking_keypair_path
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to load staking keypair from {staking_keypair_path}: {str(e)}"
                )

        # Load main keypair if configured
        if main_keypair_env:
            main_keypair_path = os.getenv(main_keypair_env)
            if not main_keypair_path:
                raise ValueError(
                    f"Missing main keypair path - env var {main_keypair_env} not set"
                )
            if not Path(main_keypair_path).exists():
                raise ValueError(f"Main keypair file not found at {main_keypair_path}")
            try:
                self.main_signing_key, self.main_public_key = load_keypair(
                    main_keypair_path
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to load main keypair from {main_keypair_path}: {str(e)}"
                )

        # Environment setup
        self.env = os.environ.copy()
        for key, value in self.env_vars.items():
            # For DATA_DIR, use the value directly
            if key == "DATA_DIR":
                self.env[key] = value
            else:
                # For other vars, get from environment
                self.env[key] = os.getenv(value)
        self.env["DATABASE_PATH"] = self.get("database_path")
        self.env["PYTHONUNBUFFERED"] = "1"
        self.env["PORT"] = str(self.get("port"))

    def _print_output(self, stream, prefix):
        """Print output from a stream with a prefix"""
        for line in stream:
            print(f"{prefix} {line.strip()}")
            sys.stdout.flush()

    def start(self):
        """Start the worker's server"""
        print(f"\nStarting {self.get('name')} server on port {self.get('port')}...")
        sys.stdout.flush()

        server_entrypoint = self.get("server_entrypoint")
        if not server_entrypoint:
            raise RuntimeError("Cannot start server - no server_entrypoint configured")

        # Start the process with unbuffered output
        self.process = subprocess.Popen(
            [sys.executable, server_entrypoint],
            env=self.env,
            cwd=Path(self.get("base_dir")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        )

        # Wait for server to start
        time.sleep(3)  # Default timeout

        # Check if server started successfully
        if self.process.poll() is not None:
            _, stderr = self.process.communicate()
            error_msg = stderr.strip() if stderr else "No error output available"
            raise RuntimeError(
                f"Failed to start {self.get('name')} server:\n{error_msg}"
            )

        stdout_thread = threading.Thread(
            target=self._print_output,
            args=(self.process.stdout, f"[{self.get('name')}]"),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=self._print_output,
            args=(self.process.stderr, f"[{self.get('name')} ERR]"),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

    def stop(self):
        """Stop the worker's server"""
        if self.process:
            print(f"\nStopping {self.get('name')} server...")
            sys.stdout.flush()

            # Send SIGTERM first to allow graceful shutdown
            os.kill(self.process.pid, signal.SIGTERM)
            time.sleep(1)

            # If still running, send SIGKILL
            if self.process.poll() is None:
                os.kill(self.process.pid, signal.SIGKILL)

            # Wait for process to fully terminate
            self.process.wait()
            self.process = None

    def get_env(self, key: str) -> Optional[str]:
        """Get an environment variable value.

        Args:
            key: The environment variable name to look up

        Returns:
            The environment variable value if found, None otherwise
        """
        return self.env.get(key)

    def get_key(self, key_type: str) -> str:
        """Get a key value.

        Args:
            key_type: Type of key to return, one of:
                     - "staking_public": The staking public key
                     - "staking_signing": The staking signing/private key
                     - "main_public": The main public key
                     - "main_signing": The main signing/private key

        Returns:
            The requested key

        Raises:
            ValueError: If key_type is not one of the valid options
        """
        if key_type == "staking_public":
            return self.staking_public_key
        elif key_type == "staking_signing":
            return self.staking_signing_key
        elif key_type == "main_public":
            return self.main_public_key
        elif key_type == "main_signing":
            return self.main_signing_key
        else:
            raise ValueError(
                'key_type must be one of: "staking_public", "staking_signing", '
                '"main_public", "main_signing"'
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get an arbitrary stored value.

        Args:
            key: The key to look up
            default: Value to return if key is not found

        Returns:
            The stored value if found, default otherwise
        """
        return self._data.get(key, default)


class TestEnvironment:
    """Manages multiple workers for testing"""

    def __init__(
        self,
        worker_configs: Dict[str, dict],
        base_dir: Path,
        base_port: int = 5000,
        data_dir: Optional[Path] = None,
    ):
        self.base_dir = base_dir
        self.workers: Dict[str, Worker] = {}

        # Create workers
        for i, (name, config) in enumerate(worker_configs.items()):
            worker = Worker(
                name=name,
                base_dir=base_dir,
                default_port=base_port + i,
                config=config,
                data_dir=data_dir,
            )
            self.workers[name] = worker

    def __enter__(self):
        """Start all worker servers"""
        print("Starting worker servers...")
        try:
            for worker in self.workers.values():
                worker.start()
            return self
        except Exception as e:
            print(f"Failed to start servers: {str(e)}")
            self._cleanup()
            raise

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Stop all worker servers"""
        print("Stopping worker servers...")
        self._cleanup()

    def _cleanup(self):
        """Clean up all worker processes"""
        for worker in self.workers.values():
            if worker.process:
                try:
                    os.kill(worker.process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass  # Process already gone
                worker.process = None

    def get_worker(self, name: str) -> Worker:
        """Get a worker by name"""
        if name not in self.workers:
            raise KeyError(f"No worker found with name: {name}")
        return self.workers[name]
