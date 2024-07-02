

### Remote Machine Install

Only Ubuntu is supported for remote machines.

<details>
<summary>
<b>Expand this section for a remote Ubuntu install.</b>
</summary>

For full instructions, see the [NVIDIA AI Workbench User Guide](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/ubuntu-remote.html). Run this installation as the user who will be using Workbench. Do not run these steps as `root`.

1. Ensure SSH Key based authentication, without a passphrase, is enabled from the local machine to the remote machine. If this is not currently enabled, the following commands will enable this is most situations.

    - From a Windows local client, use the following PowerShell:
      ```powershell
      ssh-keygen -f "C:\Users\local-user\.ssh\id_rsa" -t rsa -N '""'
      type $env:USERPROFILE\.ssh\id_rsa.pub | ssh REMOTE_USER@REMOTE-MACHINE "cat >> .ssh/authorized_keys"
      ```
    - From a MacOS or Linux local client, use the following shell:
      ```bash
      if [ ! -e ~/.ssh/id_rsa ]; then ssh-keygen -f ~/.ssh/id_rsa -t rsa -N ""; fi
      ssh-copy-id REMOTE_USER@REMOTE-MACHINE
      ```

1. SSH into the remote host. Then, use the following commands to download and execute the NVIDIA AI Workbench Installer.

    ```bash
    mkdir -p $HOME/.nvwb/bin && \
    curl -L https://workbench.download.nvidia.com/stable/workbench-cli/$(curl -L -s https://workbench.download.nvidia.com/stable/workbench-cli/LATEST)/nvwb-cli-$(uname)-$(uname -m) --output $HOME/.nvwb/bin/nvwb-cli && \
    chmod +x $HOME/.nvwb/bin/nvwb-cli && \
    sudo -E $HOME/.nvwb/bin/nvwb-cli install
    ```

1. AI Workbench will install the NVIDIA drivers for you (if needed). You will need to reboot your machine after the drivers are installed and then restart the AI Workbench installation by re-running the commands in the previous step.

1. Select Docker as your container runtime.

1. Log into your GitHub Account by using the *Sign in through GitHub.com* option.

1. Enter your git author information if requested.

1. Once the remote installation is complete, the Remote Location can be added to the local AI Workbench instance. Open the AI Workbench application, click *Add Remote Location*, and then enter the required information. When finished, click *Add Location*.

    - *Location Name: * Any short name for this new location
    - *Description: * Any breif metadata for this location.
    - *Hostname or IP Address: * The hostname or address used to remotely SSH. If step 1 was followed, this should be the same as `REMOTE-MACHINE`.
    - *SSH Port: * Usually left blank. If a nonstandard SSH port is used, it can be configured here.
    - *SSH Username: * The username used for making an SSH connection. If step 1 was followed, this should be the same as `REMOTE_USER`.
    - *SSH Key File: * The path to the private key for making SSH connections. If step 1 was followed, this should be: `/home/USER/.ssh/id_rsa`.
    - *Workbench Directory: * Usually left blank. This is where Workbench will remotely save state.


</details>
