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

/* Javascript code to handle the menu and page loading. */

async function fetchViews() {
  viewsReq = new Request("./views");
  views = await fetch(viewsReq);
  return await views.json();
}


async function fetchView() {
  views = await fetchViews();
  view_name = fetchAnchor(views[0].name);

  for (i=0; i < views.length; i++) {
    if (views[i].name == view_name) {
      return views[i];
    }
  }
}


function fetchAnchor(default_anchor) {
  anchor = window.top.location.hash.substring(1);
  if (anchor == "") {
    anchor = default_anchor;
  }
  return decodeURI(anchor);
}


async function activateView() {
  /* lookup the specified view data */
  view = await fetchView();
  leftPane = document.getElementById("left-pane");
  rightPane = document.getElementById("right-pane");

  /* update the menu */
  menuItems = document.getElementsByClassName("menu-item");
  for (i=0; i<menuItems.length; i++) {
    if (menuItems[i].innerText == view.name) {
      menuItems[i].classList.add("active");
    } else {
      menuItems[i].classList.remove("active");
    }
  }

  /* render the view */
  if (view.left != null) {
    leftPane.src = view.left + "?__theme=dark";
    leftPane.style.setProperty("display", "block");
  } else {
    leftPane.style.setProperty("display", "none");
  }
  if (view.right != null) {
    rightPane.src = view.right + "?__theme=dark";
    rightPane.style.setProperty("display", "block");
  } else {
    rightPane.style.setProperty("display", "none");
  }
}


async function populate() {
  views = await fetchViews();
  menuList = document.getElementById("menuBar");
  anchor = fetchAnchor(views[0].name)
  console.log("Loading page: " + anchor)

  for (i=0; i < views.length; i++) {
    // create link
    a = document.createElement("a");
    a.classList.add("menu-item");
    a.href = "#" + views[i].name;
    a.innerText = views[i].name;
    if (anchor == views[i].name) {
      a.classList.add("active")
    }

    // create list item
    li = document.createElement("li");
    li.appendChild(a);

    // add list item to dom
    menuList.appendChild(li);
  }

  await activateView();
}


document.addEventListener("DOMContentLoaded", populate);
window.addEventListener("hashchange", activateView);
