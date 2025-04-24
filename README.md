# NVIDIA NIM Anywhere

[![Clone Me with AI Workbench](https://img.shields.io/badge/Open_In-AI_Workbench-76B900)](https://ngc.nvidia.com/open-ai-workbench/aHR0cHM6Ly9naXRodWIuY29tL05WSURJQS9uaW0tYW55d2hlcmUK)

NIM Anywhere is a starting point into discovering enterprise AI. This branch is currently under heavy construction.

![NIM Anywhere Screenshot](data/hero.png)

# NEEDS TO BE UPDATED

# Getting  Started

## Prerequisites

### Generate your NGC Personal Key

To allow AI Workbench to access NVIDIA’s cloud resources, you’ll need to
provide it with a Personal Key. These keys begin with `nvapi-`.

<details>
<summary>
<b>Expand this section for instructions for creating this key.</b>
</summary>

1.  Go to the [NGC Personal Key
    Manager](https://org.ngc.nvidia.com/setup/personal-keys). If you are
    prompted to, then register for a new account and sign in.

    > **HINT** You can find this tool by logging into
    > [ngc.nvidia.com](https://ngc.nvidia.com), expanding your profile
    > menu on the top right, selecting *Setup*, and then selecting
    > *Generate Personal Key*.

2.  Select *Generate Personal Key*.

    ![Generate Personal Key](.static/_static/generate_personal_key.png)

3.  Enter any value as the Key name, an expiration of 12 months is fine,
    and select all the services. Press *Generate Personal Key* when you
    are finished.

    ![Personal Key Form](.static/_static/personal_key_form.png)

4.  Save your personal key for later. Workbench will need it and there
    is no way to retrieve it later. If the key is lost, a new one must
    be created. Protect this key as if it were a password.

    ![Personal Key](.static/_static/personal_key.png)

</details>

### Authenticate with Docker

Workbench will use your system's Docker client to pull NVIDIA NIM
containers, so before continuing, make sure to follow these steps to
authenticate your Docker client with your NGC Personal Key.

1.  Run the following Docker login command

    ``` bash
    docker login nvcr.io
    ```

2.  When prompted for your credentials, use the following values:

    - Username: `$oauthtoken`
    - Password: Use your NGC Personal key beggining with `nv-api`

### Install AI Workbench

This project is designed to be used with [NVIDIA AI
Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/).
While this is not a requirement, running this demo without AI Workbench
will require manual work as the pre-configured automation and
integrations may not be available.

This quick start guide will assume a remote lab machine is being used
for development and the local machine is a thin-client for remotely
accessing the development machine. This allows for compute resources to
stay centrally located and for developers to be more portable. Note, the
remote lab machine must run Ubuntu, but the local client can run
Windows, MacOS, or Ubuntu. To install this project local only, simply
skip the remote install.

``` mermaid
flowchart LR
    local
    subgraph lab environment
        remote-lab-machine
    end

    local <-.ssh.-> remote-lab-machine
```

#### Client Machine Install

Ubuntu is required if the local client will also be used for developent.
When using a remote lab machine, this can be Windows, MacOS, or Ubuntu.

<details>
<summary>
<b>Expand this section for a Windows install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User
Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/windows.html).

1.  Install Prerequisite Software

    1.  If this machine has an NVIDIA GPU, ensure the GPU drivers are
        installed. It is recommended to use the [GeForce
        Experience](https://www.nvidia.com/en-us/geforce/geforce-experience/)
        tooling to manage the GPU drivers.
    2.  Install [Docker
        Desktop](https://www.docker.com/products/docker-desktop/) for
        local container support. Please be mindful of Docker Desktop's
        licensing for enterprise use. [Rancher
        Desktop](https://rancherdesktop.io/) may be a viable
        alternative.
    3.  *\[OPTIONAL\]* If Visual Studio Code integration is desired,
        install [Visual Studio Code](https://code.visualstudio.com/).

2.  Download the [NVIDIA AI
    Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/)
    installer and execute it. Authorize Windows to allow the installer
    to make changes.

3.  Follow the instructions in the installation wizard. If you need to
    install WSL2, authorize Windows to make the changes and reboot local
    machine when requested. When the system restarts, the NVIDIA AI
    Workbench installer should automatically resume.

4.  Select Docker as your container runtime.

5.  Log into your GitHub Account by using the *Sign in through
    GitHub.com* option.

6.  Enter your git author information if requested.

</details>

<details>
<summary>
<b>Expand this section for a MacOS install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User
Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/macos.html).

1.  Install Prerequisite Software

    1.  Install [Docker
        Desktop](https://www.docker.com/products/docker-desktop/) for
        local container support. Please be mindful of Docker Desktop's
        licensing for enterprise use. [Rancher
        Desktop](https://rancherdesktop.io/) may be a viable
        alternative.
    2.  *\[OPTIONAL\]* If Visual Studio Code integration is desired,
        install [Visual Studio Code](https://code.visualstudio.com/).
        When using VSCode on a Mac, an a[dditional step must be
        performed](https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line)
        to install the VSCode CLI interface used by Workbench.

2.  Download the [NVIDIA AI
    Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/)
    disk image (*.dmg* file) and open it.

3.  Drag AI Workbench into the Applications folder and run *NVIDIA AI
    Workbench* from the application launcher. ![Mac DMG Install
    Interface](.static/_static/mac_dmg_drag.png)

4.  Select Docker as your container runtime.

5.  Log into your GitHub Account by using the *Sign in through
    GitHub.com* option.

6.  Enter your git author information if requested.

</details>

<details>
<summary>
<b>Expand this section for an Ubuntu install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User
Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/ubuntu-local.html).
Run this installation as the user who will be user Workbench. Do not run
these steps as `root`.

1.  Install Prerequisite Software

    1.  *\[OPTIONAL\]* If Visual Studio Code integration is desired,
        install [Visual Studio Code](https://code.visualstudio.com/).

2.  Download the [NVIDIA AI
    Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/)
    installer, make it executable, and then run it. You can make the
    file executable with the following command:

    ``` bash
    chmod +x NVIDIA-AI-Workbench-*.AppImage
    ```

3.  AI Workbench will install the NVIDIA drivers for you (if needed).
    You will need to reboot your local machine after the drivers are
    installed and then restart the AI Workbench installation by
    double-clicking the NVIDIA AI Workbench icon on your desktop.

4.  Select Docker as your container runtime.

5.  Log into your GitHub Account by using the *Sign in through
    GitHub.com* option.

6.  Enter your git author information if requested.

</details>

#### Remote Machine Install

Only Ubuntu is supported for remote machines.

<details>
<summary>
<b>Expand this section for a remote Ubuntu install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User
Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/ubuntu-remote.html).
Run this installation as the user who will be using Workbench. Do not
run these steps as `root`.

1.  Ensure SSH Key based authentication is enabled from the local
    machine to the remote machine. If this is not currently enabled, the
    following commands will enable this is most situations. Change
    `REMOTE_USER` and `REMOTE-MACHINE` to reflect your remote address.

    - From a Windows local client, use the following PowerShell:
      ``` powershell
      ssh-keygen -f "C:\Users\local-user\.ssh\id_rsa" -t rsa -N '""'
      type $env:USERPROFILE\.ssh\id_rsa.pub | ssh REMOTE_USER@REMOTE-MACHINE "cat >> .ssh/authorized_keys"
      ```
    - From a MacOS or Linux local client, use the following shell:
      ``` bash
      if [ ! -e ~/.ssh/id_rsa ]; then ssh-keygen -f ~/.ssh/id_rsa -t rsa -N ""; fi
      ssh-copy-id REMOTE_USER@REMOTE-MACHINE
      ```

2.  SSH into the remote host. Then, use the following commands to
    download and execute the NVIDIA AI Workbench Installer.

    ``` bash
    mkdir -p $HOME/.nvwb/bin && \
    curl -L https://workbench.download.nvidia.com/stable/workbench-cli/$(curl -L -s https://workbench.download.nvidia.com/stable/workbench-cli/LATEST)/nvwb-cli-$(uname)-$(uname -m) --output $HOME/.nvwb/bin/nvwb-cli && \
    chmod +x $HOME/.nvwb/bin/nvwb-cli && \
    sudo -E $HOME/.nvwb/bin/nvwb-cli install
    ```

3.  AI Workbench will install the NVIDIA drivers for you (if needed).
    You will need to reboot your remote machine after the drivers are
    installed and then restart the AI Workbench installation by
    re-running the commands in the previous step.

4.  Select Docker as your container runtime.

5.  Log into your GitHub Account by using the *Sign in through
    GitHub.com* option.

6.  Enter your git author information if requested.

7.  Once the remote installation is complete, the Remote Location can be
    added to the local AI Workbench instance. Open the AI Workbench
    application, click *Add Remote Location*, and then enter the
    required information. When finished, click *Add Location*.

    - \*Location Name: \* Any short name for this new location
    - \*Description: \* Any brief metadata for this location.
    - \*Hostname or IP Address: \* The hostname or address used to
      remotely SSH. If step 1 was followed, this should be the same as
      `REMOTE-MACHINE`.
    - \*SSH Port: \* Usually left blank. If a nonstandard SSH port is
      used, it can be configured here.
    - \*SSH Username: \* The username used for making an SSH connection.
      If step 1 was followed, this should be the same as `REMOTE_USER`.
    - \*SSH Key File: \* The path to the private key for making SSH
      connections. If step 1 was followed, this should be:
      `/home/USER/.ssh/id_rsa`.
    - \*Workbench Directory: \* Usually left blank. This is where
      Workbench will remotely save state.

</details>

## Installing

### Download this project

There are two ways to download this project for local use: Cloning and
Forking.

Cloning this repository is the recommended way to start. This will not
allow for local modifications, but is the fastest to get started. This
also allows for the easiest way to pull updates.

Forking this repository is recommended for development as changes will
be able to be saved. However, to get updates, the fork maintainer will
have to regularly pull from the upstream repo. To work from a fork,
follow [GitHub's
instructions](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)
and then reference the URL to your personal fork in the rest of this
section.

<details>
<summary>
<b>Expand this section for a details on downloading this project.</b>
</summary>

1.  Open the local NVIDIA AI Workbench window. From the list of
    locations displayed, select either the remote one you just set up,
    or local if you're going to work locally.

    ![AI Workbench Locations Menu](.static/_static/nvwb_locations.png)

2.  Once inside the location, select *Clone Project*.

    ![AI Workbench Projects Menu](.static/_static/nvwb_projects.png)

3.  In the 'Clone Project' pop up window, set the Repository URL to
    `https://github.com/NVIDIA/nim-anywhere.git`. You can leave the Path
    as the default of
    `/home/REMOTE_USER/nvidia-workbench/nim-anywhere.git`. Click
    *Clone*.\`

    ![AI Workbench Clone Project Menu](.static/_static/nvwb_clone.png)

4.  You will be redirected to the new project’s page. Workbench will
    automatically bootstrap the development environment. You can view
    real-time progress by expanding the Output from the bottom of the
    window.

    ![AI Workbench Log Viewer](.static/_static/nvwb_logs.png)

</details>

### Configure this project

The project must be configured to use your NGC personal key.

<details>
<summary>
<b>Expand this section for a details on configuring this project.</b>
</summary>

1.  Before running for the first time, your NGC personal key must be
    configured in Workbench. This is done using the *Environment* tab
    from the left-hand panel.

    ![AI Workbench Side Menu](.static/_static/nvwb_left_menu.png)

2.  Scroll down to the **Secrets** section and find the *NGC_API_KEY*
    entry. Press *Configure* and provide the personal key for NGC that
    was generated earlier.

</details>

### Start This Project

Even the most basic of LLM Chains depend on a few additional
microservices. These can be ignored during development for in-memory
alternatives, but then code changes are required to go to production.
Thankfully, Workbench manages those additional microservices for
development environments.

<details>
<summary>
<b>Expand this section for details on starting the demo application.</b>
</summary>

> **HINT:** For each application, the debug output can be monitored in
> the UI by clicking the Output link in the lower left corner, selecting
> the dropdown menu, and choosing the application of interest (or
> **Compose** for applications started via compose).

Since you can either pull NIMs and run them locally, or utilize the
endpoints from *ai.nvidia.com* you can run this project with *or*
without GPUs.

1.  The applications bundled in this workspace can be controlled by
    navigating to two tabs:

    - **Environment** \> **Compose**
    - **Environment** \> **Applications**

2.  First, navigate to the **Environment** \> **Compose** tab. If you're
    not working in an environment with GPUs, you can just click
    **Start** to run the project using a lightweight deployment. This
    default configuration will run the following containers:

    - *Milvus Vector DB*: An unstructured knowledge base

    - *Redis*: Used to store conversation histories

3.  If you have access to GPU resources and want to run any NIMs
    locally, use the dropdown menu under **Compose** and select which
    set of NIMs you want to run locally. Note that you *must* have at
    least 1 available GPU per NIM you plan to run locally. Below is an
    outline of the available configurations:

    - Local LLM (min 1 GPU required)

      - The first time the LLM NIM is started, it will take some time to
        download the image and the optimized models.
        - During a long start, to confirm the LLM NIM is starting, the
          progress can be observed by viewing the logs by using the
          *Output* pane on the bottom left of the UI.

        - If the logs indicate an authentication error, that means the
          provided *NGC_API_KEY* does not have access to the NIMs.
          Please verify it was generated correctly and in an NGC
          organization that has NVIDIA AI Enterprise support or trial.

        - If the logs appear to be stuck on `..........: Pull complete`.
          `..........: Verifying complete`, or
          `..........: Download complete`; this is all normal output
          from Docker that the various layers of the container image
          have been downloaded.

        - Any other failures here need to be addressed.

    - Local LLM + Embedding (min 2 GPUs required)

    - Local LLM + Embedding + Reranking (min 3 GPUs required)

    > **NOTE:**
    >
    > - Each profile will also run *Milvus Vector DB* and *Redis*
    > - Due to the nature of Docker Compose profiles, the UI will let
    >   you select multiple profiles at the same time. In the context of
    >   this project, selecting multiple profiles does not make sense.
    >   It will not cause any errors, however we recommend only
    >   selecting one profile at a time for simplicity.

4.  Once the compose services have been started, navigate to the
    **Environment** \> **Applications** tab. Now, the *Chain Server* can
    safely be started. This contains the custom LangChain code for
    performing our reasoning chain. By default, it will use the local
    Milvus and Redis, but use *ai.nvidia.com* for LLM, Embedding, and
    Reranking model inferencing.

5.  Once the *Chain Server* is up, the *Chat Frontend* can be started.
    Starting the interface will automatically open it in a browser
    window. If you are running any local NIMs, you can edit the config
    to connect to them via the *Chat Frontend*

![NIM Anywhere Frontend](.static/_static/na_frontend.png)

</details>

### Populating the Knowledge Base

To get started developing demos, a sample dataset is provided along with
a Jupyter Notebook showing how data is ingested into a Vector Database.

1.  To import PDF documentation into the vector Database, open Jupyter
    using the app launcher in AI Workbench.

2.  Use the Jupyter Notebook at `code/upload-pdfs.ipynb` to ingest the
    default dataset. If using the default dataset, no changes are
    necessary.

3.  If using a custom dataset, upload it to the `data/` directory in
    Jupyter and modify the provided notebook as necessary.

# Contributing

## Running the tests

- lint
- ci

## Managing your Development Environment

### Environment Variables

Most of the configuration for the development environment happens with
Environment Variables. To make permanent changes to environment
variables, modify [`variables.env`](./variables.env) or use the
Workbench UI.

### Python Environment Packages

This project uses one Python environment at `/usr/bin/python3` and
dependencies are managed with `pip`. Because all development is done
inside a container, any changes to the Python environment will be
ephemeral. To permanently install a Python package, add it to the
[`requirements.txt`](./requirements.txt) file or use the Workbench UI.

### Operating System Configuration

The development environment is based on Ubuntu 22.04. The primary user
has password-less sudo access, but all changes to the system will be
ephemeral. To make permanent changes to installed packages, add them to
the \[`apt.txt`\] file. To make other changes to the operating system
such as manipulating files, adding environment variables, etc; use the
[`postBuild.bash`](./postBuild.bash) and
[`preBuild.bash`](./preBuild.bash) files.

## Updating Dependencies

It is typically good practice to update dependencies monthly to ensure
no CVEs are exposed through misused dependencies. The following process
can be used to patch this project. It is recommended to run the
regression testing after the patch to ensure nothing has broken in the
update.

1.  **Update Environment:** In the workbench GUI, open the project and
    navigate to the Environment pane. Check if there is an update
    available for the base image. If an updated base image is available,
    apply the update and rebuild the environment. Address any build
    errors. Ensure that all of the applications can start.
2.  **Update Python Packages and NIMs:** The Python dependencies and NIM
    applications can be updated automatically by running the
    `/project/code/tools/bump.sh` script.
3.  **Update Remaining applications:** For the remaining applications,
    manually check their default tag and compare to the latest. Update
    where appropriate and ensure that the applications still start up
    successfully.
4.  **Restart and rebuild the environment.**
5.  **Audit Python Environment:** It is now best to check the installed
    versions of ALL Python packages, not just the direct dependencies.
    To accomplish this, run `/project/code/tools/audit.sh`. This script
    will print out a report of all Python packages in a warning state
    and all packages in an error state. Anything in an error state must
    be resolved as it will have active CVEs and known vulnerabilities.
6.  **Check Dependabot Alerts:** Check all of the
    [Dependabot](https://github.com/NVIDIA/nim-anywhere/security/dependabot)
    alerts and ensure they should be resolved.
7.  **Regression testing:** Run through the entire demo, from document
    ingesting to the frontend, and ensure it is still functional and
    that the GUI looks correct.

# License

This project is licensed under the Apache 2.0 License  -  see the [LICENSE.txt](LICENSE.txt) file for details.
