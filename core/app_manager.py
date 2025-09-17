"""
App Manager Module - Phase 5
Central coordinator for all app-related operations.
Integrates all phases to provide complete app management functionality.
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from .app_database import app_database, PinokioApp
from .environment_management.shell_runner import shell_runner, CommandResult
from .tunneling.cloudflare_manager import cloudflare_manager

class AppManager:
    """Central coordinator for all app-related operations."""
    
    def __init__(self):
        self.database = app_database
        self.shell_runner = shell_runner
        self.cloudflare_manager = cloudflare_manager
        self.installation_queue = []
        self.active_installations = {}
        self.running_processes = {}
        self.active_tunnels = {}
        self.event_listeners = []
        
    def initialize(self) -> bool:
        """Initialize the app manager and all dependencies."""
        try:
            print("🚀 Initializing App Manager...")
            
            # Load database
            if not self.database.load_database():
                print("❌ Failed to load app database")
                return False
            
            # Setup cloudflared
            if not self.cloudflare_manager.setup_cloudflared():
                print("⚠️ Cloudflared setup failed, tunneling may not work")
            
            print("✅ App Manager initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing App Manager: {e}")
            return False
    
    def get_apps(self, category: Optional[str] = None, tag: Optional[str] = None, 
                search: Optional[str] = None) -> List[PinokioApp]:
        """
        Get applications with optional filtering.
        
        Args:
            category: Filter by category
            tag: Filter by tag
            search: Search in name and description
            
        Returns:
            List of filtered applications
        """
        apps = self.database.get_all_apps()
        
        if category:
            apps = [app for app in apps if app.category == category]
        
        if tag:
            apps = [app for app in apps if tag in app.tags]
        
        if search:
            search_lower = search.lower()
            apps = [app for app in apps 
                    if search_lower in app.name.lower() or 
                    (app.description and search_lower in app.description.lower())]
        
        return apps
    
    def get_app_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an application."""
        app = self.database.get_app(app_id)
        if not app:
            return None
        
        # Get installation status
        installation_status = self.get_installation_status(app_id)
        
        # Get process status
        process_status = self.get_process_status(app_id)
        
        # Get tunnel status
        tunnel_status = self.get_tunnel_status(app_id)
        
        return {
            "app": app,
            "installation": installation_status,
            "process": process_status,
            "tunnel": tunnel_status,
            "actions": self._get_available_actions(app_id)
        }
    
    def _get_available_actions(self, app_id: str) -> List[str]:
        """Get available actions for an app."""
        actions = []
        app = self.database.get_app(app_id)
        
        if not app:
            return actions
        
        # Check installation status
        installation_status = self.get_installation_status(app_id)
        if not app.installed and installation_status != "installing":
            actions.append("install")
        
        # Check process status
        process_status = self.get_process_status(app_id)
        if app.installed and process_status != "running":
            actions.append("run")
        
        if process_status == "running":
            actions.append("stop")
        
        # Check tunnel status
        tunnel_status = self.get_tunnel_status(app_id)
        if process_status == "running" and tunnel_status != "active":
            actions.append("tunnel")
        
        if tunnel_status == "active":
            actions.append("stop_tunnel")
        
        return actions
    
    def install_app(self, app_id: str, callback: Optional[Callable] = None) -> bool:
        """
        Install an application.
        
        Args:
            app_id: ID of the application to install
            callback: Optional callback function for progress updates
            
        Returns:
            True if installation started successfully
        """
        app = self.database.get_app(app_id)
        if not app:
            print(f"❌ App not found: {app_id}")
            return False
        
        if app.installed:
            print(f"⚠️ App {app.name} is already installed")
            return False
        
        # Check if already installing
        if app_id in self.active_installations:
            print(f"⚠️ App {app.name} is already being installed")
            return False
        
        print(f"🚀 Starting installation of {app.name}...")
        
        # Create installation record
        installation_id = f"install_{app_id}_{int(time.time())}"
        self.active_installations[app_id] = {
            "id": installation_id,
            "status": "installing",
            "progress": 0,
            "started_at": time.time(),
            "logs": []
        }
        
        # Start installation in background thread
        def install_thread():
            try:
                self._perform_installation(app_id, callback)
            except Exception as e:
                print(f"❌ Installation failed: {e}")
                self.active_installations[app_id]["status"] = "failed"
                self.active_installations[app_id]["error"] = str(e)
                if callback:
                    callback({
                        "app_id": app_id,
                        "status": "failed",
                        "error": str(e)
                    })
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
        
        return True
    
    def _perform_installation(self, app_id: str, callback: Optional[Callable] = None):
        """Perform the actual installation process."""
        app = self.database.get_app(app_id)
        installation = self.active_installations[app_id]
        
        def log_message(message: str):
            log_entry = {
                "timestamp": time.time(),
                "message": message
            }
            installation["logs"].append(log_entry)
            print(f"[{app.name}] {message}")
        
        try:
            log_message("Starting installation...")
            
            # Create app directory
            app_dir = Path("apps") / app_id
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone repository
            log_message(f"Cloning repository from {app.repo_url}...")
            result = self.shell_runner.git_clone(app.repo_url, str(app_dir))
            
            if not result.success:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            log_message("Repository cloned successfully")
            installation["progress"] = 30
            
            # Install dependencies
            log_message("Installing dependencies...")
            
            # Check for requirements files
            requirements_files = [
                "requirements.txt",
                "requirements.pip",
                "deps.txt",
                "environment.yml",
                "Pipfile"
            ]
            
            dependencies_installed = False
            for req_file in requirements_files:
                req_path = app_dir / req_file
                if req_path.exists():
                    log_message(f"Found {req_file}, installing dependencies...")
                    
                    if req_file == "environment.yml":
                        # Conda environment
                        result = self.shell_runner.run_command(
                            ["conda", "env", "update", "-f", str(req_path)],
                            capture_output=True
                        )
                    elif req_file == "Pipfile":
                        # Pipenv
                        result = self.shell_runner.run_command(
                            ["pipenv", "install"],
                            working_dir=str(app_dir),
                            capture_output=True
                        )
                    else:
                        # pip requirements
                        result = self.shell_runner.run_command(
                            [self.shell_runner.working_dir + "/python", "-m", "pip", "install", "-r", str(req_path)],
                            working_dir=str(app_dir),
                            capture_output=True
                        )
                    
                    if result.success:
                        log_message("Dependencies installed successfully")
                        dependencies_installed = True
                    else:
                        log_message(f"Warning: Some dependencies failed to install: {result.stderr}")
                    
                    break
            
            if not dependencies_installed:
                log_message("No requirements file found, skipping dependency installation")
            
            installation["progress"] = 70
            
            # Run install script if specified
            if app.install_script:
                install_script = app_dir / app.install_script
                if install_script.exists():
                    log_message(f"Running install script: {app.install_script}...")
                    
                    result = self.shell_runner.run_script(
                        str(install_script),
                        capture_output=True
                    )
                    
                    if result.success:
                        log_message("Install script completed successfully")
                    else:
                        log_message(f"Warning: Install script failed: {result.stderr}")
                else:
                    log_message(f"Install script not found: {app.install_script}")
            
            installation["progress"] = 90
            
            # Mark as installed
            self.database.set_app_installed(app_id, True)
            log_message("Installation completed successfully!")
            
            installation["status"] = "completed"
            installation["progress"] = 100
            
            if callback:
                callback({
                    "app_id": app_id,
                    "status": "completed",
                    "progress": 100
                })
            
        except Exception as e:
            log_message(f"Installation failed: {str(e)}")
            installation["status"] = "failed"
            installation["error"] = str(e)
            
            if callback:
                callback({
                    "app_id": app_id,
                    "status": "failed",
                    "error": str(e)
                })
    
    def run_app(self, app_id: str, callback: Optional[Callable] = None) -> bool:
        """
        Run an application.
        
        Args:
            app_id: ID of the application to run
            callback: Optional callback function for output
            
        Returns:
            True if application started successfully
        """
        app = self.database.get_app(app_id)
        if not app:
            print(f"❌ App not found: {app_id}")
            return False
        
        if not app.installed:
            print(f"❌ App {app.name} is not installed")
            return False
        
        # Check if already running
        if app_id in self.running_processes:
            print(f"⚠️ App {app.name} is already running")
            return False
        
        print(f"▶️ Starting {app.name}...")
        
        # Determine run script
        app_dir = Path("apps") / app_id
        
        if app.run_script:
            run_script = app_dir / app.run_script
        else:
            # Try common script names
            possible_scripts = [
                "app.py", "main.py", "webui.py", "launch.py",
                "run.py", "start.py", "server.py", f"{app_id}.py"
            ]
            
            run_script = None
            for script in possible_scripts:
                if (app_dir / script).exists():
                    run_script = app_dir / script
                    break
            
            if not run_script:
                print(f"❌ No run script found for {app.name}")
                return False
        
        # Start the application
        def output_callback(output: str):
            if callback:
                callback({
                    "app_id": app_id,
                    "type": "output",
                    "output": output
                })
        
        process_id = self.shell_runner.run_command_async(
            [self.shell_runner.working_dir + "/python", str(run_script)],
            callback=output_callback,
            working_dir=str(app_dir)
        )
        
        if process_id.startswith("error"):
            print(f"❌ Failed to start {app.name}: {process_id}")
            return False
        
        self.running_processes[app_id] = {
            "process_id": process_id,
            "started_at": time.time(),
            "script": str(run_script),
            "status": "running"
        }
        
        print(f"✅ {app.name} started successfully")
        return True
    
    def stop_app(self, app_id: str) -> bool:
        """Stop a running application."""
        if app_id not in self.running_processes:
            print(f"❌ App {app_id} is not running")
            return False
        
        process_info = self.running_processes[app_id]
        process_id = process_info["process_id"]
        
        if self.shell_runner.stop_process(process_id):
            del self.running_processes[app_id]
            
            # Stop any associated tunnels
            if app_id in self.active_tunnels:
                self.stop_tunnel(app_id)
            
            print(f"✅ App {app_id} stopped")
            return True
        else:
            print(f"❌ Failed to stop app {app_id}")
            return False
    
    def create_tunnel(self, app_id: str, tunnel_name: Optional[str] = None) -> Optional[str]:
        """Create a tunnel for an application."""
        if app_id not in self.running_processes:
            print(f"❌ App {app_id} is not running")
            return None
        
        app = self.database.get_app(app_id)
        if not app:
            return None
        
        # Generate tunnel name
        tunnel_name = tunnel_name or f"{app.name}_{app_id}"
        
        # Create tunnel (assume app runs on port 3000 for now)
        tunnel_url = self.cloudflare_manager.create_tunnel(3000, tunnel_name)
        
        if tunnel_url:
            self.active_tunnels[app_id] = {
                "url": tunnel_url,
                "name": tunnel_name,
                "created_at": time.time()
            }
            print(f"✅ Tunnel created for {app.name}: {tunnel_url}")
            return tunnel_url
        else:
            print(f"❌ Failed to create tunnel for {app.name}")
            return None
    
    def stop_tunnel(self, app_id: str) -> bool:
        """Stop a tunnel for an application."""
        if app_id not in self.active_tunnels:
            print(f"❌ No active tunnel for app {app_id}")
            return False
        
        tunnel_info = self.active_tunnels[app_id]
        tunnel_name = tunnel_info["name"]
        
        if self.cloudflare_manager.stop_tunnel(tunnel_name):
            del self.active_tunnels[app_id]
            print(f"✅ Tunnel stopped for app {app_id}")
            return True
        else:
            print(f"❌ Failed to stop tunnel for app {app_id}")
            return False
    
    def get_installation_status(self, app_id: str) -> str:
        """Get installation status of an app."""
        app = self.database.get_app(app_id)
        if not app:
            return "not_found"
        
        if app.installed:
            return "completed"
        
        if app_id in self.active_installations:
            return self.active_installations[app_id]["status"]
        
        return "not_installed"
    
    def get_process_status(self, app_id: str) -> str:
        """Get process status of an app."""
        if app_id not in self.running_processes:
            return "stopped"
        
        process_info = self.running_processes[app_id]
        process_id = process_info["process_id"]
        
        status = self.shell_runner.get_process_status(process_id)
        if status and status["running"]:
            return "running"
        else:
            # Clean up dead process
            del self.running_processes[app_id]
            return "stopped"
    
    def get_tunnel_status(self, app_id: str) -> str:
        """Get tunnel status of an app."""
        if app_id not in self.active_tunnels:
            return "inactive"
        
        tunnel_info = self.active_tunnels[app_id]
        tunnel_name = tunnel_info["name"]
        
        status = self.cloudflare_manager.get_tunnel_status(tunnel_name)
        return status.get("status", "inactive")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "apps_count": len(self.database.get_all_apps()),
            "installed_apps": len(self.database.get_installed_apps()),
            "running_apps": len(self.running_processes),
            "active_tunnels": len(self.active_tunnels),
            "active_installations": len(self.active_installations),
            "categories": self.database.get_categories(),
            "shell_runner_active": len(self.shell_runner.list_active_processes()),
            "cloudflare_tunnels": len(self.cloudflare_manager.list_active_tunnels())
        }
    
    def cleanup(self):
        """Clean up all resources."""
        print("🧹 Cleaning up App Manager...")
        
        # Stop all running apps
        running_apps = list(self.running_processes.keys())
        for app_id in running_apps:
            self.stop_app(app_id)
        
        # Stop all tunnels
        active_tunnels = list(self.active_tunnels.keys())
        for app_id in active_tunnels:
            self.stop_tunnel(app_id)
        
        # Clean up cloudflare manager
        self.cloudflare_manager.cleanup()
        
        print("✅ App Manager cleanup completed")

# Global instance
app_manager = AppManager()

def initialize_app_manager() -> bool:
    """Convenience function to initialize the app manager."""
    return app_manager.initialize()

if __name__ == "__main__":
    # Test the app manager
    print("Testing App Manager...")
    
    if initialize_app_manager():
        print("✅ App Manager initialized successfully")
        
        # Get system status
        status = app_manager.get_system_status()
        print(f"📊 System Status: {json.dumps(status, indent=2)}")
        
        # Get available apps
        apps = app_manager.get_apps()
        print(f"📱 Available apps: {len(apps)}")
        
        # Test getting app details
        if apps:
            app_id = apps[0].id
            details = app_manager.get_app_details(app_id)
            print(f"📋 App details for {app_id}: {len(details)} sections")
        
        # Cleanup
        app_manager.cleanup()
        
    else:
        print("❌ Failed to initialize App Manager")
    
    print("App Manager test completed!")