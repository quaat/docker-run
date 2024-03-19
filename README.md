# Docker Run Tool

The Docker Run Tool simplifies the process of managing Docker containers by utilizing YAML configurations for container deployment. This tool allows users to define container settings, networks, and volumes in a YAML file and manage these containers with simple commands.
## Installation
### Prerequisites

* Python 3.6 or higher
* Docker installed and running on your machine
* Virtual Environment (recommended)

### Steps

1. Clone the repository (if applicable):

    ```bash
    git clone https://yourrepository.com/docker-run-tool.git
    cd docker-run-tool
    ```

2. Set up a Python virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the tool:

    Navigate to the root directory of the tool and run:
    
    ```bash
        pip install -e .
    ```

This command installs the tool in editable mode, allowing you to update the tool's code without needing to reinstall.

## Configuration Files
Configuration files should be stored in ~/.config/docker-run/. The tool accepts .yaml or .yml file extensions.

### Example Configuration

Create a file named postgres.yaml in the ~/.config/docker-run/ directory with the following content:

```yaml
container:
image: postgres:latest
name: psql
network: scinet
volume:
    - postgresdata: /var/lib/postgresql/data
ports:
    - 5432:5432
environment:
    - POSTGRES_DB: aiida
    - POSTGRES_USER: admin
    - POSTGRES_PASSWORD: admin

networks:
scinet:

volumes:
postgresdata:
```

### Example

To start a PostgreSQL container using the postgres configuration:

```bash
docker-run postgres
```

This command reads the postgres.yaml file from the ~/.config/docker-run/ directory and starts a Docker container with the specified configuration.
