"""
API REST para el Agente IA de GEO CENTER LAB
Servidor Flask que expone endpoints para interactuar con el agente
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from agente_ia import AgenteGEOCENTERLAB
from agente_ia import AgenteGEOCENTERLAB
import os
from datetime import datetime
from database import obtener_leads  # [NUEVO] Importar DB

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde cualquier origen

# Inicializar agente global
print("🚀 Inicializando Agente IA...")
agente = AgenteGEOCENTERLAB()

# HTML de prueba para el chat
TEST_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat IA - GEO CENTER LAB</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            width: 100%;
            max-width: 600px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #1e3a5f, #4a90e2);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            justify-content: flex-end;
        }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: linear-gradient(135deg, #1e3a5f, #4a90e2);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.bot .message-content {
            background: white;
            color: #333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-bottom-left-radius: 4px;
        }
        .message-time {
            font-size: 11px;
            margin-top: 5px;
            opacity: 0.7;
        }
        .typing {
            display: none;
            padding: 12px;
            background: white;
            border-radius: 18px;
            width: fit-content;
        }
        .typing.active {
            display: block;
        }
        .typing span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        .chat-input:focus {
            border-color: #4a90e2;
        }
        .send-button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #1e3a5f, #4a90e2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .send-button:hover {
            transform: scale(1.05);
        }
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .suggestions {
            padding: 10px 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }
        .suggestion-chip {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            white-space: nowrap;
            transition: background 0.3s;
        }
        .suggestion-chip:hover {
            background: #4a90e2;
            color: white;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Asistente IA</h1>
            <p>GEO CENTER LAB - Pregunta lo que necesites</p>
        </div>
        
        <div class="suggestions" id="suggestions">
            <div class="suggestion-chip" onclick="sendSuggestion('¿Qué servicios ofrecen?')">
                ¿Qué servicios ofrecen?
            </div>
            <div class="suggestion-chip" onclick="sendSuggestion('¿Cuál es su horario?')">
                ¿Cuál es su horario?
            </div>
            <div class="suggestion-chip" onclick="sendSuggestion('¿Dónde están ubicados?')">
                ¿Dónde están ubicados?
            </div>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    ¡Hola! 👋 Soy el asistente virtual de GEO CENTER LAB. 
                    Puedo ayudarte con información sobre nuestros servicios, 
                    proyectos, horarios y más. ¿En qué puedo asistirte?
                </div>
            </div>
            <div class="typing" id="typing">
                <span></span><span></span><span></span>
            </div>
        </div>
        
        <div class="chat-input-container">
            <input 
                type="text" 
                class="chat-input" 
                id="chatInput" 
                placeholder="Escribe tu pregunta aquí..."
                onkeypress="handleKeyPress(event)"
            >
            <button class="send-button" id="sendButton" onclick="sendMessage()">
                Enviar
            </button>
        </div>
    </div>

    <script>
        const API_URL = '/api/chat';
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const typing = document.getElementById('typing');

        function addMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            
            messageDiv.appendChild(contentDiv);
            chatMessages.insertBefore(messageDiv, typing);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTyping() {
            typing.classList.add('active');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTyping() {
            typing.classList.remove('active');
        }

        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            chatInput.value = '';
            sendButton.disabled = true;
            showTyping();

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pregunta: message })
                });

                const data = await response.json();
                hideTyping();
                
                if (data.error) {
                    addMessage('❌ ' + data.error, 'bot');
                } else {
                    addMessage(data.respuesta, 'bot');
                }
            } catch (error) {
                hideTyping();
                addMessage('❌ Error al conectar con el servidor', 'bot');
            } finally {
                sendButton.disabled = false;
                chatInput.focus();
            }
        }

        function sendSuggestion(text) {
            chatInput.value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Focus en el input al cargar
        chatInput.focus();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Página de prueba del chat"""
    return render_template_string(TEST_HTML)


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal para consultas al agente
    
    Body JSON:
    {
        "pregunta": "¿Qué servicios ofrecen?"
    }
    
    Response JSON:
    {
        "respuesta": "Respuesta del agente...",
        "timestamp": "2024-11-18T10:30:00"
    }
    """
    try:
        data = request.json
        
        if not data or 'pregunta' not in data:
            return jsonify({
                'error': 'Falta el campo "pregunta" en el body'
            }), 400
        
        pregunta = data.get('pregunta', '').strip()
        
        if not pregunta:
            return jsonify({
                'error': 'La pregunta no puede estar vacía'
            }), 400
        
        # Consultar al agente
        respuesta = agente.consultar(pregunta)
        
        return jsonify({
            'respuesta': respuesta,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/chat: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500


@app.route('/api/actualizar', methods=['POST'])
def actualizar():
    """
    Endpoint para actualizar los datos del agente
    
    Response JSON:
    {
        "status": "ok",
        "mensaje": "Datos actualizados correctamente",
        "servicios": 5,
        "proyectos": 8
    }
    """
    try:
        agente.actualizar_datos()
        
        return jsonify({
            'status': 'ok',
            'mensaje': 'Datos actualizados correctamente',
            'servicios': len(agente.servicios),
            'proyectos': len(agente.proyectos),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/actualizar: {e}")
        return jsonify({
            'error': 'Error al actualizar datos',
            'detalle': str(e)
        }), 500


@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """
    Endpoint para obtener estadísticas del agente
    
    Response JSON:
    {
        "servicios": 5,
        "proyectos": 8,
        "interacciones": 42
    }
    """
    try:
        return jsonify({
            'servicios': len(agente.servicios),
            'proyectos': len(agente.proyectos),
            'interacciones': len(agente.historial_conversacion) // 2,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/estadisticas: {e}")
        return jsonify({
            'error': 'Error al obtener estadísticas',
            'detalle': str(e)
        }), 500


@app.route('/api/limpiar', methods=['POST'])
def limpiar():
    """
    Endpoint para limpiar el historial de conversación
    
    Response JSON:
    {
        "status": "ok",
        "mensaje": "Historial limpiado"
    }
    """
    try:
        agente.limpiar_historial()
        
        return jsonify({
            'status': 'ok',
            'mensaje': 'Historial limpiado correctamente',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/limpiar: {e}")
        return jsonify({
            'error': 'Error al limpiar historial',
            'detalle': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'servidor': 'API Agente IA GEO CENTER LAB',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/leads', methods=['GET'])
def ver_leads():
    """
    [DASHBOARD SIMPLE] Ver lista de clientes capturados
    """
    try:
        leads = obtener_leads()
        
        # Generar tabla HTML simple
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Leads - Geo Center Lab</title>
            <style>
                body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }
                table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #1e3a5f; color: white; }
                tr:hover { background-color: #f5f5f5; }
                h1 { color: #1e3a5f; }
                .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
                .new { background: #e3f2fd; color: #1565c0; }
            </style>
        </head>
        <body>
            <h1>📋 Clientes Capturados (Leads)</h1>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Contacto</th>
                        <th>Tipo</th>
                        <th>Interés</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for lead in leads:
            html += f"""
                <tr>
                    <td>{lead['id']}</td>
                    <td>{lead['contacto']}</td>
                    <td>{lead['tipo_contacto']}</td>
                    <td>{lead['servicios_interes']}</td>
                    <td>{lead['fecha_creacion']}</td>
                    <td><span class="badge new">{lead['estado']}</span></td>
                </tr>
            """
            
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        return render_template_string(html)
        
    except Exception as e:
        return f"Error leyendo base de datos: {e}"


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 API REST - Agente IA GEO CENTER LAB")
    print("=" * 60)
    print(f"📊 Servicios cargados: {len(agente.servicios)}")
    print(f"🏗️  Proyectos cargados: {len(agente.proyectos)}")
    print("\n📡 Endpoints disponibles:")
    print("   POST /api/chat          - Consultar al agente")
    print("   POST /api/actualizar    - Actualizar datos")
    print("   GET  /api/estadisticas  - Ver estadísticas")
    print("   POST /api/limpiar       - Limpiar historial")
    print("   GET  /health            - Estado del servidor")
    print("   GET  /                  - Interfaz de prueba")
    print("\n🌐 Servidor corriendo en: http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
