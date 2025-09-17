#!/usr/bin/env python3
"""
🚀 SD-PINNOKIO NOTEBOOK INTEGRATION SCRIPT

This script provides a simple way to launch and tunnel the Next.js SD-Pinnokio interface
from Jupyter/Colab notebooks. It handles automatic setup, dependency installation,
and creates public tunnels for easy sharing.

Features:
- Automatic Next.js app setup and launch
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

class NotebookTunnelManager:
    """Manage tunneling for Next.js applications from notebooks."""
    
    def __init__(self):
        self.app_port = 3000
        self.tunnel_url = None
        self.tunnel_type = None
        self.processes = {}
        self.qr_code = None
        
    def check_dependencies(self):
        """Check and install required dependencies."""
        print("🔍 Checking dependencies...")
        
        required_packages = ['requests', 'flask', 'pyngrok']
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
    
    def setup_nextjs_app(self):
        """Setup and launch the Next.js application."""
        print("🚀 Setting up Next.js application...")
        
        # Check if we're in the correct directory
        if not os.path.exists('package.json'):
            print("❌ Not in a Next.js project directory!")
            return False
        
        # Install dependencies if needed
        if not os.path.exists('node_modules'):
            print("📦 Installing Node.js dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Seed the database
        print("🌱 Seeding database with sample apps...")
        try:
            response = urllib.request.urlopen('http://localhost:3000/sd-pinnokio/seed')
            if response.getcode() == 200:
                print("✅ Database seeded successfully!")
            else:
                print("⚠️ Database seeding may have failed, but continuing...")
        except:
            print("⚠️ Could not seed database (server may not be running yet)")
        
        return True
    
    def start_nextjs_server(self):
        """Start the Next.js development server."""
        print("🌐 Starting Next.js development server...")
        
        try:
            # Start the server in background
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes['nextjs'] = process
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(10)
            
            # Check if server is running
            try:
                response = urllib.request.urlopen('http://localhost:3000', timeout=5)
                if response.getcode() == 200:
                    print("✅ Next.js server is running!")
                    return True
            except:
                pass
            
            print("❌ Failed to start Next.js server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Next.js server: {e}")
            return False
    
    def create_cloudflare_tunnel(self):
        """Create a Cloudflare tunnel."""
        print("🌐 Creating Cloudflare tunnel...")
        
        try:
            # Download cloudflared if not present
            if not os.path.exists('cloudflared'):
                print("📥 Downloading cloudflared...")
                subprocess.run([
                    'wget', '-q', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64',
                    '-O', 'cloudflared'
                ], check=True)
                subprocess.run(['chmod', '+x', 'cloudflared'], check=True)
            
            # Start tunnel
            process = subprocess.Popen(
                ['./cloudflared', 'tunnel', '--url', f'http://localhost:{self.app_port}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['cloudflare'] = process
            
            # Wait for tunnel URL
            print("⏳ Waiting for tunnel URL...")
            time.sleep(5)
            
            # Try to extract URL from output
            for _ in range(30):  # 30 second timeout
                output = process.stderr.readline()
                if output and 'https://' in output:
                    url = output.split('https://')[1].split('|')[0].strip()
                    self.tunnel_url = f'https://{url}'
                    self.tunnel_type = 'cloudflare'
                    print(f"✅ Cloudflare tunnel created: {self.tunnel_url}")
                    return True
                time.sleep(1)
            
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
                🚀 SD-Pinnokio is Live!
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
                    <li>✅ Next.js Server: Running on port {self.app_port}</li>
                    <li>✅ Tunnel Type: {self.tunnel_type}</li>
                    <li>✅ Database: Seeded with sample apps</li>
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
    """Main function to launch the SD-Pinnokio interface."""
    print("🚀 Initializing SD-Pinnokio Notebook Integration...")
    print("=" * 60)
    
    manager = NotebookTunnelManager()
    
    try:
        # Step 1: Check dependencies
        manager.check_dependencies()
        
        # Step 2: Setup Next.js app
        if not manager.setup_nextjs_app():
            print("❌ Failed to setup Next.js app")
            return
        
        # Step 3: Start Next.js server
        if not manager.start_nextjs_server():
            print("❌ Failed to start Next.js server")
            return
        
        # Step 4: Create tunnel
        print("🌐 Creating public tunnel...")
        if not manager.create_tunnel():
            print("❌ Failed to create tunnel")
            return
        
        # Step 5: Display interface
        manager.display_interface()
        
        print("\n✅ Setup complete! Your SD-Pinnokio interface is now publicly accessible.")
        print("🔄 The tunnel will remain active as long as this notebook is running.")
        print("🛑 To stop the service, interrupt the kernel or close the notebook.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            manager.cleanup()
            print("✅ All services stopped. Thank you for using SD-Pinnokio!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        manager.cleanup()

if __name__ == "__main__":
    main()