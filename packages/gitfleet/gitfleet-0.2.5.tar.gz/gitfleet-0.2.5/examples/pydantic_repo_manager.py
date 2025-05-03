#!/usr/bin/env python3
"""
Pydantic-enabled RepoManager Example

This example demonstrates how to use the Pydantic models with the Rust-based RepoManager:
1. Use the Pydantic wrappers for RepoManager, CloneStatus, and CloneTask
2. Show serialization and validation of the models
3. Convert between Rust objects and Pydantic models

Optional dependencies:
- pydantic: Required for Pydantic models (pip install pydantic)
  Install with: pip install "gitfleet[pydantic]"
"""

import os
import sys
import json
import asyncio
from pprint import pprint
from datetime import datetime

# Add the parent directory to the Python path so we can import GitFleet modules directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Pydantic-enabled models
from GitFleet.models.repo import (
    RepoManager, CloneStatus, CloneTask, CloneStatusType,
    clone_status_to_pydantic, clone_task_to_pydantic
)


async def main():
    # Get GitHub token from environment variable
    github_token = os.environ.get("GITHUB_TOKEN", "")
    
    if not github_token:
        print("⚠️ GitHub token not found in environment variables.")
        print("Set the GITHUB_TOKEN environment variable to use this example.")
        print("You can create a token at: https://github.com/settings/tokens")
        return

    try:
        # Create a repository URL to clone (public repository for example)
        repo_url = "https://github.com/octocat/Hello-World.git"
        urls = [repo_url]

        # Create a RepoManager using the Pydantic wrapper
        print("\n🔧 Creating RepoManager with Pydantic support")
        manager = RepoManager(urls, "username", github_token)
        
        # Start cloning the repository
        print("\n🔄 Cloning the repository")
        await manager.clone_all()
        
        # Get the clone tasks and demonstrate Pydantic model features
        print("\n📋 Checking clone tasks")
        tasks = await manager.fetch_clone_tasks()
        
        # Use Pydantic serialization features
        for url, task in tasks.items():
            print(f"\n📦 Repository: {url}")
            
            # Show the task status
            status = task.status
            print(f"  Status: {status.status_type}")
            if status.status_type == CloneStatusType.CLONING:
                print(f"  Progress: {status.progress}%")
            elif status.status_type == CloneStatusType.FAILED:
                print(f"  Error: {status.error}")
            elif status.status_type == CloneStatusType.COMPLETED:
                print(f"  Temp directory: {task.temp_dir}")
            
            # Demonstrate Pydantic model serialization
            print("\n  Pydantic Model Features:")
            
            # Convert to dict
            task_dict = task.model_dump()
            print(f"  ↳ model_dump(): {list(task_dict.keys())}")
            
            # Convert to JSON
            task_json = task.model_dump_json(indent=2)
            print(f"  ↳ model_dump_json():")
            pretty_json = json.dumps(json.loads(task_json), indent=4)
            for line in pretty_json.split('\n')[:7]:
                print(f"    {line}")
            print("    ...")
            
            # Validate from Python dict
            print("\n  Validation Features:")
            try:
                # Create a CloneStatus from basic Python types
                new_status = CloneStatus(
                    status_type=CloneStatusType.COMPLETED,
                    progress=None,
                    error=None
                )
                print(f"  ↳ Created new status: {new_status.status_type}")
                
                # Create a CloneTask with validation
                new_task = CloneTask(
                    url="https://github.com/example/repo.git",
                    status=new_status,
                    temp_dir="/tmp/example"
                )
                print(f"  ↳ Created new task: {new_task.url}")
                
                # Show validation error handling
                print("\n  Validation Error Handling:")
                try:
                    # This will fail validation - invalid status_type
                    invalid_status = CloneStatus(
                        status_type="invalid_status",
                        progress=None,
                        error=None
                    )
                except Exception as e:
                    print(f"  ↳ Caught validation error: {str(e)[:100]}...")
                
            except Exception as e:
                print(f"  ↳ Error: {str(e)}")
        
        # Cleanup temp directories
        print("\n🧹 Cleaning up temporary directories")
        cleanup_results = manager.cleanup()
        for url, result in cleanup_results.items():
            print(f"  {url}: {'Success' if result is True else result}")
            
    except ImportError as e:
        print(f"\n❌ Error: {str(e)}")
        print("This example requires the Rust extension to be built.")
        print("Build it with: maturin develop")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())