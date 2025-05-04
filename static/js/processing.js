// Update the processing.html JavaScript to handle the API response
document.addEventListener('DOMContentLoaded', function() {
    const statusMessage = document.getElementById('status-message');
    const downloadSection = document.getElementById('download-section');
    const downloadLink = document.getElementById('download-link');

    statusMessage.textContent = "Processing document, please wait...";

    // Use the global FILENAME variable injected from the HTML template
    fetch(`/api/process/${FILENAME}`)
        .then(response => {
            if (!response.ok) {
                // Handle HTTP errors like 404, 500
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
         })
        .then(data => {

            if (data.status === 'success') {
                statusMessage.textContent = `Processing complete! Made ${data.revision_count} changes.`;
                downloadLink.href = data.download_url._url;
                downloadSection.classList.remove('hidden');
            } else {
                statusMessage.textContent = `Error: ${data.message || 'Unknown error occurred.'}`;
            }
        })
        .catch(error => {
            console.error("API call failed:", error); // Log the actual error
            statusMessage.textContent = `Error: ${error.message || 'Could not connect to server.'}`;
        });
});
