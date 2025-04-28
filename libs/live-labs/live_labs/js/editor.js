function main() {
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

  /* initialize the editor */
  function init() {

    /* Find the ace editor object and dom element */
    const { editor, editorDiv } = function () {
      // find the iframe with the ace editor
      const frames = window.parent.frames;
      for (let idx = 0; idx < frames.length; idx++) {
        let editorDiv = frames[idx].document.getElementById("ace-editor");
        if (editorDiv) {
          const editor = frames[idx].ace.edit("ace-editor");
          return {"editor": editor, "editorDiv": editorDiv}
        }
      }
      return {"editor": null, "editorDiv": null}
    }();

    /* If there is no editor, wait and try again. */
    if ( ! editor ) {
      setTimeout(init, 10);
      return
    }

    /* Helper function that will make the editor full height. */
    function updateEditorHeight() {
      if (!editorDiv) {
        return null;
      }
      const stApp = window.parent.document.querySelector('div[data-testid="stApp"]');
      const stMainBlock = window.parent.document.querySelector('div[data-testid="stMainBlockContainer"]');
      const appHeight      = stApp.clientHeight;
      const mainPaddingTop = parseInt(getComputedStyle(stMainBlock).paddingTop, 10) || 0;
      const editorHeight   = appHeight - mainPaddingTop;
      editorDiv.style.height = editorHeight - 150 +  "px";
    }

    // Resize the editor now and when the window is resized
    window.parent.addEventListener('resize', updateEditorHeight);
    updateEditorHeight();

    // Helper function to pop the first word off of a string, helpful for simulated streaming
    function wordPop(input) {
      if (input.startsWith('\n')) {
        return { word: '\n', newInput: input.slice(1), last: false };
      }

      const firstSpace = input.indexOf(' ');
      if (firstSpace === -1) {
        // no space found, entire input is the word
        return { word: input, newInput: '', last: true };
      }

      const word = input.slice(0, firstSpace) + " ";
      const newInput = input.slice(firstSpace + 1);
      const last = false;
      return { word, newInput, last };
    }

    // Helper function to simulate typing in the editor
    async function editorSendKeys(input) {
      if (!editor) return;

      const scrollbar = editor.container.getElementsByClassName("ace_scrollbar")[0];
      let newInput = input;

      while (newInput.length > 0) {
        let { word, newInput: updatedInput, last } = wordPop(newInput);

        if (last) {
          word += "\n";
        }

        editor.setValue(editor.getValue() + word);
        scrollbar.scrollTop = scrollbar.scrollHeight;
        editor.clearSelection();

        newInput = updatedInput;

        if (!last) {
          // sleep for 125 ms
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }
    }


    // Save the helper function to the global scope
    window.parent.editor = editor;
    window.parent.editorSendKeys = editorSendKeys;
  }

  /* Start trying to initialize in the background. */
  setTimeout(init, 1);
}( {} );



