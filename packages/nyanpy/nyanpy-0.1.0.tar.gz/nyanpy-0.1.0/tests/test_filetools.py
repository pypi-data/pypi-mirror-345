import os
import pytest
from meowmeow.filetools import dir_to_file_list, create_directory_tree

@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to create a temporary directory for testing."""
    return tmp_path

def test_dir_to_file_list(temp_dir):
    # Create test files
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.log").write_text("content2")
    (temp_dir / "file3.txt").write_text("content3")

    # Test without file_type filter
    all_files = dir_to_file_list(str(temp_dir))
    assert len(all_files) == 3
    assert str(temp_dir / "file1.txt") in all_files
    assert str(temp_dir / "file2.log") in all_files
    assert str(temp_dir / "file3.txt") in all_files

    # Test with file_type filter
    txt_files = dir_to_file_list(str(temp_dir), file_type=".txt")
    assert len(txt_files) == 2
    assert str(temp_dir / "file1.txt") in txt_files
    assert str(temp_dir / "file3.txt") in txt_files

def test_create_directory_tree(temp_dir):
    # Define directory structure
    directory_structure = {
        "folder1": {
            "subfolder1": {
                "file1.txt": None
            },
            "subfolder2": {}
        },
        "folder2": {
            "file2.txt": None
        }
    }

    # Create directory tree
    paths = create_directory_tree(str(temp_dir), directory_structure)

    # Assert directories and files are created
    assert (temp_dir / "folder1").is_dir()
    assert (temp_dir / "folder1" / "subfolder1").is_dir()
    assert (temp_dir / "folder1" / "subfolder1" / "file1.txt").is_file()
    assert (temp_dir / "folder1" / "subfolder2").is_dir()
    assert (temp_dir / "folder2").is_dir()
    assert (temp_dir / "folder2" / "file2.txt").is_file()

    # Assert paths dictionary contains correct mappings
    assert "folder1" in paths
    assert "subfolder1" in paths
    assert "file1.txt" in paths
    assert "folder2" in paths
    assert "file2.txt" in paths