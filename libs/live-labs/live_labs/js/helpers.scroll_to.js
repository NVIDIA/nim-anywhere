await async function main() {
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

  // helper  function  to find the previous streamlit  element
  function findPreviousStElementContainer(elementId) {
    const element = window.parent.document.getElementById(elementId);
    if (!element) {
      console.error(`Element with ID '${elementId}' not found.`);
      return null;
    }

    // Find nearest container upward
    let container = element.closest('div[data-testid="stElementContainer"]');
    if (!container) {
      console.error(`No parent with data-testid="stElementContainer" found for ID '${elementId}'.`);
      return null;
    }

    // Find all containers in parent document order
    const containers = Array.from(window.parent.document.querySelectorAll('div[data-testid="stElementContainer"]'));
    const index = containers.indexOf(container);

    if (index > 0) {
      return containers[index - 1];
    } else {
      console.warn(`No previous stElementContainer found before ID '${elementId}'.`);
      return null;
    }
  }

  // helper function to find the alert container in a streamlit element
  function findAlertInContainer(container) {
    if (!container) {
      console.error("Container not provided.");
      return null;
    }

    // Search inside the container for the first stAlert div
    const alertDiv = container.querySelector('div[data-testid="stAlert"]');

    if (!alertDiv) {
      console.warn("No stAlert found inside the given container.");
      return null;
    }

    return alertDiv;
  }

  const element = window.parent.document.getElementById(ARG)
  const prevElement = findPreviousStElementContainer(ARG);
  const alert = findAlertInContainer(prevElement);
  const target = alert ?? element;


  target.scrollIntoView({behavior: "smooth"});

}({});
