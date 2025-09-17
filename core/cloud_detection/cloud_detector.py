"""
Cloud Detection Module - Phase 1
Detects the current cloud platform and environment for optimal configuration.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

class CloudDetector:
    """Detects the current cloud platform and environment."""
    
    def __init__(self):
        self.platform = "unknown"
        self.platform_info = {}
        self.base_path = "/workspace"
        
    def detect_platform(self) -> str:
        """Detect the current cloud platform."""
        # Check for Google Colab
        if 'COLAB_GPU' in os.environ:
            self.platform = "colab"
            self.platform_info = {
                "type": "colab",
                "gpu_available": True,
                "base_path": "/content",
                "storage_path": "/content/drive"
            }
            return self.platform
            
        # Check for Vast.ai
        if os.path.exists('/workspace') and os.path.exists('/vast'):
            self.platform = "vast"
            self.platform_info = {
                "type": "vast",
                "gpu_available": True,
                "base_path": "/workspace",
                "storage_path": "/workspace"
            }
            return self.platform
            
        # Check for Lightning.ai
        if 'LIGHTNING_AI_PORT' in os.environ:
            self.platform = "lightning"
            self.platform_info = {
                "type": "lightning",
                "gpu_available": True,
                "base_path": "/teamspace",
                "storage_path": "/teamspace/studios"
            }
            return self.platform
            
        # Check for Paperspace
        if os.path.exists('/paperspace'):
            self.platform = "paperspace"
            self.platform_info = {
                "type": "paperspace",
                "gpu_available": True,
                "base_path": "/notebooks",
                "storage_path": "/notebooks"
            }
            return self.platform
            
        # Check for RunPod
        if 'RUNPOD_API_KEY' in os.environ:
            self.platform = "runpod"
            self.platform_info = {
                "type": "runpod",
                "gpu_available": True,
                "base_path": "/runpod",
                "storage_path": "/runpod"
            }
            return self.platform
            
        # Default to local environment
        self.platform = "local"
        self.platform_info = {
            "type": "local",
            "gpu_available": False,
            "base_path": os.getcwd(),
            "storage_path": os.getcwd()
        }
        return self.platform
    
    def get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration."""
        self.detect_platform()
        
        configs = {
            "colab": {
                "python_path": "/usr/bin/python3",
                "pip_path": "/usr/bin/pip3",
                "git_path": "/usr/bin/git",
                "use_gpu": True,
                "mount_drive": True
            },
            "vast": {
                "python_path": "/usr/bin/python3",
                "pip_path": "/usr/bin/pip3",
                "git_path": "/usr/bin/git",
                "use_gpu": True,
                "ssl_cert": True
            },
            "lightning": {
                "python_path": "/usr/bin/python3",
                "pip_path": "/usr/bin/pip3",
                "git_path": "/usr/bin/git",
                "use_gpu": True,
                "team_mode": True
            },
            "paperspace": {
                "python_path": "/opt/conda/bin/python",
                "pip_path": "/opt/conda/bin/pip",
                "git_path": "/usr/bin/git",
                "use_gpu": True
            },
            "runpod": {
                "python_path": "/usr/bin/python3",
                "pip_path": "/usr/bin/pip3",
                "git_path": "/usr/bin/git",
                "use_gpu": True
            },
            "local": {
                "python_path": sys.executable,
                "pip_path": f"{sys.executable} -m pip",
                "git_path": "git",
                "use_gpu": False
            }
        }
        
        return configs.get(self.platform, configs["local"])
    
    def get_base_path(self) -> str:
        """Get the base path for the current platform."""
        self.detect_platform()
        return self.platform_info.get("base_path", "/workspace")
    
    def get_storage_path(self) -> str:
        """Get the storage path for the current platform."""
        self.detect_platform()
        return self.platform_info.get("storage_path", "/workspace")
    
    def is_gpu_available(self) -> bool:
        """Check if GPU is available on the current platform."""
        self.detect_platform()
        return self.platform_info.get("gpu_available", False)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        self.detect_platform()
        
        # Get CPU info
        try:
            cpu_info = subprocess.run(['cat', '/proc/cpuinfo'], 
                                   capture_output=True, text=True).stdout
            cpu_cores = cpu_info.count('processor')
        except:
            cpu_cores = 1
        
        # Get memory info
        try:
            mem_info = subprocess.run(['free', '-m'], 
                                   capture_output=True, text=True).stdout
            total_memory = int([line for line in mem_info.split('\n') 
                              if line.startswith('Mem:')][0].split()[1])
        except:
            total_memory = 4096
        
        # Get GPU info if available
        gpu_info = {}
        if self.is_gpu_available():
            try:
                gpu_result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                                         capture_output=True, text=True)
                if gpu_result.returncode == 0:
                    gpu_lines = gpu_result.stdout.strip().split('\n')
                    for i, line in enumerate(gpu_lines):
                        if line.strip():
                            name, memory = line.split(',')
                            gpu_info[f"gpu_{i}"] = {
                                "name": name.strip(),
                                "memory_mb": int(memory.strip())
                            }
            except:
                pass
        
        return {
            "platform": self.platform,
            "platform_info": self.platform_info,
            "cpu_cores": cpu_cores,
            "total_memory_mb": total_memory,
            "gpu_info": gpu_info,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "base_path": self.get_base_path(),
            "storage_path": self.get_storage_path()
        }

# Global instance
cloud_detector = CloudDetector()

def detect_environment() -> Dict[str, Any]:
    """Convenience function to detect the current environment."""
    return cloud_detector.get_system_info()

def get_platform() -> str:
    """Convenience function to get the current platform."""
    return cloud_detector.detect_platform()

def get_base_path() -> str:
    """Convenience function to get the base path."""
    return cloud_detector.get_base_path()

if __name__ == "__main__":
    # Test the cloud detector
    info = detect_environment()
    print(f"Detected Platform: {info['platform']}")
    print(f"System Info: {json.dumps(info, indent=2)}")