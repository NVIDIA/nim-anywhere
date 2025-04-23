#!/bin/bash
# This file contains bash commands that will be executed at the end of the container build process,
# after all system packages and programming language specific package have been installed.
#
# Note: This file may be removed if you don't need to use it

# Grant user sudo access
echo "workbench ALL=(ALL) NOPASSWD:ALL" | \
    sudo tee /etc/sudoers.d/00-workbench > /dev/null


# install ngc binary
cd /opt
# commands from: https://org.ngc.nvidia.com/setup/installers/cli
if [ "$(uname -i)" == "x86_64" ]; then
  sudo wget --content-disposition https://api.ngc.nvidia.com/v2/resources/nvidia/ngc-apps/ngc_cli/versions/3.41.4/files/ngccli_linux.zip -O ngccli_linux.zip
else
  sudo wget --content-disposition https://api.ngc.nvidia.com/v2/resources/nvidia/ngc-apps/ngc_cli/versions/3.41.4/files/ngccli_arm64.zip -O ngccli_linux.zip
fi
sudo unzip ngccli_linux.zip
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

# clean up
sudo apt-get autoremove -y
sudo rm -rf /var/cache/apt
