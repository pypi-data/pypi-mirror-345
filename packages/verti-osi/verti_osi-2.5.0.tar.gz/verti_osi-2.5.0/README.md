# Verti-OSI CLI Tool Documentation

## Overview

Verti-OSI is a command-line tool for **generating OCI-compliant container images** and **Dockerfiles** based on your application source code.  
It supports flexible configurations via **CLI parameters** or a **YAML file**.

You can:
- Generate a Dockerfile
- Build a container image
- Supply custom build-time and run-time base images
- Use custom build commands, pre-build commands, and environment variables
- Pull code from a remote repository
- Support multiple platforms (e.g., `linux/amd64`, `linux/arm64`)

---

## Supported Languages

- **Python** (detects `requirements.txt` / `pyproject.toml`)
- **Node.js** (detects `package.json`)

---

## Prerequisites

Make sure you have:

- **Python 3.7+** installed:
  ```sh
  python --version
  ```

- **pipx** installed:
  ```sh
  pipx --version
  ```
  If not installed:
  ```sh
  python -m pip install --user pipx
  pipx ensurepath
  ```

- **A container daemon** running:
  - **Docker**:
    ```sh
    docker info
    ```
  - **Podman**:
    ```sh
    podman info
    ```

---

## Installation

Install Verti-OSI globally with `pipx`:

```sh
pipx install verti-osi
```

---

## Usage

After installing, invoke the CLI tool using:

```sh
verti-osi
```

Verti-OSI has **two main commands**:

| Command | Description |
|:--------|:------------|
| `dockerfile` | Generate a Dockerfile only |
| `image` | Build a container image (can also generate the Dockerfile internally) |

---

## Command Reference

### Generate an Image

```sh
verti-osi image [OPTIONS]
```

**Key CLI options:**

| Option | Description |
|:-------|:------------|
| `--file-dir` | Path to `verti-osi.yaml` config file |
| `--root-directory` | Project's root directory (default: `.`) |
| `--source-directory` | Source code directory (default: `.`) |
| `--image-name` | Name of the generated image |
| `--build-image` | Base image to use during build |
| `--run-time-image` | Base image for runtime |
| `--platforms` | Comma-separated build platforms |
| `--repository-url` | Git repository URL |
| `--repository-branch` | Git repository branch |
| `--env-vars` | Environment variables for all stages |
| `--env-vars-rt` | Runtime-specific environment variables |
| `--env-vars-bt` | Build-time-specific environment variables |
| `--pre-build-commands` | Commands before build |
| `--build-commands` | Build commands |
| `--output` | Image output: `tar`, `registry`, `standard` |
| `--delete-generated-dockerfile` | Delete Dockerfile after build (True/False) |
| `--run-generated-image` | Run image after build (True/False) |
| `--port` | Port to expose (default: 8080) |
| `--daemon` | Container daemon (`docker` or `podman`) |

---

### Generate a Dockerfile

```sh
verti-osi dockerfile [OPTIONS]
```

**Key CLI options:**

Same as `image` command, but without:
- `--platforms`
- `--output`
- `--run-generated-image`

---

## Configuration via YAML

You can define all parameters using a `verti-osi.yaml` config file.

Then invoke:

```sh
verti-osi <image | dockerfile> --file-dir <path-to-directory>
```

### Example `verti-osi.yaml`

```yaml
image-name: verti-node-app:v1
source-directory: ./src
root-directory: .
delete-generated-dockerfile: true
daemon: docker
output-type: tar
platform:
  - linux/amd64
  - linux/arm64
pre-build:
  - echo "Running pre-build steps"
build:
  - npm run build
env-vars:
  - name: API_KEY
    value: abc123
    type: both
  - name: DEBUG
    value: true
    type: runtime
port: 8080
remote-source-repository:
  git:
    url: https://github.com/example/project
    branch: main
images:
  build: node:20-slim
  run-time: node:20-alpine
```

---

## Examples

### 1. Build and Push an Image to Registry

```sh
verti-osi image --root-directory . \
                --source-directory ./src \
                --image-name myorg/myapp:v1 \
                --output registry
```

---

### 2. Generate Dockerfile Only

```sh
verti-osi dockerfile --root-directory . \
                     --source-directory ./src \
                     --output-directory ./dockerfiles
```

---

### 3. Full Flow (YAML + Build + Push + Clean Dockerfile)

```sh
verti-osi image --file-dir ./configs \
                --output registry \
                --delete-generated-dockerfile True
```

---

## Features Summary

✅ Automatic Language Detection  
✅ Custom Build & Run-time Images  
✅ Pre-Build and Build Commands  
✅ Pull Source from Git Repositories  
✅ Multi-Platform Build Support  
✅ Dockerfile Only Generation  
✅ Docker or Podman Support  
✅ Configurable via CLI or YAML  

---

## License

Verti-OSI is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

