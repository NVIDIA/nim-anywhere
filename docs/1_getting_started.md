## Getting Started

This project is designed to be used with [NVIDIA AI Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/). While this is not a requirement, running this demo without AI Workbench will require manual work as the pre-configured automation and integrations may not be available.

### Pre-requisites

- NVIDIA Driver
- Docker
- Ubuntu 22.04 on the developemnt machine

### AI Workbench Quickstart

1. Download execute the NVIDIA AI Workbench Installer.
2. Run the installation
    - Select Docker during the install
    - Perform any manual installs that are requested
3. If you are working on a remote machine, run the remote install of Workbench on that machine as well.
4. Open the Workbench UI
5. Go to the settings and configure the integration with GitHub.
6. If you are working on a remote machine, add the remote machine as a location.

### Cloning the project
1. Open the desired location in AI Workbench
2. Select `Clone Project`
3. Enter this repository in the repository URL
4. The default path is fine, but it can be modified as desired
5. Open the clonded project in the workbench UI then configure the secrets and mounts

### Running the project
1. In the Workbench project navigate to `Environment` -> `Apps`
2. Start Redis, Milvus, and the NIM (if local execution is desired). Wait for these to finish.
3. Start the Chain Server. The Chain Server has a UI that can be launched from Workbench. This UI is good for development and shows full chain traces.
4. Start the Chat Frontend. This will automatically open the UI.

### Populating the Knowledge Base
1. To import PDF documentation into the vector databse, open Jupyter.
1. Use the `upload-pdfs.ipynb` notebook to ingest the default dataset. If ussing the default dataset, no changes are necessary.
1. If using a custom dataset, upload it to the `data` directory in Jupyter and modify the provided notebook as necessary.
