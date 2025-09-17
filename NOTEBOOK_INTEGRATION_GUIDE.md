# 🚀 SD-Pinnokio Notebook Integration Guide

This guide shows you how to launch and share your Next.js SD-Pinnokio interface from Jupyter/Colab notebooks with public tunneling.

## 📋 Quick Start

### Option 1: Simple Copy-Paste (Recommended)

**For Jupyter/Colab Notebooks:**

```python
# Copy this entire cell and run it in your notebook
import subprocess
import sys
import time
import urllib.request
from IPython.display import display, HTML, clear_output

def launch_sdpinnokio():
    print("🚀 Launching SD-Pinnokio...")
    
    # Step 1: Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok', 'qrcode', 'pillow'], check=True)
    
    # Step 2: Start Next.js server
    print("🌐 Starting Next.js server...")
    server_process = subprocess.Popen(['npm', 'run', 'dev'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(10)
    
    # Step 3: Create ngrok tunnel
    print("🌐 Creating tunnel...")
    from pyngrok import ngrok
    tunnel = ngrok.connect(3000)
    public_url = tunnel.public_url
    
    # Step 4: Generate QR code
    print("📱 Generating QR code...")
    import qrcode
    from io import BytesIO
    import base64
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(public_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Step 5: Display interface
    clear_output(wait=True)
    display(HTML(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h1 style="color: white; text-align: center;">🚀 SD-Pinnokio is Live!</h1>
        
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3>📱 Your Application is Available At:</h3>
            <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace;">
                <a href="{public_url}" target="_blank">{public_url}</a>
            </div>
            <button onclick="navigator.clipboard.writeText('{public_url}')" 
                    style="background: #667eea; color: white; border: none; 
                           padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">
                📋 Copy URL
            </button>
            <button onclick="window.open('{public_url}', '_blank')" 
                    style="background: #28a745; color: white; border: none; 
                           padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">
                🌐 Open in New Tab
            </button>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0; text-align: center;">
            <h3>📱 Scan QR Code for Mobile Access:</h3>
            <img src="data:image/png;base64,{img_str}" style="max-width: 200px; margin: 10px;" />
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
            <h4 style="color: white;">💡 Tips:</h4>
            <ul style="color: white; padding-left: 20px;">
                <li>Bookmark the URL for easy access</li>
                <li>Share the URL with collaborators</li>
                <li>Use the QR code for mobile access</li>
                <li>Keep this notebook running to maintain the tunnel</li>
            </ul>
        </div>
    </div>
    """))
    
    print(f"✅ SD-Pinnokio is running at: {public_url}")
    return public_url, server_process, tunnel

# Launch the application
public_url, server_process, tunnel = launch_sdpinnokio()
```

### Option 2: Advanced Integration

For more control and features, use the comprehensive integration script:

```python
# Download and run the comprehensive integration script
import urllib.request

url = "https://raw.githubusercontent.com/your-repo/sd-pinnokio/main/notebook-integration.py"
urllib.request.urlretrieve(url, "notebook-integration.py")

# Run the script
%run notebook-integration.py
```

## 🔧 Manual Setup (For Advanced Users)

### Step 1: Start the Next.js Server

```python
import subprocess
import time

# Start the Next.js development server
print("🚀 Starting Next.js server...")
server_process = subprocess.Popen(['npm', 'run', 'dev'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)

# Wait for server to start
time.sleep(10)
print("✅ Server started!")
```

### Step 2: Create a Tunnel

#### Option A: ngrok (Easiest)

```python
# Install ngrok
!pip install pyngrok

# Create tunnel
from pyngrok import ngrok
tunnel = ngrok.connect(3000)
public_url = tunnel.public_url
print(f"🌐 Public URL: {public_url}")
```

#### Option B: Cloudflare Tunnel

```python
# Download cloudflared
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
!chmod +x cloudflared

# Start tunnel
import subprocess
cloudflare_process = subprocess.Popen(['./cloudflared', 'tunnel', '--url', 'http://localhost:3000'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait and extract URL (you'll need to parse the output)
import time
time.sleep(10)
# Check cloudflare_process.stderr for the URL
```

#### Option C: Localtunnel

```python
# Install localtunnel
!pip install localtunnel

# Start tunnel
import subprocess
lt_process = subprocess.Popen(['lt', '--port', '3000'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for URL
import time
time.sleep(5)
# Check lt_process.stdout for the URL
```

### Step 3: Generate QR Code (Optional)

```python
# Install qrcode
!pip install qrcode[pil]

# Generate QR code
import qrcode
from io import BytesIO
import base64
from IPython.display import HTML

qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(public_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Display QR code
HTML(f'<img src="data:image/png;base64,{img_str}" style="max-width: 200px;">')
```

## 🌐 Different Tunneling Options

### 1. ngrok
- **Pros**: Very reliable, easy to use, provides web interface
- **Cons**: Requires free account, limited bandwidth
- **Best for**: Quick sharing and development

### 2. Cloudflare Tunnel
- **Pros**: Free, unlimited bandwidth, very reliable
- **Cons**: Requires binary download, more complex setup
- **Best for**: Production use and long-running tunnels

### 3. Localtunnel
- **Pros**: No account required, simple to use
- **Cons**: Less reliable, URLs change frequently
- **Best for**: Quick testing and temporary access

### 4. serveo.net
```python
# Alternative using serveo
import subprocess
serveo_process = subprocess.Popen(['ssh', '-R', '80:localhost:3000', 'serveo.net'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```

## 📱 Mobile Access

All tunneling methods provide URLs that work on mobile devices. Additionally:

1. **QR Codes**: Generate QR codes for easy mobile scanning
2. **Responsive Design**: The Next.js interface is mobile-friendly
3. **Progressive Web App**: Can be installed on mobile home screens

## 🔒 Security Considerations

1. **Public Access**: Tunnels make your local server publicly accessible
2. **Authentication**: Consider adding password protection to your app
3. **HTTPS**: Most tunneling services provide HTTPS automatically
4. **Temporary Use**: Tunnels are best for temporary development, not production

## 🛠 Troubleshooting

### Common Issues

**Port 3000 is already in use:**
```python
# Try a different port
!PORT=3001 npm run dev
# Then tunnel to port 3001
tunnel = ngrok.connect(3001)
```

**ngrok authentication error:**
```python
# Set ngrok auth token
!ngrok authtoken YOUR_AUTH_TOKEN
```

**Dependencies not installed:**
```python
# Install all required packages
!pip install pyngrok qrcode[pil] requests flask
```

**Server not starting:**
```python
# Check if package.json exists
import os
print("package.json exists:", os.path.exists("package.json"))

# Install dependencies if needed
if not os.path.exists("node_modules"):
    !npm install
```

## 🚀 Production Deployment

For production use, consider:

1. **Vercel**: Deploy Next.js app directly to Vercel
2. **Netlify**: Static hosting with serverless functions
3. **AWS/Google Cloud**: Full cloud deployment
4. **Docker**: Containerize the app for easy deployment

## 📚 Additional Resources

- [ngrok Documentation](https://ngrok.com/docs)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Jupyter Notebook Integration](https://jupyter-notebook.readthedocs.io/)

## 🎯 Best Practices

1. **Use Environment Variables**: Store configuration in environment variables
2. **Add Health Checks**: Monitor your application status
3. **Implement Logging**: Keep track of usage and errors
4. **Use HTTPS**: Always use HTTPS for production applications
5. **Monitor Resources**: Keep an eye on memory and CPU usage

---

This guide provides everything you need to launch and share your SD-Pinnokio interface from notebooks. Choose the method that best fits your needs and technical comfort level!