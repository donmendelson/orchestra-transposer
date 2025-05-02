import os
import subprocess
import tempfile
from pathlib import Path


def test_main_orchestra10_to_11():
    # Get the path to the input file
    input_file = str(Path(__file__).parent / 'xml' / 'OrchestraFIXLatest.xml')

    # Create a temporary output file
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_output:
        output_file = temp_output.name

        # Run the main function with arguments
        result = subprocess.run(["python", "-m", '-f', 'orch', '-t', 'orch11', input_file,
                                 '-o', output_file])

        # Verify the output file was created and has content
        assert os.path.exists(output_file)
        # assert os.path.getsize(output_file) > 0

        # Verify the log file was created
        log_file = os.path.splitext(output_file)[0] + '.log'
        assert os.path.exists(log_file)

def test_main_no_arguments():
    # Run the main function without any arguments
    result = subprocess.run(["python", "-m", "orchestratransposer"], capture_output=True, text=True)

    # Capture the output
    captured = result.stderr

    # Verify the output contains usage information
    assert 'usage:' in captured.lower()


def test_main_help():
    # Run the main function without any arguments
    result = subprocess.run(["python", "-m", "orchestratransposer", "-h"], capture_output=False)
