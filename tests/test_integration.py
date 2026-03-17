import os
import subprocess
import tempfile
import shutil
import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, "src", "main.py")
PYTHON_BIN = os.path.join(PROJECT_ROOT, "venv", "bin", "python")


@pytest.fixture
def temp_dir():
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def files_in_temp_dir(temp_dir):
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"file{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"Content of file {i}")
        files.append(file_path)
    return files


@pytest.fixture
def compressed_files(temp_dir, files_in_temp_dir):
    for file_path in files_in_temp_dir:
        subprocess.run(
            [PYTHON_BIN, MAIN_SCRIPT, temp_dir, "-c"],
            check=True
        )
    return [f"{f}.br" for f in files_in_temp_dir]


def run_program(directory, *args):
    cmd = [PYTHON_BIN, MAIN_SCRIPT, directory] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result


class TestCompress:
    def test_compress_creates_br_files(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c")
        
        assert result.returncode == 0
        for original_file in files_in_temp_dir:
            compressed_file = original_file + ".br"
            assert os.path.exists(compressed_file)
    
    def test_compress_output_message(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c")
        
        assert "Compressing files" in result.stdout
        assert "Compressing: file0.txt" in result.stdout
    
    def test_compress_verbose_mode(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c", "-v")
        
        assert "Target directory" in result.stdout
        assert "Mode: compressing" in result.stdout
    
    def test_compress_skips_already_compressed(self, temp_dir, files_in_temp_dir):
        run_program(temp_dir, "-c")
        result = run_program(temp_dir, "-c")
        
        assert "Skipping" in result.stdout
        assert "already compressed" in result.stdout
    
    def test_compress_with_long_alias(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "--compress")
        
        assert result.returncode == 0
    
    def test_compress_with_remove_original(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c", "-r")
        
        assert result.returncode == 0
        for original_file in files_in_temp_dir:
            compressed_file = original_file + ".br"
            assert os.path.exists(compressed_file)
            assert not os.path.exists(original_file)
    
    def test_compress_preserves_original_by_default(self, temp_dir, files_in_temp_dir):
        result = run_program(temp_dir, "-c")
        
        assert result.returncode == 0
        for original_file in files_in_temp_dir:
            assert os.path.exists(original_file)


class TestDecompress:
    def test_decompress_creates_original_files(self, temp_dir, files_in_temp_dir, compressed_files):
        os.remove(files_in_temp_dir[0])
        
        result = run_program(temp_dir, "-d")
        
        assert result.returncode == 0
        assert os.path.exists(files_in_temp_dir[0])
    
    def test_decompress_output_message(self, temp_dir, compressed_files):
        result = run_program(temp_dir, "-d")
        
        assert "Decompressing files" in result.stdout
        assert "Decompressing: file0.txt.br" in result.stdout
    
    def test_decompress_with_long_alias(self, temp_dir, compressed_files):
        result = run_program(temp_dir, "--decompress")
        
        assert result.returncode == 0
    
    def test_decompress_skips_non_br_files(self, temp_dir, files_in_temp_dir, compressed_files):
        result = run_program(temp_dir, "-d")
        
        for original_file in files_in_temp_dir:
            assert f"Skipping {os.path.basename(original_file)}" not in result.stdout
    
    def test_decompress_with_remove_original(self, temp_dir, compressed_files):
        result = run_program(temp_dir, "-d", "-r")
        
        assert result.returncode == 0
        for compressed_file in compressed_files:
            original_file = compressed_file[:-3]
            assert os.path.exists(original_file)
            assert not os.path.exists(compressed_file)
    
    def test_decompress_preserves_original_by_default(self, temp_dir, compressed_files):
        result = run_program(temp_dir, "-d")
        
        assert result.returncode == 0
        for compressed_file in compressed_files:
            assert os.path.exists(compressed_file)


class TestHelp:
    def test_help_flag(self):
        result = run_program("--help")
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
    
    def test_help_shows_options(self):
        result = run_program("--help")
        
        output = result.stdout + result.stderr
        assert "-c" in output or "--compress" in output
        assert "-d" in output or "--decompress" in output
        assert "-r" in output or "--remove-original" in output


class TestEdgeCases:
    def test_empty_directory(self, temp_dir):
        result = run_program(temp_dir, "-c")
        
        assert result.returncode == 0
        assert "No files found" in result.stdout
    
    def test_invalid_directory(self):
        result = run_program("/nonexistent/directory", "-c")
        
        assert "Error" in result.stdout
        assert "not a valid directory" in result.stdout


class TestExclude:
    def test_exclude_single_directory(self, temp_dir):
        subdir_a = os.path.join(temp_dir, "a")
        subdir_b = os.path.join(temp_dir, "b")
        os.makedirs(subdir_a)
        os.makedirs(subdir_b)
        
        file_a = os.path.join(subdir_a, "file_a.txt")
        file_b = os.path.join(subdir_b, "file_b.txt")
        
        with open(file_a, "w") as f:
            f.write("Content A")
        with open(file_b, "w") as f:
            f.write("Content B")
        
        result = run_program(temp_dir, "-c", "-e", "b")
        
        assert result.returncode == 0
        assert os.path.exists(file_a + ".br")
        assert os.path.exists(file_b)
        assert not os.path.exists(file_b + ".br")
    
    def test_exclude_directory_with_subdirectories(self, temp_dir):
        subdir_a = os.path.join(temp_dir, "a")
        subdir_b = os.path.join(subdir_a, "b")
        subdir_c = os.path.join(subdir_a, "c")
        os.makedirs(subdir_b)
        os.makedirs(subdir_c)
        
        file_a = os.path.join(subdir_a, "file_a.txt")
        file_b = os.path.join(subdir_b, "file_b.txt")
        file_c = os.path.join(subdir_c, "file_c.txt")
        
        with open(file_a, "w") as f:
            f.write("Content A")
        with open(file_b, "w") as f:
            f.write("Content B")
        with open(file_c, "w") as f:
            f.write("Content C")
        
        result = run_program(temp_dir, "-c", "-e", "a/c")
        
        assert result.returncode == 0
        assert os.path.exists(file_a + ".br")
        assert os.path.exists(file_b + ".br")
        assert os.path.exists(file_c)
        assert not os.path.exists(file_c + ".br")
    
    def test_exclude_multiple_directories(self, temp_dir):
        subdir_a = os.path.join(temp_dir, "a")
        subdir_b = os.path.join(temp_dir, "b")
        subdir_c = os.path.join(temp_dir, "c")
        os.makedirs(subdir_a)
        os.makedirs(subdir_b)
        os.makedirs(subdir_c)
        
        file_a = os.path.join(subdir_a, "file_a.txt")
        file_b = os.path.join(subdir_b, "file_b.txt")
        file_c = os.path.join(subdir_c, "file_c.txt")
        
        with open(file_a, "w") as f:
            f.write("Content A")
        with open(file_b, "w") as f:
            f.write("Content B")
        with open(file_c, "w") as f:
            f.write("Content C")
        
        result = run_program(temp_dir, "-c", "-e", "b", "c")
        
        assert result.returncode == 0
        assert os.path.exists(file_a + ".br")
        assert os.path.exists(file_b)
        assert os.path.exists(file_c)
        assert not os.path.exists(file_b + ".br")
        assert not os.path.exists(file_c + ".br")
    
    def test_exclude_with_decompress(self, temp_dir):
        subdir_a = os.path.join(temp_dir, "a")
        subdir_b = os.path.join(temp_dir, "b")
        os.makedirs(subdir_a)
        os.makedirs(subdir_b)
        
        file_a = os.path.join(subdir_a, "file_a.txt")
        file_b = os.path.join(subdir_b, "file_b.txt")
        
        with open(file_a, "w") as f:
            f.write("Content A")
        with open(file_b, "w") as f:
            f.write("Content B")
        
        subprocess.run(
            [PYTHON_BIN, MAIN_SCRIPT, temp_dir, "-c", "-r"],
            check=True
        )
        
        file_a_br = file_a + ".br"
        file_b_br = file_b + ".br"
        
        result = run_program(temp_dir, "-d", "-r", "-e", "b")
        
        assert result.returncode == 0
        assert os.path.exists(file_a)
        assert not os.path.exists(file_a_br)
        assert os.path.exists(file_b_br)
        assert not os.path.exists(file_b)
    
    def test_exclude_with_long_alias(self, temp_dir):
        subdir_a = os.path.join(temp_dir, "a")
        subdir_b = os.path.join(temp_dir, "b")
        os.makedirs(subdir_a)
        os.makedirs(subdir_b)
        
        file_a = os.path.join(subdir_a, "file_a.txt")
        file_b = os.path.join(subdir_b, "file_b.txt")
        
        with open(file_a, "w") as f:
            f.write("Content A")
        with open(file_b, "w") as f:
            f.write("Content B")
        
        result = run_program(temp_dir, "-c", "--exclude", "b")
        
        assert result.returncode == 0
        assert os.path.exists(file_a + ".br")
        assert os.path.exists(file_b)
