import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the inspectomat package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inspectomat.clean_empty_dirs import find_empty_dirs

class TestCleanEmptyDirs(unittest.TestCase):
    """Test the clean_empty_dirs module"""
    
    def setUp(self):
        """Set up a temporary directory structure for testing"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a directory structure for testing
        # temp_dir/
        #   ├── empty_dir/
        #   ├── non_empty_dir/
        #   │   ├── file.txt
        #   │   └── empty_subdir/
        #   └── nested/
        #       └── empty_nested/
        
        # Create empty directory
        self.empty_dir = os.path.join(self.temp_dir, 'empty_dir')
        os.mkdir(self.empty_dir)
        
        # Create non-empty directory with a file
        self.non_empty_dir = os.path.join(self.temp_dir, 'non_empty_dir')
        os.mkdir(self.non_empty_dir)
        with open(os.path.join(self.non_empty_dir, 'file.txt'), 'w') as f:
            f.write('test')
        
        # Create empty subdirectory in non-empty directory
        self.empty_subdir = os.path.join(self.non_empty_dir, 'empty_subdir')
        os.mkdir(self.empty_subdir)
        
        # Create nested empty directory
        self.nested_dir = os.path.join(self.temp_dir, 'nested')
        os.mkdir(self.nested_dir)
        self.empty_nested = os.path.join(self.nested_dir, 'empty_nested')
        os.mkdir(self.empty_nested)
    
    def tearDown(self):
        """Clean up the temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_find_empty_dirs(self):
        """Test the find_empty_dirs function"""
        empty_dirs = find_empty_dirs(self.temp_dir)
        
        # Convert to set for easier comparison
        empty_dirs_set = set(empty_dirs)
        expected_empty_dirs = {
            self.empty_dir,
            self.empty_subdir,
            self.empty_nested
        }
        
        self.assertEqual(empty_dirs_set, expected_empty_dirs)
    
    def test_find_empty_dirs_with_non_existent_dir(self):
        """Test find_empty_dirs with a non-existent directory"""
        non_existent_dir = os.path.join(self.temp_dir, 'non_existent')
        # The function should return an empty list for non-existent directories
        empty_dirs = find_empty_dirs(non_existent_dir)
        self.assertEqual(empty_dirs, [])

if __name__ == '__main__':
    unittest.main()
