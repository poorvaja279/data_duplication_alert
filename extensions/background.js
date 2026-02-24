chrome.downloads.onDeterminingFilename.addListener(
  function (downloadItem, suggest) {

    let safeFilename = downloadItem.filename;

    if (!safeFilename || safeFilename.trim() === "") {
      safeFilename = downloadItem.url.split("/").pop() || "unknown_file";
    }

    // Always call suggest immediately to avoid blocking
    suggest({ filename: downloadItem.filename });
    
    // IMPORTANT: return true for async handling
    handleDuplicateCheck(downloadItem.id, safeFilename, downloadItem.url);

    return true;
  }
);


function handleDuplicateCheck(downloadId, filename, url) {

  fetch("http://127.0.0.1:5000/check", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      filename: filename,
      url: url
    })
  })
  .then(response => response.json())
  .then(data => {

    console.log("Backend response:", data);

    if (data.duplicate) {

      console.log("Duplicate detected. Pausing download.");

      chrome.downloads.pause(downloadId);

      chrome.storage.local.set({
        pendingDownloadId: downloadId,
        pendingFileName: filename
      });

      chrome.action.openPopup();
    }

  })
  .catch(error => {
    console.error("Error:", error);
  });
}