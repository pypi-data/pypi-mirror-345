#!/usr/bin/env python3
"""
Interactive shell client for the inspectomat package
"""
import os
import sys
import cmd
import importlib
import inspect
import argparse
import traceback
import logging
from typing import Dict, List, Callable, Any

# Import the logger and config modules
from inspectomat.logger import get_logger, setup_logging, set_log_level
from inspectomat.config import get_config, get_config_value, set_config_value

# Get logger for this module
logger = get_logger(__name__)

class InspectomatShell(cmd.Cmd):
    intro = "Welcome to the Inspectomat interactive shell. Type help or ? to list commands.\n"
    prompt = "inspectomat> "
    
    def __init__(self):
        super().__init__()
        # Get all Python modules in the package directory
        self.modules = {}
        package_dir = os.path.dirname(__file__)
        for filename in os.listdir(package_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'cli.py':
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module dynamically
                    module = importlib.import_module(f'inspectomat.{module_name}')
                    self.modules[module_name] = module
                except ImportError as e:
                    logger.warning(f"Could not import {module_name}: {e}")
        
        # Dynamically create commands for each module's main function
        for module_name, module in self.modules.items():
            if hasattr(module, 'main'):
                command_name = module_name.replace('_', '')
                setattr(InspectomatShell, f'do_{command_name}', 
                        lambda self, arg, module=module: module.main())
                setattr(InspectomatShell, f'help_{command_name}', 
                        lambda self, module=module: self._get_module_help(module))
    
    def _get_module_help(self, module):
        """Get help text for a module"""
        doc = module.__doc__ or "No documentation available"
        print(doc)
        if hasattr(module, 'main'):
            main_doc = module.main.__doc__ or "No documentation for main function"
            print("\nMain function:")
            print(main_doc)
    
    def do_menu(self, arg):
        """Show the original menu interface"""
        try:
            from inspectomat import menu
            menu.main()
        except ImportError:
            logger.error("Menu module not available")
            print("Menu module not available")
    
    def do_exit(self, arg):
        """Exit the inspectomat shell"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the inspectomat shell"""
        return self.do_exit(arg)
    
    def do_list(self, arg):
        """List all available commands"""
        print("Available commands:")
        for module_name in self.modules:
            cmd_name = module_name.replace('_', '')
            if hasattr(self, f'do_{cmd_name}'):
                print(f"  {cmd_name} - {module_name.replace('_', ' ')}")
        print("  menu - Show the original menu interface")
        print("  config - View or edit configuration")
        print("  repair - Check and repair dependencies")
        print("  exit/quit - Exit the inspectomat shell")
    
    def do_repair(self, arg):
        """Check and repair dependencies"""
        try:
            from inspectomat import dependency_manager
            if dependency_manager.verify_environment():
                dependency_manager.install_missing_dependencies()
            else:
                logger.error("Environment verification failed")
                print("Environment verification failed. Please fix the issues before continuing.")
        except ImportError:
            logger.error("Dependency manager not available")
            print("Dependency manager not available")
    
    def do_config(self, arg):
        """View or edit configuration settings"""
        args = arg.split()
        if not args:
            # Show all configuration
            config = get_config().config
            print("Current configuration:")
            self._print_config(config)
            return
        
        if args[0] == "set" and len(args) >= 3:
            # Set configuration value
            key = args[1]
            value = " ".join(args[2:])
            
            # Try to convert value to appropriate type
            try:
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit():
                    value = float(value)
            except (ValueError, AttributeError):
                pass
            
            if set_config_value(key, value):
                logger.info(f"Configuration value '{key}' set to '{value}'")
                print(f"Configuration value '{key}' set to '{value}'")
            else:
                logger.error(f"Failed to set configuration value '{key}'")
                print(f"Failed to set configuration value '{key}'")
        
        elif args[0] == "get" and len(args) >= 2:
            # Get configuration value
            key = args[1]
            value = get_config_value(key)
            if value is not None:
                print(f"{key} = {value}")
            else:
                print(f"Configuration value '{key}' not found")
        
        elif args[0] == "reset":
            # Reset configuration to defaults
            from inspectomat.config import reset_config
            reset_config()
            logger.info("Configuration reset to defaults")
            print("Configuration reset to defaults")
        
        else:
            print("Usage:")
            print("  config - Show all configuration")
            print("  config get <key> - Get configuration value")
            print("  config set <key> <value> - Set configuration value")
            print("  config reset - Reset configuration to defaults")
    
    def _print_config(self, config, prefix=""):
        """Print configuration recursively"""
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._print_config(value, prefix + "  ")
            else:
                print(f"{prefix}{key} = {value}")
    
    def get_available_commands(self):
        """Get a list of all available commands"""
        commands = []
        # Add module-based commands
        for module_name in self.modules:
            cmd_name = module_name.replace('_', '')
            if hasattr(self, f'do_{cmd_name}'):
                commands.append(cmd_name)
        
        # Add built-in commands
        commands.extend(['menu', 'config', 'repair', 'exit', 'quit', 'list', 'help'])
        return commands
    
    def completenames(self, text, *ignored):
        """Override completenames to provide command completion"""
        commands = self.get_available_commands()
        return [cmd for cmd in commands if cmd.startswith(text)]
    
    def complete_config(self, text, line, begidx, endidx):
        """Provide completion for config subcommands"""
        subcommands = ['get', 'set', 'reset']
        
        # If line starts with "config " and no further text, complete with subcommands
        if line.startswith('config ') and len(line.split()) == 2:
            return [cmd for cmd in subcommands if cmd.startswith(text)]
        
        # If line starts with "config get " or "config set ", complete with config keys
        if line.startswith('config get ') or line.startswith('config set '):
            config = get_config().config
            keys = self._get_config_keys(config)
            return [key for key in keys if key.startswith(text)]
        
        return []
    
    def _get_config_keys(self, config, prefix=''):
        """Get all configuration keys recursively"""
        keys = []
        for key, value in config.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(self._get_config_keys(value, f"{full_key}."))
            else:
                keys.append(full_key)
        return keys

    def do_suggest_dirs(self, arg):
        """Suggest common directories to the user"""
        home = os.path.expanduser("~")
        suggestions = [
            home, 
            os.path.join(home, "Documents"), 
            os.path.join(home, "Downloads"), 
            os.path.join(home, "Pictures")
        ]
        print("Example directories:")
        for s in suggestions:
            print(f"- {s}")

class ScriptableShell:
    """
    Scriptable shell interface that allows passing parameters directly from the command line
    """
    def __init__(self):
        # Get all Python modules in the package directory
        self.modules = {}
        package_dir = os.path.dirname(__file__)
        for filename in os.listdir(package_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'cli.py':
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module dynamically
                    module = importlib.import_module(f'inspectomat.{module_name}')
                    self.modules[module_name] = module
                except ImportError as e:
                    logger.warning(f"Could not import {module_name}: {e}")
    
    def list_commands(self):
        """List all available commands"""
        print("Available commands:")
        for module_name in self.modules:
            cmd_name = module_name.replace('_', '')
            if hasattr(self.modules[module_name], 'main'):
                print(f"  {cmd_name} - {module_name.replace('_', ' ')}")
        print("  menu - Show the original menu interface")
        print("  config - View or edit configuration")
        print("  repair - Check and repair dependencies")
    
    def get_module_functions(self, module_name):
        """Get all public functions from a module"""
        if module_name not in self.modules:
            return {}
        
        module = self.modules[module_name]
        functions = {}
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                functions[name] = obj
        
        return functions
    
    def get_function_params(self, func):
        """Get parameters for a function"""
        params = []
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param.default is inspect.Parameter.empty:
                # Required parameter
                params.append((param_name, None, True))
            else:
                # Optional parameter with default value
                params.append((param_name, param.default, False))
        return params
    
    def run_command(self, command, args):
        """Run a command with arguments"""
        # Special case for repair command
        if command == 'repair':
            try:
                from inspectomat import dependency_manager
                if dependency_manager.verify_environment():
                    dependency_manager.install_missing_dependencies(interactive=not args.yes)
                else:
                    logger.error("Environment verification failed")
                    print("Environment verification failed. Please fix the issues before continuing.")
            except ImportError:
                logger.error("Dependency manager not available")
                print("Dependency manager not available")
            return
        
        # Special case for config command
        if command == 'config':
            self._handle_config_command(args)
            return
            
        # Convert command to module name (e.g., cleanemptydirs -> clean_empty_dirs)
        module_name = None
        
        # Try to find the module that corresponds to the command
        for mod_name in self.modules:
            cmd_name = mod_name.replace('_', '')
            if cmd_name == command:
                module_name = mod_name
                break
        
        if not module_name:
            logger.error(f"Command '{command}' not found")
            print(f"Command '{command}' not found. Use 'inspectomat list' to see available commands.")
            return
        
        module = self.modules[module_name]
        
        # If no function is specified, run the main function
        if not args.function:
            if hasattr(module, 'main'):
                # If there are parameters, parse them
                if args.params:
                    logger.warning("Parameters provided but main() doesn't accept command-line parameters")
                    print("Warning: Parameters provided but main() doesn't accept command-line parameters.")
                    print("Running main() without parameters...")
                
                try:
                    module.main()
                except Exception as e:
                    self._handle_exception(e, module_name)
            else:
                logger.error(f"Module {module_name} does not have a main function")
                print(f"Module {module_name} does not have a main function")
            return
        
        # If a function is specified, run that function
        functions = self.get_module_functions(module_name)
        if args.function not in functions:
            logger.error(f"Function '{args.function}' not found in module '{module_name}'")
            print(f"Function '{args.function}' not found in module '{module_name}'")
            print("Available functions:")
            for func_name in functions:
                print(f"  {func_name}")
            return
        
        func = functions[args.function]
        params = self.get_function_params(func)
        
        # Parse parameters
        func_args = []
        func_kwargs = {}
        
        if args.params:
            # Simple parsing of key=value pairs
            for param in args.params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    func_kwargs[key] = value
                else:
                    func_args.append(param)
        
        # Call the function
        try:
            logger.debug(f"Calling {module_name}.{args.function} with args={func_args}, kwargs={func_kwargs}")
            result = func(*func_args, **func_kwargs)
            if result is not None:
                print(result)
        except Exception as e:
            self._handle_exception(e, module_name)
    
    def _handle_config_command(self, args):
        """Handle the config command"""
        if not args.params:
            # Show all configuration
            config = get_config().config
            print("Current configuration:")
            self._print_config(config)
            return
        
        if len(args.params) >= 2 and args.params[0] == "set":
            # Set configuration value
            if len(args.params) < 3:
                print("Usage: inspectomat config set <key> <value>")
                return
            
            key = args.params[1]
            value = " ".join(args.params[2:])
            
            # Try to convert value to appropriate type
            try:
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit():
                    value = float(value)
            except (ValueError, AttributeError):
                pass
            
            if set_config_value(key, value):
                logger.info(f"Configuration value '{key}' set to '{value}'")
                print(f"Configuration value '{key}' set to '{value}'")
            else:
                logger.error(f"Failed to set configuration value '{key}'")
                print(f"Failed to set configuration value '{key}'")
        
        elif len(args.params) >= 2 and args.params[0] == "get":
            # Get configuration value
            key = args.params[1]
            value = get_config_value(key)
            if value is not None:
                print(f"{key} = {value}")
            else:
                print(f"Configuration value '{key}' not found")
        
        elif len(args.params) >= 1 and args.params[0] == "reset":
            # Reset configuration to defaults
            from inspectomat.config import reset_config
            reset_config()
            logger.info("Configuration reset to defaults")
            print("Configuration reset to defaults")
        
        else:
            print("Usage:")
            print("  inspectomat config - Show all configuration")
            print("  inspectomat config get <key> - Get configuration value")
            print("  inspectomat config set <key> <value> - Set configuration value")
            print("  inspectomat config reset - Reset configuration to defaults")
    
    def _print_config(self, config, prefix=""):
        """Print configuration recursively"""
        for key, value in sorted(config.items()):
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._print_config(value, prefix + "  ")
            else:
                print(f"{prefix}{key} = {value}")
    
    def _handle_exception(self, exception, module_name=None):
        """Handle an exception, possibly by installing missing dependencies"""
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        logger.error(f"{error_type}: {error_msg}")
        print(f"Error: {error_type}: {error_msg}")
        
        # Check if it's an ImportError or ModuleNotFoundError
        if isinstance(exception, (ImportError, ModuleNotFoundError)):
            missing_module = error_msg.split("'")[1] if "'" in error_msg else None
            
            if missing_module:
                logger.info(f"Detected missing dependency: {missing_module}")
                print(f"\nDetected missing dependency: {missing_module}")
                try:
                    from inspectomat import dependency_manager
                    
                    # Add the missing dependency to the dependency manager if it's not already there
                    if missing_module not in dependency_manager.DEPENDENCIES:
                        dependency_manager.DEPENDENCIES[missing_module] = missing_module
                    
                    if dependency_manager.verify_environment():
                        print("Attempting to fix the issue...")
                        if dependency_manager.install_missing_dependencies():
                            logger.info(f"Dependency {missing_module} installed")
                            print(f"\nDependency {missing_module} installed. You can now retry your command.")
                            return
                    else:
                        logger.error("Environment verification failed")
                        print("Environment verification failed. Please fix the issues before continuing.")
                except ImportError:
                    logger.error("Dependency manager not available")
                    print("Dependency manager not available. Please install the required dependencies manually.")
        
        # If we couldn't fix the issue or it's not a dependency issue, show the traceback
        print("\nFull error traceback:")
        traceback.print_exc()

def main():
    """Entry point for the inspectomat command"""
    parser = argparse.ArgumentParser(description="Inspectomat - System cleanup and file management toolbox")
    parser.add_argument('command', nargs='?', help='Command to run')
    parser.add_argument('-f', '--function', help='Function to call within the module')
    parser.add_argument('-p', '--params', nargs='*', help='Parameters for the function (key=value format)')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive shell')
    parser.add_argument('-l', '--list', action='store_true', help='List available commands')
    parser.add_argument('-y', '--yes', action='store_true', help='Automatically answer yes to all prompts')
    parser.add_argument('--repair', action='store_true', help='Check and repair dependencies')
    parser.add_argument('--config', nargs='*', help='View or edit configuration')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the log level')
    
    args = parser.parse_args()
    
    # Configure logging based on configuration
    log_console_level = get_config_value('logging.console_level', 'INFO')
    log_file_level = get_config_value('logging.file_level', 'DEBUG')
    log_file = get_config_value('logging.log_file')
    enable_console = get_config_value('logging.enable_console', True)
    enable_file = get_config_value('logging.enable_file', True)
    
    # Override log level if specified on command line
    if args.log_level:
        log_console_level = args.log_level
    
    # Convert string log levels to integers
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    console_level = log_levels.get(log_console_level, logging.INFO)
    file_level = log_levels.get(log_file_level, logging.DEBUG)
    
    # Setup logging
    setup_logging(
        console_level=console_level,
        file_level=file_level,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file
    )
    
    logger.debug("Inspectomat starting up")
    
    # First, try to import the dependency manager and check for critical dependencies
    try:
        from inspectomat import dependency_manager
        if not dependency_manager.verify_environment():
            logger.warning("Environment verification failed")
            print("Environment verification failed. Some features may not work correctly.")
        
        # Check for missing critical dependencies
        missing = dependency_manager.get_missing_dependencies()
        if missing and (args.repair or args.yes):
            logger.info(f"Installing missing dependencies: {missing}")
            dependency_manager.install_missing_dependencies(interactive=not args.yes)
    except ImportError:
        # Dependency manager itself is not available, but we can continue
        logger.warning("Dependency manager not available")
        pass
    
    # If config flag is set, handle configuration
    if args.config is not None:
        shell = ScriptableShell()
        shell._handle_config_command(args)
        return
    
    # If repair flag is set, run the repair and exit
    if args.repair:
        try:
            from inspectomat import dependency_manager
            if dependency_manager.verify_environment():
                logger.info("Running dependency repair")
                dependency_manager.install_missing_dependencies(interactive=not args.yes)
            else:
                logger.error("Environment verification failed")
                print("Environment verification failed. Please fix the issues before continuing.")
        except ImportError:
            logger.error("Dependency manager not available")
            print("Dependency manager not available")
        return
    
    # If no arguments or interactive flag, start the interactive shell
    if args.interactive or (len(sys.argv) == 1):
        logger.info("Starting interactive shell")
        InspectomatShell().cmdloop()
        return
    
    # Create scriptable shell
    shell = ScriptableShell()
    
    # If list flag, list available commands
    if args.list:
        logger.debug("Listing available commands")
        shell.list_commands()
        return
    
    # If command is provided, run it
    if args.command:
        logger.info(f"Running command: {args.command}")
        shell.run_command(args.command, args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
