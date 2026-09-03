#!/bin/bash
set -euo pipefail

# This file contains bash commands that will be executed at the end of the container build process,
# after all system packages and programming language specific package have been installed.
#
# Note: This file may be removed if you don't need to use it

# install ngc binary
cd /opt
NGC_CLI_VERSION="4.34.10"
case "$(uname -m)" in
  x86_64)
    NGC_CLI_ARCHIVE="ngccli_linux.zip"
    NGC_CLI_SHA256="58bc4d7b6901551a095ce5a43a0065b1c22d5eaf1a164d40029ee3fda11ccd47"
    ;;
  aarch64|arm64)
    NGC_CLI_ARCHIVE="ngccli_arm64.zip"
    NGC_CLI_SHA256="5c18c5d14ad9e4b8c8ac0b5c596cd4ed33c1e4a3f2bd93f851eb974a6f3f6847"
    ;;
  *)
    echo "Unsupported architecture for NGC CLI: $(uname -m)" >&2
    exit 1
    ;;
esac
sudo wget --https-only --content-disposition \
  "https://api.ngc.nvidia.com/v2/resources/nvidia/ngc-apps/ngc_cli/versions/${NGC_CLI_VERSION}/files/${NGC_CLI_ARCHIVE}" \
  -O ngccli_linux.zip
echo "${NGC_CLI_SHA256}  ngccli_linux.zip" | sha256sum --check --strict -
sudo unzip -o ngccli_linux.zip
find ngc-cli/ -type f -exec md5sum {} + | LC_ALL=C sort | md5sum --check --strict ngc-cli.md5
sudo rm ngc-cli.md5 ngccli_linux.zip
sudo chmod ugo+x ngc-cli/ngc
cat <<EOM | sudo tee /etc/profile.d/ngc-cli.sh > /dev/null
export PATH=\$PATH:/opt/ngc-cli
EOM
cd -

# custom python environment configuration
cat <<EOM | sudo tee /etc/profile.d/python.sh > /dev/null
export PATH=\$PATH:/home/workbench/.local/bin
export PYTHONPATH=/project/code:\$PYTHONPATH
if [ ! -x /usr/bin/python ]; then sudo ln -s `which python3` /usr/bin/python; fi
EOM

# install scripts to initialize the development environment
cat <<EOM | sudo tee /etc/profile.d/init-dev-env.sh > /dev/null
if [ -f /project/code/config_sample.yaml ] && [ ! -f /project/code/config.yaml ]; then
  cp /project/code/config_sample.yaml /project/code/config.yaml &> /dev/null
fi
EOM

# setup the tutorial app
cd /opt
sudo python3 -m venv live-labs
sudo ./live-labs/bin/pip install wheel
sudo ./live-labs/bin/pip install git+https://github.com/NVIDIA/nim-anywhere.git#subdirectory=libs/live-labs
sudo ln -s /opt/live-labs/bin/streamlit /home/workbench/.local/bin/streamlit

# Run browser-authored tutorial code as a dedicated, unprivileged account. The workbench user can
# invoke only this exact isolated Python command as that account; it does not receive root sudo.
if ! id -u live-labs-sandbox > /dev/null 2>&1; then
  sudo useradd --system --no-create-home --shell /usr/sbin/nologin live-labs-sandbox
fi
echo "workbench ALL=(live-labs-sandbox) NOPASSWD: /opt/live-labs/bin/python -I -" | \
    sudo tee /etc/sudoers.d/live-labs-sandbox > /dev/null
sudo chmod 0440 /etc/sudoers.d/live-labs-sandbox
sudo visudo -cf /etc/sudoers.d/live-labs-sandbox

# clean up
sudo apt-get autoremove -y
sudo rm -rf /var/cache/apt
