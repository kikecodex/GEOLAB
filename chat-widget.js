/**
 * Widget de Chat IA para GEO CENTER LAB
 * Versión corregida - Header ya no tapa las opciones
 */

class ChatWidgetIA {
    constructor(config = {}) {
        this.apiUrl = config.apiUrl || 'http://localhost:8000/api/chat';
        this.position = config.position || 'bottom-right';
        this.theme = config.theme || 'modern';
        this.isOpen = false;
        this.messageHistory = [];
        this.isTyping = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
        this.addStyles();
        this.showWelcomeMessage();
    }

    createWidget() {
        const widgetHTML = `
            <div id="chat-widget-ia" class="chat-widget-ia ${this.position}">
                <button id="chat-toggle-btn" class="chat-toggle-btn" aria-label="Abrir chat">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                    <span class="chat-notification" id="chat-notification"></span>
                </button>
                
                <div id="chat-container-ia" class="chat-container-ia" style="display: none;">
                    <div class="chat-header-ia">
                        <div class="chat-header-info">
                            <div class="chat-avatar">
                                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                                </svg>
                            </div>
                            <div>
                                <h3>Asistente IA</h3>
                                <p class="chat-status">
                                    <span class="status-dot"></span>
                                    En línea
                                </p>
                            </div>
                        </div>
                        <button id="chat-close-btn" class="chat-close-btn" aria-label="Cerrar chat">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="chat-content-wrapper">
                        <div id="chat-messages-ia" class="chat-messages-ia">
                            <div class="chat-message bot-message">
                                <div class="message-avatar">🤖</div>
                                <div class="message-content">
                                    <p>¡Hola! 👋 ¿En qué te puedo ayudar? <strong>¡Conversemos!</strong></p>
                                    <p>Soy tu asistente de <strong>GEO CENTER LAB</strong> y puedo ayudarte con:</p>
                                    <ul>
                                        <li>✅ Servicios de laboratorio</li>
                                        <li>✅ Estudios topográficos</li>
                                        <li>✅ Proyectos realizados</li>
                                        <li>✅ Horarios y contacto</li>
                                    </ul>
                                    <p>Escribe tu consulta o elige una opción 👇</p>
                                </div>
                            </div>
                            
                            <div class="chat-suggestions-ia" id="chat-suggestions">
                                <button class="suggestion-btn" data-text="¿Qué servicios ofrecen?">
                                    📋 Servicios
                                </button>
                                <button class="suggestion-btn" data-text="¿Cuál es su horario?">
                                    🕐 Horarios
                                </button>
                                <button class="suggestion-btn" data-text="¿Dónde están ubicados?">
                                    📍 Ubicación
                                </button>
                                <button class="suggestion-btn" data-text="¿Realizan topografía?">
                                    📐 Topografía
                                </button>
                            </div>
                            
                            <div id="typing-indicator" class="typing-indicator" style="display: none;">
                                <div class="message-avatar">🤖</div>
                                <div class="typing-dots">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="chat-input-container-ia">
                            <input 
                                type="text" 
                                id="chat-input-ia" 
                                class="chat-input-ia" 
                                placeholder="Escribe tu pregunta..."
                                autocomplete="off"
                            >
                            <button id="chat-send-btn" class="chat-send-btn" aria-label="Enviar mensaje">
                                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div class="chat-footer-ia">
                        <small>Powered by OpenAI • GEO CENTER LAB</small>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chat-toggle-btn');
        const closeBtn = document.getElementById('chat-close-btn');
        const sendBtn = document.getElementById('chat-send-btn');
        const input = document.getElementById('chat-input-ia');
        const suggestions = document.querySelectorAll('.suggestion-btn');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        sendBtn.addEventListener('click', () => this.sendMessage());

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        input.addEventListener('input', () => {
            sendBtn.disabled = !input.value.trim();
        });

        suggestions.forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.getAttribute('data-text');
                this.sendPredefinedMessage(text);
            });
        });
    }

    addStyles() {
        if (document.getElementById('chat-widget-styles')) return;

        const styles = `
            <style id="chat-widget-styles">
                :root {
                    --primary-color: #1e3a5f;
                    --secondary-color: #4a90e2;
                    --success-color: #4ade80;
                    --background-chat: #f8f9fa;
                    --text-primary: #1f2937;
                    --text-secondary: #6b7280;
                    --border-color: #e5e7eb;
                    --white: #ffffff;
                    --shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .chat-widget-ia {
                    position: fixed;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                }
                
                .chat-widget-ia.bottom-right {
                    bottom: 20px;
                    right: 20px;
                }
                
                .chat-toggle-btn {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    border: none;
                    color: var(--white);
                    cursor: pointer;
                    box-shadow: var(--shadow);
                    transition: var(--transition);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                }
                
                .chat-toggle-btn:hover {
                    transform: scale(1.1) translateY(-5px);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
                }
                
                .chat-toggle-btn:active {
                    transform: scale(0.95);
                }
                
                .chat-notification {
                    position: absolute;
                    top: 2px;
                    right: 2px;
                    width: 16px;
                    height: 16px;
                    background: #ef4444;
                    border-radius: 50%;
                    border: 3px solid var(--white);
                    display: none;
                    animation: pulseStrong 1.5s infinite;
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                }
                
                .chat-notification.active {
                    display: block;
                }
                
                @keyframes pulseStrong {
                    0% {
                        transform: scale(1);
                        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                    }
                    50% {
                        transform: scale(1.3);
                        box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
                    }
                    100% {
                        transform: scale(1);
                        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
                    }
                }
                
                .chat-container-ia {
                    position: fixed;
                    bottom: 100px;
                    right: 20px;
                    width: 420px;
                    max-width: calc(100vw - 40px);
                    height: 650px;
                    max-height: calc(100vh - 140px);
                    background: var(--white);
                    border-radius: 20px;
                    box-shadow: var(--shadow);
                    display: flex;
                    flex-direction: column;
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    overflow: hidden;
                    transform: translateY(20px);
                    opacity: 0;
                    transition: var(--transition);
                }
                
                .chat-container-ia:not([style*="display: none"]) {
                    transform: translateY(0);
                    opacity: 1;
                }
                
                .chat-header-ia {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: var(--white);
                    padding: 18px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-shrink: 0;
                }
                
                .chat-header-info {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .chat-avatar {
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .chat-header-ia h3 {
                    margin: 0;
                    font-size: 17px;
                    font-weight: 600;
                }
                
                .chat-status {
                    margin: 3px 0 0 0;
                    font-size: 12px;
                    opacity: 0.9;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: var(--success-color);
                    border-radius: 50%;
                    animation: blink 2s infinite;
                }
                
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.6; }
                }
                
                .chat-close-btn {
                    background: none;
                    border: none;
                    color: var(--white);
                    cursor: pointer;
                    padding: 8px;
                    border-radius: 50%;
                    transition: var(--transition);
                    opacity: 0.9;
                }
                
                .chat-close-btn:hover {
                    opacity: 1;
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .chat-content-wrapper {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                    position: relative;
                }
                
                .chat-messages-ia {
                    flex: 1;
                    overflow-y: auto;
                    padding: 25px 20px 10px;
                    background: var(--background-chat);
                    scroll-behavior: smooth;
                }
                
                .chat-message {
                    display: flex;
                    gap: 12px;
                    margin-bottom: 25px;
                    animation: fadeIn 0.4s ease;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(15px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .message-avatar {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    flex-shrink: 0;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }
                
                .bot-message .message-avatar {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                }
                
                .user-message {
                    flex-direction: row-reverse;
                }
                
                .user-message .message-avatar {
                    background: var(--success-color);
                }
                
                .message-content {
                    background: var(--white);
                    padding: 14px 18px;
                    border-radius: 18px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    max-width: 80%;
                    font-size: 14px;
                    line-height: 1.5;
                    color: var(--text-primary);
                }
                
                .user-message .message-content {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: var(--white);
                }
                
                .message-content p {
                    margin: 0 0 10px 0;
                }
                
                .message-content p:last-child,
                .message-content ul:last-child {
                    margin-bottom: 0;
                }
                
                .message-content ul {
                    margin: 10px 0;
                    padding-left: 20px;
                }
                
                .message-content li {
                    margin: 5px 0;
                }
                
                .message-content a {
                    color: var(--secondary-color);
                    text-decoration: none;
                    border-bottom: 1px dashed var(--secondary-color);
                }
                
                .message-content a:hover {
                    border-bottom-style: solid;
                }
                
                .user-message .message-content a {
                    color: var(--white);
                    border-bottom-color: var(--white);
                }
                
                .typing-indicator {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                    animation: fadeIn 0.3s ease;
                }
                
                .typing-dots {
                    background: var(--white);
                    padding: 12px 16px;
                    border-radius: 18px;
                    display: flex;
                    gap: 5px;
                    align-items: center;
                }
                
                .typing-dots span {
                    width: 8px;
                    height: 8px;
                    background: var(--text-secondary);
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }
                
                .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
                .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
                
                @keyframes typing {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
                    30% { transform: translateY(-8px); opacity: 1; }
                }
                
                .chat-suggestions-ia {
                    display: flex;
                    gap: 10px;
                    padding: 15px 20px 20px;
                    background: var(--white);
                    border-top: 1px solid var(--border-color);
                    overflow-x: auto;
                    scrollbar-width: none;
                    -ms-overflow-style: none;
                    flex-shrink: 0;
                }
                
                .chat-suggestions-ia::-webkit-scrollbar {
                    display: none;
                }
                
                .suggestion-btn {
                    padding: 10px 16px;
                    background: rgba(74, 144, 226, 0.1);
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    font-size: 13px;
                    cursor: pointer;
                    white-space: nowrap;
                    transition: var(--transition);
                    color: var(--primary-color);
                    font-weight: 500;
                    flex-shrink: 0;
                }
                
                .suggestion-btn:hover {
                    background: var(--secondary-color);
                    border-color: var(--secondary-color);
                    color: var(--white);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
                }
                
                .chat-input-container-ia {
                    padding: 16px 20px;
                    background: var(--white);
                    border-top: 1px solid var(--border-color);
                    display: flex;
                    gap: 12px;
                    align-items: center;
                    flex-shrink: 0;
                }
                
                .chat-input-ia {
                    flex: 1;
                    padding: 14px 18px;
                    border: 2px solid var(--border-color);
                    border-radius: 25px;
                    font-size: 14px;
                    outline: none;
                    transition: var(--transition);
                    font-family: inherit;
                    background: #f9fafb;
                }
                
                .chat-input-ia:focus {
                    border-color: var(--secondary-color);
                    background: var(--white);
                }
                
                .chat-send-btn {
                    width: 44px;
                    height: 44px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    border: none;
                    color: var(--white);
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: var(--transition);
                    flex-shrink: 0;
                    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
                }
                
                .chat-send-btn:hover:not(:disabled) {
                    transform: scale(1.05);
                    box-shadow: 0 6px 15px rgba(74, 144, 226, 0.4);
                }
                
                .chat-send-btn:active:not(:disabled) {
                    transform: scale(0.95);
                }
                
                .chat-send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                .chat-footer-ia {
                    padding: 8px 10px;
                    text-align: center;
                    background: rgba(248, 249, 250, 0.7);
                    border-top: 1px solid var(--border-color);
                    flex-shrink: 0;
                }
                
                .chat-footer-ia small {
                    color: var(--text-secondary);
                    font-size: 11px;
                }
                
                @media (max-width: 480px) {
                    .chat-container-ia {
                        bottom: 0;
                        right: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        max-height: 100vh;
                        border-radius: 0;
                        border: none;
                    }
                    
                    .chat-header-ia {
                        border-radius: 0;
                        padding: 20px;
                    }
                }
                /* Scrollbar personalizada */
                .chat-messages-ia::-webkit-scrollbar {
                    width: 6px;
                }
                
                .chat-messages-ia::-webkit-scrollbar-track {
                    background: rgba(0, 0, 0, 0.03);
                }
                
                .chat-messages-ia::-webkit-scrollbar-thumb {
                    background: rgba(0, 0, 0, 0.1);
                    border-radius: 3px;
                }
                
                .chat-messages-ia::-webkit-scrollbar-thumb:hover {
                    background: rgba(0, 0, 0, 0.15);
                }
                
                /* Toast notifications */
                .chat-toast {
                    position: fixed;
                    bottom: 100px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.85);
                    color: var(--white);
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    z-index: 10000;
                    opacity: 0;
                    transform: translateY(20px);
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                
                .chat-toast.show {
                    opacity: 1;
                    transform: translateY(0);
                }
                
                /* Animación mejorada para mensajes */
                @keyframes slideInMessage {
                    from {
                        opacity: 0;
                        transform: translateY(20px) scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
                
                .chat-message {
                    animation: slideInMessage 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
                }
                
                /* Efecto hover en mensajes */
                .message-content:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                    transition: all 0.2s ease;
                }
                
                /* Indicador de conexión */
                .connection-status {
                    position: absolute;
                    top: 12px;
                    right: 60px;
                    font-size: 10px;
                    opacity: 0.7;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }
                
                .connection-status.online::before {
                    content: '';
                    width: 6px;
                    height: 6px;
                    background: var(--success-color);
                    border-radius: 50%;
                    animation: blink 2s infinite;
                }
                
                .connection-status.offline::before {
                    content: '';
                    width: 6px;
                    height: 6px;
                    background: #ef4444;
                    border-radius: 50%;
                }

                /* Botón WhatsApp mejorado */
                .whatsapp-btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background-color: #25D366;
                    color: white !important;
                    padding: 8px 16px;
                    border-radius: 20px;
                    text-decoration: none !important;
                    font-weight: 600;
                    margin-top: 8px;
                    border: none;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 6px rgba(37, 211, 102, 0.2);
                }

                .whatsapp-btn:hover {
                    background-color: #128C7E;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(37, 211, 102, 0.3);
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    toggleChat() {
        const container = document.getElementById('chat-container-ia');
        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            container.style.display = 'flex';
            document.getElementById('chat-input-ia').focus();
            this.hideNotification();
            setTimeout(() => this.scrollToBottom(), 100);
        } else {
            container.style.display = 'none';
        }
    }

    closeChat() {
        const container = document.getElementById('chat-container-ia');
        container.style.display = 'none';
        this.isOpen = false;
    }

    async sendMessage(retry = false) {
        const input = document.getElementById('chat-input-ia');
        const sendBtn = document.getElementById('chat-send-btn');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

        this.isTyping = true;
        sendBtn.disabled = true;

        if (!retry) {
            this.addMessage(message, 'user');
            this.messageHistory.push({ role: 'user', content: message });
            input.value = '';
            this.retryCount = 0;
        }

        this.showTyping();

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos timeout

            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta: message }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.hideTyping();

            if (data.error) {
                this.addMessage('❌ ' + data.error, 'bot');
                this.messageHistory.push({ role: 'assistant', content: data.error });
            } else {
                this.addMessage(data.respuesta, 'bot');
                this.messageHistory.push({ role: 'assistant', content: data.respuesta });
                this.retryCount = 0;
            }
        } catch (error) {
            this.hideTyping();
            console.error('Error en sendMessage:', error);

            if (error.name === 'AbortError') {
                this.addMessage('⏱️ La solicitud tardó demasiado. Por favor, intenta de nuevo.', 'bot');
            } else if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                this.addMessage(`🔄 Reintentando (${this.retryCount}/${this.maxRetries})...`, 'bot');
                setTimeout(() => this.sendMessage(true), 2000);
                return;
            } else {
                this.addMessage('❌ No pude conectar con el servidor. Por favor, verifica tu conexión o contáctanos directamente al WhatsApp.', 'bot');
            }
        } finally {
            this.isTyping = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    sendPredefinedMessage(text) {
        document.getElementById('chat-input-ia').value = text;
        this.sendMessage();
    }

    addMessage(text, type) {
        const messagesContainer = document.getElementById('chat-messages-ia');
        const typingIndicator = document.getElementById('typing-indicator');

        // Siempre mantener sugerencias al final del scroll
        const suggestions = document.getElementById('chat-suggestions');
        if (suggestions) {
            suggestions.remove();
            messagesContainer.insertBefore(suggestions, typingIndicator);
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        // Detectar enlace de WhatsApp y convertirlo en botón
        let formattedText = text;
        const whatsappRegex = /(https:\/\/wa\.me\/[^\s]+)/g;

        if (whatsappRegex.test(text)) {
            formattedText = text.replace(whatsappRegex, (url) => {
                return `<br><a href="${url}" target="_blank" class="whatsapp-btn">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.304-5.235c0-5.453 4.435-9.884 9.884-9.884 5.449 0 9.892 4.435 9.892 9.884s-4.444 9.867-9.892 9.867c-1 0-1 0-1 0z"/></svg>
                    Abrir en WhatsApp
                </a><br>`;
            });
        }

        // Detectar otros enlaces
        formattedText = formattedText.replace(
            /(?<!href=")(https?:\/\/[^\s]+)(?!")/g,
            (url) => {
                // Evitar reemplazar el link que ya convertimos a boton
                if (url.includes('wa.me')) return url;
                return `<a href="${url}" target="_blank" rel="noopener">${url}</a>`;
            }
        );

        // Convertir Markdown bold a HTML bold
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        content.innerHTML = formattedText.replace(/\n/g, '<br>');

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        messagesContainer.insertBefore(messageDiv, typingIndicator);
        this.scrollToBottom();
    }

    showTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        document.getElementById('typing-indicator').style.display = 'none';
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages-ia');
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);
    }

    showNotification() {
        document.getElementById('chat-notification').classList.add('active');
    }

    hideNotification() {
        document.getElementById('chat-notification').classList.remove('active');
    }

    showWelcomeMessage() {
        // Abrir automáticamente el chat después de 1 minuto
        setTimeout(() => {
            if (!this.isOpen) {
                this.toggleChat();
                // Añadir un mensaje inicial atractivo
                setTimeout(() => {
                    this.addMessage('👋 ¡Hola! Bienvenido a GEO CENTER LAB. ¿En qué puedo ayudarte hoy?', 'bot');
                }, 500);
            }
        }, 60000); // 1 minuto

        // Mostrar notificación pulsante antes de abrir (a los 10 segundos)
        setTimeout(() => {
            if (!this.isOpen) {
                this.showNotification();
            }
        }, 10000);
    }

    // Funcionalidades adicionales
    saveToLocalStorage() {
        try {
            const data = {
                history: this.messageHistory.slice(-20),
                timestamp: Date.now()
            };
            localStorage.setItem('geocenterlab_chat_history', JSON.stringify(data));
        } catch (e) {
            console.warn('No se pudo guardar el historial:', e);
        }
    }

    loadFromLocalStorage() {
        try {
            const data = localStorage.getItem('geocenterlab_chat_history');
            if (data) {
                const parsed = JSON.parse(data);
                const oneDay = 24 * 60 * 60 * 1000;

                if (Date.now() - parsed.timestamp < oneDay) {
                    this.messageHistory = parsed.history || [];
                    return true;
                }
            }
        } catch (e) {
            console.warn('No se pudo cargar el historial:', e);
        }
        return false;
    }

    clearHistory() {
        this.messageHistory = [];
        localStorage.removeItem('geocenterlab_chat_history');
        const messagesContainer = document.getElementById('chat-messages-ia');
        const messages = messagesContainer.querySelectorAll('.chat-message');
        messages.forEach((msg, index) => {
            if (index > 0) msg.remove();
        });
    }

    showToast(message) {
        const existingToast = document.querySelector('.chat-toast');
        if (existingToast) existingToast.remove();

        const toast = document.createElement('div');
        toast.className = 'chat-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 20px;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 10000;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatWidget);
} else {
    initChatWidget();
}

function initChatWidget() {
    try {
        const config = {
            apiUrl: 'http://localhost:8000/api/chat',
            position: 'bottom-right',
            theme: 'modern'
        };

        window.chatWidget = new ChatWidgetIA(config);
        console.log('✅ Chat Widget IA inicializado correctamente');
    } catch (error) {
        console.error('❌ Error al inicializar el chat:', error);
    }
}