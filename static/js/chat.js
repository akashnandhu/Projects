document.addEventListener("DOMContentLoaded", () => {
    const sessionIdElement = document.getElementById("session-id");
    if (!sessionIdElement) return;

    const sessionId = JSON.parse(sessionIdElement.textContent);
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/chat/${sessionId}/`;
    
    let chatSocket = null;
    
    const messagesDiv = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-button');
    const statusIndicator = document.getElementById('connection-status-indicator');
    const statusText = document.getElementById('connection-status-text');
    const typingIndicator = document.getElementById('typing-indicator');
    
    const crisisModal = document.getElementById('crisis-modal');
    const crisisModalContent = document.getElementById('crisis-modal-content');

    function appendMessage(sender, content, timestamp) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${sender === 'USER' ? 'justify-end' : 'justify-start'}`;
        
        const innerDiv = document.createElement('div');
        innerDiv.className = `px-4 py-2 rounded-lg max-w-[80%] shadow-sm ${
            sender === 'USER' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : (sender === 'SYSTEM' ? 'bg-amber-100 text-amber-900 italic font-medium' : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none')
        }`;
        
        innerDiv.textContent = content;
        msgDiv.appendChild(innerDiv);
        messagesDiv.appendChild(msgDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function showCrisisModal(alertType, resources, message) {
        let title = alertType === 'SELF_HARM' ? "We're Here With You" : "Public Safety Notice";
        let headerColor = alertType === 'SELF_HARM' ? "bg-blue-50 text-blue-800" : "bg-red-50 text-red-800";
        let iconHtml = alertType === 'SELF_HARM' 
            ? `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                 <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                 </svg>
               </div>`
            : `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                 <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                 </svg>
               </div>`;

        let linksHtml = '';
        if (resources.hotlines) {
            linksHtml = resources.hotlines.map(h => {
                if(h.number) return `<li class="py-2"><a href="tel:${h.number}" class="text-blue-600 hover:underline font-medium">${h.name}: ${h.number}</a></li>`;
                if(h.url) return `<li class="py-2"><a href="${h.url}" target="_blank" class="text-blue-600 hover:underline font-medium">${h.name}</a></li>`;
                return '';
            }).join('');
        }

        let extraHtml = '';
        if (alertType === 'SELF_HARM') {
            extraHtml = `
                <div class="mt-4 p-4 bg-blue-50 rounded-md">
                    <h4 class="font-semibold text-blue-900 mb-2">Breathing Exercise</h4>
                    <p class="text-sm text-blue-800">${resources.breathing_exercise || ''}</p>
                </div>
                <div class="mt-4 p-4 bg-green-50 rounded-md">
                    <h4 class="font-semibold text-green-900 mb-2">Grounding Exercise</h4>
                    <p class="text-sm text-green-800">${resources.grounding_exercise || ''}</p>
                </div>
            `;
        }

        crisisModalContent.innerHTML = `
            <div class="${headerColor} px-4 py-3 border-b">
                <h3 class="text-lg leading-6 font-medium text-center" id="modal-title">${title}</h3>
            </div>
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                    ${iconHtml}
                    <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                        <div class="mt-2">
                            <p class="text-sm text-gray-700 font-medium">${message}</p>
                            
                            <div class="mt-4">
                                <h4 class="font-semibold text-gray-900 border-b pb-2">Resources</h4>
                                <ul class="divide-y divide-gray-100 text-sm mt-2">
                                    ${linksHtml}
                                </ul>
                            </div>
                            
                            ${extraHtml}
                        </div>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-gray-600 text-base font-medium text-white hover:bg-gray-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm" onclick="closeCrisisModal()">
                    I'm safe, continue chatting
                </button>
            </div>
        `;
        
        crisisModal.classList.remove('hidden');
    }

    window.closeCrisisModal = function() {
        crisisModal.classList.add('hidden');
    }

    function connect() {
        chatSocket = new WebSocket(wsUrl);

        chatSocket.onopen = function(e) {
            statusIndicator.classList.remove('bg-red-500');
            statusIndicator.classList.add('bg-green-500');
            statusText.textContent = "Connected";
        };

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            if (data.type === 'system_update') {
                const counter = document.getElementById('online-counter');
                if (counter) counter.textContent = data.online_staff;
                return;
            }
            
            if (data.type === 'mood_confirmation') {
                const feedback = document.getElementById('mood-feedback');
                if (feedback) {
                    feedback.textContent = data.message;
                    feedback.classList.remove('hidden');
                    feedback.classList.remove('opacity-0');
                    setTimeout(() => {
                        feedback.classList.add('opacity-0');
                        setTimeout(() => feedback.classList.add('hidden'), 300);
                    }, 3000);
                }
                return;
            }
            
            if (data.type === 'typing') {
                if (data.is_typing) {
                    typingIndicator.classList.remove('hidden');
                    scrollToBottom();
                } else {
                    typingIndicator.classList.add('hidden');
                }
                return;
            }
            
            if (data.type === 'crisis_intervention') {
                typingIndicator.classList.add('hidden');
                showCrisisModal(data.alert_type, data.resources, data.message);
                appendMessage('SYSTEM', data.message, new Date().toISOString());
                return;
            }
            
            if (data.sender !== 'USER') {
                typingIndicator.classList.add('hidden');
            }
            appendMessage(data.sender, data.message, new Date().toISOString());
        };

        chatSocket.onclose = function(e) {
            statusIndicator.classList.remove('bg-green-500');
            statusIndicator.classList.add('bg-red-500');
            statusText.textContent = "Reconnecting...";
            setTimeout(connect, 3000);
        };
    }

    connect();

    function sendMessage() {
        const message = input.value.trim();
        if (message && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'type': 'chat_message',
                'message': message
            }));
            input.value = '';
            scrollToBottom();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Setup mood tracker buttons
    document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const mood = this.getAttribute('data-mood');
            if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                chatSocket.send(JSON.stringify({
                    'type': 'mood_update',
                    'mood': mood
                }));
            }
        });
    });

    fetch(`/api/chat/${sessionId}/history/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    appendMessage(msg.sender, msg.content, msg.timestamp);
                });
            }
        })
        .catch(err => console.error("Could not fetch history", err));
});
