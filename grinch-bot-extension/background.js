// Initialize extension when installed
chrome.runtime.onInstalled.addListener(function() {
    // Clear any existing stored metrics
    chrome.storage.local.clear();
    
    // Set default icon
    chrome.action.setIcon({
        path: {
            "16": "images/icon16.png",
            "48": "images/icon48.png",
            "128": "images/icon128.png"
        }
    });
});

// Session data
let activeSession = false;

// Listen for messages from content script
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type === "metrics_update") {
        // Update badge if suspicious activity detected
        if (request.data.isSuspicious) {
            chrome.action.setBadgeText({text: "!"});
            chrome.action.setBadgeBackgroundColor({color: "#FF0000"});
        } else {
            chrome.action.setBadgeText({text: ""});
        }
    } else if (request.type === "session_update") {
        if (request.status === "started") {
            // Update badge to indicate active session
            activeSession = true;
            chrome.action.setBadgeText({text: "REC"});
            chrome.action.setBadgeBackgroundColor({color: "#FF9800"});
        } else if (request.status === "ended") {
            activeSession = false;
            if (request.prediction && request.prediction.is_bot) {
                // Show warning badge if bot detected
                chrome.action.setBadgeText({text: "!"});
                chrome.action.setBadgeBackgroundColor({color: "#FF0000"});
            } else {
                // Clear badge
                chrome.action.setBadgeText({text: ""});
            }
        }
    } else if (request.type === "checkpoint_update") {
        // Flash badge to indicate checkpoint reached
        if (activeSession) {
            const originalText = chrome.action.getBadgeText({});
            chrome.action.setBadgeText({text: "✓"});
            chrome.action.setBadgeBackgroundColor({color: "#4CAF50"});
            
            // Reset badge after a short delay
            setTimeout(() => {
                if (activeSession) {
                    chrome.action.setBadgeText({text: "REC"});
                    chrome.action.setBadgeBackgroundColor({color: "#FF9800"});
                }
            }, 1000);
        }
    }
    return true;
});

// Listen for tab updates to reset session state
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'complete' && activeSession) {
        // Reset session badge on page navigation
        activeSession = false;
        chrome.action.setBadgeText({text: ""});
    }
}); 