#!/usr/bin/env python3
"""
🚀 SD-TAILNOKIO NOTEBOOK INTEGRATION SCRIPT

This script provides a simple way to launch the SD-Tailnokio interface
from Jupyter/Colab notebooks. It handles automatic setup, dependency installation,
and creates public tunnels for easy sharing.

Features:
- Direct Python interface (no Next.js required)
- Public tunnel creation (Cloudflare, ngrok, or localtunnel)
- QR code generation for mobile access
- Real-time status monitoring
- Easy copy-paste notebook integration

Usage in Jupyter/Colab:
    %run notebook-integration.py
    # OR
    exec(open('notebook-integration.py').read())
"""

import os
import sys
import json
import subprocess
import threading
import time
import tempfile
from pathlib import Path
import urllib.request
import urllib.parse
from IPython.display import display, HTML, clear_output
import base64

# Import core modules
from core.cloud_detection.cloud_detector import CloudDetector
from core.environment_management.shell_runner import ShellRunner
from core.app_database import AppDatabase
from core.app_manager import AppManager
from core.tunneling.cloudflare_manager import CloudflareManager

class NotebookTunnelManager:
    """Manage tunneling for SD-Tailnokio applications from notebooks."""
    
    def __init__(self):
        self.app_port = 8080
        self.tunnel_url = None
        self.tunnel_type = None
        self.processes = {}
        self.qr_code = None
        self.app_manager = None
        self.web_server_process = None
        
    def check_dependencies(self):
        """Check and install required dependencies."""
        print("🔍 Checking dependencies...")
        
        required_packages = ['requests', 'flask', 'flask-cors', 'qrcode', 'pillow']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully!")
        else:
            print("✅ All dependencies are already installed!")
    
    def setup_sd_tailnokio(self):
        """Setup SD-Tailnokio components."""
        print("🚀 Setting up SD-Tailnokio...")
        
        try:
            # Initialize core components
            self.cloud_detector = CloudDetector()
            self.shell_runner = ShellRunner()
            self.app_database = AppDatabase()
            self.app_manager = AppManager(self.shell_runner, self.app_database)
            self.cloudflare_manager = CloudflareManager()
            
            # Load applications
            print("📚 Loading application database...")
            apps_loaded = self.app_database.load_applications()
            print(f"✅ Loaded {apps_loaded} applications")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up SD-Tailnokio: {e}")
            return False
    
    def create_web_interface(self):
        """Create a simple web interface for SD-Tailnokio."""
        print("🌐 Creating web interface...")
        
        # Create a simple Flask web server
        web_app_code = '''
import json
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
sys.path.append('/tmp/sd-tailnokio')

from core.cloud_detection.cloud_detector import CloudDetector
from core.environment_management.shell_runner import ShellRunner
from core.app_database import AppDatabase
from core.app_manager import AppManager

app = Flask(__name__)
CORS(app)

# Initialize components
cloud_detector = CloudDetector()
shell_runner = ShellRunner()
app_database = AppDatabase()
app_manager = AppManager(shell_runner, app_database)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SD-Tailnokio - AI Application Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 { color: #667eea; margin-bottom: 10px; }
        .header p { color: #666; font-size: 18px; }
        .search-bar { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .search-bar input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e0e0e0; 
            border-radius: 8px; 
            font-size: 16px;
        }
        .search-bar input:focus { outline: none; border-color: #667eea; }
        .apps-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .app-card { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .app-card:hover { transform: translateY(-5px); }
        .app-card h3 { color: #667eea; margin-bottom: 10px; }
        .app-card p { color: #666; margin-bottom: 15px; }
        .app-card .category { 
            background: #f0f0f0; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px; 
            display: inline-block;
            margin-bottom: 10px;
        }
        .app-card .actions { display: flex; gap: 10px; }
        .btn { 
            padding: 8px 16px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 14px;
            transition: background-color 0.2s;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5a6fd8; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; }
        .status { 
            margin-top: 10px; 
            padding: 8px; 
            border-radius: 5px; 
            font-size: 12px;
        }
        .status.installed { background: #d4edda; color: #155724; }
        .status.running { background: #d1ecf1; color: #0c5460; }
        .status.available { background: #f8d7da; color: #721c24; }
        .loading { 
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: rgba(0,0,0,0.5); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            z-index: 1000;
        }
        .loading-content { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
        }
        .logs { 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 5px; 
            margin-top: 10px; 
            font-family: monospace; 
            font-size: 12px; 
            max-height: 200px; 
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SD-Tailnokio</h1>
            <p>AI Application Manager for Notebook Environments</p>
        </div>
        
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="🔍 Search applications..." onkeyup="searchApps()">
        </div>
        
        <div id="appsContainer" class="apps-grid">
            <!-- Apps will be loaded here -->
        </div>
    </div>
    
    <div id="loadingModal" class="loading" style="display: none;">
        <div class="loading-content">
            <h3>Processing...</h3>
            <p id="loadingText">Please wait...</p>
            <div id="logsContainer" class="logs" style="display: none;"></div>
        </div>
    </div>

    <script>
        let apps = [];
        
        async function loadApps() {
            try {
                const response = await fetch('/api/apps');
                apps = await response.json();
                displayApps(apps);
            } catch (error) {
                console.error('Error loading apps:', error);
            }
        }
        
        function displayApps(appsToDisplay) {
            const container = document.getElementById('appsContainer');
            container.innerHTML = '';
            
            appsToDisplay.forEach(app => {
                const statusClass = app.status === 'running' ? 'running' : 
                                  app.status === 'installed' ? 'installed' : 'available';
                const statusText = app.status === 'running' ? 'Running' : 
                                 app.status === 'installed' ? 'Installed' : 'Available';
                
                const appCard = document.createElement('div');
                appCard.className = 'app-card';
                appCard.innerHTML = `
                    <div class="category">${app.category}</div>
                    <h3>${app.name}</h3>
                    <p>${app.description}</p>
                    <div class="status ${statusClass}">${statusText}</div>
                    <div class="actions">
                        ${app.status === 'available' ? 
                            `<button class="btn btn-primary" onclick="installApp('${app.id}')">Install</button>` :
                            app.status === 'installed' ?
                            `<button class="btn btn-success" onclick="runApp('${app.id}')">Run</button>` :
                            `<button class="btn btn-primary" onclick="stopApp('${app.id}')">Stop</button>`
                        }
                    </div>
                `;
                container.appendChild(appCard);
            });
        }
        
        function searchApps() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const filteredApps = apps.filter(app => 
                app.name.toLowerCase().includes(searchTerm) ||
                app.description.toLowerCase().includes(searchTerm) ||
                app.category.toLowerCase().includes(searchTerm)
            );
            displayApps(filteredApps);
        }
        
        async function installApp(appId) {
            showLoading('Installing application...');
            try {
                const response = await fetch('/api/install', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ app_id: appId })
                });
                const result = await response.json();
                if (result.success) {
                    await loadApps();
                } else {
                    alert('Installation failed: ' + result.error);
                }
            } catch (error) {
                console.error('Error installing app:', error);
                alert('Installation failed');
            }
            hideLoading();
        }
        
        async function runApp(appId) {
            showLoading('Starting application...');
            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ app_id: appId })
                });
                const result = await response.json();
                if (result.success) {
                    await loadApps();
                } else {
                    alert('Failed to start app: ' + result.error);
                }
            } catch (error) {
                console.error('Error running app:', error);
                alert('Failed to start app');
            }
            hideLoading();
        }
        
        async function stopApp(appId) {
            showLoading('Stopping application...');
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ app_id: appId })
                });
                const result = await response.json();
                if (result.success) {
                    await loadApps();
                } else {
                    alert('Failed to stop app: ' + result.error);
                }
            } catch (error) {
                console.error('Error stopping app:', error);
                alert('Failed to stop app');
            }
            hideLoading();
        }
        
        function showLoading(text) {
            document.getElementById('loadingModal').style.display = 'flex';
            document.getElementById('loadingText').textContent = text;
        }
        
        function hideLoading() {
            document.getElementById('loadingModal').style.display = 'none';
        }
        
        // Load apps when page loads
        loadApps();
    </script>
</body>
</html>
''')

@app.route('/api/apps')
def get_apps():
    try:
        apps = app_database.get_all_apps()
        return jsonify([{
            'id': app.get('id', ''),
            'name': app.get('name', ''),
            'description': app.get('description', ''),
            'category': app.get('category', ''),
            'status': app.get('status', 'available')
        } for app in apps])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/install', methods=['POST'])
def install_app():
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        
        if not app_id:
            return jsonify({'error': 'App ID required'}), 400
        
        # Install the app
        success = app_manager.install_app(app_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Installation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run', methods=['POST'])
def run_app():
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        
        if not app_id:
            return jsonify({'error': 'App ID required'}), 400
        
        # Run the app
        success = app_manager.run_app(app_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to start app'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_app():
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        
        if not app_id:
            return jsonify({'error': 'App ID required'}), 400
        
        # Stop the app
        success = app_manager.stop_app(app_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to stop app'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
'''
        
        # Write the web app to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(web_app_code)
            web_app_path = f.name
        
        # Start the web server
        try:
            self.web_server_process = subprocess.Popen(
                [sys.executable, web_app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['web_server'] = self.web_server_process
            
            # Wait for server to start
            print("⏳ Waiting for web server to start...")
            time.sleep(5)
            
            # Check if server is running
            try:
                response = urllib.request.urlopen(f'http://localhost:{self.app_port}', timeout=5)
                if response.getcode() == 200:
                    print("✅ Web server is running!")
                    return True
            except:
                pass
            
            print("❌ Failed to start web server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting web server: {e}")
            return False
    
    def create_cloudflare_tunnel(self):
        """Create a Cloudflare tunnel."""
        print("🌐 Creating Cloudflare tunnel...")
        
        try:
            # Use the CloudflareManager from core
            success, tunnel_url = self.cloudflare_manager.create_tunnel(self.app_port)
            
            if success and tunnel_url:
                self.tunnel_url = tunnel_url
                self.tunnel_type = 'cloudflare'
                print(f"✅ Cloudflare tunnel created: {self.tunnel_url}")
                return True
            else:
                print("❌ Failed to create Cloudflare tunnel")
                return False
                
        except Exception as e:
            print(f"❌ Error creating Cloudflare tunnel: {e}")
            return False
    
    def create_ngrok_tunnel(self):
        """Create an ngrok tunnel."""
        print("🌐 Creating ngrok tunnel...")
        
        try:
            from pyngrok import ngrok
            
            # Start ngrok tunnel
            tunnel = ngrok.connect(self.app_port)
            self.tunnel_url = tunnel.public_url
            self.tunnel_type = 'ngrok'
            
            print(f"✅ ngrok tunnel created: {self.tunnel_url}")
            return True
            
        except ImportError:
            print("❌ pyngrok not installed. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok'], check=True)
            return self.create_ngrok_tunnel()
        except Exception as e:
            print(f"❌ Error creating ngrok tunnel: {e}")
            return False
    
    def create_localtunnel_tunnel(self):
        """Create a localtunnel tunnel."""
        print("🌐 Creating localtunnel tunnel...")
        
        try:
            # Install localtunnel if not present
            try:
                subprocess.run(['lt', '--version'], check=True, capture_output=True)
            except:
                print("📦 Installing localtunnel...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'localtunnel'], check=True)
            
            # Start tunnel
            process = subprocess.Popen(
                ['lt', '--port', str(self.app_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['localtunnel'] = process
            
            # Wait for tunnel URL
            print("⏳ Waiting for tunnel URL...")
            time.sleep(5)
            
            # Try to extract URL from output
            for _ in range(30):  # 30 second timeout
                output = process.stdout.readline()
                if output and 'https://' in output:
                    self.tunnel_url = output.strip()
                    self.tunnel_type = 'localtunnel'
                    print(f"✅ Localtunnel created: {self.tunnel_url}")
                    return True
                time.sleep(1)
            
            print("❌ Failed to create localtunnel")
            return False
            
        except Exception as e:
            print(f"❌ Error creating localtunnel: {e}")
            return False
    
    def generate_qr_code(self):
        """Generate QR code for the tunnel URL."""
        if not self.tunnel_url:
            return None
        
        try:
            import qrcode
            from io import BytesIO
            
            # Create QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.tunnel_url)
            qr.make(fit=True)
            
            # Generate image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            self.qr_code = f"data:image/png;base64,{img_str}"
            return self.qr_code
            
        except ImportError:
            print("📦 Installing qrcode...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'qrcode[pil]'], check=True)
            return self.generate_qr_code()
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
            return None
    
    def create_tunnel(self, tunnel_type='auto'):
        """Create a tunnel of the specified type."""
        if tunnel_type == 'auto':
            # Try different tunnel types in order of preference
            for t in ['cloudflare', 'ngrok', 'localtunnel']:
                if t == 'cloudflare' and self.create_cloudflare_tunnel():
                    break
                elif t == 'ngrok' and self.create_ngrok_tunnel():
                    break
                elif t == 'localtunnel' and self.create_localtunnel_tunnel():
                    break
        elif tunnel_type == 'cloudflare':
            self.create_cloudflare_tunnel()
        elif tunnel_type == 'ngrok':
            self.create_ngrok_tunnel()
        elif tunnel_type == 'localtunnel':
            self.create_localtunnel_tunnel()
        
        if self.tunnel_url:
            self.generate_qr_code()
            return True
        return False
    
    def display_interface(self):
        """Display the notebook interface with tunnel information."""
        clear_output(wait=True)
        
        html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; margin: 20px 0; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <h1 style="color: white; text-align: center; margin-bottom: 20px;">
                🚀 SD-Tailnokio is Live!
            </h1>
            
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>📱 Your Application is Available At:</h3>
                <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; 
                            font-family: monospace; word-break: break-all; margin: 10px 0;">
                    <a href="{self.tunnel_url}" target="_blank" style="color: #667eea; text-decoration: none;">
                        {self.tunnel_url}
                    </a>
                </div>
                
                <button onclick="navigator.clipboard.writeText('{self.tunnel_url}')" 
                        style="background: #667eea; color: white; border: none; 
                               padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">
                    📋 Copy URL
                </button>
                
                <button onclick="window.open('{self.tunnel_url}', '_blank')" 
                        style="background: #28a745; color: white; border: none; 
                               padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">
                    🌐 Open in New Tab
                </button>
            </div>
        """
        
        if self.qr_code:
            html += f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0; text-align: center;">
                <h3>📱 Scan QR Code for Mobile Access:</h3>
                <img src="{self.qr_code}" style="max-width: 200px; margin: 10px;" />
                <p style="font-size: 12px; color: #666;">Scan with your phone camera to open the app</p>
            </div>
            """
        
        html += f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3>📊 Status Information:</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>✅ Web Server: Running on port {self.app_port}</li>
                    <li>✅ Tunnel Type: {self.tunnel_type}</li>
                    <li>✅ Applications: {len(self.app_database.get_all_apps()) if self.app_database else 'Unknown'} loaded</li>
                    <li>✅ Interface: Ready to use</li>
                </ul>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4 style="color: white; margin-top: 0;">💡 Tips:</h4>
                <ul style="color: white; padding-left: 20px;">
                    <li>Bookmark the URL for easy access later</li>
                    <li>Share the URL with collaborators</li>
                    <li>Use the QR code for quick mobile access</li>
                    <li>The tunnel will remain active as long as this notebook is running</li>
                </ul>
            </div>
        </div>
        """
        
        display(HTML(html))
    
    def cleanup(self):
        """Clean up all processes."""
        print("🧹 Cleaning up processes...")
        for name, process in self.processes.items():
            try:
                process.terminate()
                print(f"✅ Terminated {name}")
            except:
                pass
        
        # Kill ngrok tunnels if using ngrok
        if self.tunnel_type == 'ngrok':
            try:
                from pyngrok import ngrok
                ngrok.kill()
                print("✅ Terminated ngrok")
            except:
                pass

def main():
    """Main function to launch the SD-Tailnokio interface."""
    print("🚀 Initializing SD-Tailnokio Notebook Integration...")
    print("=" * 60)
    
    manager = NotebookTunnelManager()
    
    try:
        # Step 1: Check dependencies
        manager.check_dependencies()
        
        # Step 2: Setup SD-Tailnokio
        if not manager.setup_sd_tailnokio():
            print("❌ Failed to setup SD-Tailnokio")
            return
        
        # Step 3: Create web interface
        if not manager.create_web_interface():
            print("❌ Failed to create web interface")
            return
        
        # Step 4: Create tunnel
        print("🌐 Creating public tunnel...")
        if not manager.create_tunnel():
            print("❌ Failed to create tunnel")
            return
        
        # Step 5: Display interface
        manager.display_interface()
        
        print("\n✅ Setup complete! Your SD-Tailnokio interface is now publicly accessible.")
        print("🔄 The tunnel will remain active as long as this notebook is running.")
        print("🛑 To stop the service, interrupt the kernel or close the notebook.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            manager.cleanup()
            print("✅ All processes have been stopped. Thank you for using SD-Tailnokio!")
    
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        manager.cleanup()

if __name__ == "__main__":
    main()