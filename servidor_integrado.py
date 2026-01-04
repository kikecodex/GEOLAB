"""
Servidor Integrado - Agente IA + Página Web
Combina el servidor web y la API del agente en uno solo
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agente_ia import AgenteGEOCENTERLAB
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Inicializar agente global
print("🚀 Inicializando Agente IA...")
agente = AgenteGEOCENTERLAB()

# Servir archivos estáticos
@app.route('/')
def index():
    return send_from_directory('.', 'cipda.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal para consultas al agente"""
    try:
        data = request.json
        
        if not data or 'pregunta' not in data:
            return jsonify({'error': 'Falta el campo "pregunta" en el body'}), 400
        
        pregunta = data.get('pregunta', '').strip()
        
        if not pregunta:
            return jsonify({'error': 'La pregunta no puede estar vacía'}), 400
        
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

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Endpoint para enviar cotizaciones por correo electrónico"""
    try:
        data = request.json
        
        # Validar campos requeridos
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        required_fields = ['destinatario', 'asunto', 'contenido']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400
        
        destinatario = data['destinatario'].strip()
        asunto = data['asunto'].strip()
        contenido = data['contenido']
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, destinatario):
            return jsonify({'error': 'Formato de correo electrónico inválido'}), 400
        
        # Intentar enviar el correo
        from email_utils import enviar_email_gmail
        enviar_email_gmail(destinatario, asunto, contenido)
        
        print(f"✅ Correo enviado exitosamente a: {destinatario}")
        
        return jsonify({
            'success': True,
            'mensaje': 'Correo enviado exitosamente',
            'destinatario': destinatario,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/send-email: {e}")
        return jsonify({
            'error': 'Error al enviar el correo',
            'detalle': str(e)
        }), 500

@app.route('/api/whatsapp-quote', methods=['POST'])
def whatsapp_quote():
    """Endpoint para generar enlace de WhatsApp con cotización"""
    try:
        data = request.json
        
        # Validar campos requeridos
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Obtener datos de la cotización
        nombre = data.get('nombre', 'Cliente')
        servicios = data.get('servicios', [])
        mensaje_adicional = data.get('mensaje', '')
        generar_cotizacion = data.get('generar_cotizacion', False)
        datos_servicios = data.get('datos_servicios', [])
        
        # Número de WhatsApp de GEO CENTER LAB
        whatsapp_number = '51921593127'
        
        # Si se solicita cotización completa, usar el generador
        if generar_cotizacion and datos_servicios:
            try:
                from generador_cotizacion import GeneradorCotizacion
                generador = GeneradorCotizacion()
                
                # Formatear servicios
                servicios_formateados = []
                for servicio in datos_servicios:
                    servicios_formateados.append({
                        'nombre': servicio.get('nombre', ''),
                        'cantidad': servicio.get('cantidad', 1),
                        'urgente': servicio.get('urgente', False)
                    })
                
                # Generar cotización profesional
                mensaje = generador.generar_cotizacion_whatsapp(
                    cliente_nombre=nombre,
                    servicios_solicitados=servicios_formateados,
                    ubicacion="",
                    es_primer_servicio=True,
                    notas_adicionales=mensaje_adicional
                )
                
                print(f"✅ Cotización profesional generada para: {nombre}")
                
            except ImportError:
                print("⚠️ No se pudo importar generador_cotizacion, usando mensaje simple")
                # Fallback a mensaje simple
                mensaje = f"🏢 *SOLICITUD DE COTIZACIÓN - GEO CENTER LAB*\n\n"
                mensaje += f"👤 *Cliente:* {nombre}\n\n"
                
                if servicios:
                    mensaje += "📋 *Servicios solicitados:*\n"
                    for i, servicio in enumerate(servicios, 1):
                        mensaje += f"  {i}. {servicio}\n"
                    mensaje += "\n"
                
                if mensaje_adicional:
                    mensaje += f"💬 *Mensaje adicional:*\n{mensaje_adicional}\n\n"
                
                mensaje += "✅ Por favor, envíeme una cotización detallada.\n\n"
                mensaje += "_Solicitud enviada desde: www.geocenterlab.com_"
        else:
            # Mensaje simple sin cotización completa
            mensaje = f"🏢 *SOLICITUD DE COTIZACIÓN - GEO CENTER LAB*\n\n"
            mensaje += f"👤 *Cliente:* {nombre}\n\n"
            
            if servicios:
                mensaje += "📋 *Servicios solicitados:*\n"
                for i, servicio in enumerate(servicios, 1):
                    mensaje += f"  {i}. {servicio}\n"
                mensaje += "\n"
            
            if mensaje_adicional:
                mensaje += f"💬 *Mensaje adicional:*\n{mensaje_adicional}\n\n"
            
            mensaje += "✅ Por favor, envíeme una cotización detallada.\n\n"
            mensaje += "_Solicitud enviada desde: www.geocenterlab.com_"
        
        # Codificar mensaje para URL
        from urllib.parse import quote
        mensaje_encoded = quote(mensaje)
        
        # Generar enlace de WhatsApp
        whatsapp_link = f"https://wa.me/{whatsapp_number}?text={mensaje_encoded}"
        
        print(f"✅ Enlace de WhatsApp generado para: {nombre}")
        
        return jsonify({
            'success': True,
            'whatsapp_link': whatsapp_link,
            'mensaje': mensaje,
            'numero': whatsapp_number,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Error en /api/whatsapp-quote: {e}")
        return jsonify({
            'error': 'Error al generar enlace de WhatsApp',
            'detalle': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'modo_demo': agente.modo_demo,
        'servicios': len(agente.servicios),
        'proyectos': len(agente.proyectos),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌐 SERVIDOR INTEGRADO - GEO CENTER LAB")
    print("=" * 60)
    print(f"📊 Servicios cargados: {len(agente.servicios)}")
    print(f"🏗️  Proyectos cargados: {len(agente.proyectos)}")
    print(f"🤖 Modo IA: {'Demo (sin API Key)' if agente.modo_demo else 'OpenAI Activado'}")
    print("\n🌐 Servidor corriendo en: http://localhost:8000")
    print("   📄 Página principal: http://localhost:8000/")
    print("   🤖 Chat IA integrado en la página")
    print("   📧 Endpoint de email: http://localhost:8000/api/send-email")
    print("   💬 Endpoint de WhatsApp: http://localhost:8000/api/whatsapp-quote")
    print("=" * 60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8000, threaded=True)
