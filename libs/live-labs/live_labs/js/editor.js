function setupUpdateEditorHeight() {
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

  /* Frontend code for ensuring the editor stays full height. */
  function updateEditorHeight() {
      const stApp = window.parent.document.querySelector('div[data-testid="stApp"]');
      const stMainBlock = window.parent.document.querySelector('div[data-testid="stMainBlockContainer"]');
      const appHeight      = stApp.clientHeight;
      const mainPaddingTop = parseInt(getComputedStyle(stMainBlock).paddingTop, 10) || 0;
      const editorHeight   = appHeight - mainPaddingTop;

      const frames = window.parent.frames;
      for (let idx = 0; idx < frames.length; idx++) {
        let editor = frames[idx].document.getElementById("ace-editor");
        if (editor) {
          editor.style.height = editorHeight - 150 +  "px";
        }
      }
  }

  window.addEventListener('resize', updateEditorHeight);
  setTimeout(updateEditorHeight, 500);
}({});
