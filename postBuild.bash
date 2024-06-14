#!/bin/bash
# This file contains bash commands that will be executed at the end of the container build process,
# after all system packages and programming language specific package have been installed.
#
# Note: This file may be removed if you don't need to use it

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the docker repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker-out-of-Docker
sudo apt-get install -y docker-ce-cli
cat <<EOM | sudo tee /etc/profile.d/docker-out-of-docker.sh > /dev/null
if ! groups workbench | grep docker > /dev/null; then
    docker_gid=\$(stat -c %g /var/host-run/docker.sock)
    sudo groupadd -g \$docker_gid docker
    sudo usermod -aG docker workbench
fi
export DOCKER_HOST="unix:///var/host-run/docker.sock"
EOM

# setup docker authentication to ngc
cat <<EOM | sudo tee /etc/profile.d/docker-ngc-auth.sh > /dev/null
if [ ! -x ~/.docker/config.json ]; then
    mkdir -p ~/.docker
    authstr=\$(echo -n '\$oauthtoken:'\$NGC_API_KEY | base64 -w 0)
    jq -n --arg key \$authstr '{"auths": {"nvcr.io": {"auth": \$key}}}' > ~/.docker/config.json
fi
EOM

# Grant user sudo access
echo "workbench ALL=(ALL) NOPASSWD:ALL" | \
    sudo tee /etc/sudoers.d/00-workbench > /dev/null

# Setup apps support
sudo apt install -y jq

# install ngc binary
sudo apt-get install -y wget unzip
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

# custom python environment configuration
cat <<EOM | sudo tee /etc/profile.d/python.sh > /dev/null
export PATH=\$PATH:/home/workbench/.local/bin
export PYTHONPATH=/project/code:\$PYTHONPATH
if [ ! -x /usr/bin/python ]; then sudo ln -s `which python3` /usr/bin/python; fi
EOM

# setup documentation tooling
export NODE_VERSION=20.13.1
export NVM_VERSION=0.39.7
# install nodejs
curl -o- https://raw.githubusercontent.com/creationix/nvm/v${NVM_VERSION}/install.sh | bash
export PATH=$PATH:~/.nvm/versions/node/v$NODE_VERSION/bin
# install mermaid
sudo apt-get install -y \
  ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
  libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
  libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
  libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils
npm install -g @mermaid-js/mermaid-cli
cat <<EOM | sudo tee /etc/profile.d/node.sh > /dev/null
export PATH=\$PATH:~/.nvm/versions/node/v$NODE_VERSION/bin
EOM

# install pandoc and pandoc filters
npm install -g mermaid-filter
sudo apt-get install -y make pandoc

# install scripts to initialize the development environment
cat <<EOM | sudo tee /etc/profile.d/init-dev-env.sh > /dev/null
if [ -f /project/code/config_sample.yaml ] && [ ! -f /project/code/config.yaml ]; then
  cp /project/code/config_sample.yaml /project/code/config.yaml &> /dev/null
fi
EOM

# clean up
sudo apt-get autoremove -y
sudo rm -rf /var/cache/apt
