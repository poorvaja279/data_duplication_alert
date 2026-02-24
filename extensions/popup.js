document.addEventListener("DOMContentLoaded", function () {

  chrome.storage.local.get(
    ["pendingDownloadId", "pendingFileName"],
    function (data) {

      if (data.pendingFileName) {
        document.getElementById("fileName").textContent =
          "File: " + data.pendingFileName;
      }

      document.getElementById("downloadBtn").addEventListener("click", function () {

        if (data.pendingDownloadId) {
          chrome.downloads.resume(data.pendingDownloadId);
          chrome.storage.local.remove(["pendingDownloadId", "pendingFileName"]);
          window.close();
        }

      });

      document.getElementById("cancelBtn").addEventListener("click", function () {

        if (data.pendingDownloadId) {
          chrome.downloads.cancel(data.pendingDownloadId);
          chrome.storage.local.remove(["pendingDownloadId", "pendingFileName"]);
          window.close();
        }

      });

    }
  );

});