# SD-Tailnokio

A clean, up-to-date repository with notebook interface for SD-Pinnokio integration. This repository provides a complete solution for running AI applications in notebook environments with tunnel support.

## Features

- 📓 **Complete Notebook Interface**: Jupyter/Colab compatible interfaces
- 🌐 **Tunnel Support**: Cloudflare, ngrok, and localtunnel integration
- 🔍 **280+ AI Applications**: Comprehensive application library
- 📊 **Real-time Monitoring**: Process and tunnel status tracking
- 📱 **Mobile Friendly**: QR code generation for easy access
- 🚀 **Production Ready**: Complete error handling and cleanup

## Quick Start

### Jupyter Notebook Environment
```python
# Option 1: Complete Jupyter Notebook Interface
%run SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb

# Option 2: Simplified Python Interface
exec(open('SD_PINNOKIO_SIMPLE_INTERFACE.py').read())

# Option 3: Comprehensive Integration Script (Recommended)
%run notebook-integration.py
```

### Google Colab
```python
# Colab-specific integration
%run colab_integration.py
```

### Testing Your Installation
```python
# Run the test script to verify everything works
%run test-integration.py
```

## Repository Structure

```
SD-Tailnokio/
├── SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb    # Complete Jupyter notebook interface
├── SD_PINNOKIO_SIMPLE_INTERFACE.py         # Simplified Python interface
├── notebook-integration.py                 # Comprehensive integration script (Recommended)
├── colab_integration.py                    # Google Colab specific integration
├── test-integration.py                     # Test script for verification
├── NOTEBOOK_INTEGRATION_GUIDE.md          # Detailed integration guide
├── requirements.txt                        # Python dependencies
├── core/                                  # Core implementation
│   ├── app_database.py                    # Application database management
│   ├── app_manager.py                     # Application installation/execution engine
│   ├── cleaned_pinokio_apps.json         # 280+ AI applications library
│   ├── cloud_detection/
│   │   └── cloud_detector.py              # Cloud platform detection
│   ├── environment_management/
│   │   └── shell_runner.py                # Enhanced shell command execution
│   └── tunneling/
│       └── cloudflare_manager.py          # Enterprise tunnel management
├── README.md                             # This file
├── LICENSE                               # MIT License
└── .gitignore                            # Python/.gitignore file
```

## Key Components

### 1. Notebook Interfaces
- **SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb**: Complete ipywidgets interface with full functionality
- **SD_PINNOKIO_SIMPLE_INTERFACE.py**: Lightweight interface for any Python environment
- **notebook-integration.py**: Production-ready integration with web interface and tunnel support (Recommended)
- **colab_integration.py**: Optimized for Google Colab environment
- **test-integration.py**: Comprehensive testing script for verification

### 2. Core Implementation (core/)
- **cloud_detector.py**: Detects cloud platforms and environments
- **shell_runner.py**: Enhanced shell command execution with output capture
- **app_database.py**: Manages application metadata and state
- **app_manager.py**: Core application installation and execution engine
- **cloudflare_manager.py**: Enterprise-grade tunnel management
- **cleaned_pinokio_apps.json**: Curated library of 280+ AI applications

### 3. Tunnel Support
- **Cloudflare Tunnel**: Enterprise reliability with custom domains
- **ngrok**: User-friendly with web interface
- **localtunnel**: Simple setup, no account required
- **QR Code Generation**: Mobile device access

## Usage Examples

### Testing Your Setup
```python
# First, test that everything works
%run test-integration.py

# If all tests pass, proceed with the interface
```

### Basic Application Management
```python
# Initialize the interface (Recommended approach)
%run notebook-integration.py

# The web interface will automatically open with:
# - Application browser and search
# - One-click install/run functionality
# - Real-time status monitoring
# - Public tunnel with QR code
```

### Advanced Features (Direct API Usage)
```python
# For advanced users who want direct API access
from core.app_database import AppDatabase
from core.app_manager import AppManager
from core.environment_management.shell_runner import ShellRunner

# Initialize components
shell_runner = ShellRunner()
app_database = AppDatabase()
app_manager = AppManager(shell_runner, app_database)

# Browse available applications
apps = app_database.get_all_apps()
print(f"Available applications: {len(apps)}")

# Search applications
search_results = app_database.search_apps("text to image")

# Filter by category
category_apps = app_database.get_apps_by_category("Image Generation")

# Install an application
success = app_manager.install_app("stable-diffusion-webui")

# Run the application
success = app_manager.run_app("stable-diffusion-webui")

# Monitor process status
status = app_manager.get_process_status("stable-diffusion-webui")
```

## System Requirements

- Python 3.8+
- Jupyter Notebook/Lab (for notebook interfaces)
- Internet connection for application downloads
- Cloud platform account (for tunnel services)

### Installation
```bash
# Clone the repository
git clone https://github.com/remphanostar/SD-Tailnokio.git
cd SD-Tailnokio

# Install dependencies
pip install -r requirements.txt
```

### Quick Verification
```python
# In Jupyter/Colab, run the test script
%run test-integration.py
```

## Supported Platforms

- **Local**: Jupyter Notebook, JupyterLab
- **Cloud**: Google Colab, Kaggle Notebooks
- **Enterprise**: JupyterHub, Binder

## Security Features

- **Token-based Authentication**: Secure API access
- **Process Isolation**: Separate processes for each application
- **Tunnel Encryption**: HTTPS for all external access
- **Resource Cleanup**: Automatic cleanup on exit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [Integration Guide](NOTEBOOK_INTEGRATION_GUIDE.md)
- Review the notebook interface examples
- Submit an issue on GitHub

---

**SD-Tailnokio** - Bringing the power of SD-Pinnokio to notebook environments with enterprise-grade reliability and ease of use.
