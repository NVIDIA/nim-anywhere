<details>
<summary>
<b>Expand this section for a Windows install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/windows.html).

1. Install Prerequisite Software
    1. If this machine has an NVIDIA GPU, ensure the GPU drivers are installed. It is recommended to use the [GeForce Experience](https://www.nvidia.com/en-us/geforce/geforce-experience/) tooling to manage the GPU drivers.
    1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for local container support. Please be mindful of Docker Desktop's licensing for enterprise use. [Rancher Desktop](https://rancherdesktop.io/) may be a viable alternative.
    1. *[OPTIONAL]* If Visual Studio Code integration is desired, install [Visual Studio Code](https://code.visualstudio.com/).

1. Download the [NVIDIA AI Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/) installer and execute it. Authorize Windows to allow the installer to make changes.

1. Follow the instructions in the installation wizard. If you need to install WSL2, authorize Windows to make the changes and reboot when requested. When the system restarts, the NVIDIA AI Workbench installer should automatically resume.

1. Select Docker as your container runtime.

1. Log into your GitHub Account by using the *Sign in through GitHub.com* option.

1. Enter your git author information if requested.

</details>
