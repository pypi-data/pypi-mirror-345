"""
Jimiko - High-performance SSH client for network automation and device management
"""

import os
import platform
import sys
from pathlib import Path
from typing import Tuple, Type, TypeVar

T = TypeVar('T')

def _get_linux_distribution(os_name):
    """Detect the Linux distribution by checking for distribution-specific files."""
    if os_name == 'darwin':
        return 'macos'
    elif os_name == 'linux':
        if os.path.exists('/etc/redhat-release'):
            return 'rhel'  
        elif os.path.exists('/etc/debian_version') or os.path.exists('/etc/lsb-release'):
            return 'linux' 
    return None 

def _load_binary(wrapper_name: str) -> T:
    """
    Lazily load a binary module.
    
    Args:
        wrapper_name: Name of the wrapper module to load ('_jimiko_wrapper' or '_jimikosftp_wrapper')
        
    Returns:
        For SSH: PyJimikoClient class
        For SFTP: Tuple of (PyJimikoSFTPClient, PyFileInfo) classes
    """
    # For Windows, add the module's directory to PATH temporarily to find binaries 
    original_path = None
    if platform.system().lower() == 'windows':
        original_path = os.environ.get('PATH', '')
        module_dir = str(Path(__file__).parent.absolute())
        os.environ['PATH'] = module_dir + os.pathsep + original_path
    
    # Try direct import first
    try:
        if wrapper_name == '_jimiko_wrapper':
            from ._jimiko_wrapper import PyJimikoClient
            return PyJimikoClient
        elif wrapper_name == '_jimikosftp_wrapper':
            from ._jimikosftp_wrapper import PyJimikoSFTPClient, PyFileInfo
            return PyJimikoSFTPClient, PyFileInfo
    except ImportError as e:
        # If direct import fails, try to load from the package directory
        package_dir = Path(__file__).parent
        os_name = platform.system().lower()
        machine = platform.machine().lower()
        python_version = f"{sys.version_info.major}{sys.version_info.minor}"  
        linux_distro = _get_linux_distribution(os_name)
        
        # If package directory doesn't exist, we can't load from there
        if not linux_distro:
            raise ImportError(f"No compatible binary found for OS: {os_name} Linux Distro: {linux_distro} Machine: {machine} (Python {python_version}). Original error: {e}")
        if not package_dir.exists():
            raise ImportError(f"Failed to import {wrapper_name} directly and no binary directory found. Original error: {e}")
            
        binary_pattern = None
        if linux_distro == 'rhel':
            binary_pattern = f'{wrapper_name}.cp*-{python_version}-manylinux*.so'
        elif linux_distro == 'linux':
            binary_pattern = f'{wrapper_name}.cp*-{python_version}-linux.so'
        elif linux_distro == 'macos':
            binary_pattern = f'{wrapper_name}.cp*-{python_version}-darwin.so'
        elif os_name == 'windows':
            binary_pattern = f'{wrapper_name}.cp*-{python_version}-win*.pyd'
            
        if binary_pattern:
            binaries = list(package_dir.glob(binary_pattern))
            if binaries:
                # Use the first matching binary
                binary_path = binaries[0]
                import importlib.util
                spec = importlib.util.spec_from_file_location(wrapper_name, binary_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if wrapper_name == '_jimiko_wrapper':
                    return module.PyJimikoClient
                elif wrapper_name == '_jimikosftp_wrapper':
                    return module.PyJimikoSFTPClient, module.PyFileInfo
                
        raise ImportError(f"No compatible binary found for OS: {os_name} Linux Distro: {linux_distro} Machine: {machine} (Python {python_version}). Original error: {e}")
    finally:
        # Restore original PATH if we modified it
        if original_path is not None:
            os.environ['PATH'] = original_path

class LazyLoader:
    def __init__(self, wrapper_name: str):
        self._wrapper_name = wrapper_name
        self._loaded_module = None
    
    def __call__(self):
        if self._loaded_module is None:
            self._loaded_module = _load_binary(self._wrapper_name)
        return self._loaded_module

# Lazy loaders for SSH and SFTP clients
_ssh_loader = LazyLoader('_jimiko_wrapper')
_sftp_loader = LazyLoader('_jimikosftp_wrapper')

def get_ssh_client() -> Type:
    """Get the SSH client class. Only loads the binary when first called."""
    return _ssh_loader()

def get_sftp_client() -> Tuple[Type, Type]:
    """Get the SFTP client and FileInfo classes. Only loads the binary when first called."""
    return _sftp_loader()

# Proper implementation with lazy loading
class _SFTPComponents:
    def __init__(self):
        self._sftp_client = None
        self._file_info = None
        
    @property
    def PyJimikoSFTPClient(self):
        if self._sftp_client is None:
            self._sftp_client, self._file_info = get_sftp_client()
        return self._sftp_client
    
    @property
    def PyFileInfo(self):
        if self._file_info is None:
            self._sftp_client, self._file_info = get_sftp_client()
        return self._file_info

_sftp_components = _SFTPComponents()

# Make SSH client available at module level (already loaded eagerly)
PyJimikoClient = get_ssh_client()

# Provide getter functions for SFTP components
def get_sftp_client_class():
    """Get the SFTP client class. Only loads the binary when first called."""
    return _sftp_components.PyJimikoSFTPClient

def get_file_info_class():
    """Get the FileInfo class. Only loads the binary when first called."""
    return _sftp_components.PyFileInfo

# Simple solution - create module-level placeholders that will be updated when imported
class _LazyLoader:
    """
    A transparent lazy-loading proxy for classes.
    
    This class allows us to make classes available at the module level,
    while only loading them when they are first accessed. This avoids
    importing heavy dependencies until they are actually needed.
    
    The loader is completely transparent - all attribute access, method calls,
    instantiation, and string representation will be forwarded to the real class.
    The first access will trigger loading of the real class.
    """
    def __init__(self, loader_func):
        self.loader_func = loader_func
        self._real_cls = None
        
    def __getattr__(self, name):
        # Load the real class and get attribute from it
        if self._real_cls is None:
            self._real_cls = self.loader_func()
        return getattr(self._real_cls, name)
    
    def __call__(self, *args, **kwargs):
        # Load the real class and instantiate it
        if self._real_cls is None:
            self._real_cls = self.loader_func()
        return self._real_cls(*args, **kwargs)
    
    def __repr__(self):
        # Force loading the real class for better debugging
        if self._real_cls is None:
            self._real_cls = self.loader_func()
        return repr(self._real_cls)
        
    def __str__(self):
        # Force loading the real class for better debugging
        if self._real_cls is None:
            self._real_cls = self.loader_func()
        return str(self._real_cls)

# Create lazy loaders for module-level components
PyJimikoSFTPClient = _LazyLoader(get_sftp_client_class)
PyFileInfo = _LazyLoader(get_file_info_class)

# Export the public API
__all__ = ['PyJimikoClient', 'PyJimikoSFTPClient', 'PyFileInfo', 
           'get_ssh_client', 'get_sftp_client', 
           'get_sftp_client_class', 'get_file_info_class']