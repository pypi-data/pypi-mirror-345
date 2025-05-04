import typer
from queue import Queue
import subprocess
import threading
import queue


def stream_subprocess_output(process, queue, stream_name):
    """
    Read from a subprocess stream (stdout/stderr) line by line and put into a queue
    """
    stream = process.stdout if stream_name == 'stdout' else process.stderr
    for line in iter(stream.readline, ''):
        queue.put((stream_name, line.strip()))
    stream.close()


def run_and_log_commands(command):
    try:
        # Log the command being executed
        typer.echo(f"Executing command: {command}")

        # Create the subprocess
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        # Create a queue to hold the output
        output_queue = Queue()

        # Create threads to read stdout and stderr
        stdout_thread = threading.Thread(
            target=stream_subprocess_output,
            args=(process, output_queue, 'stdout')
        )
        stderr_thread = threading.Thread(
            target=stream_subprocess_output,
            args=(process, output_queue, 'stderr')
        )

        # Start the threads
        stdout_thread.start()
        stderr_thread.start()

        # Print output as it becomes available
        error_output = []
        while stdout_thread.is_alive() or stderr_thread.is_alive() or not output_queue.empty():
            try:
                # Get output from queue with timeout
                stream_name, line = output_queue.get(timeout=0.1)
                if stream_name == 'stdout':
                    typer.echo(line)
                else:
                    typer.echo(line, err=True)
                    error_output.append(line)
            except queue.Empty:
                continue

        # Wait for process to complete
        process.wait()

        # Wait for reader threads to finish
        stdout_thread.join()
        stderr_thread.join()

        # Check for errors
        if process.returncode != 0:
            error_message = "\n".join(error_output)
            typer.echo(f"Error executing command {command}:\n{
                       error_message}", err=True)
            raise typer.Exit(code=process.returncode)

    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(1)
