#!/usr/bin/env python3
"""
🚀 SD-TAILNOKIO COLAB SIMPLE SETUP

This is a simplified Colab setup script that can be copied and pasted directly into Colab.
It handles all setup and provides multiple launch options.

Usage in Colab:
    1. Copy this entire script
    2. Paste it into a Colab cell
    3. Run the cell
    4. Choose your preferred launch option
"""

import os
import sys
import subprocess
import threading
import time
from IPython.display import clear_output, HTML, display
import ipywidgets as widgets

# Repository information
REPO_URL = "https://github.com/remphanostar/SD-Tailnokio.git"
REPO_DIR = "/content/SD-Tailnokio"

def run_command(cmd, description=""):
    """Run a command and display output."""
    if description:
        print(f"\n📋 {description}")
    print(f"🔧 Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("✅ Output:")
        print(result.stdout)
    
    if result.stderr:
        print("❌ Errors:")
        print(result.stderr)
    
    return result.returncode == 0

def setup_repository():
    """Setup or update the repository."""
    print("🚀 Setting up SD-Tailnokio...")
    print("=" * 50)
    
    # Remove existing repository if it exists
    if os.path.exists(REPO_DIR):
        print("🗑️ Removing existing repository...")
        subprocess.run(["rm", "-rf", REPO_DIR], check=True)
        print("✅ Existing repository removed")
    
    # Clone the repository
    print("\n📥 Cloning SD-Tailnokio repository...")
    success = run_command(f"git clone {REPO_URL} {REPO_DIR}", "Cloning repository")
    
    if not success:
        print("❌ Failed to clone repository")
        return False
    
    # Change to repository directory
    os.chdir(REPO_DIR)
    print(f"\n📁 Changed to directory: {os.getcwd()}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    success = run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages")
    
    if not success:
        print("❌ Failed to install dependencies")
        return False
    
    # Install additional dependencies
    additional_deps = [
        "flask", "flask-cors", "requests", "qrcode[pil]", 
        "pyngrok", "psutil", "ipywidgets"
    ]
    
    for dep in additional_deps:
        run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}")
    
    print("\n✅ Setup completed successfully!")
    return True

def launch_option_1():
    """Launch Option 1: Full Web Interface"""
    print("\n🌐 Starting Full Web Interface...")
    try:
        exec(open('notebook-integration.py').read())
    except Exception as e:
        print(f"❌ Error: {e}")

def launch_option_2():
    """Launch Option 2: Jupyter Notebook Interface"""
    print("\n📓 Starting Jupyter Notebook Interface...")
    try:
        %load_ext ipywidgets
        %run SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb
    except Exception as e:
        print(f"❌ Error: {e}")

def launch_option_3():
    """Launch Option 3: Simplified Python Interface"""
    print("\n🐍 Starting Simplified Python Interface...")
    try:
        exec(open('SD_PINNOKIO_SIMPLE_INTERFACE.py').read())
    except Exception as e:
        print(f"❌ Error: {e}")

def launch_option_4():
    """Launch Option 4: Direct API Access"""
    print("\n🎯 Setting up Direct API Access...")
    try:
        from core.cloud_detection.cloud_detector import CloudDetector
        from core.environment_management.shell_runner import ShellRunner
        from core.app_database import AppDatabase
        from core.app_manager import AppManager
        
        cloud_detector = CloudDetector()
        shell_runner = ShellRunner()
        app_database = AppDatabase()
        app_manager = AppManager(shell_runner, app_database)
        
        apps_loaded = app_database.load_applications()
        print(f"✅ Loaded {apps_loaded} applications")
        
        apps = app_database.get_all_apps()
        print(f"\n📚 Available Applications (first 10):")
        for i, app in enumerate(apps[:10]):
            print(f"{i+1}. {app.get('name', 'Unknown')} - {app.get('category', 'Unknown')}")
        
        print("\n💡 Example usage:")
        print("search_results = app_database.search_apps('text to image')")
        print("success = app_manager.install_app('stable-diffusion-webui')")
        print("success = app_manager.run_app('stable-diffusion-webui')")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def launch_option_5():
    """Launch Option 5: Next.js Environment"""
    print("\n🔄 Setting up Next.js Environment...")
    
    nextjs_dir = "/content/nextjs-sd-tailnokio"
    
    # Remove existing Next.js project
    if os.path.exists(nextjs_dir):
        subprocess.run(["rm", "-rf", nextjs_dir], check=True)
    
    # Create Next.js project
    try:
        subprocess.run([
            "npx", "create-next-app@latest", nextjs_dir,
            "--typescript", "--tailwind", "--eslint", "--app", "--src-dir", "--import-alias", "@/*"
        ], check=True, capture_output=True)
        
        os.chdir(nextjs_dir)
        print(f"📁 Next.js project created at: {os.getcwd()}")
        
        # Install additional dependencies
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        
        # Start development server
        print("\n🚀 Starting Next.js development server...")
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(10)
        
        display(HTML(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h1 style="color: white; text-align: center;">
                🚀 Next.js Development Server Started!
            </h1>
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>📱 Your Next.js App is Available At:</h3>
                <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace;">
                    <a href="http://localhost:3000" target="_blank" style="color: #667eea;">
                        http://localhost:3000
                    </a>
                </div>
            </div>
        </div>
        """))
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function with interactive menu."""
    print("🚀 SD-Tailnokio Colab Setup")
    print("=" * 50)
    
    # Setup repository
    if not setup_repository():
        print("❌ Setup failed!")
        return
    
    # Create interactive menu
    print("\n" + "=" * 50)
    print("🚀 Choose a launch option:")
    print("=" * 50)
    
    # Create buttons for each option
    button_layout = widgets.Layout(width='300px', height='50px')
    
    btn1 = widgets.Button(description="🌐 Full Web Interface (Recommended)", layout=button_layout)
    btn2 = widgets.Button(description="📓 Jupyter Notebook Interface", layout=button_layout)
    btn3 = widgets.Button(description="🐍 Simplified Python Interface", layout=button_layout)
    btn4 = widgets.Button(description="🎯 Direct API Access", layout=button_layout)
    btn5 = widgets.Button(description="🔄 Next.js Environment", layout=button_layout)
    
    # Button click handlers
    def on_btn1_click(b):
        clear_output(wait=True)
        launch_option_1()
    
    def on_btn2_click(b):
        clear_output(wait=True)
        launch_option_2()
    
    def on_btn3_click(b):
        clear_output(wait=True)
        launch_option_3()
    
    def on_btn4_click(b):
        clear_output(wait=True)
        launch_option_4()
    
    def on_btn5_click(b):
        clear_output(wait=True)
        launch_option_5()
    
    # Attach handlers
    btn1.on_click(on_btn1_click)
    btn2.on_click(on_btn2_click)
    btn3.on_click(on_btn3_click)
    btn4.on_click(on_btn4_click)
    btn5.on_click(on_btn5_click)
    
    # Display buttons
    print("Click a button to choose your launch option:")
    display(widgets.VBox([
        btn1, btn2, btn3, btn4, btn5
    ]))
    
    print("\n💡 Tips:")
    print("- Option 1 is recommended for most users")
    print("- Option 5 creates a complete Next.js environment")
    print("- You can run this cell multiple times to try different options")

if __name__ == "__main__":
    main()