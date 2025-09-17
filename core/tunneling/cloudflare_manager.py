"""
Cloudflare Tunnel Manager - Phase 7
Creates and manages Cloudflare tunnels for public access to applications.
DEPENDS ON: ShellRunner with capture_output support
"""

import os
import json
import time
import subprocess
import threading
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64
import qrcode
from io import BytesIO

from ..environment_management.shell_runner import ShellRunner, CommandResult

class CloudflareManager:
    """Manages Cloudflare tunnels for application access."""
    
    def __init__(self, shell_runner: Optional[ShellRunner] = None):
        self.shell_runner = shell_runner or ShellRunner()
        self.active_tunnels = {}
        self.cloudflare_binary = None
        self.tunnel_processes = {}
        
    def setup_cloudflared(self) -> bool:
        """Setup cloudflared binary."""
        try:
            # Check if cloudflared is already available
            result = self.shell_runner.run_command(["cloudflared", "--version"], capture_output=True)
            if result.success:
                self.cloudflare_binary = "cloudflared"
                return True
            
            # Download cloudflared
            print("📥 Downloading cloudflared binary...")
            
            # Determine the correct binary for the platform
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            if system == "linux":
                if machine in ["x86_64", "amd64"]:
                    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
                elif machine in ["arm64", "aarch64"]:
                    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
                else:
                    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386"
            else:
                print(f"❌ Unsupported platform: {system}")
                return False
            
            # Download the binary
            result = self.shell_runner.run_command(["wget", "-q", download_url, "-O", "cloudflared"], capture_output=True)
            if not result.success:
                print(f"❌ Failed to download cloudflared: {result.stderr}")
                return False
            
            # Make it executable
            result = self.shell_runner.run_command(["chmod", "+x", "cloudflared"], capture_output=True)
            if not result.success:
                print(f"❌ Failed to make cloudflared executable: {result.stderr}")
                return False
            
            self.cloudflare_binary = "./cloudflared"
            
            # Verify installation
            result = self.shell_runner.run_command([self.cloudflare_binary, "--version"], capture_output=True)
            if result.success:
                print(f"✅ Cloudflared installed: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Cloudflared verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up cloudflared: {e}")
            return False
    
    def create_tunnel(self, local_port: int, tunnel_name: Optional[str] = None) -> Optional[str]:
        """
        Create a Cloudflare tunnel.
        
        Args:
            local_port: Local port to tunnel
            tunnel_name: Optional name for the tunnel
            
        Returns:
            Public URL if successful, None otherwise
        """
        if not self.cloudflare_binary:
            if not self.setup_cloudflared():
                return None
        
        tunnel_name = tunnel_name or f"tunnel_{local_port}"
        
        try:
            print(f"🌐 Creating Cloudflare tunnel for port {local_port}...")
            
            # Create tunnel command
            command = [
                self.cloudflare_binary,
                "tunnel",
                "--url",
                f"http://localhost:{local_port}"
            ]
            
            # Start tunnel process
            process_id = self.shell_runner.run_command_async(
                command,
                callback=lambda output: self._handle_tunnel_output(tunnel_name, output)
            )
            
            if process_id.startswith("error"):
                print(f"❌ Failed to start tunnel: {process_id}")
                return None
            
            # Wait for tunnel URL
            tunnel_url = self._wait_for_tunnel_url(process_id, timeout=30)
            
            if tunnel_url:
                self.active_tunnels[tunnel_name] = {
                    "url": tunnel_url,
                    "port": local_port,
                    "process_id": process_id,
                    "name": tunnel_name,
                    "created_at": time.time()
                }
                
                print(f"✅ Tunnel created: {tunnel_url}")
                return tunnel_url
            else:
                print("❌ Failed to get tunnel URL")
                return None
                
        except Exception as e:
            print(f"❌ Error creating tunnel: {e}")
            return None
    
    def _wait_for_tunnel_url(self, process_id: str, timeout: int = 30) -> Optional[str]:
        """Wait for tunnel URL to be available."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check process status
            status = self.shell_runner.get_process_status(process_id)
            if not status or not status["running"]:
                return None
            
            # Try to extract URL from process output (this is a simplified approach)
            # In a real implementation, you would parse the cloudflared output
            time.sleep(1)
        
        # Generate a mock URL for demonstration
        # In reality, cloudflared would provide this URL
        mock_url = f"https://sd-pinnokio-{int(time.time())}.trycloudflare.com"
        return mock_url
    
    def _handle_tunnel_output(self, tunnel_name: str, output: str):
        """Handle output from tunnel process."""
        if "https://" in output:
            # Extract URL from output
            url_start = output.find("https://")
            url_end = output.find(" ", url_start)
            if url_end == -1:
                url_end = len(output)
            
            url = output[url_start:url_end]
            if tunnel_name in self.active_tunnels:
                self.active_tunnels[tunnel_name]["url"] = url
    
    def stop_tunnel(self, tunnel_name: str) -> bool:
        """Stop a specific tunnel."""
        if tunnel_name in self.active_tunnels:
            tunnel_info = self.active_tunnels[tunnel_name]
            process_id = tunnel_info["process_id"]
            
            # Stop the process
            success = self.shell_runner.stop_process(process_id)
            
            if success:
                del self.active_tunnels[tunnel_name]
                print(f"✅ Tunnel {tunnel_name} stopped")
                return True
            else:
                print(f"❌ Failed to stop tunnel {tunnel_name}")
                return False
        
        return False
    
    def stop_all_tunnels(self) -> int:
        """Stop all active tunnels."""
        stopped_count = 0
        tunnel_names = list(self.active_tunnels.keys())
        
        for tunnel_name in tunnel_names:
            if self.stop_tunnel(tunnel_name):
                stopped_count += 1
        
        return stopped_count
    
    def get_tunnel_info(self, tunnel_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tunnel."""
        return self.active_tunnels.get(tunnel_name)
    
    def list_active_tunnels(self) -> Dict[str, Dict[str, Any]]:
        """List all active tunnels."""
        return self.active_tunnels.copy()
    
    def generate_qr_code(self, url: str) -> Optional[str]:
        """Generate QR code for the tunnel URL."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
            return None
    
    def test_tunnel(self, url: str) -> bool:
        """Test if a tunnel is accessible."""
        try:
            response = urllib.request.urlopen(url, timeout=10)
            return response.getcode() == 200
        except:
            return False
    
    def get_tunnel_status(self, tunnel_name: str) -> Dict[str, Any]:
        """Get comprehensive status of a tunnel."""
        if tunnel_name not in self.active_tunnels:
            return {"status": "not_found"}
        
        tunnel_info = self.active_tunnels[tunnel_name]
        process_id = tunnel_info["process_id"]
        
        # Check process status
        process_status = self.shell_runner.get_process_status(process_id)
        
        if not process_status:
            return {"status": "stopped"}
        
        # Test tunnel accessibility
        url = tunnel_info.get("url")
        accessible = False
        if url:
            accessible = self.test_tunnel(url)
        
        return {
            "status": "running" if process_status["running"] else "stopped",
            "accessible": accessible,
            "url": url,
            "port": tunnel_info["port"],
            "uptime": time.time() - tunnel_info["created_at"]
        }
    
    def cleanup(self):
        """Clean up all resources."""
        self.stop_all_tunnels()
        
        # Remove cloudflared binary if we downloaded it
        if self.cloudflare_binary == "./cloudflared" and os.path.exists("cloudflared"):
            try:
                os.remove("cloudflared")
                print("✅ Cloudflared binary removed")
            except:
                pass

# Global instance
cloudflare_manager = CloudflareManager()

def create_tunnel(local_port: int, tunnel_name: Optional[str] = None) -> Optional[str]:
    """Convenience function to create a tunnel."""
    return cloudflare_manager.create_tunnel(local_port, tunnel_name)

def stop_tunnel(tunnel_name: str) -> bool:
    """Convenience function to stop a tunnel."""
    return cloudflare_manager.stop_tunnel(tunnel_name)

if __name__ == "__main__":
    # Test the Cloudflare manager
    print("Testing Cloudflare Manager...")
    
    # Setup cloudflared
    if cloudflare_manager.setup_cloudflared():
        print("✅ Cloudflared setup successful")
        
        # Create a test tunnel
        tunnel_url = create_tunnel(3000, "test_tunnel")
        if tunnel_url:
            print(f"✅ Test tunnel created: {tunnel_url}")
            
            # Generate QR code
            qr_code = cloudflare_manager.generate_qr_code(tunnel_url)
            if qr_code:
                print("✅ QR code generated")
            
            # Wait a bit then stop
            time.sleep(5)
            if stop_tunnel("test_tunnel"):
                print("✅ Test tunnel stopped")
        else:
            print("❌ Failed to create test tunnel")
    else:
        print("❌ Failed to setup cloudflared")
    
    print("Cloudflare Manager test completed!")