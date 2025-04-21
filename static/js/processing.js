// Update the processing.html JavaScript to handle the API response
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progress-bar');
    const statusMessage = document.getElementById('status-message');
    const downloadSection = document.getElementById('download-section');
    const downloadLink = document.getElementById('download-link');

    // Get the filename from the URL
    const pathParts = window.location.pathname.split('/');
    const filename = pathParts[pathParts.length - 1];

    statusMessage.textContent = "Processing document, please wait...";
    progressBar.style.width = '97%'; // Or use Bootstrap's progress-bar-animated class if using Bootstrap
    progressBar.classList.add('progress-bar-striped', 'progress-bar-animated'); // Example for Bootstrap

    fetch(`/api/process/${filename}`)
        .then(response => {
            if (!response.ok) {
                // Handle HTTP errors like 404, 500
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
         })
        .then(data => {
            progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated'); // Stop animation

            if (data.status === 'success') {
                statusMessage.textContent = `Processing complete! Made ${data.revision_count} changes.`;
                downloadLink.href = data.download_url;
                downloadSection.classList.remove('hidden');
                progressBar.style.width = '100%'; // Show completion
                progressBar.classList.add('bg-success'); // Optional: make bar green
            } else {
                // Handle errors reported in the JSON payload
                statusMessage.textContent = `Error: ${data.message || 'Unknown error occurred.'}`;
                progressBar.style.width = '100%'; // Show bar filled on error too
                progressBar.classList.add('bg-danger'); // Make bar red on error
            }
        })
        .catch(error => {
            progressBar.classList.remove('progress-bar-striped', 'progress-bar-animated'); // Stop animation
            // Handle network errors or errors thrown from .then()
            console.error("API call failed:", error); // Log the actual error
            statusMessage.textContent = `Error: ${error.message || 'Could not connect to server.'}`;
            progressBar.style.width = '100%'; // Show bar filled on error too
            progressBar.classList.add('bg-danger'); // Make bar red on error
        });
});
