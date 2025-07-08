document.addEventListener('DOMContentLoaded', function() {
    // Get UI elements
    const checkButton = document.getElementById('checkPage');
    const sessionButton = document.getElementById('sessionButton');
    const viewResultsButton = document.getElementById('viewResults');
    const status = document.getElementById('status');
    const sessionStatus = document.getElementById('session-status');
    const resultStatus = document.getElementById('result-status');
    
    // Tab handling
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const contentId = 'content-' + this.id.split('-')[1];
            document.getElementById(contentId).classList.add('active');
            
            // Refresh data when switching tabs
            updateUI();
        });
    });
    
    // Check if a session is active when popup opens
    checkSessionStatus();
    
    // Set interval to update session duration
    const updateInterval = setInterval(updateSessionDuration, 1000);
    
    // Update UI with current data from storage
    updateUI();
    
    // Handle session monitoring button click
    sessionButton.addEventListener('click', function() {
        if (sessionButton.textContent === 'Start Monitoring Session') {
            // Start a new session
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {action: "start_session"}, function(response) {
                    if (response) {
                        sessionStatus.textContent = 'Session active: Monitoring behavior...';
                        sessionStatus.className = 'status warning';
                        sessionButton.textContent = 'Stop Monitoring Session';
                        sessionButton.classList.add('stop');
                        updateUI();
                    }
                });
            });
        } else {
            // Stop the current session
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {action: "stop_session"}, function(response) {
                    if (response) {
                        sessionStatus.textContent = 'Session ended: Analyzing data...';
                        sessionButton.textContent = 'Start Monitoring Session';
                        sessionButton.classList.remove('stop');
                        updateUI();
                    }
                });
            });
        }
    });
    
    // Handle check metrics button click
    checkButton.addEventListener('click', function() {
        status.textContent = 'Analyzing page behavior...';
        status.className = 'status';
        
        // Send message to content script to analyze current page
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: "analyze"}, function(response) {
                if (response && response.metrics) {
                    updateMetricsDisplay(response.metrics);
                    if (response.prediction) {
                        updatePredictionDisplay(response.prediction);
                    }
                    if (response.isSessionActive) {
                        // Update session info if a session is active
                        document.getElementById('dataPoints').textContent = response.sessionData.dataPoints;
                        document.getElementById('sessionDuration').textContent = formatTime(response.sessionData.duration);
                    }
                }
            });
        });
    });
    
    // Handle view results button click
    viewResultsButton.addEventListener('click', function() {
        // Get latest prediction from storage and display
        chrome.storage.local.get(['prediction', 'sessionSummary'], function(result) {
            if (result.prediction) {
                updateResultsDisplay(result.prediction, result.sessionSummary);
            } else {
                resultStatus.textContent = 'No results available yet';
                resultStatus.className = 'status';
            }
        });
    });
    
    // Listen for messages from background script or content script
    chrome.runtime.onMessage.addListener(function(message) {
        if (message.type === 'session_update') {
            if (message.status === 'ended') {
                sessionStatus.textContent = message.completed ? 
                    'Session completed successfully!' : 
                    'Session ended';
                sessionStatus.className = 'status safe';
                sessionButton.textContent = 'Start Monitoring Session';
                sessionButton.classList.remove('stop');
                
                // Switch to results tab if prediction is available
                if (message.prediction) {
                    document.getElementById('tab-results').click();
                    updateResultsDisplay(message.prediction);
                }
            }
        } else if (message.type === 'checkpoint_update') {
            updateCheckpoint(message.action);
        }
        updateUI();
    });
    
    // Clean up interval when popup closes
    window.addEventListener('unload', function() {
        clearInterval(updateInterval);
    });
});

// Check if a session is active
function checkSessionStatus() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "get_session_status"}, function(response) {
            if (response && response.isActive) {
                // Update UI for active session
                document.getElementById('session-status').textContent = 'Session active: Monitoring behavior...';
                document.getElementById('session-status').className = 'status warning';
                document.getElementById('sessionButton').textContent = 'Stop Monitoring Session';
                document.getElementById('sessionButton').classList.add('stop');
                
                // Update metrics
                document.getElementById('dataPoints').textContent = response.dataPoints || 0;
                updateMetricsDisplay(response.currentMetrics);
            }
        });
    });
}

// Update the UI with current data
function updateUI() {
    chrome.storage.local.get(['metrics', 'prediction', 'sessionData', 'sessionStartTime'], function(result) {
        if (result.metrics) {
            updateMetricsDisplay(result.metrics);
        }
        if (result.prediction) {
            updateResultsDisplay(result.prediction);
        }
        if (result.sessionData) {
            document.getElementById('dataPoints').textContent = result.sessionData.length;
        }
    });
}

// Update checkpoint display
function updateCheckpoint(action) {
    const checkpoints = {
        'add_to_cart': 'checkpoint-cart',
        'checkout': 'checkpoint-checkout',
        'purchase_complete': 'checkpoint-purchase'
    };
    
    if (checkpoints[action]) {
        const checkpoint = document.getElementById(checkpoints[action]);
        checkpoint.classList.add('completed');
        
        // Mark all previous checkpoints as completed
        if (action === 'checkout') {
            document.getElementById('checkpoint-cart').classList.add('completed');
        } else if (action === 'purchase_complete') {
            document.getElementById('checkpoint-cart').classList.add('completed');
            document.getElementById('checkpoint-checkout').classList.add('completed');
        }
    }
}

// Update session duration display
function updateSessionDuration() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "get_session_status"}, function(response) {
            if (response && response.isActive) {
                document.getElementById('sessionDuration').textContent = 
                    formatTime(response.currentMetrics.time_spent_on_page_sec);
            }
        });
    });
}

// Format time in seconds to MM:SS format
function formatTime(seconds) {
    if (!seconds) return '0s';
    
    if (seconds < 60) {
        return Math.floor(seconds) + 's';
    } else {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return minutes + 'm ' + secs + 's';
    }
}

// Update metrics display
function updateMetricsDisplay(metrics) {
    document.getElementById('mouseMovement').textContent = metrics.mouseMovement.toFixed(2);
    document.getElementById('typingSpeed').textContent = metrics.typingSpeed.toFixed(0) + ' CPM';
    document.getElementById('clickPattern').textContent = metrics.clickPattern.toFixed(2);
    document.getElementById('timeOnPage').textContent = metrics.timeOnPage.toFixed(0) + 's';
    
    // Update new metric displays
    const scrollMap = {0: 'None', 1: 'Minimal', 2: 'Normal', 3: 'Rapid'};
    document.getElementById('scrollBehavior').textContent = 
        metrics.scrollBehavior_encoded ? scrollMap[metrics.scrollBehavior_encoded] : metrics.scrollBehavior;
    document.getElementById('formFillTime').textContent = 
        (metrics.formFillTime || metrics.form_fill_time_sec || 0).toFixed(1) + 's';
}

// Update prediction display for individual page check
function updatePredictionDisplay(prediction) {
    const status = document.getElementById('status');
    
    if (prediction.is_bot) {
        status.className = 'status alert';
        status.innerHTML = `
            ⚠️ Bot Activity Detected (${(prediction.probability * 100).toFixed(1)}%)
            <br><small>${prediction.risk_factors ? prediction.risk_factors.join('<br>') : ''}</small>
        `;
    } else {
        status.className = 'status safe';
        status.innerHTML = `
            ✅ Human Activity (${((1 - prediction.probability) * 100).toFixed(1)}% confidence)
        `;
    }

    // Update bot probability in results tab
    document.getElementById('botProbability').textContent = 
        (prediction.probability * 100).toFixed(1) + '%';
}

// Update results display for session analysis
function updateResultsDisplay(prediction, sessionSummary) {
    const resultStatus = document.getElementById('result-status');
    
    if (prediction.is_bot) {
        resultStatus.className = 'status alert';
        resultStatus.innerHTML = `
            ⚠️ Bot Session Detected (${(prediction.probability * 100).toFixed(1)}%)
            <br><small>${prediction.risk_factors ? prediction.risk_factors.join('<br>') : ''}</small>
        `;
    } else {
        resultStatus.className = 'status safe';
        resultStatus.innerHTML = `
            ✅ Human Session (${((1 - prediction.probability) * 100).toFixed(1)}% confidence)
        `;
    }
    
    // Update bot probability
    document.getElementById('botProbability').textContent = 
        (prediction.probability * 100).toFixed(1) + '%';
    
    // Add confidence metrics visualization if available
    if (prediction.confidence_metrics) {
        const confidenceMetrics = document.getElementById('confidence-metrics');
        const confidenceHtml = Object.entries(prediction.confidence_metrics)
            .map(([key, value]) => `
                <div class="metric-item">
                    <span>${key.replace(/_/g, ' ')}:</span>
                    <span>${(value * 100).toFixed(0)}%</span>
                </div>
            `).join('');
        
        // Update confidence metrics section
        confidenceMetrics.innerHTML = `
            <h4>Confidence Metrics</h4>
            ${confidenceHtml}
            <div class="metric-item">
                <span>Bot Probability:</span>
                <span id="botProbability">${(prediction.probability * 100).toFixed(1)}%</span>
            </div>
        `;
    }
    
    // Add session summary if available
    if (sessionSummary) {
        const metrics = document.getElementById('confidence-metrics');
        const sessionHtml = `
            <h4>Session Summary</h4>
            <div class="metric-item">
                <span>Mouse Movement:</span>
                <span>${sessionSummary.mouse_movement_units.toFixed(2)}</span>
            </div>
            <div class="metric-item">
                <span>Typing Speed:</span>
                <span>${sessionSummary.typing_speed_cpm.toFixed(0)} CPM</span>
            </div>
            <div class="metric-item">
                <span>Click Pattern:</span>
                <span>${sessionSummary.click_pattern_score.toFixed(2)}</span>
            </div>
            <div class="metric-item">
                <span>Time Spent:</span>
                <span>${formatTime(sessionSummary.time_spent_on_page_sec)}</span>
            </div>
        `;
        
        metrics.insertAdjacentHTML('beforeend', sessionHtml);
    }
} 