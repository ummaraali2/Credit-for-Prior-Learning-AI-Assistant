// Faculty/Advisor Portal Script
// No file upload needed - advisors query existing documents

let waInstance = null;

// Initialize Watson Assistant for Faculty
window.watsonAssistantChatOptions = {
    integrationID: "1dd5be01-8457-4c7c-9962-9d3e9979e9d9", // Faculty integration ID
    region: "au-syd",
    serviceInstanceID: "fb664aa6-6a7e-4626-b086-668dc8b1fa15",
    
    onLoad: async (instance) => {
        waInstance = instance;
        
        console.log('[SUCCESS] Faculty Watson Assistant loaded');
        
        instance.on({
            type: 'view:change',
            handler: (event) => {
                console.log('[VIEW] View changed');
            }
        });
        
        // Listen for custom responses if needed
        instance.on({
            type: 'customResponse',
            handler: (event) => {
                console.log('📨 Custom response received:', event.data);
            }
        });
        
        await instance.render();
    }
};

// Load Watson Assistant
setTimeout(function() {
    const t = document.createElement('script');
    t.src = "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + 
            (window.watsonAssistantChatOptions.clientVersion || 'latest') + 
            "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
});

// Optional: Add any faculty-specific functionality here
// For example, custom search filters, student record lookups, etc.

console.log('🎓 Faculty Portal initialized');