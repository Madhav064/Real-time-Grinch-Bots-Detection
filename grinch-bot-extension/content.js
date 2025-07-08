// Initialize metrics
let metrics = {
    mouseMovement: 0,
    typingSpeed: 0,
    clickPattern: 0,
    timeOnPage: 0,
    scrollBehavior: 'none',
    captchaSuccess: 1,
    formFillTime: 0
};

// Session tracking variables
let isSessionActive = false;
let sessionStartTime = null;
let sessionData = [];
let currentSessionPoint = {};

let lastMouseX = 0;
let lastMouseY = 0;
let typingStartTime = null;
let typedCharacters = 0;
let clickTimes = [];
let formStartTime = null;
const pageLoadTime = Date.now();

// Track mouse movement
document.addEventListener('mousemove', function(e) {
    if (!isSessionActive) return;
    
    const deltaX = Math.abs(e.clientX - lastMouseX);
    const deltaY = Math.abs(e.clientY - lastMouseY);
    metrics.mouseMovement += Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    currentSessionPoint.mouse_movement_units = metrics.mouseMovement;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
});

// Track typing speed
document.addEventListener('keypress', function(e) {
    if (!isSessionActive) return;
    
    if (!typingStartTime) {
        typingStartTime = Date.now();
    }
    typedCharacters++;
    
    const timeElapsed = (Date.now() - typingStartTime) / 1000 / 60; // Convert to minutes
    metrics.typingSpeed = timeElapsed > 0 ? typedCharacters / timeElapsed : 0;
    currentSessionPoint.typing_speed_cpm = metrics.typingSpeed;
});

// Track click patterns
document.addEventListener('click', function(e) {
    if (!isSessionActive) return;
    
    const clickTime = Date.now();
    clickTimes.push(clickTime);
    
    // Detect cart additions or checkout actions
    const target = e.target;
    if (target.textContent && (
        target.textContent.toLowerCase().includes('add to cart') || 
        target.textContent.toLowerCase().includes('buy now') ||
        target.closest('button') && target.closest('button').textContent && 
        (target.closest('button').textContent.toLowerCase().includes('add to cart') || 
         target.closest('button').textContent.toLowerCase().includes('buy now'))
    )) {
        recordCheckpoint('add_to_cart');
    } else if (target.textContent && (
        target.textContent.toLowerCase().includes('checkout') || 
        target.textContent.toLowerCase().includes('place order') ||
        target.closest('button') && target.closest('button').textContent && 
        (target.closest('button').textContent.toLowerCase().includes('checkout') || 
         target.closest('button').textContent.toLowerCase().includes('place order'))
    )) {
        recordCheckpoint('checkout');
    } else if (target.textContent && (
        target.textContent.toLowerCase().includes('complete purchase') || 
        target.textContent.toLowerCase().includes('confirm order') ||
        target.closest('button') && target.closest('button').textContent && 
        (target.closest('button').textContent.toLowerCase().includes('complete purchase') || 
         target.closest('button').textContent.toLowerCase().includes('confirm order'))
    )) {
        recordCheckpoint('purchase_complete');
        if (isSessionActive) {
            stopSession(true);
        }
    }
    
    // Keep only last 5 clicks for pattern analysis
    if (clickTimes.length > 5) {
        clickTimes.shift();
    }
    
    // Analyze click pattern regularity
    if (clickTimes.length >= 2) {
        const intervals = [];
        for (let i = 1; i < clickTimes.length; i++) {
            intervals.push(clickTimes[i] - clickTimes[i-1]);
        }
        
        // Calculate variance in click intervals
        const mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
        const variance = intervals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / intervals.length;
        
        // Normalize to 0-1 range (higher means more random/human-like)
        metrics.clickPattern = Math.min(1, 1 / (1 + Math.sqrt(variance) / 1000));
        currentSessionPoint.click_pattern_score = metrics.clickPattern;
    }
});

// Track form interactions
document.addEventListener('focusin', function(e) {
    if (!isSessionActive) return;
    
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (!formStartTime) {
            formStartTime = Date.now();
        }
    }
});

document.addEventListener('focusout', function(e) {
    if (!isSessionActive) return;
    
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (formStartTime) {
            metrics.formFillTime = (Date.now() - formStartTime) / 1000;
            currentSessionPoint.form_fill_time_sec = metrics.formFillTime;
            formStartTime = null;
        }
    }
});

// Track scroll behavior
let lastScrollTime = Date.now();
let scrollCount = 0;
let scrollBehaviorCode = 0; // 0: none, 1: minimal, 2: normal, 3: rapid

document.addEventListener('scroll', function() {
    if (!isSessionActive) return;
    
    scrollCount++;
    const now = Date.now();
    const timeSinceLastScroll = now - lastScrollTime;
    
    // Update scroll behavior classification
    if (scrollCount > 50 && timeSinceLastScroll < 50) {
        metrics.scrollBehavior = 'rapid';
        scrollBehaviorCode = 3;
    } else if (scrollCount > 20) {
        metrics.scrollBehavior = 'normal';
        scrollBehaviorCode = 2;
    } else if (scrollCount > 0) {
        metrics.scrollBehavior = 'minimal';
        scrollBehaviorCode = 1;
    }
    
    currentSessionPoint.scroll_behavior_encoded = scrollBehaviorCode;
    lastScrollTime = now;
});

// Update time on page
setInterval(function() {
    if (!isSessionActive) return;
    
    metrics.timeOnPage = (Date.now() - pageLoadTime) / 1000;
    currentSessionPoint.time_spent_on_page_sec = metrics.timeOnPage;
    
    // Add the latest data point every 5 seconds
    if (metrics.timeOnPage % 5 === 0) {
        recordDataPoint();
    }
}, 1000);

// Record a checkpoint in the session
function recordCheckpoint(action) {
    if (!isSessionActive) return;
    
    recordDataPoint();
    sessionData[sessionData.length - 1].action = action;
    sessionData[sessionData.length - 1].timestamp = Date.now();
    
    // Notify about checkpoint
    chrome.runtime.sendMessage({
        type: "checkpoint_update",
        action: action
    });
}

// Record current metrics as a data point
function recordDataPoint() {
    if (!isSessionActive) return;
    
    // Create a copy of current session point
    const dataPoint = {
        mouse_movement_units: currentSessionPoint.mouse_movement_units || 0,
        typing_speed_cpm: currentSessionPoint.typing_speed_cpm || 0,
        click_pattern_score: currentSessionPoint.click_pattern_score || 0,
        time_spent_on_page_sec: currentSessionPoint.time_spent_on_page_sec || 0,
        scroll_behavior_encoded: currentSessionPoint.scroll_behavior_encoded || 0,
        captcha_success: metrics.captchaSuccess,
        form_fill_time_sec: currentSessionPoint.form_fill_time_sec || 0,
        timestamp: Date.now()
    };
    
    sessionData.push(dataPoint);
}

// Start a new session
function startSession() {
    // Reset session data
    isSessionActive = true;
    sessionStartTime = Date.now();
    sessionData = [];
    currentSessionPoint = {};
    
    // Reset metrics
    metrics = {
        mouseMovement: 0,
        typingSpeed: 0,
        clickPattern: 0,
        timeOnPage: 0,
        scrollBehavior: 'none',
        captchaSuccess: 1,
        formFillTime: 0
    };
    
    // Record initial data point
    recordDataPoint();
    
    // Notify background script
    chrome.runtime.sendMessage({
        type: "session_update",
        status: "started"
    });
}

// Stop the current session
function stopSession(completed = false) {
    if (!isSessionActive) return;
    
    isSessionActive = false;
    
    // Record final data point
    recordDataPoint();
    
    // Calculate session summary metrics
    const sessionSummary = calculateSessionSummary();
    
    // Send session data to backend
    sendSessionToBackend(sessionSummary).then(prediction => {
        // Store session data and prediction
        chrome.storage.local.set({
            sessionData: sessionData,
            sessionSummary: sessionSummary,
            prediction: prediction,
            sessionCompleted: completed
        });
        
        // Notify background script
        chrome.runtime.sendMessage({
            type: "session_update",
            status: "ended",
            completed: completed,
            prediction: prediction
        });
    });
}

// Calculate summary metrics for the entire session
function calculateSessionSummary() {
    // If no data points, return empty summary
    if (sessionData.length === 0) {
        return {
            mouse_movement_units: 0,
            typing_speed_cpm: 0,
            click_pattern_score: 0,
            time_spent_on_page_sec: 0,
            scroll_behavior_encoded: 0,
            captcha_success: 1,
            form_fill_time_sec: 0
        };
    }
    
    // Calculate averages and totals
    const summary = {
        mouse_movement_units: sessionData[sessionData.length - 1].mouse_movement_units,
        typing_speed_cpm: 0,
        click_pattern_score: 0,
        time_spent_on_page_sec: (Date.now() - sessionStartTime) / 1000,
        scroll_behavior_encoded: sessionData[sessionData.length - 1].scroll_behavior_encoded,
        captcha_success: metrics.captchaSuccess,
        form_fill_time_sec: 0
    };
    
    // Calculate averages for metrics that should be averaged
    let typingPoints = 0;
    let clickPoints = 0;
    let formPoints = 0;
    
    sessionData.forEach(point => {
        if (point.typing_speed_cpm > 0) {
            summary.typing_speed_cpm += point.typing_speed_cpm;
            typingPoints++;
        }
        if (point.click_pattern_score > 0) {
            summary.click_pattern_score += point.click_pattern_score;
            clickPoints++;
        }
        if (point.form_fill_time_sec > 0) {
            summary.form_fill_time_sec += point.form_fill_time_sec;
            formPoints++;
        }
    });
    
    if (typingPoints > 0) summary.typing_speed_cpm /= typingPoints;
    if (clickPoints > 0) summary.click_pattern_score /= clickPoints;
    if (formPoints > 0) summary.form_fill_time_sec /= formPoints;
    
    return summary;
}

// Function to send session data to backend
async function sendSessionToBackend(sessionData) {
    try {
        const response = await fetch('http://localhost:8000/predict_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sessionData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const prediction = await response.json();
        return prediction;
    } catch (error) {
        console.error('Error sending session data to backend:', error);
        return {
            is_bot: false,
            probability: 0,
            error: error.message
        };
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "start_session") {
        startSession();
        sendResponse({status: "Session started"});
    } else if (request.action === "stop_session") {
        stopSession(true);
        sendResponse({status: "Session ended"});
    } else if (request.action === "get_session_status") {
        sendResponse({
            isActive: isSessionActive,
            currentMetrics: {
                mouse_movement_units: metrics.mouseMovement,
                typing_speed_cpm: metrics.typingSpeed,
                click_pattern_score: metrics.clickPattern,
                time_spent_on_page_sec: metrics.timeOnPage,
                scroll_behavior_encoded: scrollBehaviorCode,
                captcha_success: metrics.captchaSuccess,
                form_fill_time_sec: metrics.formFillTime
            },
            dataPoints: sessionData.length
        });
    } else if (request.action === "analyze") {
        // For backwards compatibility
        if (isSessionActive) {
            // Send current session data
            sendResponse({
                metrics: metrics,
                isSessionActive: true,
                sessionData: {
                    dataPoints: sessionData.length,
                    duration: (Date.now() - sessionStartTime) / 1000
                }
            });
        } else {
            // Send metrics to backend and get prediction
            sendMetricsToBackend().then(prediction => {
                if (prediction) {
                    // Store current metrics and prediction
                    chrome.storage.local.set({
                        metrics: metrics,
                        prediction: prediction
                    });
                    
                    // Send metrics and prediction back to popup
                    sendResponse({
                        metrics: metrics,
                        prediction: prediction
                    });

                    // Notify background script if suspicious
                    if (prediction.is_bot) {
                        chrome.runtime.sendMessage({
                            type: "metrics_update",
                            data: { isSuspicious: true }
                        });
                    }
                }
            });
        }
        return true; // Keep the message channel open for async response
    }
    return true; // Keep the message channel open for async response
});

// Legacy function for backward compatibility
async function sendMetricsToBackend() {
    try {
        const response = await fetch('http://localhost:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mouse_movement: metrics.mouseMovement,
                typing_speed: metrics.typingSpeed,
                click_pattern: metrics.clickPattern,
                time_spent: metrics.timeOnPage,
                scroll_behavior: metrics.scrollBehavior,
                captcha_success: metrics.captchaSuccess,
                form_fill_time: metrics.formFillTime
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const prediction = await response.json();
        return prediction;
    } catch (error) {
        console.error('Error sending metrics to backend:', error);
        return null;
    }
} 