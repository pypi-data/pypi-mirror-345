# Setting Up the Development Environment

To contribute to the uynab project, it's important to set up a development environment that matches the project's requirements. This ensures consistency and reduces the time spent debugging non-existent bugs.

## Prerequisites

Before setting up the environment, ensure you have the following installed:

- **Python**: The project is built using Python. Make sure you have Python installed on your machine. The project has to be compatible with **python3.10**
- **Make**: We use Make to simplify various tasks such as setup, testing, and building the project.
- **Curl**: Required for downloading scripts.
- **Linux** machine: It is not a hard requirement, but all instructions here are based on **Ubuntu 22.04**.

## Steps to Set Up the Environment

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/ajwalkiewicz/uynab.git
    cd uynab
    ```

2. **Install UV**:
    UV is used for project management. If UV is not installed, the setup script will install it for you.
    ```sh
    make check-uv
    ```

3. **Set Up the Project**:
    Run the setup command to install all necessary dependencies and set up the project.
    ```sh
    make setup
    ```

4. **Verify the Setup**:
    Ensure that the setup was successful by running the following command:
    ```sh
    make check
    ```

## Additional Commands

- **Build the Project**:
  ```sh
  make build
  ```

- **Run Tests**:
  ```sh
  make test
  ```

- **Run All Tests**:
  ```sh
  make test_all
  ```

- **Clean the Environment**:
  ```sh
  make clean
  ```

- **Format the Code**:
  ```sh
  make format
  ```

- **Check Typing**:
  ```sh
  make type
  ```

- **Serve Documentation Locally**:
  ```sh
  make docs_serve
  ```

- **Upload Documentation**:
  ```sh
  make docs_upload
  ```

By following these steps, you will have a development environment that is consistent with the project's requirements. For any issues or further details, refer to the [Contribution Guidelines](contribution.md).

## References

* Python: https://www.python.org/ 
* Project management tool: [UV](https://docs.astral.sh/uv/)
* Formatter: [Ruff](https://docs.astral.sh/ruff/)
* Testing: [Pytest](https://docs.pytest.org/en/stable/index.html)