#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

source  $(dirname $0)/functions

# NIM options
SVC_NAME="llm-nim-0"

# NIM constants
SLUG=$(echo ${SVC_NAME^^} | tr - _)
NAME="${SVC_NAME}"

# workspace configuration options
MODEL=$(config_lkp "${SLUG}_MODEL" "meta/llama3-8b-instruct")
TAG=$(config_lkp "${SLUG}_NIM_VERSION" "1.0.0")
GPUS=$(config_lkp "${SLUG}_NIM_GPUS" "all")
IMAGE="nvcr.io/nim/meta/llama3-8b-instruct"

# This function is responsible for running creating a running the container
# and its dependencies.
_docker_run() {
    docker run \
        --name=$NAME \
        --runtime=nvidia \
        --gpus "$GPUS" \
        --ipc host \
        -e NGC_API_KEY \
        -v $(hostpath $NGC_HOME):/opt/nim/.cache \
        -u $(id -u) \
        --health-cmd="python -c \"import requests; resp = requests.get('http://localhost:8000/v1/health/ready'); resp.raise_for_status()\"" \
        --health-interval=30s \
        --health-start-period=600s \
        --health-timeout=20s \
        --health-retries=3 \
        $DOCKER_NETWORK $IMAGE:$TAG
}

# stop and remove the running container
_docker_stop() {
	docker stop -t "$STOP_TIMEOUT" "$NAME" > /dev/null
	docker rm -f "$NAME" > /dev/null
}

# print the project's metadata
_meta() {
	cat <<-EOM
		name: "LLM NIM: $SVC_NAME"
		type: custom
		class: process
		icon_url: www.nvidia.com/favicon.ico
		EOM
}


main "$1" "$NAME"
