"""
Dependency manager for the cleaner package.
Handles automatic detection and installation of missing dependencies.
"""
import importlib
import subprocess
import sys
import os
import logging
from typing import Dict, List, Optional, Tuple, Set

# Use importlib.metadata instead of pkg_resources (which is deprecated)
try:
    # Python 3.8+
    from importlib import metadata as importlib_metadata
except ImportError:
    # Python < 3.8
    import importlib_metadata

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('cleaner.dependency_manager')

# Define package dependencies
# Format: module_name: package_name (if different from module name)
DEPENDENCIES = {
    # Core dependencies
    'argparse': 'argparse',
    
    # Optional dependencies for specific modules
    'PIL': 'pillow',  # For image processing in media_deduplicate
    'numpy': 'numpy',  # For array operations
    'tqdm': 'tqdm',   # For progress bars
    'psutil': 'psutil',  # For system information
}

def check_dependency(module_name: str) -> bool:
    """
    Check if a dependency is installed.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        bool: True if the dependency is installed, False otherwise
    """
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def get_missing_dependencies() -> Dict[str, str]:
    """
    Get a list of missing dependencies.
    
    Returns:
        Dict[str, str]: Dictionary of missing dependencies {module_name: package_name}
    """
    missing = {}
    for module_name, package_name in DEPENDENCIES.items():
        if not check_dependency(module_name):
            missing[module_name] = package_name
    return missing

def install_dependency(package_name: str) -> Tuple[bool, str]:
    """
    Install a dependency using pip.
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        Tuple[bool, str]: (Success status, Error message if any)
    """
    try:
        logger.info(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, str(e)

def install_missing_dependencies(interactive: bool = True) -> bool:
    """
    Install all missing dependencies.
    
    Args:
        interactive: If True, ask for confirmation before installing
        
    Returns:
        bool: True if all dependencies were installed successfully, False otherwise
    """
    missing = get_missing_dependencies()
    
    if not missing:
        return True
    
    logger.info("Missing dependencies detected:")
    for module_name, package_name in missing.items():
        logger.info(f"  - {module_name} (package: {package_name})")
    
    if interactive:
        response = input("Do you want to install these dependencies? [y/N]: ").strip().lower()
        if response != 'y':
            logger.info("Dependency installation cancelled by user.")
            return False
    
    success = True
    for module_name, package_name in missing.items():
        installed, error = install_dependency(package_name)
        if not installed:
            logger.error(f"Failed to install {package_name}: {error}")
            success = False
    
    if success:
        logger.info("All dependencies installed successfully.")
    else:
        logger.warning("Some dependencies could not be installed.")
    
    return success

def check_and_fix_dependencies(module_name: Optional[str] = None, interactive: bool = True) -> bool:
    """
    Check and fix dependencies for a specific module or all modules.
    
    Args:
        module_name: Name of the module to check, or None for all modules
        interactive: If True, ask for confirmation before installing
        
    Returns:
        bool: True if all dependencies are satisfied, False otherwise
    """
    if module_name:
        # Check only dependencies for the specified module
        # This would require a more detailed mapping of modules to dependencies
        # For now, we'll just check all dependencies
        pass
    
    return install_missing_dependencies(interactive)

def get_installed_packages() -> Set[str]:
    """
    Get a set of all installed packages.
    
    Returns:
        Set[str]: Set of installed package names
    """
    try:
        # Use importlib.metadata instead of pkg_resources
        return {dist.metadata['Name'].lower() for dist in importlib_metadata.distributions()}
    except Exception as e:
        logger.error(f"Error getting installed packages: {e}")
        return set()

def verify_environment() -> bool:
    """
    Verify that the Python environment is properly set up.
    
    Returns:
        bool: True if the environment is properly set up, False otherwise
    """
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        logger.warning(f"Python version {python_version.major}.{python_version.minor} is not supported. "
                      f"Please use Python 3.6 or higher.")
        return False
    
    # Check pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("pip is not available. Please install pip to enable automatic dependency installation.")
        return False
    
    return True

if __name__ == "__main__":
    # If run directly, check and install dependencies
    if verify_environment():
        install_missing_dependencies()
    else:
        logger.error("Environment verification failed. Please fix the issues before continuing.")
