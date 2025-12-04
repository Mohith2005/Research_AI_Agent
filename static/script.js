class ResearchApp {
    constructor() {
        this.currentResearchId = null;
        this.pollInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('researchForm');
        form.addEventListener('submit', (e) => this.handleResearchSubmit(e));
        
        // Character count for topic input
        const topicInput = document.getElementById('topic');
        topicInput.addEventListener('input', (e) => this.updateCharCount(e));
        
        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleExampleClick(e));
        });
    }

    updateCharCount(e) {
        const count = e.target.value.length;
        const charCount = document.getElementById('charCount');
        charCount.textContent = count;
        
        if (count > 200) {
            charCount.style.color = '#dc3545';
        } else {
            charCount.style.color = '#666';
        }
    }

    handleExampleClick(e) {
        const topic = e.target.dataset.topic;
        document.getElementById('topic').value = topic;
        this.updateCharCount({ target: document.getElementById('topic') });
    }

    async handleResearchSubmit(e) {
        e.preventDefault();
        
        const topicInput = document.getElementById('topic');
        const topic = topicInput.value.trim();
        
        if (!topic) {
            this.showAlert('Please enter a research topic', 'error');
            return;
        }

        if (topic.length > 200) {
            this.showAlert('Topic must be 200 characters or less', 'error');
            return;
        }

        this.showLoadingState();
        
        try {
            const response = await fetch('/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.currentResearchId = data.result_id;
                this.startProgressPolling();
            } else {
                throw new Error(data.error || 'Failed to start research');
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    startProgressPolling() {
        // Clear any existing interval
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/research/${this.currentResearchId}`);
                const data = await response.json();
                
                this.updateProgress(data);
                
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(this.pollInterval);
                    if (data.status === 'completed') {
                        this.showResults(data);
                    } else {
                        this.showError(data.error || 'Research failed');
                    }
                }
            } catch (error) {
                console.error('Error polling research status:', error);
            }
        }, 2000);
    }

    updateProgress(data) {
        const progressMessage = document.getElementById('progressMessage');
        const progressFill = document.getElementById('progressFill');
        
        if (data.message) {
            progressMessage.textContent = data.message;
        }
        
        // Update progress bar based on status
        switch(data.status) {
            case 'initializing':
                progressFill.style.width = '10%';
                break;
            case 'searching':
                progressFill.style.width = '40%';
                break;
            case 'analyzing':
                progressFill.style.width = '75%';
                break;
            case 'completed':
                progressFill.style.width = '100%';
                break;
            case 'error':
                progressFill.style.background = '#dc3545';
                break;
        }
    }

    showLoadingState() {
        const researchBtn = document.getElementById('researchBtn');
        const researchProgress = document.getElementById('researchProgress');
        const spinner = researchBtn.querySelector('.loading-spinner');
        
        researchBtn.disabled = true;
        researchBtn.querySelector('span').textContent = 'Researching...';
        spinner.style.display = 'inline-block';
        researchProgress.style.display = 'block';
        
        // Reset progress bar
        document.getElementById('progressFill').style.width = '5%';
        document.getElementById('progressFill').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }

    showResults(data) {
        const researchBtn = document.getElementById('researchBtn');
        const spinner = researchBtn.querySelector('.loading-spinner');
        const researchResults = document.getElementById('researchResults');
        
        researchBtn.disabled = false;
        researchBtn.querySelector('span').textContent = 'Start New Research';
        spinner.style.display = 'none';
        
        document.getElementById('progressMessage').textContent = 'Research completed!';
        
        researchResults.style.display = 'block';
        researchResults.innerHTML = `
            <div class="presentation-result">
                <h3>Research Complete: ${this.escapeHtml(data.topic)}</h3>
                <div class="presentation-content">
                    ${data.html_content}
                </div>
                <a href="/download/${this.currentResearchId}" class="download-btn">
                    📥 Download Presentation
                </a>
            </div>
        `;
        
        // Scroll to results
        researchResults.scrollIntoView({ behavior: 'smooth' });
    }

    showError(message) {
        const researchBtn = document.getElementById('researchBtn');
        const spinner = researchBtn.querySelector('.loading-spinner');
        
        researchBtn.disabled = false;
        researchBtn.querySelector('span').textContent = 'Start Research';
        spinner.style.display = 'none';
        
        document.getElementById('progressMessage').textContent = 'Research failed';
        document.getElementById('progressFill').style.background = '#dc3545';
        
        this.showAlert(`Error: ${message}`, 'error');
    }

    showAlert(message, type = 'info') {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'error') {
            alert.style.background = '#dc3545';
        } else {
            alert.style.background = '#28a745';
        }

        alert.textContent = message;
        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Add CSS for alert animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ResearchApp();
});