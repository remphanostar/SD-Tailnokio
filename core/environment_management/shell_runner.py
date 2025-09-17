"""
Shell Runner Module - Phase 2
Executes shell commands with proper output handling and error management.
CRITICAL: This module needs to support capture_output parameter for tunneling to work.
"""

import subprocess
import sys
import os
import json
import threading
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

@dataclass
class CommandResult:
    """Result of a shell command execution."""
    stdout: str
    stderr: str
    returncode: int
    success: bool
    
    def __post_init__(self):
        self.success = self.returncode == 0

class ShellRunner:
    """Executes shell commands with comprehensive output handling."""
    
    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir or os.getcwd()
        self.command_history = []
        self.active_processes = {}
        
    def run_command(self, command: Union[str, List[str]], 
                   capture_output: bool = False,
                   timeout: Optional[int] = None,
                   env: Optional[Dict[str, str]] = None,
                   working_dir: Optional[str] = None) -> CommandResult:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute (string or list)
            capture_output: Whether to capture stdout/stderr (CRITICAL for tunneling)
            timeout: Timeout in seconds
            env: Environment variables
            working_dir: Working directory for command
            
        Returns:
            CommandResult object with execution details
        """
        # Prepare command
        if isinstance(command, str):
            cmd_list = command.split()
        else:
            cmd_list = command
            
        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
            
        # Set working directory
        cmd_workdir = working_dir or self.working_dir
        
        # Log command
        command_info = {
            "command": cmd_list,
            "working_dir": cmd_workdir,
            "capture_output": capture_output,
            "timestamp": time.time()
        }
        self.command_history.append(command_info)
        
        try:
            # Execute command
            if capture_output:
                # Capture output (required for tunneling)
                result = subprocess.run(
                    cmd_list,
                    cwd=cmd_workdir,
                    env=cmd_env,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return CommandResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode
                )
            else:
                # Don't capture output (stream to console)
                result = subprocess.run(
                    cmd_list,
                    cwd=cmd_workdir,
                    env=cmd_env,
                    timeout=timeout
                )
                
                return CommandResult(
                    stdout="",
                    stderr="",
                    returncode=result.returncode
                )
                
        except subprocess.TimeoutExpired:
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                returncode=-1
            )
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                returncode=-1
            )
    
    def run_command_async(self, command: Union[str, List[str]], 
                         callback: Optional[callable] = None,
                         working_dir: Optional[str] = None) -> str:
        """
        Execute a command asynchronously and return process ID.
        
        Args:
            command: Command to execute
            callback: Optional callback function for output
            working_dir: Working directory
            
        Returns:
            Process ID string
        """
        if isinstance(command, str):
            cmd_list = command.split()
        else:
            cmd_list = command
            
        cmd_workdir = working_dir or self.working_dir
        
        try:
            # Start process
            process = subprocess.Popen(
                cmd_list,
                cwd=cmd_workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            process_id = f"proc_{len(self.active_processes)}"
            self.active_processes[process_id] = process
            
            # Start output streaming thread
            if callback:
                def stream_output():
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            callback(output.strip())
                    
                    # Get any remaining stderr
                    error_output = process.stderr.read()
                    if error_output:
                        callback(f"ERROR: {error_output.strip()}")
                
                thread = threading.Thread(target=stream_output, daemon=True)
                thread.start()
            
            return process_id
            
        except Exception as e:
            return f"error: {str(e)}"
    
    def stop_process(self, process_id: str) -> bool:
        """Stop an asynchronous process."""
        if process_id in self.active_processes:
            try:
                process = self.active_processes[process_id]
                process.terminate()
                
                # Wait for graceful termination
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                del self.active_processes[process_id]
                return True
            except:
                return False
        return False
    
    def get_process_status(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an asynchronous process."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            return {
                "pid": process.pid,
                "running": process.poll() is None,
                "returncode": process.poll()
            }
        return None
    
    def list_active_processes(self) -> Dict[str, Dict[str, Any]]:
        """List all active processes."""
        return {
            pid: self.get_process_status(pid)
            for pid in self.active_processes
        }
    
    def run_script(self, script_path: str, 
                   args: Optional[List[str]] = None,
                   capture_output: bool = False) -> CommandResult:
        """
        Run a Python script.
        
        Args:
            script_path: Path to the script
            args: Arguments to pass to the script
            capture_output: Whether to capture output
            
        Returns:
            CommandResult object
        """
        if not os.path.exists(script_path):
            return CommandResult(
                stdout="",
                stderr=f"Script not found: {script_path}",
                returncode=-1
            )
        
        command = [sys.executable, script_path]
        if args:
            command.extend(args)
            
        return self.run_command(command, capture_output=capture_output)
    
    def install_package(self, package: str, package_manager: str = "pip") -> CommandResult:
        """
        Install a Python package.
        
        Args:
            package: Package name to install
            package_manager: Package manager to use (pip, conda)
            
        Returns:
            CommandResult object
        """
        if package_manager == "pip":
            command = [sys.executable, "-m", "pip", "install", package]
        elif package_manager == "conda":
            command = ["conda", "install", "-y", package]
        else:
            return CommandResult(
                stdout="",
                stderr=f"Unsupported package manager: {package_manager}",
                returncode=-1
            )
        
        return self.run_command(command, capture_output=True)
    
    def git_clone(self, repo_url: str, target_dir: Optional[str] = None) -> CommandResult:
        """
        Clone a git repository.
        
        Args:
            repo_url: URL of the repository
            target_dir: Target directory (optional)
            
        Returns:
            CommandResult object
        """
        command = ["git", "clone", repo_url]
        if target_dir:
            command.append(target_dir)
            
        return self.run_command(command, capture_output=True)
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get the command execution history."""
        return self.command_history
    
    def clear_history(self):
        """Clear the command history."""
        self.command_history.clear()

# Global instance
shell_runner = ShellRunner()

def run_command(command: Union[str, List[str]], capture_output: bool = False, **kwargs) -> CommandResult:
    """Convenience function to run a command."""
    return shell_runner.run_command(command, capture_output=capture_output, **kwargs)

def run_command_async(command: Union[str, List[str]], callback: Optional[callable] = None) -> str:
    """Convenience function to run a command asynchronously."""
    return shell_runner.run_command_async(command, callback)

if __name__ == "__main__":
    # Test the shell runner
    print("Testing Shell Runner...")
    
    # Test simple command
    result = run_command("echo 'Hello World'", capture_output=True)
    print(f"Command result: {result.stdout}")
    print(f"Return code: {result.returncode}")
    
    # Test with capture_output=False (for tunneling compatibility)
    result = run_command("echo 'Testing capture_output=False'", capture_output=False)
    print(f"Command executed successfully: {result.success}")
    
    print("Shell Runner test completed!")