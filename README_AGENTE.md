# 🤖 Agente IA - GEO CENTER LAB

Asistente virtual inteligente para responder consultas sobre servicios, proyectos y información de GEO CENTER LAB.

## 🚀 Características

- ✅ Extrae automáticamente información de la página web
- ✅ Responde preguntas sobre servicios y proyectos
- ✅ Mantiene contexto de conversación
- ✅ Respuestas profesionales y personalizadas
- ✅ Modo interactivo y modo de ejemplos
- ✅ Exporta conversaciones a JSON
- ✅ Estadísticas de uso

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI con API Key

## 🔧 Instalación

### 1. Instalar Python
Descarga e instala Python desde [python.org](https://www.python.org/downloads/)

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar API Key de OpenAI

#### Opción A: Crear archivo .env
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env y agregar tu API Key
# OPENAI_API_KEY=sk-tu-clave-aqui
```

#### Opción B: Obtener API Key
1. Ve a [platform.openai.com](https://platform.openai.com/api-keys)
2. Inicia sesión o crea una cuenta
3. Crea una nueva API Key
4. Copia la clave y pégala en el archivo `.env`

## 🎯 Uso

### Modo Automático (con ejemplos)
```bash
python agente_ia.py
```

Esto ejecutará:
- Carga automática de datos de la página
- 3 consultas de ejemplo
- Modo interactivo

### Modo Interactivo
Una vez iniciado, puedes:
- Hacer preguntas libremente
- Escribir `limpiar` para reiniciar conversación
- Escribir `stats` para ver estadísticas
- Escribir `salir` para terminar (guarda conversación automáticamente)

## 📝 Ejemplos de Consultas

```
¿Qué servicios de laboratorio ofrecen?
¿Realizan estudios topográficos?
¿Cuál es su horario de atención?
¿Cómo puedo contactarlos?
¿Qué proyectos han realizado?
¿Hacen supervisión de obras?
¿Realizan ensayos de mecánica de suelos?
¿Tienen servicio de perforación diamantina?
¿Cuánto cuesta un estudio de suelos?
¿Pueden hacer levantamientos con drones?
```

## 🔌 Integración con la Página Web

### Opción 1: Widget de Chat (JavaScript)

Crea un archivo `chat-widget.js`:

```javascript
// Chat Widget para integrar el agente IA
class ChatWidgetIA {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api/chat'; // URL de tu API
        this.init();
    }
    
    init() {
        // Crear HTML del widget
        const widgetHTML = `
            <div id="chat-widget" class="chat-widget">
                <button id="chat-toggle" class="chat-toggle">
                    <i class="fas fa-comments"></i>
                </button>
                <div id="chat-container" class="chat-container" style="display: none;">
                    <div class="chat-header">
                        <h3>Asistente GEO CENTER LAB</h3>
                        <button id="chat-close">×</button>
                    </div>
                    <div id="chat-messages" class="chat-messages"></div>
                    <div class="chat-input-container">
                        <input type="text" id="chat-input" placeholder="Escribe tu pregunta...">
                        <button id="chat-send">Enviar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        document.getElementById('chat-toggle').addEventListener('click', () => {
            const container = document.getElementById('chat-container');
            container.style.display = container.style.display === 'none' ? 'flex' : 'none';
        });
        
        document.getElementById('chat-close').addEventListener('click', () => {
            document.getElementById('chat-container').style.display = 'none';
        });
        
        document.getElementById('chat-send').addEventListener('click', () => this.sendMessage());
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta: message })
            });
            
            const data = await response.json();
            this.addMessage(data.respuesta, 'bot');
        } catch (error) {
            this.addMessage('Error al conectar con el servidor', 'bot');
        }
    }
    
    addMessage(text, type) {
        const messagesDiv = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        messageDiv.textContent = text;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// Inicializar widget cuando la página cargue
document.addEventListener('DOMContentLoaded', () => {
    new ChatWidgetIA();
});
```

### Opción 2: API REST (Flask)

Crea `api_server.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from agente_ia import AgenteGEOCENTERLAB

app = Flask(__name__)
CORS(app)

# Inicializar agente global
agente = AgenteGEOCENTERLAB()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    pregunta = data.get('pregunta', '')
    
    if not pregunta:
        return jsonify({'error': 'Pregunta vacía'}), 400
    
    respuesta = agente.consultar(pregunta)
    return jsonify({'respuesta': respuesta})

@app.route('/api/actualizar', methods=['POST'])
def actualizar():
    agente.actualizar_datos()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Instalar dependencias adicionales:
```bash
pip install flask flask-cors
```

## 📊 Estructura del Proyecto

```
Cipda/
├── agente_ia.py           # Código principal del agente
├── api_server.py          # API REST (opcional)
├── chat-widget.js         # Widget web (opcional)
├── requirements.txt       # Dependencias
├── .env                   # Variables de entorno (crear)
├── .env.example           # Ejemplo de configuración
├── README_AGENTE.md       # Esta documentación
├── conversacion.json      # Historial exportado
└── cipda.html            # Página web
```

## 🎨 Estilos CSS para el Widget

Agrega a `styles.css`:

```css
/* Chat Widget Styles */
.chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}

.chat-toggle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1e3a5f, #4a90e2);
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.3s;
}

.chat-toggle:hover {
    transform: scale(1.1);
}

.chat-container {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 5px 40px rgba(0,0,0,0.3);
    display: flex;
    flex-direction: column;
}

.chat-header {
    background: linear-gradient(135deg, #1e3a5f, #4a90e2);
    color: white;
    padding: 15px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-messages {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
}

.chat-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
}

.chat-message.user {
    background: #e3f2fd;
    margin-left: auto;
}

.chat-message.bot {
    background: #f5f5f5;
}

.chat-input-container {
    padding: 15px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
}

.chat-input-container input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.chat-input-container button {
    padding: 10px 20px;
    background: #4a90e2;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
```

## 💰 Costos de OpenAI

Con GPT-4o-mini:
- ~$0.15 por millón de tokens de entrada
- ~$0.60 por millón de tokens de salida
- Promedio: $0.002 - $0.005 por consulta
- 1000 consultas ≈ $2 - $5 USD

## 🔒 Seguridad

- ⚠️ Nunca subas tu `.env` a repositorios públicos
- ⚠️ Mantén tu API Key privada
- ✅ Usa variables de entorno
- ✅ Agrega `.env` al `.gitignore`

## 🐛 Solución de Problemas

### Error: "No module named 'openai'"
```bash
pip install openai
```

### Error: "API Key not found"
Verifica que el archivo `.env` existe y contiene `OPENAI_API_KEY=tu-clave`

### Error: "Rate limit exceeded"
Has excedido el límite de consultas. Espera unos minutos o verifica tu plan de OpenAI.

## 📞 Soporte

Para problemas técnicos:
- Email: geocenter.lab@gmail.com
- WhatsApp: +51 921593127

## 📄 Licencia

Este proyecto es de uso interno para GEO CENTER LAB.

---

Desarrollado con ❤️ para GEO CENTER LAB
