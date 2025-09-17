"""
App Database Module - Phase 3
Manages the local database of available Pinokio applications.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class PinokioApp:
    """Data class for Pinokio application information."""
    id: str
    name: str
    description: str
    category: str
    repo_url: str
    tags: List[str]
    vram: Optional[int] = None
    install_script: Optional[str] = None
    run_script: Optional[str] = None
    dependencies: Optional[List[str]] = None
    webui_type: Optional[str] = None
    installed: bool = False
    last_updated: Optional[float] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = time.time()

class AppDatabase:
    """Manages the local database of Pinokio applications."""
    
    def __init__(self, database_path: Optional[str] = None):
        self.database_path = database_path or "cleaned_pinokio_apps.json"
        self.apps: Dict[str, PinokioApp] = {}
        self.categories: Set[str] = set()
        self.tags: Set[str] = set()
        self.last_loaded = 0
        
    def load_database(self, force_reload: bool = False) -> bool:
        """
        Load the application database from JSON file.
        
        Args:
            force_reload: Force reload even if recently loaded
            
        Returns:
            True if successful, False otherwise
        """
        # Check if we need to reload
        current_time = time.time()
        if not force_reload and current_time - self.last_loaded < 300:  # 5 minutes cache
            return True
        
        try:
            if not os.path.exists(self.database_path):
                print(f"❌ Database file not found: {self.database_path}")
                return False
            
            print(f"📚 Loading app database from {self.database_path}...")
            
            with open(self.database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse apps
            self.apps.clear()
            self.categories.clear()
            self.tags.clear()
            
            for app_id, app_data in data.items():
                app = PinokioApp(
                    id=app_id,
                    name=app_data.get('name', app_id),
                    description=app_data.get('description', ''),
                    category=app_data.get('category', 'Unknown'),
                    repo_url=app_data.get('repo_url', ''),
                    tags=app_data.get('tags', []),
                    vram=app_data.get('vram'),
                    install_script=app_data.get('install_script'),
                    run_script=app_data.get('run_script'),
                    dependencies=app_data.get('dependencies'),
                    webui_type=app_data.get('webui_type'),
                    installed=app_data.get('installed', False),
                    last_updated=app_data.get('last_updated')
                )
                
                self.apps[app_id] = app
                self.categories.add(app.category)
                self.tags.update(app.tags)
            
            self.last_loaded = current_time
            print(f"✅ Loaded {len(self.apps)} applications")
            print(f"📂 Categories: {sorted(list(self.categories))}")
            print(f"🏷️  Total tags: {len(self.tags)}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in database file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return False
    
    def save_database(self) -> bool:
        """
        Save the application database to JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert apps to dictionary
            data = {}
            for app_id, app in self.apps.items():
                data[app_id] = asdict(app)
            
            # Create backup
            if os.path.exists(self.database_path):
                backup_path = f"{self.database_path}.backup"
                import shutil
                shutil.copy2(self.database_path, backup_path)
            
            # Save to file
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Database saved to {self.database_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving database: {e}")
            return False
    
    def get_app(self, app_id: str) -> Optional[PinokioApp]:
        """Get an application by ID."""
        return self.apps.get(app_id)
    
    def get_apps_by_category(self, category: str) -> List[PinokioApp]:
        """Get all applications in a specific category."""
        return [app for app in self.apps.values() if app.category == category]
    
    def get_apps_by_tag(self, tag: str) -> List[PinokioApp]:
        """Get all applications with a specific tag."""
        return [app for app in self.apps.values() if tag in app.tags]
    
    def search_apps(self, query: str) -> List[PinokioApp]:
        """Search applications by name or description."""
        query_lower = query.lower()
        results = []
        
        for app in self.apps.values():
            if (query_lower in app.name.lower() or 
                (app.description and query_lower in app.description.lower())):
                results.append(app)
        
        return results
    
    def get_all_apps(self) -> List[PinokioApp]:
        """Get all applications."""
        return list(self.apps.values())
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(list(self.categories))
    
    def get_tags(self) -> List[str]:
        """Get all unique tags."""
        return sorted(list(self.tags))
    
    def add_app(self, app: PinokioApp) -> bool:
        """Add a new application to the database."""
        if app.id in self.apps:
            print(f"⚠️ App with ID {app.id} already exists")
            return False
        
        self.apps[app.id] = app
        self.categories.add(app.category)
        self.tags.update(app.tags)
        
        return self.save_database()
    
    def update_app(self, app_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing application."""
        if app_id not in self.apps:
            print(f"❌ App with ID {app_id} not found")
            return False
        
        app = self.apps[app_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(app, key):
                setattr(app, key, value)
        
        app.last_updated = time.time()
        
        return self.save_database()
    
    def delete_app(self, app_id: str) -> bool:
        """Delete an application from the database."""
        if app_id not in self.apps:
            print(f"❌ App with ID {app_id} not found")
            return False
        
        app = self.apps[app_id]
        self.apps.pop(app_id)
        
        # Update categories and tags
        self.categories.clear()
        self.tags.clear()
        for remaining_app in self.apps.values():
            self.categories.add(remaining_app.category)
            self.tags.update(remaining_app.tags)
        
        return self.save_database()
    
    def get_installed_apps(self) -> List[PinokioApp]:
        """Get all installed applications."""
        return [app for app in self.apps.values() if app.installed]
    
    def set_app_installed(self, app_id: str, installed: bool) -> bool:
        """Set the installation status of an application."""
        return self.update_app(app_id, {"installed": installed})
    
    def get_apps_by_vram_requirement(self, max_vram: Optional[int] = None) -> List[PinokioApp]:
        """Get applications filtered by VRAM requirement."""
        if max_vram is None:
            return self.get_all_apps()
        
        return [app for app in self.apps.values() 
                if app.vram is None or app.vram <= max_vram]
    
    def get_apps_by_webui_type(self, webui_type: str) -> List[PinokioApp]:
        """Get applications by web UI type."""
        return [app for app in self.apps.values() if app.webui_type == webui_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        total_apps = len(self.apps)
        installed_apps = len(self.get_installed_apps())
        categories_count = len(self.categories)
        tags_count = len(self.tags)
        
        # Apps by category
        apps_by_category = {}
        for category in self.categories:
            apps_by_category[category] = len(self.get_apps_by_category(category))
        
        # Apps by webui type
        webui_types = {}
        for app in self.apps.values():
            if app.webui_type:
                webui_types[app.webui_type] = webui_types.get(app.webui_type, 0) + 1
        
        # VRAM distribution
        vram_distribution = {"unknown": 0}
        for app in self.apps.values():
            if app.vram:
                vram_range = f"{(app.vram // 4096) * 4096}-{((app.vram // 4096) + 1) * 4096 - 1}"
                vram_distribution[vram_range] = vram_distribution.get(vram_range, 0) + 1
            else:
                vram_distribution["unknown"] += 1
        
        return {
            "total_apps": total_apps,
            "installed_apps": installed_apps,
            "categories_count": categories_count,
            "tags_count": tags_count,
            "apps_by_category": apps_by_category,
            "webui_types": webui_types,
            "vram_distribution": vram_distribution,
            "last_updated": self.last_loaded
        }
    
    def validate_database(self) -> Dict[str, Any]:
        """Validate the database and return validation results."""
        errors = []
        warnings = []
        
        # Check required fields
        for app_id, app in self.apps.items():
            if not app.name:
                errors.append(f"App {app_id}: Missing name")
            if not app.repo_url:
                errors.append(f"App {app_id}: Missing repo_url")
            if not app.category:
                warnings.append(f"App {app_id}: Missing category")
            
            # Validate URL format
            if app.repo_url and not app.repo_url.startswith(('http://', 'https://')):
                warnings.append(f"App {app_id}: Invalid repo_url format")
        
        # Check for duplicate names
        names = {}
        for app_id, app in self.apps.items():
            if app.name in names:
                errors.append(f"Duplicate app name: {app.name} ({app_id} and {names[app.name]})")
            else:
                names[app.name] = app_id
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_apps": len(self.apps)
        }
    
    def export_database(self, export_path: str, format_type: str = "json") -> bool:
        """Export database to different formats."""
        try:
            if format_type.lower() == "json":
                data = {app_id: asdict(app) for app_id, app in self.apps.items()}
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format_type.lower() == "csv":
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Description', 'Category', 'Repo URL', 'Tags', 'VRAM', 'WebUI Type'])
                    
                    for app_id, app in self.apps.items():
                        writer.writerow([
                            app_id, app.name, app.description, app.category,
                            app.repo_url, ','.join(app.tags), app.vram or '', app.webui_type or ''
                        ])
            
            else:
                print(f"❌ Unsupported export format: {format_type}")
                return False
            
            print(f"✅ Database exported to {export_path} ({format_type})")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting database: {e}")
            return False

# Global instance
app_database = AppDatabase()

def load_database(force_reload: bool = False) -> bool:
    """Convenience function to load the database."""
    return app_database.load_database(force_reload)

def get_app(app_id: str) -> Optional[PinokioApp]:
    """Convenience function to get an app."""
    return app_database.get_app(app_id)

def get_all_apps() -> List[PinokioApp]:
    """Convenience function to get all apps."""
    return app_database.get_all_apps()

if __name__ == "__main__":
    # Test the app database
    print("Testing App Database...")
    
    # Load database
    if load_database():
        print("✅ Database loaded successfully")
        
        # Get statistics
        stats = app_database.get_statistics()
        print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
        
        # Validate database
        validation = app_database.validate_database()
        print(f"✅ Validation: {validation}")
        
        # Search test
        search_results = app_database.search_apps("stable")
        print(f"🔍 Search results for 'stable': {len(search_results)} apps")
        
        # Export test
        app_database.export_database("test_export.json", "json")
        
    else:
        print("❌ Failed to load database")
    
    print("App Database test completed!")