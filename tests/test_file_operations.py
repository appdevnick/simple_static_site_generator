import unittest
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from utils import copy_from_to_dir


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.source_dir = self.test_dir / 'source'
        self.dest_dir = self.test_dir / 'dest'
        self.source_dir.mkdir()
        self.dest_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_copy_single_file(self):
        # Create a test file
        test_file = self.source_dir / 'test.txt'
        test_file.write_text('test content')
        
        # Copy file
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if file was copied
        copied_file = self.dest_dir / 'test.txt'
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_text(), 'test content')

    def test_copy_nested_directories(self):
        # Create nested directory structure
        nested_dir = self.source_dir / 'subdir' / 'nested'
        nested_dir.mkdir(parents=True)
        
        # Create test files
        test_file1 = self.source_dir / 'test1.txt'
        test_file2 = nested_dir / 'test2.txt'
        test_file1.write_text('content1')
        test_file2.write_text('content2')
        
        # Copy directory
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if files were copied with structure preserved
        copied_file1 = self.dest_dir / 'test1.txt'
        copied_file2 = self.dest_dir / 'subdir' / 'nested' / 'test2.txt'
        self.assertTrue(copied_file1.exists())
        self.assertTrue(copied_file2.exists())
        self.assertEqual(copied_file1.read_text(), 'content1')
        self.assertEqual(copied_file2.read_text(), 'content2')

    def test_copy_empty_directory(self):
        # Copy empty directory
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if destination exists but is empty
        self.assertTrue(self.dest_dir.exists())
        self.assertEqual(len(list(self.dest_dir.iterdir())), 0)

    def test_copy_with_existing_destination(self):
        # Create source file
        test_file = self.source_dir / 'test.txt'
        test_file.write_text('new content')
        
        # Create existing destination file
        existing_file = self.dest_dir / 'test.txt'
        existing_file.write_text('old content')
        
        # Copy directory
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if file was overwritten
        self.assertEqual(existing_file.read_text(), 'new content')

    def test_copy_preserves_file_modes(self):
        # Create executable file
        test_file = self.source_dir / 'script.sh'
        test_file.write_text('#!/bin/bash\necho "test"')
        test_file.chmod(0o755)
        
        # Copy directory
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if permissions were preserved
        copied_file = self.dest_dir / 'script.sh'
        self.assertEqual(test_file.stat().st_mode, copied_file.stat().st_mode)

    def test_copy_handles_symlinks(self):
        # Create target file and symlink
        target_file = self.source_dir / 'target.txt'
        target_file.write_text('target content')
        symlink = self.source_dir / 'link.txt'
        symlink.symlink_to(target_file)
        
        # Copy directory
        copy_from_to_dir(str(self.source_dir), str(self.dest_dir))
        
        # Check if both files exist in destination
        copied_target = self.dest_dir / 'target.txt'
        copied_link = self.dest_dir / 'link.txt'
        self.assertTrue(copied_target.exists())
        self.assertTrue(copied_link.exists())
        self.assertTrue(copied_link.is_symlink())


if __name__ == '__main__':
    unittest.main()
