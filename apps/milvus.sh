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

NAME="milvus"
IMAGE="milvusdb/milvus"
TAG=$(config_lkp "MILVUS_VERSION" "v2.4.0")

# This function is responsible for running creating a running the container
# and its dependencies.
_docker_run() {
	docker volume create $NAME > /dev/null
	docker run \
		--name $NAME \
		--security-opt seccomp:unconfined \
		-e ETCD_USE_EMBED=true \
		-e ETCD_DATA_DIR=/var/lib/milvus/etcd \
		-e COMMON_STORAGETYPE=local \
		--mount src=$NAME,target=/var/lib/milvus \
		--health-cmd="curl -f http://localhost:9091/healthz" \
		--health-interval=30s \
		--health-start-period=90s \
		--health-timeout=20s \
		--health-retries=3 \
        $DOCKER_NETWORK $IMAGE:$TAG \
		milvus run standalone > /dev/null
}

# stop and remove the running container
_docker_stop() {
	docker stop -t "$STOP_TIMEOUT" "$NAME" > /dev/null
	docker rm -f "$NAME" > /dev/null
}

# print the project's metadata
_meta() {
	cat <<-EOM
		name: Milvus Vector DB
		type: custom
		class: process
		icon_url: milvus.io/favicon-32x32.png
		EOM
}


main "$1" "$NAME"
