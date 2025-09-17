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

# Option 3: Comprehensive Integration Script
%run notebook-integration.py
```

### Google Colab
```python
# Colab-specific integration
%run colab_integration.py
```

## Repository Structure

```
SD-Tailnokio/
├── SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb    # Complete Jupyter notebook interface
├── SD_PINNOKIO_SIMPLE_INTERFACE.py         # Simplified Python interface
├── notebook-integration.py                 # Comprehensive integration script
├── colab_integration.py                    # Google Colab specific integration
├── NOTEBOOK_INTEGRATION_GUIDE.md          # Detailed integration guide
├── github_repo/                           # Core 12-phase implementation
│   ├── cloud_detection/                   # Phase 1: Cloud platform detection
│   │   └── cloud_detector.py
│   ├── environment_management/            # Phase 2: Environment management
│   │   └── shell_runner.py
│   ├── app_database.py                    # Phase 3: Application database
│   ├── app_manager.py                     # Phase 5: Application engine
│   ├── tunneling/                         # Phase 7: Tunnel management
│   │   └── cloudflare_manager.py
│   └── cleaned_pinokio_apps.json         # Application library (280+ apps)
└── README.md                             # This file
```

## Key Components

### 1. Notebook Interfaces
- **SD_PINNOKIO_NOTEBOOK_INTERFACE.ipynb**: Complete ipywidgets interface with full functionality
- **SD_PINNOKIO_SIMPLE_INTERFACE.py**: Lightweight interface for any Python environment
- **notebook-integration.py**: Production-ready integration with multiple tunnel options
- **colab_integration.py**: Optimized for Google Colab environment

### 2. Core Implementation (github_repo/)
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

### Basic Application Management
```python
# Initialize the interface
interface = NotebookInterface()

# Browse available applications
apps = interface.get_apps()
print(f"Available applications: {len(apps)}")

# Install an application
interface.install_app("stable-diffusion-webui")

# Run the application
interface.run_app("stable-diffusion-webui")

# Create tunnel for external access
tunnel_url = interface.create_tunnel("cloudflare")
print(f"Tunnel URL: {tunnel_url}")
```

### Advanced Features
```python
# Search applications
search_results = interface.search_apps("text to image")

# Filter by category
category_apps = interface.get_apps_by_category("Image Generation")

# Monitor process status
status = interface.get_process_status("stable-diffusion-webui")

# Generate QR code for mobile access
qr_code = interface.generate_qr_code(tunnel_url)
```

## System Requirements

- Python 3.8+
- Jupyter Notebook/Lab (for notebook interfaces)
- Internet connection for application downloads
- Cloud platform account (for tunnel services)

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
