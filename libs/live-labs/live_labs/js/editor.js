function() {
  function reportEditorHeight() {
      const stApp = window.parent.document.querySelector('div[data-testid="stApp"]');
      const stMainBlock = window.parent.document.querySelector('div[data-testid="stMainBlockContainer"]');
      const appHeight      = stApp.clientHeight;
      const mainPaddingTop = parseInt(getComputedStyle(stMainBlock).paddingTop, 10) || 0;
      const editorHeight   = appHeight - mainPaddingTop;

      window.top.stBridges.send('editor-height', editorHeight - 150);
  }

  window.addEventListener('resize', reportEditorHeight);
  setTimeout(reportEditorHeight, 500);
}();
