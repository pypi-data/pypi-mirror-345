#!/usr/bin/env python3
"""
Simple Repository Analysis Example

This example demonstrates how to:
1. Clone a well-known repository (Flask)
2. Monitor the cloning process with verbose output
3. Extract commit history from the repository
4. Run bulk blame analysis on files in a specific directory
5. Display and analyze results using pandas dataframes

Prerequisites:
- pandas: For data analysis and visualization (pip install pandas)
  Install with: pip install "gitfleet[all]"
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path to import GitFleet directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import GitFleet components
from GitFleet import RepoManager
from GitFleet import to_pydantic_task, to_pydantic_status, convert_clone_tasks

# Try to import pandas - show a nice error if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas is not installed. Install with: pip install pandas")
    print("Continuing with basic output...")

# GitHub credentials - replace with your own or use environment variables
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "your-username")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your-personal-access-token")

# Target repository - Flask is a well-known Python web framework with a stable structure
REPO_URL = "https://github.com/bmeddeb/SER402-Team3.git"
TARGET_DIR = "plots"  # Known directory for blame analysis


class RepositoryAnalyzer:
    """Handles repository cloning, monitoring, and analysis with pandas integration."""
    
    def __init__(self, repo_url: str, github_username: str, github_token: str):
        """Initialize the analyzer with repository info and GitHub credentials."""
        self.repo_url = repo_url
        self.manager = RepoManager(
            urls=[repo_url],
            github_username=github_username,
            github_token=github_token
        )
        self.temp_dir = None
        self.is_verbose = True
        self.start_time = None
        self.blame_results = {}
        self.commit_history = []
        
    async def clone_with_monitoring(self) -> bool:
        """Clone the repository with detailed progress monitoring."""
        self.start_time = time.time()
        self.log(f"Starting clone of {self.repo_url}")
        
        # Start clone operation asynchronously
        clone_future = self.manager.clone_all()
        
        # Monitor the cloning process with detailed updates
        previous_progress = 0
        while not clone_future.done():
            # Get current status of clone tasks
            tasks = await self.manager.fetch_clone_tasks()
            task = tasks.get(self.repo_url)
            
            if not task:
                self.log("No task found for repository")
                break
                
            status = task.status.status_type
            progress = task.status.progress
            
            # Clear terminal for better display
            if os.name != "nt":
                os.system("clear")
            else:
                os.system("cls")
                
            # Current duration
            duration = time.time() - self.start_time
            
            self.log(f"==== Repository Clone Status ====")
            self.log(f"Repository: {self.repo_url}")
            self.log(f"Status: {status.upper()}")
            self.log(f"Time elapsed: {self._format_duration(duration)}")
            
            # Display progress bar for cloning
            if status == "cloning" and progress is not None:
                self._display_progress_bar(progress)
                
                # Estimate remaining time if progress is increasing
                if progress > previous_progress and progress > 0:
                    elapsed_per_percent = duration / progress
                    remaining_seconds = elapsed_per_percent * (100 - progress)
                    self.log(f"Estimated time remaining: {self._format_duration(remaining_seconds)}")
                    
                previous_progress = progress
                
            # Show error if failed
            if status == "failed" and task.status.error:
                self.log(f"Error: {task.status.error}")
                return False
                
            # Show clone directory if available
            if task.temp_dir:
                self.temp_dir = task.temp_dir
                self.log(f"Directory: {task.temp_dir}")
                
            # Exit loop if complete or failed
            if status in ["completed", "failed"]:
                break
                
            # Wait before checking again
            await asyncio.sleep(1)
            
        # Ensure clone operation is complete
        await clone_future
        
        # Final check to get temp_dir
        if not self.temp_dir:
            tasks = await self.manager.fetch_clone_tasks()
            task = tasks.get(self.repo_url)
            if task and task.temp_dir:
                self.temp_dir = task.temp_dir
                
        # Report success or failure
        duration = time.time() - self.start_time
        
        if self.temp_dir:
            self.log(f"Repository cloned successfully in {self._format_duration(duration)}")
            self.log(f"Clone directory: {self.temp_dir}")
            return True
        else:
            self.log("Failed to clone repository")
            return False
    
    async def extract_commits(self) -> bool:
        """Extract commit history from the repository."""
        if not self.temp_dir:
            self.log("No repository directory. Clone the repository first.")
            return False
            
        self.log("\n==== Extracting Commit History ====")
        self.start_time = time.time()
        
        try:
            self.log(f"Analyzing commit history for {self.repo_url}...")
            self.commit_history = await self.manager.extract_commits(self.temp_dir)
            
            if isinstance(self.commit_history, list):
                duration = time.time() - self.start_time
                self.log(f"Successfully extracted {len(self.commit_history)} commits in {self._format_duration(duration)}")
                return True
            else:
                self.log(f"Error extracting commits: {self.commit_history}")
                return False
                
        except Exception as e:
            self.log(f"Error during commit extraction: {str(e)}")
            return False
    
    async def run_blame_analysis(self, target_dir: Optional[str] = None) -> bool:
        """Run blame analysis on files in the target directory."""
        if not self.temp_dir:
            self.log("No repository directory. Clone the repository first.")
            return False
            
        # Determine directory to analyze
        if target_dir:
            dir_path = os.path.join(self.temp_dir, target_dir)
        else:
            dir_path = self.temp_dir
            
        # Check if directory exists
        if not os.path.isdir(dir_path):
            self.log(f"Directory not found: {dir_path}")
            return False
            
        self.log(f"\n==== Running Blame Analysis on {target_dir or '/'} ====")
        self.start_time = time.time()
        
        # Find files to analyze
        file_paths = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".py", ".js", ".html", ".css")):  # Common web files
                    rel_path = os.path.relpath(os.path.join(root, file), self.temp_dir)
                    file_paths.append(rel_path)
                    
        if not file_paths:
            self.log(f"No suitable files found in {target_dir or '/'}")
            return False
            
        self.log(f"Found {len(file_paths)} files to analyze")
        
        # Run blame analysis
        try:
            self.log("Starting blame analysis...")
            self.blame_results = await self.manager.bulk_blame(self.temp_dir, file_paths)
            
            # Check results
            success_count = sum(1 for result in self.blame_results.values() if isinstance(result, list))
            error_count = len(self.blame_results) - success_count
            
            duration = time.time() - self.start_time
            self.log(f"Completed blame analysis in {self._format_duration(duration)}")
            self.log(f"Successfully analyzed {success_count} files")
            
            if error_count > 0:
                self.log(f"Failed to analyze {error_count} files")
                
            return success_count > 0
                
        except Exception as e:
            self.log(f"Error during blame analysis: {str(e)}")
            return False
    
    def display_results(self) -> None:
        """Display analysis results, optionally using pandas DataFrames."""
        if not self.commit_history and not self.blame_results:
            self.log("No analysis results to display")
            return
            
        self.log("\n==== Analysis Results ====")
        
        # Display commit history
        if self.commit_history and isinstance(self.commit_history, list):
            self._display_commit_history()
            
        # Display blame results
        if self.blame_results:
            self._display_blame_results()
    
    def cleanup(self) -> None:
        """Clean up temporary repository clones."""
        self.log("\n==== Cleaning Up ====")
        cleanup_results = self.manager.cleanup()
        
        for url, result in cleanup_results.items():
            status = "Success" if result is True else f"Failed: {result}"
            self.log(f"Cleanup {url}: {status}")
    
    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.is_verbose:
            print(message)
    
    def _display_progress_bar(self, progress: int) -> None:
        """Display a progress bar for the current operation."""
        bar_length = 40
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        self.log(f"Progress: [{bar}] {progress}%")
    
    def _format_duration(self, seconds: float) -> str:
        """Format a duration in seconds to a human-readable string."""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = seconds % 60
            return f"{minutes} min {int(remaining_seconds)} sec"
        else:
            hours = int(seconds / 3600)
            remaining_minutes = int((seconds % 3600) / 60)
            return f"{hours} hr {remaining_minutes} min"
    
    def _display_commit_history(self) -> None:
        """Display commit history analysis, using pandas if available."""
        self.log(f"\n--- Commit History Analysis ({len(self.commit_history)} commits) ---")
        
        if HAS_PANDAS:
            # Convert to DataFrame for better analysis
            df = pd.DataFrame(self.commit_history)
            
            # Convert Unix timestamps (seconds since epoch) to datetime objects
            df['author_timestamp'] = pd.to_datetime(df['author_timestamp'], unit='s')
            df['committer_timestamp'] = pd.to_datetime(df['committer_timestamp'], unit='s')
            
            # Add day and month columns for time series analysis
            df['date'] = df['author_timestamp'].dt.date
            df['month'] = df['author_timestamp'].dt.to_period('M')
            df['year'] = df['author_timestamp'].dt.year
            
            # Display basic statistics
            self.log("\nCommit Statistics:")
            
            # Debug raw timestamps
            if len(self.commit_history) > 0:
                self.log(f"Debug: First commit raw author_timestamp: {self.commit_history[0]['author_timestamp']}")
                self.log(f"Debug: First commit converted timestamp: {df['author_timestamp'].iloc[0]}")
            
            # Time range
            self.log(f"Date Range: {df['date'].min()} to {df['date'].max()}")
            
            # Author summary
            author_counts = df['author_name'].value_counts()
            self.log("\nTop Contributors:")
            for author, count in author_counts.head(5).items():
                self.log(f"  {author}: {count} commits")
                
            # Code changes
            total_additions = df['additions'].sum()
            total_deletions = df['deletions'].sum()
            self.log(f"\nTotal Lines Added: {total_additions}")
            self.log(f"Total Lines Deleted: {total_deletions}")
            self.log(f"Net Change: {total_additions - total_deletions} lines")
            
            # Time-based patterns
            commits_by_month = df.groupby('month').size()
            self.log("\nCommits by Month (most recent):")
            for month, count in commits_by_month.tail(6).items():
                self.log(f"  {month}: {count} commits")
                
        else:
            # Basic non-pandas analysis
            self.log("\nRecent Commits:")
            for commit in self.commit_history[:5]:
                # Convert Unix timestamp to human-readable date
                timestamp = datetime.fromtimestamp(commit['author_timestamp'])
                self.log(f"Commit: {commit['sha'][:8]}")
                self.log(f"Author: {commit['author_name']}")
                self.log(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                message = commit['message'].split('\n')[0][:50]
                self.log(f"Message: {message}...")
                self.log(f"Changes: +{commit['additions']} -{commit['deletions']}")
                self.log("---")
    
    def _display_blame_results(self) -> None:
        """Display blame analysis results, using pandas if available."""
        # Count successful analyses
        success_files = [f for f, result in self.blame_results.items() 
                         if isinstance(result, list)]
        
        if not success_files:
            self.log("No successful blame analyses to display")
            return
            
        self.log(f"\n--- Blame Analysis Results ({len(success_files)} files) ---")
        
        if HAS_PANDAS:
            # Convert blame data to a more usable format
            all_blame_data = []
            
            for file_path, blame_lines in self.blame_results.items():
                if not isinstance(blame_lines, list):
                    continue
                    
                # Add each blame line as a row with file information
                for line in blame_lines:
                    blame_row = {
                        'file': file_path,
                        'line_number': line.get('final_line_no'),  # Correct field name
                        'author': line.get('author_name'),
                        'email': line.get('author_email'),
                        'commit': line.get('commit_id', '')[:8],  # Correct field name
                    }
                    all_blame_data.append(blame_row)
            
            # Create DataFrame from all blame data
            blame_df = pd.DataFrame(all_blame_data)
            
            # No timestamp field in blame data - the Rust library doesn't provide it
            # We'll analyze without timestamp information
            
            # Summary by file
            file_summary = blame_df.groupby('file').size().sort_values(ascending=False)
            self.log("\nFiles by Line Count:")
            for file, count in file_summary.head(5).items():
                self.log(f"  {file}: {count} lines")
            
            # Summary by author
            author_summary = blame_df.groupby('author').size().sort_values(ascending=False)
            self.log("\nTop Contributors by Lines:")
            for author, count in author_summary.head(5).items():
                self.log(f"  {author}: {count} lines")
                
            # Author distribution by file
            self.log("\nAuthor Distribution for Top Files:")
            for file in file_summary.head(3).index:
                file_df = blame_df[blame_df['file'] == file]
                file_authors = file_df.groupby('author').size().sort_values(ascending=False)
                
                self.log(f"\n  {file}:")
                author_percentage = file_authors / file_authors.sum() * 100
                for author, percent in author_percentage.head(3).items():
                    self.log(f"    {author}: {percent:.1f}%")
        
        else:
            # Basic non-pandas analysis
            self.log("\nFile Analysis:")
            for file_path, blame_lines in self.blame_results.items():
                if not isinstance(blame_lines, list):
                    continue
                    
                authors = {}
                for line in blame_lines:
                    author = line.get('author_name')
                    if author in authors:
                        authors[author] += 1
                    else:
                        authors[author] = 1
                
                self.log(f"\n  {file_path} ({len(blame_lines)} lines):")
                
                # Sort by number of lines
                sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
                for author, count in sorted_authors[:3]:
                    percentage = (count / len(blame_lines)) * 100
                    self.log(f"    {author}: {count} lines ({percentage:.1f}%)")


async def main():
    """Main function to run the repository analysis."""
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your-personal-access-token":
        print("⚠️ GitHub token not found. Set the GITHUB_TOKEN environment variable.")
        print("You can create a token at: https://github.com/settings/tokens")
        return
        
    print(f"📊 Simple Repository Analysis: {REPO_URL}")
    
    # Create analyzer instance
    analyzer = RepositoryAnalyzer(
        repo_url=REPO_URL,
        github_username=GITHUB_USERNAME,
        github_token=GITHUB_TOKEN
    )
    
    # Clone repository with monitoring
    clone_success = await analyzer.clone_with_monitoring()
    if not clone_success:
        print("❌ Failed to clone repository. Exiting.")
        return
        
    # Extract commit history
    commit_success = await analyzer.extract_commits()
    
    # Show diagnostic info about a commit if available
    if analyzer.commit_history and isinstance(analyzer.commit_history, list) and len(analyzer.commit_history) > 0:
        commit = analyzer.commit_history[0]
        print(f"Debug: Sample commit data:")
        print(f"  SHA: {commit.get('sha', '')[:8]}")
        print(f"  Author: {commit.get('author_name', '')}")
        print(f"  Raw timestamp: {commit.get('author_timestamp', 'N/A')}")
        
        # Convert timestamp to a date
        import datetime
        if 'author_timestamp' in commit:
            timestamp = commit['author_timestamp']
            date = datetime.datetime.fromtimestamp(timestamp)
            print(f"  Converted to: {date.strftime('%Y-%m-%d %H:%M:%S')}")
            
    # Run blame analysis on target directory
    blame_success = await analyzer.run_blame_analysis(TARGET_DIR)
    
    # Display results (using pandas if available)
    analyzer.display_results()
    
    # Clean up temporary directories
    analyzer.cleanup()
    
    print("\n✅ Analysis complete!")
    

if __name__ == "__main__":
    # Set up the event loop and run the main async function
    asyncio.run(main())