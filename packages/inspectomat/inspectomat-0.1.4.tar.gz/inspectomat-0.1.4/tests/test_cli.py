import unittest
import os
import sys
import io
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout

# Add the parent directory to the path so we can import the cleaner package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cleaner.cli import CleanerShell, ScriptableShell, main

class TestCleanerShell(unittest.TestCase):
    """Test the CleanerShell class"""
    
    def setUp(self):
        """Set up the test"""
        self.shell = CleanerShell()
    
    def test_init(self):
        """Test that the shell initializes correctly"""
        self.assertIsInstance(self.shell, CleanerShell)
        self.assertIsNotNone(self.shell.modules)
        self.assertGreater(len(self.shell.modules), 0)
    
    def test_do_exit(self):
        """Test the exit command"""
        result = self.shell.do_exit("")
        self.assertTrue(result)
    
    def test_do_quit(self):
        """Test the quit command"""
        result = self.shell.do_quit("")
        self.assertTrue(result)
    
    def test_do_list(self):
        """Test the list command"""
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.do_list("")
        output = f.getvalue()
        self.assertIn("Available commands:", output)
        # Check that at least one command is listed
        self.assertIn("  ", output)

class TestScriptableShell(unittest.TestCase):
    """Test the ScriptableShell class"""
    
    def setUp(self):
        """Set up the test"""
        self.shell = ScriptableShell()
    
    def test_init(self):
        """Test that the shell initializes correctly"""
        self.assertIsInstance(self.shell, ScriptableShell)
        self.assertIsNotNone(self.shell.modules)
        self.assertGreater(len(self.shell.modules), 0)
    
    def test_list_commands(self):
        """Test the list_commands method"""
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.list_commands()
        output = f.getvalue()
        self.assertIn("Available commands:", output)
        # Check that at least one command is listed
        self.assertIn("  ", output)
    
    def test_get_module_functions(self):
        """Test the get_module_functions method"""
        # Find a module that exists
        module_name = next(iter(self.shell.modules.keys()))
        functions = self.shell.get_module_functions(module_name)
        self.assertIsNotNone(functions)
        self.assertIsInstance(functions, dict)
    
    def test_get_function_params(self):
        """Test the get_function_params method"""
        # Create a test function with parameters
        def test_func(a, b, c=1, d="test"):
            pass
        
        params = self.shell.get_function_params(test_func)
        self.assertEqual(len(params), 4)
        # Check that required parameters are marked as required
        self.assertEqual(params[0][0], "a")
        self.assertTrue(params[0][2])  # Required
        self.assertEqual(params[1][0], "b")
        self.assertTrue(params[1][2])  # Required
        # Check that optional parameters have their default values
        self.assertEqual(params[2][0], "c")
        self.assertEqual(params[2][1], 1)  # Default value
        self.assertFalse(params[2][2])  # Not required
        self.assertEqual(params[3][0], "d")
        self.assertEqual(params[3][1], "test")  # Default value
        self.assertFalse(params[3][2])  # Not required

class TestMain(unittest.TestCase):
    """Test the main function"""
    
    @patch('sys.argv', ['cleaner', '-l'])
    @patch('cleaner.cli.ScriptableShell')
    def test_main_list(self, mock_shell):
        """Test the main function with the list flag"""
        # Create a mock shell instance
        mock_shell_instance = MagicMock()
        mock_shell.return_value = mock_shell_instance
        
        # Call the main function
        main()
        
        # Check that list_commands was called
        mock_shell_instance.list_commands.assert_called_once()
    
    @patch('sys.argv', ['cleaner', 'test_command'])
    @patch('cleaner.cli.ScriptableShell')
    def test_main_command(self, mock_shell):
        """Test the main function with a command"""
        # Create a mock shell instance
        mock_shell_instance = MagicMock()
        mock_shell.return_value = mock_shell_instance
        
        # Call the main function
        main()
        
        # Check that run_command was called with the correct arguments
        mock_shell_instance.run_command.assert_called_once()
        args, kwargs = mock_shell_instance.run_command.call_args
        self.assertEqual(args[0], 'test_command')

if __name__ == '__main__':
    unittest.main()
