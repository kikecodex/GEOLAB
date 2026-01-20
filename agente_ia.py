import os
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import re
import logging
from urllib.parse import urljoin
from generador_pdf import GeneradorPDF
from database import guardar_lead  # [NUEVO] DB

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Datos reales verificados como fallback
DATOS_REALES = {
    "nombre": "GEO CENTER LAB PEYTON COMPANY S.A.C.",
    "ruc": "20610467866",
    "descripcion": "Servicios de ensayos de laboratorio e investigación de geotecnia, geología, ingeniería; y análisis de suelo, agua, aire y medio ambiente",
    "fundacion": "2015",
    "ubicacion": "VILLÓN ALTO MZ. C. LOTE 7 - HUARAZ - ANCASH",
    "telefono": ["932203111", "921593127"],
    "email": "geocenter.lab@gmail.com",
    "horario": "Lunes a viernes: 8:00 am - 10:00 pm, Sábados: 8:00 am - 12:00 pm",
    "redes_sociales": {
        "whatsapp": "51932203111",
        "facebook": "https://www.facebook.com/profile.php?id=100095258914422"
    },
    "mision": "Proporcionar servicios de laboratorio de alta calidad con tecnología de última generación, contribuyendo al desarrollo seguro de proyectos de ingeniería en la región",
    "vision": "Ser el laboratorio de referencia líder en el norte del Perú, reconocido por nuestra precisión, confiabilidad e innovación en análisis geotécnicos y ambientales"
}

SERVICIOS_REALES = [
    {
        'categoria': 'Laboratorio de Mecánica de Suelos',
        'subsecciones': [
            {
                'titulo': 'Ensayos Básicos',
                'items': [
                    {'nombre': 'Análisis granulométrico', 'descripcion': 'Distribución del tamaño de partículas según norma técnica'},
                    {'nombre': 'Límites de Atterberg', 'descripcion': 'Límite líquido y plástico para clasificación de suelos'},
                    {'nombre': 'Densidad y peso unitario', 'descripcion': 'Relaciones de peso y volumen del suelo'},
                    {'nombre': 'Contenido de humedad', 'descripcion': 'Determinación de agua en la muestra'}
                ]
            },
            {
                'titulo': 'Ensayos Avanzados',
                'items': [
                    {'nombre': 'CBR (California Bearing Ratio)', 'descripcion': 'Resistencia de suelos para pavimentos'},
                    {'nombre': 'Proctor modificado', 'descripcion': 'Densidad máxima y humedad óptima'},
                    {'nombre': 'Corte directo', 'descripcion': 'Parámetros de resistencia al corte'},
                    {'nombre': 'Consolidación', 'descripcion': 'Compresibilidad del suelo bajo carga'}
                ]
            }
        ]
    },
    {
        'categoria': 'Análisis de Materiales de Construcción',
        'subsecciones': [
            {
                'titulo': 'Concreto y Agregados',
                'items': [
                    {'nombre': 'Resistencia a compresión', 'descripcion': 'Control de calidad de concreto (cylinders)'},
                    {'nombre': 'Granulometría de agregados', 'descripcion': 'Análisis de arenas y piedras'},
                    {'nombre': 'Abración y desgaste', 'descripcion': 'Durabilidad de agregados para pavimentos'}
                ]
            }
        ]
    },
    {
        'categoria': 'Estudios Geotécnicos y Ambientales',
        'subsecciones': [
            {
                'titulo': 'Investigación de Campo',
                'items': [
                    {'nombre': 'Perforación diamantina', 'descripcion': 'Muestreo de suelos hasta 50m de profundidad'},
                    {'nombre': 'Calicatas y test-pits', 'descripcion': 'Excavación para inspección visual'},
                    {'nombre': 'Ensayos in-situ', 'descripcion': 'Densidad de campo, CBR, permeabilidad'},
                    {'nombre': 'SPT (Standard Penetration Test)', 'descripcion': 'Número de golpes para determinar resistencia'}
                ]
            },
            {
                'titulo': 'Análisis Ambiental',
                'items': [
                    {'nombre': 'Análisis de calidad de agua', 'descripcion': 'Físicoquímicos y microbiológicos'},
                    {'nombre': 'Análisis de aire', 'descripcion': 'Partículas y gases'},
                    {'nombre': 'Contaminación de suelos', 'descripcion': 'Metales pesados y hidrocarburos'}
                ]
            }
        ]
    },
    {
        'categoria': 'Topografía y Geodesia',
        'subsecciones': [
            {
                'titulo': 'Servicios Topográficos',
                'items': [
                    {'nombre': 'Levantamiento planimétrico y altimétrico', 'descripcion': 'Con estación total y GPS'},
                    {'nombre': 'Fotogrametría con drones', 'descripcion': 'Modelos 3D y cálculo de volúmenes'},
                    {'nombre': 'Replanteo de obras', 'descripcion': 'Control de ejes y niveles'},
                    {'nombre': 'Curvas de nivel y perfiles', 'descripcion': 'Representación del terreno'}
                ]
            }
        ]
    },
    {
        'categoria': 'Supervisión y Control de Calidad',
        'subsecciones': [
            {
                'titulo': 'Servicios de Construcción',
                'items': [
                    {'nombre': 'Control de calidad de suelos', 'descripcion': 'Supervisión de compactación'},
                    {'nombre': 'Control de concreto', 'descripcion': 'Muestreo y ensayos en obra'},
                    {'nombre': 'Inspección de pavimentos', 'descripcion': 'Control de espesores y densidad'},
                    {'nombre': 'Certificación de obras', 'descripcion': 'Informes técnicos finales'}
                ]
            }
        ]
    }
]

PROYECTOS_REALES = [
    {'nombre': 'Proyecto Vivienda Multifamiliar Huaraz', 'descripcion': 'Estudio de mecánica de suelos y diseño de cimentaciones para 120 viviendas', 'imagen': ''},
    {'nombre': 'Ampliación Carretera Huaraz-Carhuaz', 'descripcion': 'Control de calidad de materiales y supervisión geotécnica', 'imagen': ''},
    {'nombre': 'Sistema de Riego Yungay', 'descripcion': 'Análisis ambiental y geotécnico para canal de irrigación', 'imagen': ''},
    {'nombre': 'Planta de Tratamiento de Aguas', 'descripcion': 'Ensayos de permeabilidad y estabilidad de taludes', 'imagen': ''}
]


# Definición de Flujos de Consulta Experta
FLUJOS_SERVICIO = {
    'ems': {
        'nombre': 'Estudio de Mecánica de Suelos',
        'slots': [
            {'id': 'tipo_proyecto', 'pregunta': 'Para calibrar el estudio, ¿qué tipo de proyecto es? (Ej: Vivienda, Edificio, Carretera)'},
            {'id': 'pisos', 'pregunta': '¿Cuántos niveles o pisos tendrá la edificación? (Incluyendo sótanos)'},
            {'id': 'area', 'pregunta': '¿Cuál es el área aproximada del terreno en m²?'},
            {'id': 'ubicacion', 'pregunta': '¿En qué distrito u localidad se ubica el proyecto? (Para logística)'}
        ]
    },
    'concreto': {
        'nombre': 'Ensayo de Concreto',
        'slots': [
            {'id': 'tipo_muestra', 'pregunta': '¿Qué tipo de muestras necesitas ensayar? (Ej: Probetas, Vigas, Testigos)'},
            {'id': 'cantidad', 'pregunta': '¿Cuántas muestras tienes en total?'},
            {'id': 'edad', 'pregunta': '¿A qué edad se deben romper? (Ej: 7, 14, 28 días)'},
            {'id': 'servicio', 'pregunta': '¿Deseas que recojamos las muestras en obra o las traes al laboratorio?'}
        ]
    },
    'topografia': {
        'nombre': 'Servicio de Topografía',
        'slots': [
            {'id': 'terreno', 'pregunta': '¿Cómo es el terreno? (Plano, Ladera, Accidentado)'},
            {'id': 'area', 'pregunta': '¿De qué extensión estamos hablando? (m² o Hectáreas)'},
            {'id': 'entregables', 'pregunta': '¿Qué entregables necesitas? (Ej: Solo planos, Curvas de nivel, Vuelo con Drone)'}
        ]
    }
}

class AgenteGEOCENTERLAB:
    def __init__(self, respuesta_extendida=False, url_personalizada=None):
        """Inicializa el agente con soporte para URL personalizada"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        # FORZAR modo demo para usar el flujo conversacional mejorado
        self.modo_demo = True  # Usar siempre el flujo real optimizado

        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Usar gemini-2.0-flash - modelo actual de Google (2024/2025)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.chat_session = None # Para mantener sesión si fuera necesario
            logger.info("🤖 Modo híbrido: Flujo real + Gemini AI disponible")
        else:
            self.model = None
            logger.warning("⚠️ MODO DEMO: No se encontró GEMINI_API_KEY")
            logger.warning("   El fallback a IA NO funcionará. Solo menú real disponible.")
        
        # Datos con fallback a valores reales
        self.datos_empresa = {}
        self.servicios = []
        self.proyectos = []
        
        # Historial y contexto
        self.historial_conversacion = []
        self.respuesta_extendida = respuesta_extendida
        self.contexto_usuario = {}
        self.ultima_opcion = None
        self.interacciones_count = 0
        self.solicito_contacto = False
        
        # [NUEVO] Estado del Motor de Consulta
        self.flujo_consulta = {
            'activo': False,
            'tipo': None, # 'ems', 'concreto', etc.
            'datos': {},  # {'pisos': 5, 'area': 200..}
            'step': 0     # Índice de pregunta actual
        }
        
        # URL para scraping
        self.url_pagina = url_personalizada or os.getenv("URL_PAGINA", "http://localhost:8000/cipda.html")
        
        # Intentar actualizar datos al iniciar
        self.actualizar_datos()
    
    def _realizar_peticion_http(self, url, timeout=15):
        """Realiza petición HTTP con manejo de errores robusto"""
        try:
            logger.info(f"🌐 Intentando acceder a: {url}")
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; GEOCENTERLAB-Bot/1.0)'
            })
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error HTTP: {e}")
            return None
    
    def _extraer_de_html_local(self):
        """Intenta cargar HTML local"""
        archivos_posibles = ["cipda.html", "index.html", "geocenter.html", "index.htm"]
        
        for archivo in archivos_posibles:
            if os.path.exists(archivo):
                logger.info(f"📄 Cargando archivo local: {archivo}")
                with open(archivo, "r", encoding="utf-8") as f:
                    return f.read()
        return None
    
    def actualizar_datos(self):
        """Extrae datos de múltiples fuentes con fallback inteligente"""
        logger.info("🔄 Actualizando información de GEO CENTER LAB...")
        
        html_content = None
        
        # 1. Intentar HTML local
        html_content = self._extraer_de_html_local()
        
        # 2. Si no hay local, intentar URL remota
        if not html_content and self.url_pagina:
            html_content = self._realizar_peticion_http(self.url_pagina)
        
        # 3. Si hay contenido HTML, parsearlo
        if html_content:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                self._extraer_info_empresa(soup)
                self._extraer_servicios(soup)
                self._extraer_proyectos(soup)
                logger.info("✅ Datos extraídos de HTML exitosamente")
            except Exception as e:
                logger.error(f"❌ Error parseando HTML: {e}")
                self._cargar_datos_reales()
        
        # 4. Fallback a datos reales siempre disponible
        if not self.servicios or not self.datos_empresa:
            logger.warning("⚠️ Usando datos reales verificados como fallback")
            self._cargar_datos_reales()
        
        self._actualizar_estadisticas()
    
    def _extraer_info_empresa(self, soup):
        """Extrae info de empresa de forma más inteligente"""
        # Buscar meta tags y estructuras comunes
        self.datos_empresa = {}
        
        # Meta tags
        meta_description = soup.find('meta', {'name': 'description'})
        if meta_description:
            self.datos_empresa['descripcion'] = meta_description.get('content', '')
        
        # Buscar información de contacto en múltiples formatos
        self._extraer_contacto(soup)
        
        # Misión y Visión
        for key, cls in [("mision", "mission"), ("vision", "vision"), ("mision", "mision"), ("vision", "vision")]:
            elem = soup.find(['div', 'section'], class_=cls)
            if elem and (p := elem.find(['p', 'span'])):
                self.datos_empresa[key] = p.get_text(strip=True)
        
        # Combinar con datos reales como base
        self.datos_empresa = {**DATOS_REALES, **self.datos_empresa}
    
    def _extraer_contacto(self, soup):
        """Extrae información de contacto de múltiples ubicaciones"""
        # Buscar teléfonos (múltiples formatos)
        telefonos = []
        for link in soup.find_all('a', href=re.compile(r'tel:')):
            telefonos.append(link.get_text(strip=True))
        
        # Buscar emails
        emails = []
        for link in soup.find_all('a', href=re.compile(r'mailto:')):
            emails.append(link.get_text(strip=True))
        
        # Actualizar datos
        if telefonos:
            self.datos_empresa['telefono'] = telefonos
        if emails:
            self.datos_empresa['email'] = emails[0]
    
    def _extraer_servicios(self, soup):
        """Extrae servicios con mejor detección de estructura"""
        self.servicios = []
        
        # Múltiples selectores posibles
        selectores = [
            'div.service-card', 'div.service', 'section.service',
            '.servicio', '.service-item', 'div.col-md-4'
        ]
        
        service_cards = []
        for selector in selectores:
            cards = soup.select(selector)
            if len(cards) > 2:  # Encontrar el selector que devuelva resultados
                service_cards = cards
                logger.info(f"✅ Encontrados {len(cards)} servicios con selector: {selector}")
                break
        
        for card in service_cards:
            titulo = card.find(['h2', 'h3', 'h4'])
            if not titulo:
                continue
            
            titulo = titulo.get_text(strip=True)
            
            # Extraer ícono si existe
            icono = None
            img = card.find('img')
            if img and img.get('src'):
                icono = img.get('src')
            elif card.find('i', class_=re.compile(r'fa-|icon')):
                icono = card.find('i')['class']
            
            # Extraer descripción
            desc = card.find(['p', 'div.description'])
            descripcion = desc.get_text(strip=True) if desc else ""
            
            # Buscar lista de items
            items = self._extraer_items_servicio(card)
            
            self.servicios.append({
                'categoria': titulo,
                'descripcion': descripcion,
                'icono': icono,
                'items': items
            })
        
        # Fallback si no se encontraron servicios en HTML
        if not self.servicios:
            self.servicios = SERVICIOS_REALES
    
    def _extraer_items_servicio(self, card):
        """Extrae items de un servicio específico"""
        items = []
        for li in card.find_all('li'):
            # Limpiar imágenes
            for img in li.find_all(['img', 'svg']):
                img.decompose()
            
            texto = li.get_text(strip=True)
            if texto and len(texto) > 5:
                items.append({
                    'nombre': texto,
                    'descripcion': li.get('data-desc', '')
                })
        
        return items
    
    def _extraer_proyectos(self, soup):
        """Extrae proyectos de forma más flexible"""
        self.proyectos = []
        
        project_cards = soup.find_all(['div', 'section'], class_=re.compile(r'project|portfolio|proyecto'))
        
        for card in project_cards:
            titulo = card.find(['h2', 'h3'])
            descripcion = card.find(['p', 'div.description'])
            img = card.find('img')
            
            if titulo:
                self.proyectos.append({
                    'nombre': titulo.get_text(strip=True),
                    'descripcion': descripcion.get_text(strip=True) if descripcion else '',
                    'imagen': img.get('src', '') if img else ''
                })
        
        # Fallback a proyectos reales
        if not self.proyectos:
            self.proyectos = PROYECTOS_REALES
    
    def _cargar_datos_reales(self):
        """Carga datos reales verificados"""
        logger.info("📋 Cargando datos reales verificados")
        self.datos_empresa = DATOS_REALES.copy()
        self.servicios = SERVICIOS_REALES.copy()
        self.proyectos = PROYECTOS_REALES.copy()
    
    def _construir_contexto_inteligente(self):
        """Construye contexto optimizado y relevante"""
        # Seleccionar servicios principales (más solicitados)
        servicios_top = []
        
        if len(self.servicios) >= 3:
            # Priorizar laboratorio, topografía y perforación
            for cat in ['Laboratorio', 'Topografía', 'Perforación']:
                serv = next((s for s in self.servicios if cat.lower() in s['categoria'].lower()), None)
                if serv:
                    items = [item['nombre'] for sub in serv.get('subsecciones', []) 
                            for item in sub.get('items', [])][:3]
                    servicios_top.append(f"- {serv['categoria']}: {', '.join(items)}...")
        
        contacto = f"📞 {self.datos_empresa.get('telefono', ['932203111'])[0]} | 📧 {self.datos_empresa.get('email', '')}"
        
        contexto = f"""🏢 EMPRESA: {self.datos_empresa.get('nombre', 'GEO CENTER LAB')}

{self.datos_empresa.get('descripcion', '')}

📍 {self.datos_empresa.get('ubicacion', '')}
{contacto}
🕐 {self.datos_empresa.get('horario', '')}

SERVICIOS DESTACADOS:
{chr(10).join(servicios_top)}

ÚLTIMOS PROYECTOS: {', '.join([p['nombre'][:40] + '...' for p in self.proyectos[:2]])}"""
        
        return contexto
    
    def consultar(self, pregunta, idioma="español"):
        """Procesa consultas con contexto enriquecido y memoria inteligente"""
        logger.info(f"\uD83D\uDCAC Consulta #{self.interacciones_count + 1}: {pregunta[:50]}...")
        self.interacciones_count += 1

        # Si está en modo demo, usar el flujo real (menú)
        if self.modo_demo:
            pregunta_lower = pregunta.lower()
            
            # SIEMPRE ejecutar _respuesta_demo_mejorada primero
            # Esto permite que se detecten servicios y contactos
            respuesta_real = self._respuesta_demo_mejorada(pregunta)
            
            # Detectar si la respuesta es genérica/menu para fallback a OpenAI
            if self._es_respuesta_generica(respuesta_real):
                if self.model:
                    logger.info("🤖 Respuesta genérica detectada, usando Gemini como fallback...")
                    respuesta_ia = self._consultar_gemini(pregunta)
                    return respuesta_ia
                else:
                    logger.warning("❌ No hay API Key, solo menú real disponible.")
                    return respuesta_real + "\n\n⚠️ El modo IA avanzado no está disponible por falta de API Key."
            else:
                return respuesta_real

        # Modo IA directo (Gemini)
        try:
            return self._consultar_gemini(pregunta)
        except Exception as e:
            logger.error(f"❌ Error en consulta: {e}")
            return f"⚠️ Hubo un problema. Llámanos directamente: {self.datos_empresa.get('telefono', ['932203111'])[0]} 📞"

    def _es_respuesta_generica(self, respuesta):
        """Detecta si la respuesta es genérica/menu para activar fallback a OpenAI"""
        
        # SI la respuesta contiene un enlace de WhatsApp, NO es genérica
        # Estos son enlaces de cotización generados correctamente
        if "wa.me/" in respuesta or "whatsapp" in respuesta.lower():
            return False
        
        # Si contiene información de contacto confirmada, NO es genérica
        if "✅" in respuesta and ("número guardado" in respuesta.lower() or "perfecto" in respuesta.lower()):
            return False
        
        patrones_genericos = [
            "¿En qué te puedo ayudar?",
            "Escribe el número",
            "Opción no válida",
            "opción no válida",
            "¿Qué necesitas? Escribe el número",
            "¿Qué servicio necesitas?",
            "¿Cuál te interesa",
            "Menú principal",
            "Escribe 1-5",
            "Escribe 1-4",
            "elige una opción",
            "opciones principales",
            "¿Te ayudamos con algo más?",
            "¿Tienes un proyecto en mente?",
            "¿Qué servicio?",
            "¿Qué tipo?",
            "¿Qué profundidad necesitas?",
            "¿Qué estás construyendo/revisando?",
            "¿A dónde enviamos tu cotización?",
            "¿A dónde te lo enviamos?",
            "¿Necesitas agendar cita fuera de horario?",
            "¿Tu proyecto es en Huaraz?",
            "¿Quieres ver demo?",
            "¿Cuándo inicias?",
            "¿Cuándo necesitas?",
            "¿Superficie?",
            "¿Altura del proyecto?",
            "¿Cuántos puntos?",
            "¿Qué profundidad necesitas?",
            "¿Necesitas certificación?",
            "¿Qué servicio?",
            "¿Qué ensayo necesitas?",
            "¿Qué servicio te interesa?",
            "¿Qué necesitas exactamente?",
            "¿En qué puedo ayudarte?"
        ]
        for patron in patrones_genericos:
            if patron.lower() in respuesta.lower():
                return True
        return False

    def _consultar_gemini(self, pregunta):
        """Consulta a Gemini AI como fallback con contexto"""
        try:
            contexto = self._construir_contexto_inteligente()
            
            # Prompt de Sistema (Instrucciones)
            instrucciones = f"""Eres el asistente virtual senior de GEO CENTER LAB. Tu objetivo es convertir visitantes en clientes.
Mantén conversaciones naturales, breves y orientadas a la acción.

CONTEXTO EMPRESA:
{contexto}

REGLAS DE ORO:
- 2-3 frases máximo por respuesta
- Usa opciones numeradas para guiar
- Siempre pregunta algo al final para mantener conversación
- Para cotizaciones: "Necesito [dato] para personalizar tu presupuesto"
- Usa emojis estratégicamente (1-2 por mensaje)
- Precios: NUNCA dar cifras exactas sin contexto, usar "desde" o "cotización personalizada"

Ejemplo de interacción ideal:
U: "¿Qué servicios tienen?"
A: "Somos especialistas en:
1. 🔬 Laboratorio de suelos y concreto
2. 📐 Topografía y Geodesia
3. ⚙️ Perforación Diamantina

¿Cuál es para tu proyecto? (Escribe el número)"
"""
            
            # Construir chat completo en texto plano para Gemini (forma más robusta stateless)
            chat_history = [instrucciones]
            
            # Añadir historial reciente (últimos 8 mensajes)
            for msg in self.historial_conversacion[-8:]:
                rol = "Usuario" if msg['role'] == 'user' else "Asistente"
                chat_history.append(f"{rol}: {msg['content']}")
            
            # Añadir mensaje actual
            chat_history.append(f"Usuario: {pregunta}")
            chat_history.append("Asistente: ")
            
            prompt_final = "\n\n".join(chat_history)
            
            # Generar contenido
            response = self.model.generate_content(prompt_final)
            respuesta = response.text
            
            self._actualizar_historial(pregunta, respuesta)
            logger.info("✅ Respuesta Gemini generada exitosamente")
            return respuesta
            
        except Exception as e:
            logger.error(f"❌ Error en consulta Gemini: {e}")
            return f"⚠️ Disculpa, tuve un lapso técnico. ¿Podrías llamarnos directamente? {self.datos_empresa.get('telefono', ['932203111'])[0]} 📞"
    
    def _detectar_intencion(self, pregunta):
        """Detecta la intención del usuario para personalizar respuesta"""
        pregunta_lower = pregunta.lower()
        
        if any(word in pregunta_lower for word in ['cotiza', 'precio', 'costo', 'presupuesto', 'cuanto']):
            return 'cotizacion'
        elif any(word in pregunta_lower for word in ['contacto', 'llamar', 'visitar', 'direccion', 'ubicacion']):
            return 'contacto'
        elif any(word in pregunta_lower for word in ['servicio', 'ofrece', 'hacen', 'tienen', 'que hacen']):
            return 'informacion_general'
        elif any(word in pregunta_lower for word in ['proyecto', 'experiencia', 'obra', 'referencia']):
            return 'proyectos'
        elif any(word in pregunta_lower for word in ['gracias', 'adios', 'chao']):
            return 'despedida'
        return 'otros'
    
    def _detectar_servicios_mencionados(self, pregunta):
        """Detecta servicios mencionados en la pregunta del usuario"""
        pregunta_lower = pregunta.lower()
        servicios_detectados = []
        
        # Mapeo de palabras clave a servicios completos
        mapeo_servicios = {
            # Ensayos básicos
            'cbr': 'CBR (California Bearing Ratio)',
            'california bearing ratio': 'CBR (California Bearing Ratio)',
            'granulometri': 'Análisis granulométrico',
            'granulometric': 'Análisis granulométrico',
            'atterberg': 'Límites de Atterberg',
            'limite liquido': 'Límites de Atterberg',
            'limite plastico': 'Límites de Atterberg',
            'humedad': 'Contenido de humedad',
            'contenido de humedad': 'Contenido de humedad',
            
            # Compactación
            'proctor': 'Proctor modificado',
            'proctor modificado': 'Proctor modificado',
            'proctor estandar': 'Proctor estándar',
            'compactacion': 'Proctor modificado',
            'compactación': 'Proctor modificado',
            
            # Resistencia
            'corte directo': 'Corte directo',
            'consolidacion': 'Consolidación',
            'consolidación': 'Consolidación',
            'triaxial': 'Ensayo Triaxial',
            'compresion simple': 'Compresión simple',
            'compresión simple': 'Compresión simple',
            'compresion': 'Resistencia a compresión',
            'compresión': 'Resistencia a compresión',
            'resistencia': 'Resistencia a compresión',
            
            # Concreto
            'cilindro': 'Resistencia a compresión',
            'probeta': 'Resistencia a compresión',
            'testigo': 'Extracción de testigos',
            'concreto': 'Resistencia a compresión',
            'hormigon': 'Resistencia a compresión',
            
            # Agregados
            'agregado': 'Granulometría de agregados',
            'arena': 'Granulometría de agregados',
            'grava': 'Granulometría de agregados',
            'piedra': 'Granulometría de agregados',
            'abrasion': 'Abrasión y desgaste',
            'abrasión': 'Abrasión y desgaste',
            'desgaste': 'Abrasión y desgaste',
            'los angeles': 'Abrasión Los Ángeles',
            
            # Perforación y muestreo
            'perforacion': 'Perforación diamantina',
            'perforación': 'Perforación diamantina',
            'diamantina': 'Perforación diamantina',
            'calicata': 'Calicatas y test-pits',
            'excavacion': 'Calicatas y test-pits',
            'excavación': 'Calicatas y test-pits',
            'pozo exploratorio': 'Calicatas y test-pits',
            
            # Ensayos de campo
            'spt': 'SPT (Standard Penetration Test)',
            'penetracion': 'SPT (Standard Penetration Test)',
            'penetración': 'SPT (Standard Penetration Test)',
            'penetracion estandar': 'SPT (Standard Penetration Test)',
            'densidad de campo': 'Ensayos in-situ',
            'densidad campo': 'Ensayos in-situ',
            'cono de arena': 'Ensayos in-situ',
            'in-situ': 'Ensayos in-situ',
            'in situ': 'Ensayos in-situ',
            'insitu': 'Ensayos in-situ',
            'placa de carga': 'Ensayo de placa de carga',
            
            # Químicos y ambientales
            'agua': 'Análisis de calidad de agua',
            'calidad de agua': 'Análisis de calidad de agua',
            'fisicoquimico': 'Análisis de calidad de agua',
            'microbiologico': 'Análisis microbiológico',
            'ph': 'Análisis químico',
            'sales': 'Análisis de sales solubles',
            'sulfatos': 'Análisis químico',
            'cloruros': 'Análisis químico',
            'ambiental': 'Contaminación de suelos',
            'contaminacion': 'Contaminación de suelos',
            'contaminación': 'Contaminación de suelos',
            'metales pesados': 'Contaminación de suelos',
            
            # Topografía
            'topografi': 'Levantamiento planimétrico y altimétrico',
            'levantamiento': 'Levantamiento planimétrico y altimétrico',
            'topografico': 'Levantamiento planimétrico y altimétrico',
            'topográfico': 'Levantamiento planimétrico y altimétrico',
            'dron': 'Fotogrametría con drones',
            'drone': 'Fotogrametría con drones',
            'fotogrametri': 'Fotogrametría con drones',
            'replanteo': 'Replanteo de obras',
            'curvas de nivel': 'Levantamiento planimétrico y altimétrico',
            'volumen': 'Cálculo de volúmenes',
            'volumenes': 'Cálculo de volúmenes',
            
            # Geofísica
            'refraccion': 'Ensayo de Refracción Sísmica',
            'refracción': 'Ensayo de Refracción Sísmica',
            'sismica': 'Ensayo de Refracción Sísmica',
            'sísmica': 'Ensayo de Refracción Sísmica',
            'geofisica': 'Ensayo de Refracción Sísmica',
            
            # Estudios completos
            'mecanica de suelos': 'Estudio de Mecánica de Suelos Completo',
            'mecánica de suelos': 'Estudio de Mecánica de Suelos Completo',
            'estudio de suelos': 'Estudio de Mecánica de Suelos Completo',
            'ems': 'Estudio de Mecánica de Suelos Completo',
            'estudio geotecnico': 'Estudio de Mecánica de Suelos Completo',
            
            # Otros
            'permeabilidad': 'Ensayo de permeabilidad',
            'batimetria': 'Estudio de Batimetría',
            'batimetría': 'Estudio de Batimetría'
        }
        
        # Buscar servicios en la pregunta
        for palabra_clave, servicio_completo in mapeo_servicios.items():
            if palabra_clave in pregunta_lower:
                if servicio_completo not in servicios_detectados:
                    servicios_detectados.append(servicio_completo)
        
        return servicios_detectados
    
    
    def _detectar_tipo_flujo(self, texto):
        """Detecta si la consulta corresponde a uno de los flujos expertos"""
        texto = texto.lower()
        if any(x in texto for x in ['suelo', 'ems', 'calicata', 'cbr', 'proctor']):
            return 'ems'
        if any(x in texto for x in ['concreto', 'probbeta', 'testigo', 'rotura', 'compresion']):
            return 'concreto'
        if any(x in texto for x in ['topografia', 'levantamiento', 'curvas', 'drone', 'plano']):
            return 'topografia'
        return None

    def _iniciar_flujo_consulta(self, tipo_servicio):
        """Inicializa un nuevo flujo de consulta"""
        if tipo_servicio not in FLUJOS_SERVICIO:
            return False
            
        logger.info(f"🚀 Iniciando flujo de consulta experto: {tipo_servicio}")
        self.flujo_consulta = {
            'activo': True,
            'tipo': tipo_servicio,
            'datos': {},
            'step': 0
        }
        
        # Retornar la primera pregunta
        primera_pregunta = FLUJOS_SERVICIO[tipo_servicio]['slots'][0]['pregunta']
        return f"👋 Claro que sí. Soy el especialista encargado del área de {FLUJOS_SERVICIO[tipo_servicio]['nombre']}.\n\nPara poder darte una cotización exacta y técnica, necesito hacerte un par de preguntas rápidas.\n\n{primera_pregunta}"

    def _gestionar_flujo_consulta(self, mensaje_usuario):
        """Gestiona el avance del flujo de preguntas"""
        flujo = self.flujo_consulta
        tipo = flujo['tipo']
        paso_actual = flujo['step']
        slots = FLUJOS_SERVICIO[tipo]['slots']
        
        # 1. Guardar respuesta del paso anterior (si no es el inicio)
        # Nota: Aquí podríamos usar IA para extraer el dato exacto, pero por ahora guardamos todo el texto
        slot_actual = slots[paso_actual]
        flujo['datos'][slot_actual['id']] = mensaje_usuario
        logger.info(f"✅ Dato guardado [{slot_actual['id']}]: {mensaje_usuario}")
        
        # 2. Avanzar al siguiente paso
        flujo['step'] += 1
        
        # 3. Verificar si quedan preguntas
        if flujo['step'] < len(slots):
            siguiente_pregunta = slots[flujo['step']]['pregunta']
            return f"Entendido. 👍\n\n{siguiente_pregunta}"
        else:
            # 4. Flujo completado -> Generar Cotización
            return self._finalizar_flujo_consulta()

    def _finalizar_flujo_consulta(self):
        """Genera el cierre y el enlace de cotización"""
        flujo = self.flujo_consulta
        tipo = flujo['tipo']
        datos = flujo['datos']
        nombre_servicio = FLUJOS_SERVICIO[tipo]['nombre']
        
        # Construir resumen para el mensaje de WhatsApp
        resumen = f"*COTIZACIÓN - {nombre_servicio.upper()}*\n"
        resumen_texto = f"Perfecto, tengo toda la información técnica para tu {nombre_servicio}. 👷‍♂️\n\nHe preparado un resumen:\n"
        
        for slot in FLUJOS_SERVICIO[tipo]['slots']:
            key = slot['id']
            val = datos.get(key, 'No especificado')
            resumen += f"- *{key.capitalize()}*: {val}\n"
            resumen_texto += f"✅ **{key.capitalize()}**: {val}\n"
            
        # Limpiar estado
        self.flujo_consulta['activo'] = False
        
        # Generar Link
        whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
        mensaje_encoded = requests.utils.quote(f"Hola GEO CENTER, acabo de hablar con el asistente IA.\n\n{resumen}\nQuisiera saber el costo final.")
        link = f"https://wa.me/{whatsapp}?text={mensaje_encoded}"
        
        return f"""{resumen_texto}
Hemos analizado tus requerimientos. Según normas técnicas, tu proyecto requiere un enfoque específico.

👉 **Mira tu cotización premilinar aquí:**
[Solicitar Precio Final en WhatsApp]({link})

¿Te gustaría que te llame un ingeniero especialista ahora mismo?"""

    def _respuesta_demo_mejorada(self, pregunta):
        """Modo demo con lógica conversacional avanzada"""
        pregunta_lower = pregunta.lower()
        pregunta_stripped = pregunta.strip()
        
        # [NUEVO] 0. Verificar si hay un flujo de consulta experto activo
        if self.flujo_consulta['activo']:
            return self._gestionar_flujo_consulta(pregunta)
            
        # [NUEVO] 1. Detectar si inicia un flujo experto (Intención de Cotización + Servicio Específico)
        tipo_flujo = self._detectar_tipo_flujo(pregunta_lower)
        # Si detecta servicio Y (pide cotización O menciona palabras clave fuertes)
        es_cotizacion = any(x in pregunta_lower for x in ['cotiz', 'costo', 'precio', 'cuanto', 'quiero', 'necesito'])
        
        if tipo_flujo and es_cotizacion:
            return self._iniciar_flujo_consulta(tipo_flujo)

        # 2. Detectar servicios mencionados (Lógica anterior)
        servicios_mencionados = self._detectar_servicios_mencionados(pregunta)
        if servicios_mencionados:
            # Si menciona "ahora" + servicio, resetea contexto anterior
            if any(palabra in pregunta_lower for palabra in ['ahora quiero', 'ahora enviame', 'ahora cotizacion']):
                logger.info("🔄 Nueva cotización solicitada - reseteando servicios anteriores")
            self.contexto_usuario['servicios_solicitados'] = servicios_mencionados
            logger.info(f"🔍 Servicios detectados: {servicios_mencionados}")
        
        # SEGUNDO: Detectar contacto (prioridad alta)
        email, telefono = self._extraer_contacto_texto(pregunta)
        
        if email or telefono:
            if email:
                self.contexto_usuario['email'] = email
            if telefono:
                self.contexto_usuario['telefono'] = telefono
            
            self.solicito_contacto = True
            return self._generar_respuesta_contacto_confirmado(email or telefono)
        
        # Manejo de selección numérica
        if pregunta_stripped.isdigit():
            return self._manejar_seleccion_numero(int(pregunta_stripped))
        
        # Reset opción si es texto libre
        if not pregunta_stripped.isdigit():
            self.ultima_opcion = None
        
        # Mapeo de intenciones con respuestas específicas
        return self._generar_respuesta_intencion(pregunta_lower)
    
    def _extraer_contacto_texto(self, texto):
        """Extrae email y teléfono de texto usando regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{9,}\b'
        
        email = re.search(email_pattern, texto)
        telefono = re.search(phone_pattern, texto)
        
        return (email.group() if email else None, telefono.group() if telefono else None)
    
    def _generar_respuesta_contacto_confirmado(self, contacto):
        """Genera respuesta cuando el usuario proporciona contacto y envía cotización por WhatsApp"""
        es_email = '@' in contacto

        # [MEJORA] Guardar en Base de Datos (Para Email y Teléfono)
        servicios_cotizar = self.contexto_usuario.get('servicios_solicitados', [])
        if not servicios_cotizar:
             servicios_cotizar = ["Servicios Generales"]
             
        print(f"------------ INTENTANDO GUARDAR LEAD: {contacto} ---------------")
        try:
            lid = guardar_lead(
                contacto=contacto,
                nombre=f"Cliente {contacto}", 
                servicios=servicios_cotizar,
                tipo="email" if es_email else "whatsapp"
            )
            print(f"------------ LEAD GUARDADO CON ID: {lid} ---------------")
            logger.info(f"✅ Lead guardado en BD: {contacto}")
        except Exception as e:
            print(f"------------ ERROR GUARDANDO LEAD: {e} ---------------")
            logger.error(f"❌ Error guardando lead en BD: {e}")
        
        if es_email:
            # Prioritize WhatsApp over email
            whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
            return f"""✅ Perfecto! Te enviaré la cotización.

📱 **Opción más rápida:** WhatsApp
👉 Click aquí para recibir tu cotización: https://wa.me/{whatsapp}?text=Hola,%20quiero%20recibir%20una%20cotización

📧 **Alternativa:** Email a {contacto}
Si prefieres email, responde "email" y te lo enviamos.

💬 ¿Cuál prefieres? (Recomendamos WhatsApp para respuesta inmediata)"""
        else:
            # Es un número de teléfono - generar cotización automáticamente
            whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
            
            # Revalidar servicios para el PDF
            servicios_cotizar = self.contexto_usuario.get('servicios_solicitados', [])
            if not servicios_cotizar:
                servicios_cotizar = ["Análisis granulométrico", "CBR (California Bearing Ratio)"]

            # Generar enlace de cotización con servicios
            whatsapp_link = self._generar_enlace_whatsapp_cotizacion(
                nombre="Cliente",
                servicios=servicios_cotizar,
                mensaje=""
            )
            
            # [MEJORA] Intentar Generar PDF
            pdf_path = ""
            msg_pdf = ""
            try:
                # Formatear servicios para el PDF
                servs_fmt = [{'nombre': s, 'cantidad': 1, 'urgente': False} for s in servicios_cotizar]
                
                # Nombre de archivo único
                filename = f"Cotizacion_{re.sub(r'[^0-9]', '', contacto)}_{datetime.now().strftime('%H%M')}.pdf"
                pdf_gen = GeneradorPDF()
                pdf_gen.generar_cotizacion(
                    cliente_nombre=f"Cliente {contacto}", 
                    servicios=servs_fmt, 
                    numero_cotizacion=f"COT-{datetime.now().strftime('%Y%m%d')}-{re.sub(r'[^0-9]', '', contacto)[-4:]}",
                    output_filename=filename
                )
                pdf_path = os.path.abspath(filename)
                msg_pdf = f"\n📄 **¡PDF GENERADO!**\nHe creado un PDF formal con tu cotización. Te lo enviaré por WhatsApp junto con el detalle."
                logger.info(f"✅ PDF Generado: {pdf_path}")
            except Exception as e:
                logger.error(f"❌ Error generando PDF: {e}")
            
            # Mensaje personalizado según servicios detectados
            servicios_text = ", ".join(servicios_cotizar)
            
            return f"""✅ ¡Perfecto! Aquí está tu cotización lista para enviar:

📱 **CLICK AQUÍ PARA ABRIR WHATSAPP:**
{whatsapp_link}

📋 La cotización incluye:
• **Servicios solicitados:** {servicios_text}
• Precios detallados
• Descuentos aplicables
• Tiempos de entrega
• Términos y condiciones
{msg_pdf}

💡 El mensaje ya está listo - solo presiona ENVIAR en WhatsApp y te responderemos al instante con tu cotización personalizada.

¿Necesitas agregar otro servicio? Dime cuál y actualizo la cotización 🎯"""
    
    def _generar_enlace_whatsapp_cotizacion(self, nombre="Cliente", servicios=[], mensaje=""):
        """Genera enlace de WhatsApp para cotización usando el generador profesional"""
        try:
            from urllib.parse import quote
            whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
            
            # Si se especificaron servicios, generar cotización profesional
            if servicios:
                try:
                    from generador_cotizacion import GeneradorCotizacion
                    generador = GeneradorCotizacion()
                    
                    # Formatear servicios
                    servicios_formateados = []
                    for servicio in servicios:
                        if isinstance(servicio, str):
                            servicios_formateados.append({
                                'nombre': servicio,
                                'cantidad': 1,
                                'urgente': False
                            })
                        else:
                            servicios_formateados.append(servicio)
                    
                    # Generar cotización completa
                    cotizacion = generador.generar_cotizacion_whatsapp(
                        cliente_nombre=nombre,
                        servicios_solicitados=servicios_formateados,
                        ubicacion="",
                        es_primer_servicio=True,
                        notas_adicionales=mensaje
                    )
                    
                    mensaje_encoded = quote(cotizacion)
                    whatsapp_link = f"https://wa.me/{whatsapp}?text={mensaje_encoded}"
                    return whatsapp_link
                    
                except ImportError as e:
                    logger.warning(f"No se pudo importar generador_cotizacion: {e}")
                    # Fallback al mensaje simple
                    pass
            
            # Mensaje simple si no hay servicios o falla el generador
            mensaje_base = f"🏢 *SOLICITUD DE COTIZACIÓN - GEO CENTER LAB*\n\n👤 *Cliente:* {nombre}\n\n"
            if mensaje:
                mensaje_base += f"💬 *Consulta:* {mensaje}\n\n"
            mensaje_base += "✅ Por favor, envíeme una cotización detallada."
            
            mensaje_encoded = quote(mensaje_base)
            whatsapp_link = f"https://wa.me/{whatsapp}?text={mensaje_encoded}"
            
            return whatsapp_link
        except Exception as e:
            logger.error(f"❌ Error generando enlace WhatsApp: {e}")
            whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
            return f"https://wa.me/{whatsapp}"
    
    def _manejar_seleccion_numero(self, num):
        """Maneja selección numérica del menú"""
        # Menú principal (1-5)
        if self.ultima_opcion is None:
            return self._menu_principal(num)
        
        # Submenús
        return self._submenu_opciones(num)
    
    def _menu_principal(self, num):
        """Menú principal con 5 opciones"""
        menus = {
            1: ('laboratorio', self._menu_laboratorio()),
            2: ('topografia', self._menu_topografia()),
            3: ('perforacion', self._menu_perforacion()),
            4: ('cotizacion', self._menu_cotizacion()),
            5: ('contacto', self._menu_contacto())
        }
        
        if num in menus:
            opcion, respuesta = menus[num]
            # Para cotizacion y contacto, no hay submenu
            if num in [4, 5]:
                self.solicito_contacto = True
                self.ultima_opcion = None
            else:
                self.ultima_opcion = opcion
            return respuesta
        
        return "❌ Opción no válida. Escribe 1-5 para continuar 👇"
    
    def _submenu_opciones(self, num):
        """Maneja submenús según última opción"""
        opciones = {
            'laboratorio': {
                1: "🔬 MECÁNICA DE SUELOS: Ensayos granulométricos, límites Atterberg, CBR, Proctor. ¿Cuál necesitas? Déjanos tu email para enviarte precios 📧",
                2: "🏗️ MATERIALES: Concreto, agregados, ladrillos. Control de calidad garantizado. ¿Tu proyecto es en Huaraz? Comparte ubicación para cotización 📍",
                3: "🧪 ANÁLISIS QUÍMICOS: pH, sales solubles, contaminación. Ideal para estudios de impacto ambiental. ¿Necesitas certificación? 📋",
                4: "⚗️ ENSAYOS ESPECIALES: Triaxial, consolidación, permeabilidad. Para proyectos complejos. ¿Qué profundidad necesitas? 🎯"
            },
            'topografia': {
                1: "📍 LEVANTAMIENTO: Estación total + GPS + planos CAD. OFERTA: Primera visita GRATIS en Huaraz. ¿Cuándo necesitas? 📅",
                2: "🚁 FOTOGRAMETRÍA: Drones profesionales con cámara 4K. Modelos 3D y cálculo de volúmenes exactos. ¿Quieres ver demo? 🎥",
                3: "📐 REPLANTEO: Precisión milimétrica para tu obra. Incluye BMs y ejes de construcción. ¿Cuándo inicias? ⚡",
                4: "📊 VOLÚMENES: Cálculo exacto de movimiento de tierras. Software especializado. Para presupuestos precisos. 💰"
            },
            'perforacion': {
                1: "💎 DIAMANTINA: Hasta 50m profundidad. Diámetros NX, BX, AX. Muestras inalteradas. Para edificaciones altas. ¿Altura del proyecto? 🏢",
                2: "🕳️ CALICATAS: Excavación manual hasta 4m. Descripción estratigráfica detallada. Para viviendas y obras menores. ¿Superficie? 🏠",
                3: "🔨 SPT: Ensayo de penetración estándar. Norma técnica peruana. Resultados en 24h. ¿Cuántos puntos? 📍",
                4: "⚡ IN-SITU: Densidad de campo, CBR, placa de carga. Directamente en terreno. Sin esperar muestras. Ideal para control de obra ✅"
            }
        }
        
        # Verificar si existe la opción en el menú actual
        if self.ultima_opcion and self.ultima_opcion in opciones:
            if num in opciones[self.ultima_opcion]:
                respuesta = opciones[self.ultima_opcion][num]
                self.solicito_contacto = True
                self.ultima_opcion = None
                return respuesta + "\n\n💰 Para cotización exacta, necesitamos tu 📧 email o 📱 WhatsApp 👇"
        
        # Si no es válido, dar opciones
        return """❌ Opción no válida.

Escribe 1-4 para elegir un servicio específico
O escríbeme tu consulta y te ayudo 💬"""
    
    def _menu_laboratorio(self):
        return """🔬 LABORATORIO - ¿Qué ensayo necesitas?

1. Mecánica de suelos básicos
2. Materiales de construcción
3. Análisis químicos
4. Ensayos especiales avanzados

Escribe el número 👇"""
    
    def _menu_topografia(self):
        return """📐 TOPOGRAFÍA - ¿Qué servicio?

1. Levantamiento completo
2. Fotogrametría con drones
3. Replanteo de obra
4. Cálculo de volúmenes

Escribe el número 👇"""
    
    def _menu_perforacion(self):
        return """⚙️ PERFORACIÓN - ¿Qué tipo?

1. Perforación diamantina
2. Calicatas (pozos)
3. Muestreo SPT
4. Ensayos in-situ

Escribe el número 👇"""
    
    def _menu_cotizacion(self):
        self.solicito_contacto = True
        return """💰 COTIZACIÓN EXPRESS

Para enviarte propuesta necesito:
✓ Servicio específico
✓ Ubicación del proyecto
✓ Alcance aproximado

¿A dónde enviamos tu cotización?

📧 Email o 📱 WhatsApp:
(Ej: juan@empresa.com o 932203111)

Te respondemos en 30 min ⏰"""
    
    def _menu_contacto(self):
        whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
        tel = self.datos_empresa['telefono'][0]
        
        return f"""📍 CONTÁCTANOS AHORA

📱 WhatsApp: https://wa.me/{whatsapp}
☎️ Teléfono: {tel}
📧 Email: {self.datos_empresa['email']}
🗺️ Dirección: {self.datos_empresa['ubicacion']}

🕐 Horario: Lun-Vie 8am-10pm, Sáb 8am-12pm

¿Tienes un proyecto en mente? Cuéntanos qué necesitas 💬"""
    
    def _generar_respuesta_intencion(self, pregunta_lower):
        """Genera respuestas según intención detectada"""
        # Servicios
        if any(word in pregunta_lower for word in ['servicio', 'ofrece', 'hacen', 'tienen', 'hola', 'buenos', 'buenas']):
            self.ultima_opcion = None
            return """¡Hola! 👋 Somos GEO CENTER LAB, especialistas en:

1. 🔬 Laboratorio de suelos y Agua
2. 📐 Topografía y drones
3. ⚙️ Perforación diamantina
4. 💰 Cotización personalizada
5. 📞 Contacto directo

¿Qué necesitas? Escribe el número 👇"""
        
        # Precios (nunca dar cifras exactas)
        if any(word in pregunta_lower for word in ['precio', 'costo', 'cuanto', 'cotiza', 'tarifa']):
            self.solicito_contacto = True
            
            # Detectar si menciona WhatsApp
            if any(word in pregunta_lower for word in ['whatsapp', 'whats app', 'wsp', 'wpp']):
                whatsapp_link = self._generar_enlace_whatsapp_cotizacion()
                whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
                return f"""✅ ¡Perfecto! Te envío la cotización por WhatsApp.

📱 **Click aquí para abrir WhatsApp:**
{whatsapp_link}

📋 El mensaje ya está listo, solo dale ENVIAR y te responderemos al instante con:
• Precios personalizados
• Descuentos disponibles  
• Plazo de entrega

💬 ¿Qué servicio necesitas específicamente?"""
            
            # Respuesta general de cotización
            return """💰 PRECIOS PERSONALIZADOS

Cada proyecto es único. Depende de:
• Tipo de ensayo/servicio
• Cantidad de muestras
• Ubicación
• Urgencia

🎁 Te garantizamos:
✓ Mejor precio de la región
✓ 10% descuento primer servicio
✓ Paquetes corporativos

¿A dónde enviamos tu cotización detallada?

Email o WhatsApp 👇"""
        
        # Horario
        if any(word in pregunta_lower for word in ['horario', 'hora', 'abierto', 'atienden']):
            return f"""🕐 HORARIO DE ATENCIÓN

Lunes a Viernes: 8:00am - 10:00pm
Sábados: 8:00am - 12:00pm
Domingos: Cerrado

📱 WhatsApp 24/7: {self.datos_empresa['redes_sociales']['whatsapp']}

¿Necesitas agendar cita fuera de horario? Déjanos tu número 📞"""
        
        # Proyectos
        if any(word in pregunta_lower for word in ['proyecto', 'experiencia', 'obra', 'trabajo', 'referencia']):
            proyectos_list = '\n• '.join([p['nombre'] for p in self.proyectos])
            return f"""🏗️ PROYECTOS REALIZADOS EN HUARAZ

• {proyectos_list}

Total: {len(self.proyectos)} proyectos entregados con éxito

¿Qué tipo de proyecto tienes? Comparte detalles para mostrarte casos similares 📊"""
        
        # Despedida
        if any(word in pregunta_lower for word in ['gracias', 'adios', 'chao', 'hasta luego']):
            if self.interacciones_count >= 3 and not self.solicito_contacto:
                self.solicito_contacto = True
                return """😊 ¡Gracias por contactarnos!

🎁 Antes de irte... ¿Te gustaría recibir GRATIS?

✅ Catálogo digital completo
✅ Lista de precios 2024
✅ 10% descuento primera vez

¿A dónde te lo enviamos? 📧 o 📱"""
            
            return f"""👋 ¡Gracias por tu interés!

¿Te ayudamos con algo más?

Si no, recuerda:
📱 WhatsApp: {self.datos_empresa['redes_sociales']['whatsapp']}
🌐 Siempre a tu servicio"""
        
        # Respuesta por defecto (después de 4 interacciones, pedir contacto)
        if self.interacciones_count >= 4 and not self.solicito_contacto:
            self.solicito_contacto = True
            return """🤔 Veo que estás explorando nuestras opciones...

🎯 Para asesorarte MEJOR, necesito entender tu proyecto.

¿Qué estás construyendo/revisando?
🏠 Vivienda | 🏢 Edificio | 🛣️ Carretera | 💧 Proyecto hidráulico

Y tu 📧 email o 📱 número para enviarte info específica:"""
        
        return """👋 ¿En qué te puedo ayudar?

1. 🔬 Ver servicios de laboratorio
2. 📐 Conocer topografía y drones
3. ⚙️ Perforación geotécnica
4. 💰 Cotización personalizada
5. 📞 Contacto directo

Escribe el número o tu pregunta 💬"""
    
    def _actualizar_historial(self, pregunta, respuesta):
        """Actualiza historial de conversación"""
        self.historial_conversacion.append({
            "role": "user",
            "content": pregunta,
            "timestamp": datetime.now().isoformat()
        })
        self.historial_conversacion.append({
            "role": "assistant",
            "content": respuesta,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener historial limitado (últimos 10 intercambios)
        if len(self.historial_conversacion) > 20:
            self.historial_conversacion = self.historial_conversacion[-20:]
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas internas"""
        logger.info(f"📊 Servicios cargados: {len(self.servicios)} | Proyectos: {len(self.proyectos)} | Interacciones: {self.interacciones_count}")
    
    def limpiar_historial(self):
        """Limpia historial y contexto"""
        self.historial_conversacion = []
        self.contexto_usuario = {}
        self.interacciones_count = 0
        self.solicito_contacto = False
        logger.info("🗑️ Historial y contexto limpiados")
    
    def exportar_conversacion(self, archivo="conversacion.json"):
        """Exporta conversación completa"""
        try:
            data = {
                "fecha": datetime.now().isoformat(),
                "datos_empresa": self.datos_empresa,
                "estadisticas": {
                    "interacciones": self.interacciones_count,
                    "contactos_solicitados": self.solicito_contacto,
                    "servicios_cargados": len(self.servicios)
                },
                "historial": self.historial_conversacion
            }
            
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Exportado a {archivo}")
            return True
        except Exception as e:
            logger.error(f"❌ Error exportando: {e}")
            return False
    
    def estadisticas(self):
        """Muestra estadísticas detalladas"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DEL AGENTE GEO CENTER LAB")
        print("="*60)
        print(f"✅ Servicios cargados: {len(self.servicios)}")
        print(f"🏗️ Proyectos cargados: {len(self.proyectos)}")
        print(f"💬 Interacciones totales: {self.interacciones_count}")
        print(f"👤 Contactos solicitados: {'Sí' if self.solicito_contacto else 'No'}")
        print(f"📧 Contactos guardados: {len(self.contexto_usuario)}")
        print(f"📝 Registros en historial: {len(self.historial_conversacion) // 2}")
        print(f"🌐 URL configurada: {self.url_pagina}")
        print(f"🤖 Modo: {'Demo' if self.modo_demo else 'IA Activo'}")
        print("="*60)
        print(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Función principal con mejor UI"""
    print("\n" + "="*60)
    print("🤖 AGENTE IA - GEO CENTER LAB")
    print("Asistente Virtual de Laboratorio Geotécnico")
    print("="*60)
    
    # Preguntar por URL personalizada
    url_input = input("🌐 ¿Tienes URL específica del sitio web? (Enter para usar .env o default): ").strip()
    
    agente = AgenteGEOCENTERLAB(url_personalizada=url_input if url_input else None)
    agente.estadisticas()
    
    print("\n" + "="*60)
    print("💡 MODO INTERACTIVO")
    print("Comandos especiales: stats | limpiar | guardar | salir")
    print("="*60)
    
    while True:
        try:
            pregunta = input("\n👤 Tú: ").strip()
            
            if not pregunta:
                continue
            
            # Comandos especiales
            if pregunta.lower() == 'salir':
                print("\n👋 ¡Gracias por usar GEO CENTER LAB Assistant!")
                agente.exportar_conversacion()
                break
            
            elif pregunta.lower() == 'limpiar':
                agente.limpiar_historial()
                print("🗑️ Conversación reiniciada")
                continue
            
            elif pregunta.lower() == 'stats':
                agente.estadisticas()
                continue
            
            elif pregunta.lower() == 'guardar':
                agente.exportar_conversacion()
                continue
            
            # Procesar consulta
            respuesta = agente.consultar(pregunta)
            print(f"\n🤖 Assistant: {respuesta}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por usuario")
            break
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            print(f"\n⚠️ Error: {e}")

if __name__ == "__main__":
    main()