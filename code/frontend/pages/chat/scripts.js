// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

function chatResize(event) {
  chat = document.getElementById("chat");
  input_row = document.getElementById("input-row");
  // iframe height - total gradio container padding - input height
  newHeight = window.innerHeight - 40 - input_row.offsetHeight + "px";
  chat.style.height = newHeight;
};

function registerHandlers() {
  window.addEventListener("resize", chatResize);
  document.querySelector("#msg").querySelector("textarea").addEventListener("keyup", chatResize);
  document.querySelector("#msg").querySelector("textarea").addEventListener("changed", chatResize);
}

window.addEventListener(
  "message",
  (event) => {
      if (event.isTrusted) {
          if ("use_kb" in event.data) {
              use_kb = gradio_config.components.find((element) => element.props.elem_id == "use_kb");
              use_kb.props.value = event.data["use_kb"];
          }
          if ("use_reranker" in event.data){
              use_reranker = gradio_config.components.find((element) => element.props.elem_id == "use_reranker");
              use_reranker.props.value = event.data["use_reranker"];
          }
      };
  },
  false);