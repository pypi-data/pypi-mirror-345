import typer
from vertibit_osi_image_generator.shared_aux.shared import delete_files
from vertibit_osi_image_generator.shared_aux.extract_and_run_image import run_docker_image
from vertibit_osi_image_generator.shared_aux.comand_runner import run_and_log_commands


def stream_subprocess_output(process, queue, stream_name):
    """
    Read from a subprocess stream (stdout/stderr) line by line and put into a queue
    """
    stream = process.stdout if stream_name == 'stdout' else process.stderr
    for line in iter(stream.readline, ''):
        queue.put((stream_name, line.strip()))
    stream.close()


def build_docker_image(daemon, image_name, container_file, build_context, run_generated_image="False", delete_generated_dockerfile="False", output="", platforms: list = ["linux/amd64", "linux/arm64"]):
    """
    Builds a Docker image using the provided parameters.

    Args:
        daemon (str): Docker daemon to use (e.g., "docker" or "podman").
        image_name (str): Name of the Docker image to build.
        container_file (str): Path to the Dockerfile or Containerfile.
        build_context (str): Path to the build context.

    Raises:
        typer.Exit: Exits the CLI with an error code if the command fails.
    """
    formatted_platforms = ','.join(platforms)
    platform = f"--platform {formatted_platforms}"
    if output == 'push':
        command = f"{
            daemon} build {platform} -t {image_name} -f {container_file} -o type=registry,name={image_name} {build_context}"

    if output == 'tar':
        command = f"{
            daemon} build {platform} -t {image_name} -f {container_file} {build_context} && {daemon} save {image_name} -o {image_name}.tar"

    if output == 'normal' or output == '':
        command = f"{
            daemon} build {platform} -t {image_name} -f {container_file} {build_context}"

    try:
        run_and_log_commands(command)

        typer.echo(f"Docker image '{image_name}' built successfully!")

        if delete_generated_dockerfile == True:
            delete_files([container_file])

        if run_generated_image == True and output in ['push', 'normal', '']:
            run_docker_image(image_name)

        # if run_generated_image.lower() == 'true' and output == 'tar':
        #     run_docker_image_from_tgz(image_name, f'./tmp/{image_name}.tar')

    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(1)
