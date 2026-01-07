// QA-Pilot Agent - Dashboard JavaScript

// Example test templates
const examples = {
    login: `Navigate to http://localhost:5000/test_site
Fill the email field with "test@example.com"
Fill the password field with "password123"
Click the "Login" button
Verify that the page contains "Login successful"`,
    
    amazon: `Navigate to www.amazon.com
Search for "noise headphones"
Wait 3 seconds
Check that the page contains "results"`,
    
    google: `Navigate to www.google.com
Type "karnataka famous festivals" in search box
Press Enter
Wait 2 seconds
Verify that the page contains "Dasara"`,
    
    youtube: `Navigate to www.youtube.com
Search for "AI tutorial"
Wait 2 seconds
Check that the page contains "video"`
};

// Load example
function loadExample(type) {
    const instruction = examples[type];
    if (instruction) {
        document.getElementById('test-instruction').value = instruction;
        
        // Extract URL from instruction and set it
        const lines = instruction.split('\n');
        const firstLine = lines[0].toLowerCase();
        if (firstLine.includes('navigate') || firstLine.includes('go to') || firstLine.includes('open')) {
            const urlMatch = instruction.match(/(?:navigate to|go to|open)\s+([^\n]+)/i);
            if (urlMatch) {
                document.getElementById('target-url').value = urlMatch[1].trim();
            }
        }
        
        // Smooth scroll to form
        document.getElementById('test-instruction').focus();
    }
}

// Clear form
function clearForm() {
    document.getElementById('target-url').value = '';
    document.getElementById('test-instruction').value = '';
    document.querySelector('input[name="browser-mode"][value="headless"]').checked = true;
}

// Show test form
function showTestForm() {
    document.getElementById('test-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
}

// Show reports (placeholder)
function showReports() {
    alert('Test reports feature coming soon!');
}

// Update loading steps
function updateLoadingSteps(steps) {
    const stepsContainer = document.getElementById('loading-steps');
    stepsContainer.innerHTML = '';
    
    steps.forEach((step, index) => {
        const stepEl = document.createElement('div');
        stepEl.className = 'loading-step';
        stepEl.style.animationDelay = `${index * 0.1}s`;
        stepEl.innerHTML = `
            <div class="step-icon">${step.icon}</div>
            <div class="step-text">${step.text}</div>
        `;
        stepsContainer.appendChild(stepEl);
    });
}

// Display results
function displayResults(data) {
    const summaryContainer = document.getElementById('results-summary');
    const detailsContainer = document.getElementById('results-details');
    
    // Calculate success rate
    const successRate = data.success_rate || 0;
    const totalSteps = data.total_steps || 0;
    const passed = data.passed || 0;
    const failed = data.failed || 0;
    
    // Create summary cards
    summaryContainer.innerHTML = `
        <div class="summary-card">
            <div class="summary-label">Total Steps</div>
            <div class="summary-value">${totalSteps}</div>
        </div>
        <div class="summary-card success">
            <div class="summary-label">Passed</div>
            <div class="summary-value">${passed}</div>
        </div>
        <div class="summary-card error">
            <div class="summary-label">Failed</div>
            <div class="summary-value">${failed}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label">Success Rate</div>
            <div class="summary-value">${successRate.toFixed(1)}%</div>
        </div>
    `;
    
    // Create detailed results
    let detailsHTML = '<h3 style="margin-bottom: 20px; font-size: 1.2rem;">Test Execution Details</h3>';
    
    // Passed tests
    if (data.passed_tests && data.passed_tests.length > 0) {
        data.passed_tests.forEach(test => {
            detailsHTML += `
                <div class="result-item passed">
                    <div class="result-icon">✓</div>
                    <div class="result-content">
                        <div class="result-step">Step ${test.step}</div>
                        <div class="result-description">${test.description || test.action}</div>
                        ${test.expected ? `<div class="result-error" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">Expected: ${test.expected}</div>` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    // Failed tests
    if (data.failed_tests && data.failed_tests.length > 0) {
        data.failed_tests.forEach(test => {
            detailsHTML += `
                <div class="result-item failed">
                    <div class="result-icon">✗</div>
                    <div class="result-content">
                        <div class="result-step">Step ${test.step}</div>
                        <div class="result-description">${test.description || test.action}</div>
                        ${test.error ? `<div class="result-error">Error: ${test.error}</div>` : ''}
                        ${test.expected ? `<div class="result-error">Expected: ${test.expected}</div>` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    // Generated code (collapsed by default)
    if (data.generated_code) {
        detailsHTML += `
            <div class="code-display collapsed" id="code-display">
                <div class="code-header" style="cursor: pointer;" onclick="toggleCode()">
                    <div class="code-title">
                        <svg class="btn-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" style="transition: transform 0.3s;" id="code-arrow">
                            <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        View Generated Playwright Code
                    </div>
                    <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); copyCode();">
                        <svg class="btn-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M13 5.5V13.5C13 14.0523 12.5523 14.5 12 14.5H4C3.44772 14.5 3 14.0523 3 13.5V2.5C3 1.94772 3.44772 1.5 4 1.5H9.5M13 5.5L9.5 1.5M13 5.5H10C9.72386 5.5 9.5 5.27614 9.5 5V1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Copy
                    </button>
                </div>
                <div class="code-content" id="generated-code"><pre>${escapeHtml(data.generated_code)}</pre></div>
            </div>
        `;
    }
    
    detailsContainer.innerHTML = detailsHTML;
    
    // Update stats
    updateTestCount();
}

// Copy generated code
function copyCode() {
    const codeContent = document.getElementById('generated-code').innerText;
    navigator.clipboard.writeText(codeContent).then(() => {
        alert('Code copied to clipboard!');
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update test count
function updateTestCount() {
    const today = localStorage.getItem('tests_today') || 0;
    const newCount = parseInt(today) + 1;
    localStorage.setItem('tests_today', newCount);
    document.getElementById('tests-today').textContent = newCount;
}

// Initialize test count
function initTestCount() {
    const today = new Date().toDateString();
    const lastDate = localStorage.getItem('test_date');
    
    if (lastDate !== today) {
        localStorage.setItem('tests_today', '0');
        localStorage.setItem('test_date', today);
    }
    
    const count = localStorage.getItem('tests_today') || 0;
    document.getElementById('tests-today').textContent = count;
}

// Handle form submission
document.getElementById('test-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const targetUrl = document.getElementById('target-url').value;
    const instruction = document.getElementById('test-instruction').value;
    const browserType = document.getElementById('browser-type') ? document.getElementById('browser-type').value : 'chromium';
    const executionModeSelect = document.getElementById('execution-mode-select');
    const headless = executionModeSelect ? (executionModeSelect.value === 'headless') : true;
    
    if (!instruction.trim()) {
        alert('Please enter test instructions');
        return;
    }
    
    // Show loading state
    document.getElementById('test-section').style.display = 'none';
    document.getElementById('loading-state').style.display = 'flex';
    
    // Update loading steps
    const browserText = headless ? 'headless browser' : 'visible browser (watch it work!)';
    updateLoadingSteps([
        { icon: '🔍', text: 'Parsing your natural language instructions...' },
        { icon: '💻', text: 'Generating Playwright test code...' },
        { icon: '✅', text: 'Validating generated code...' },
        { icon: '🚀', text: 'Executing test in ' + browserText + '...' },
        { icon: '📊', text: 'Generating test report...' }
    ]);
    
    if (!headless) {
        alert('Visible Browser Mode!\n\nA browser window will open showing the test execution.\nThe browser will stay open after completion.\nPress Enter in the console to close it when done.');
    }
    
    // Disable button
    const btn = document.getElementById('run-test-btn');
    btn.disabled = true;
    btn.innerHTML = '<svg class="btn-icon" width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="2"/></svg> Running...';
    
    try {
        // Make API request
        const response = await fetch('/api/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: targetUrl,
                instruction: instruction,
                browser: browserType,
                headless: headless
            })
        });
        
        const result = await response.json();
        
        // Hide loading
        document.getElementById('loading-state').style.display = 'none';
        
        if (result.success) {
            // Show results
            document.getElementById('results-section').style.display = 'block';
            displayResults(result.data);
        } else {
            // Show error
            alert('Test execution failed: ' + result.error);
            document.getElementById('test-section').style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('test-section').style.display = 'block';
        alert('An error occurred: ' + error.message);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = '<svg class="btn-icon" width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M6 3L14 9L6 15V3Z" fill="currentColor"/></svg> Run Test';
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTestCount();
});

// Toggle code display
function toggleCode() {
    const codeDisplay = document.getElementById('code-display');
    const arrow = document.getElementById('code-arrow');
    
    if (codeDisplay.classList.contains('collapsed')) {
        codeDisplay.classList.remove('collapsed');
        arrow.style.transform = 'rotate(90deg)';
    } else {
        codeDisplay.classList.add('collapsed');
        arrow.style.transform = 'rotate(0deg)';
    }
}

// Make functions globally available
window.loadExample = loadExample;
window.clearForm = clearForm;
window.showTestForm = showTestForm;
window.showReports = showReports;
window.copyCode = copyCode;
window.toggleCode = toggleCode;
