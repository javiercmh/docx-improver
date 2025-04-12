// Update the processing.html JavaScript to handle the API response
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.getElementById('progress-bar');
    const statusMessage = document.getElementById('status-message');
    const downloadSection = document.getElementById('download-section');
    const downloadLink = document.getElementById('download-link');
    
    // Get the filename from the URL
    const pathParts = window.location.pathname.split('/');
    const filename = pathParts[pathParts.length - 1];
    
    let progress = 0;
    const interval = setInterval(function() {
        progress += 5;
        progressBar.style.width = progress + '%';
        
        if (progress === 30) {
            statusMessage.textContent = "Improving text with Gemini AI...";
        } else if (progress === 60) {
            statusMessage.textContent = "Applying track changes...";
        } else if (progress === 90) {
            statusMessage.textContent = "Finalizing document...";
        } else if (progress >= 100) {
            clearInterval(interval);
            
            // Call the API to process the file
            fetch(`/api/process/${filename}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        statusMessage.textContent = `Processing complete! Made ${data.improved_count} changes in ${data.paragraphs_count} paragraphs.`;
                        downloadLink.href = data.download_url;
                        downloadSection.classList.remove('hidden');
                    } else {
                        statusMessage.textContent = `Error: ${data.message}`;
                    }
                })
                .catch(error => {
                    statusMessage.textContent = `Error: ${error.message}`;
                });
        }
    }, 500);
});
