#!/usr/bin/env python3
"""
🚀 SD-PINNOKIO GOOGLE COLAB INTEGRATION

This script is optimized for Google Colab and provides a simple way to
launch and tunnel the Next.js SD-Pinnokio interface.

Usage in Colab:
    1. Upload this script to Colab or copy the content into a cell
    2. Run the cell
    3. Click the generated link to access your SD-Pinnokio interface
"""

import subprocess
import sys
import time
import urllib.request
from IPython.display import display, HTML, clear_output
import base64
import os

def install_dependencies():
    """Install required dependencies for Colab."""
    print("📦 Installing dependencies...")
    
    # Install Python packages
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok', 'qrcode', 'pillow'], 
                  check=True, capture_output=True)
    
    # Install Node.js if not present
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
    except:
        print("📥 Installing Node.js...")
        subprocess.run(['curl', '-fsSL', 'https://deb.nodesource.com/setup_18.x', '-o', 'nodesource_setup.sh'], 
                      check=True, capture_output=True)
        subprocess.run(['sudo', '-E', 'bash', 'nodesource_setup.sh'], check=True, capture_output=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nodejs'], check=True, capture_output=True)
    
    print("✅ Dependencies installed!")

def check_nextjs_project():
    """Check if we're in a Next.js project directory."""
    if not os.path.exists('package.json'):
        print("❌ Not in a Next.js project directory!")
        print("📁 Please make sure you're in the correct directory with package.json")
        return False
    
    print("✅ Next.js project detected!")
    return True

def start_nextjs_server():
    """Start the Next.js development server."""
    print("🌐 Starting Next.js server...")
    
    # Install npm dependencies
    if not os.path.exists('node_modules'):
        print("📦 Installing npm dependencies...")
        subprocess.run(['npm', 'install'], check=True, capture_output=True)
    
    # Start the server
    server_process = subprocess.Popen(['npm', 'run', 'dev'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     start_new_session=True)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(15)
    
    # Check if server is running
    try:
        response = urllib.request.urlopen('http://localhost:3000', timeout=5)
        if response.getcode() == 200:
            print("✅ Next.js server is running!")
            return server_process
    except:
        pass
    
    print("❌ Failed to start Next.js server")
    return None

def create_ngrok_tunnel():
    """Create an ngrok tunnel."""
    print("🌐 Creating ngrok tunnel...")
    
    try:
        from pyngrok import ngrok
        
        # Kill any existing ngrok processes
        try:
            ngrok.kill()
        except:
            pass
        
        # Create tunnel
        tunnel = ngrok.connect(3000)
        public_url = tunnel.public_url
        print(f"✅ ngrok tunnel created: {public_url}")
        return public_url, tunnel
        
    except Exception as e:
        print(f"❌ Error creating ngrok tunnel: {e}")
        return None, None

def generate_qr_code(url):
    """Generate QR code for the URL."""
    try:
        import qrcode
        from io import BytesIO
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return None

def display_interface(public_url, qr_code_url=None):
    """Display the Colab interface with tunnel information."""
    clear_output(wait=True)
    
    html = f"""
    <div style="background: linear-gradient(135deg, #4285f4 0%, #34a853 100%); 
                padding: 30px; border-radius: 20px; margin: 20px 0; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; font-size: 2.5em; margin: 0;">
                🚀 SD-Pinnokio is Live!
            </h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2em; margin: 10px 0;">
                Your AI Application Manager is ready to use
            </p>
        </div>
        
        <div style="background: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-top: 0;">📱 Your Application is Available At:</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; 
                        font-family: 'Courier New', monospace; font-size: 14px; 
                        word-break: break-all; margin: 15px 0; border: 2px solid #e9ecef;">
                <a href="{public_url}" target="_blank" style="color: #4285f4; text-decoration: none; font-weight: bold;">
                    {public_url}
                </a>
            </div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
                <button onclick="navigator.clipboard.writeText('{public_url}')" 
                        style="background: #4285f4; color: white; border: none; 
                               padding: 12px 24px; border-radius: 8px; cursor: pointer; 
                               font-size: 16px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    📋 Copy URL
                </button>
                
                <button onclick="window.open('{public_url}', '_blank')" 
                        style="background: #34a853; color: white; border: none; 
                               padding: 12px 24px; border-radius: 8px; cursor: pointer; 
                               font-size: 16px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    🌐 Open in New Tab
                </button>
            </div>
        </div>
    """
    
    if qr_code_url:
        html += f"""
        <div style="background: white; padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-top: 0;">📱 Scan QR Code for Mobile Access:</h3>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; display: inline-block; margin: 15px 0;">
                <img src="{qr_code_url}" style="max-width: 200px; border-radius: 10px;" />
            </div>
            <p style="color: #666; font-size: 14px; margin: 10px 0;">
                Scan with your phone camera to open the app instantly
            </p>
        </div>
        """
    
    html += f"""
        <div style="background: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-top: 0;">📊 Status Information:</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="background: #e8f5e8; padding: 15px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">✅</div>
                    <div style="font-weight: bold; color: #2e7d32;">Next.js Server</div>
                    <div style="font-size: 12px; color: #666;">Running on port 3000</div>
                </div>
                <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">🌐</div>
                    <div style="font-weight: bold; color: #1976d2;">Tunnel Type</div>
                    <div style="font-size: 12px; color: #666;">ngrok</div>
                </div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">🗄️</div>
                    <div style="font-weight: bold; color: #f57c00;">Database</div>
                    <div style="font-size: 12px; color: #666;">Seeded with sample apps</div>
                </div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 5px;">🎯</div>
                    <div style="font-weight: bold; color: #7b1fa2;">Interface</div>
                    <div style="font-size: 12px; color: #666;">Ready to use</div>
                </div>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h4 style="color: white; margin-top: 0;">💡 Pro Tips:</h4>
            <ul style="color: white; padding-left: 20px;">
                <li><strong>Bookmark the URL</strong> for easy access later</li>
                <li><strong>Share the URL</strong> with team members or collaborators</li>
                <li><strong>Use the QR code</strong> for quick mobile access</li>
                <li><strong>Keep this notebook running</strong> to maintain the tunnel</li>
                <li><strong>Try the mobile interface</strong> - it's fully responsive!</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p style="color: rgba(255,255,255,0.8); font-size: 14px;">
                🔄 The tunnel will remain active as long as this Colab notebook is running
            </p>
            <p style="color: rgba(255,255,255,0.8); font-size: 14px;">
                🛑 To stop the service, interrupt the runtime or close the notebook
            </p>
        </div>
    </div>
    """
    
    display(HTML(html))

def main():
    """Main function to launch SD-Pinnokio in Colab."""
    print("🚀 Initializing SD-Pinnokio Google Colab Integration...")
    print("=" * 60)
    
    try:
        # Step 1: Install dependencies
        install_dependencies()
        
        # Step 2: Check Next.js project
        if not check_nextjs_project():
            return
        
        # Step 3: Start Next.js server
        server_process = start_nextjs_server()
        if not server_process:
            return
        
        # Step 4: Create tunnel
        public_url, tunnel = create_ngrok_tunnel()
        if not public_url:
            return
        
        # Step 5: Generate QR code
        qr_code_url = generate_qr_code(public_url)
        
        # Step 6: Display interface
        display_interface(public_url, qr_code_url)
        
        print("\n✅ Setup complete! Your SD-Pinnokio interface is now publicly accessible.")
        print(f"🌐 Public URL: {public_url}")
        print("🔄 The tunnel will remain active as long as this Colab notebook is running.")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            try:
                server_process.terminate()
                tunnel.close()
                from pyngrok import ngrok
                ngrok.kill()
            except:
                pass
            print("✅ All services stopped. Thank you for using SD-Pinnokio!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# Run the main function
if __name__ == "__main__":
    main()