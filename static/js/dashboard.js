document.addEventListener('DOMContentLoaded', () => {
    const logout = document.getElementById("logout")
    logout.addEventListener('click', () =>{
        fetch('/logout', {
            method: "POST"
        })   
        .then(response => {
            if(response.ok){
                window.location.href='/'
            }
        });
    });

    function reloadStatus() {
        const container = document.getElementById("reports-container");
        fetch('/reload/status')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                
                if (!container) {
                    return;
                }
                container.innerHTML = ''; 
                
                if (data.reports && data.reports.length > 0) {
                    data.reports.forEach(report => {
                        appendReport(report);
                    });
                } else {
                    container.innerHTML = ''; 
                    appendError("No reports available");
                }
            })
            .catch(error => {
                container.innerHTML = ''; 
                appendError("Error loading reports");
            })
            .finally(() => {
                setTimeout(reloadStatus, 5000); 
            });
    }

    function appendReport(reportText) {
        const container = document.getElementById("reports-container");
        const link = document.createElement("a");
        link.className = "report-link";
        link.href = `/report?text=${encodeURIComponent(reportText)}`;
        link.textContent = reportText;       
        container.appendChild(link);
        container.appendChild(document.createElement("br"));
    }

    function appendError(errorText) {
        const container = document.getElementById("reports-container");
        const error = document.createElement("div");
        error.textContent = errorText;       
        container.appendChild(error);
    }

    reloadStatus();
});

function submitReport() {
    const formData = new FormData(document.getElementById('reportForm'));
    const outputElement = document.getElementById('output');
    
    fetch('/add-report', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        if (error.message) {
            alert(error.message);
        } else {
            alert('An error occurred while submitting the report.');
        }
        if (outputElement) {
            outputElement.textContent = '';
        }
    });
}

