## Authenticate with Docker

Workbench will use your system's Docker client to pull NVIDIA NIM containers, so before continuing, make sure to follow these steps to authenticate your Docker client with your NGC Personal Key.

1. Run the following Docker login command

    ```bash
    docker login nvcr.io
    ```

1. When prompted for your credentials, use the following values:

    - Username: `$oauthtoken`
    - Password: Use your NGC Personal key beggining with `nv-api`
