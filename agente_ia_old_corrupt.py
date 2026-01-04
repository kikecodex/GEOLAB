import os
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import re
import logging
from urllib.parse import urljoin

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
                'titulo': 'Ensayos de Identificación y Físicos',
                'items': [
                    {'nombre': 'Análisis granulométrico por tamizado e hidrómetro', 'descripcion': 'Distribución de partículas (ASTM D422)'},
                    {'nombre': 'Límites de Atterberg', 'descripcion': 'Límite líquido, plástico y contracción (ASTM D4318)'},
                    {'nombre': 'Contenido de humedad', 'descripcion': 'Humedad natural del suelo (ASTM D2216)'},
                    {'nombre': 'Gravedad específica', 'descripcion': 'Densidad de sólidos (ASTM D854)'},
                    {'nombre': 'Peso volumétrico', 'descripcion': 'Densidad natural y seca'}
                ]
            },
            {
                'titulo': 'Ensayos de Resistencia y Mecánicos',
                'items': [
                    {'nombre': 'CBR (California Bearing Ratio)', 'descripcion': 'Capacidad portante para pavimentos (ASTM D1883)'},
                    {'nombre': 'Proctor Estándar y Modificado', 'descripcion': 'Compactación de suelos (ASTM D698/D1557)'},
                    {'nombre': 'Corte Directo', 'descripcion': 'Ángulo de fricción y cohesión (ASTM D3080)'},
                    {'nombre': 'Compresión No Confinada', 'descripcion': 'Resistencia a la compresión simple (ASTM D2166)'},
                    {'nombre': 'Consolidación Unidimensional', 'descripcion': 'Asentamientos y compresibilidad (ASTM D2435)'},
                    {'nombre': 'Triaxial (UU, CU, CD)', 'descripcion': 'Parámetros de resistencia avanzados (ASTM D2850)'},
                    {'nombre': 'Expansión (Lambe/Hinchamiento)', 'descripcion': 'Potencial de cambio de volumen'}
                ]
            }
        ]
    },
    {
        'categoria': 'Geotecnia y Geofísica',
        'subsecciones': [
            {
                'titulo': 'Ensayos de Campo',
                'items': [
                    {'nombre': 'SPT (Standard Penetration Test)', 'descripcion': 'Resistencia a la penetración (ASTM D1586)'},
                    {'nombre': 'DPL (Dinamic Probing Light)', 'descripcion': 'Sondeo dinámico ligero'},
                    {'nombre': 'Cono de Arena', 'descripcion': 'Densidad de campo (ASTM D1556)'},
                    {'nombre': 'Placa de Carga', 'descripcion': 'Módulo de reacción de subrasante (ASTM D1194)'},
                    {'nombre': 'Vane Test', 'descripcion': 'Corte en veleta de campo'}
                ]
            },
            {
                'titulo': 'Geofísica y Refracción Sísmica',
                'items': [
                    {'nombre': 'Refracción Sísmica', 'descripcion': 'Perfil de velocidades de onda P (ASTM D5777)'},
                    {'nombre': 'MASW (Análisis Multicanal)', 'descripcion': 'Perfil de velocidades de onda S (Vs30)'},
                    {'nombre': 'Sondajes Eléctricos Verticales (SEV)', 'descripcion': 'Resistividad del suelo'},
                    {'nombre': 'Tomografía Eléctrica', 'descripcion': 'Imágenes 2D del subsuelo'},
                    {'nombre': 'Estudios de Ripabilidad', 'descripcion': 'Facilidad de excavación'}
                ]
            }
        ]
    },
    {
        'categoria': 'Hidráulica e Hidrología',
        'subsecciones': [
            {
                'titulo': 'Ensayos Hidráulicos',
                'items': [
                    {'nombre': 'Permeabilidad (Carga Constante/Variable)', 'descripcion': 'Conductividad hidráulica (ASTM D2434)'},
                    {'nombre': 'Infiltración', 'descripcion': 'Pruebas de infiltración en campo'},
                    {'nombre': 'Pruebas Hidrostáticas', 'descripcion': 'Estanqueidad en tuberías y tanques'},
                    {'nombre': 'Aforo de Caudales', 'descripcion': 'Medición de flujo en canales y ríos'}
                ]
            },
            {
                'titulo': 'Estudios',
                'items': [
                    {'nombre': 'Estudios Hidrológicos', 'descripcion': 'Cálculo de avenidas y diseño de drenaje'},
                    {'nombre': 'Modelación Hidráulica', 'descripcion': 'Simulación de flujo (Hec-RAS, Iber)'},
                    {'nombre': 'Diseño de Presas y Canales', 'descripcion': 'Ingeniería hidráulica'}
                ]
            }
        ]
    },
    {
        'categoria': 'Perforación Diamantina',
        'subsecciones': [
            {
                'titulo': 'Servicios de Perforación',
                'items': [
                    {'nombre': 'Perforación Diamantina (Diamond Drilling)', 'descripcion': 'Recuperación de núcleos de roca (Core)'},
                    {'nombre': 'Diámetros BQ, NQ, HQ, PQ', 'descripcion': 'Diferentes diámetros de testigo'},
                    {'nombre': 'Perforación Geotécnica', 'descripcion': 'Para estudios de cimentación y taludes'},
                    {'nombre': 'Instalación de Piezómetros', 'descripcion': 'Monitoreo de nivel freático'},
                    {'nombre': 'Orientación de Testigos', 'descripcion': 'Análisis estructural'}
                ]
            }
        ]
    },
    {
        'categoria': 'Análisis de Materiales',
        'subsecciones': [
            {
                'titulo': 'Concreto y Agregados',
                'items': [
                    {'nombre': 'Resistencia a compresión (Probetas)', 'descripcion': 'Rotura de cilindros de concreto (ASTM C39)'},
                    {'nombre': 'Diseño de Mezclas', 'descripcion': 'Dosificación de concreto'},
                    {'nombre': 'Granulometría de Agregados', 'descripcion': 'Análisis de arena y piedra'},
                    {'nombre': 'Abrasión Los Ángeles', 'descripcion': 'Desgaste de agregados (ASTM C131)'},
                    {'nombre': 'Sanidad (Sulfatos)', 'descripcion': 'Durabilidad de agregados'}
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
                    {'nombre': 'Levantamiento Topográfico', 'descripcion': 'Estación Total y GPS Diferencial'},
                    {'nombre': 'Fotogrametría con Drones', 'descripcion': 'Ortofotos y Modelos Digitales (DEM)'},
                    {'nombre': 'Geodesia Satelital', 'descripcion': 'Puntos de control geodésico (IGN)'},
                    {'nombre': 'Batimetría', 'descripcion': 'Topografía de fondo marino/lacustre'}
                ]
            }
        ]
    }
]

PROYECTOS_REALES = [
    {'nombre': 'Estudio Geotécnico Edificio Residencial Huaraz', 'descripcion': 'Mecánica de suelos con fines de cimentación, 3 calicatas y ensayos estándar.', 'imagen': ''},
    {'nombre': 'Perforación Diamantina Mina Pierina', 'descripcion': '500m de perforación HQ para exploración geológica.', 'imagen': ''},
    {'nombre': 'Estudio Hidrológico Río Santa', 'descripcion': 'Modelación hidráulica para defensa ribereña.', 'imagen': ''},
    {'nombre': 'Carretera Carhuaz - Chacas', 'descripcion': 'Control de calidad de compactación y asfalto.', 'imagen': ''},
    {'nombre': 'Refracción Sísmica Parque Industrial', 'descripcion': 'Determinación de Vs30 y perfil estratigráfico.', 'imagen': ''}
]

class AgenteGEOCENTERLAB:
    def __init__(self, respuesta_extendida=False, url_personalizada=None):
        """Inicializa el agente con soporte para URL personalizada"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        # FORZAR modo demo para usar el flujo conversacional mejorado
        self.modo_demo = True  # Usar siempre el flujo real optimizado

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("🤖 Modo híbrido: Flujo real + OpenAI disponible")
        else:
            self.client = None
            logger.warning("⚠️ MODO DEMO: No se encontró API Key de OpenAI")
            logger.warning("   El fallback a OpenAI NO funcionará. Solo menú real disponible.")
        
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
            for cat in ['Laboratorio', 'Geotecnia', 'Hidráulica', 'Perforación', 'Topografía']:
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
            # Palabras técnicas que deben ir directo a OpenAI
            palabras_tecnicas = [
                'cbr', 'triaxial', 'proctor', 'atterberg', 'consolidación', 'consolidacion', 'permeabilidad',
                'refracción', 'refraccion', 'sismica', 'sísmica', 'masw', 'sev', 'tomografía', 'tomografia',
                'curvas de nivel', 'ensayo directo', 'límites', 'limites', 'granulometría', 'granulometria',
                'compactación', 'compactacion', 'ph', 'sales', 'contaminación', 'contaminacion',
                'mecánica de suelos', 'mecanica de suelos', 'spt', 'dpl', 'cono de arena', 'placa de carga',
                'muestreo', 'test-pit', 'calicata', 'diamantina', 'bq', 'nq', 'hq', 'pq', 'testigo', 'nucleo',
                'hidráulica', 'hidraulica', 'hidrología', 'hidrologia', 'caudal', 'aforo', 'presa', 'canal',
                'replanteo', 'fotogrametría', 'fotogrametria', 'drones', 'volúmenes', 'volumenes',
                'ensayo', 'ensayos', 'certificación', 'certificacion', 'probeta', 'cilindro', 'compresión', 'compresion',
                'abrasión', 'abrasion', 'humedad', 'contenido de humedad', 'resistencia', 'agregados', 'concreto',
                'norma', 'astm', 'ntp', 'mallas', 'tamices', 'laboratorio', 'geotecnia', 'geología', 'geologia'
            ]
            
            # Si detecta palabra técnica, intenta OpenAI primero si está disponible
            if any(pal in pregunta_lower for pal in palabras_tecnicas):
                if self.client:
                    logger.info("🤖 Palabra técnica detectada, usando OpenAI directamente...")
                    return self._consultar_openai(pregunta)
            
            # Intentar respuesta por menú/lógica local
            respuesta_real = self._respuesta_demo_mejorada(pregunta)
            
            # Detectar si la respuesta es genérica/menu para fallback a OpenAI
            if self._es_respuesta_generica(respuesta_real):
                if self.client:
                    logger.info("🤖 Respuesta genérica detectada, usando OpenAI como fallback...")
                    respuesta_ia = self._consultar_openai(pregunta)
                    return respuesta_ia
                else:
                    logger.warning("❌ No hay API Key, solo menú real disponible.")
                    return respuesta_real + "\n\n⚠️ El modo IA avanzado no está disponible por falta de API Key."
            else:
                return respuesta_real

        # Modo IA directo (OpenAI) - Código legacy si modo_demo fuera False
        return self._consultar_openai(pregunta)

    def _es_respuesta_generica(self, respuesta):
        """Detecta si la respuesta es genérica/menu para activar fallback a OpenAI"""
        patrones_genericos = [
            "¿En qué te puedo ayudar?",
            "Opción no válida",
            "opción no válida",
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

    def _consultar_openai(self, pregunta):
        """Consulta a OpenAI directamente como fallback"""
        try:
            contexto = self._construir_contexto_inteligente()
            mensajes = [
                {
                    "role": "system",
                    "content": f"""Eres el asistente virtual senior de GEO CENTER LAB. Tu objetivo es convertir visitantes en clientes. Sé natural, breve y útil.
                    
                    Si te preguntan por servicios específicos, usa la información detallada del contexto.
                    Si te piden buscar en la web, simula que buscas y responde con la información técnica que tienes en tu base de conocimientos (que es muy completa).
                    
                    {contexto}"""
                },
                {
                    "role": "user",
                    "content": pregunta
                }
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=mensajes,
                temperature=0.5,
                max_tokens=400
            )
            respuesta = response.choices[0].message.content
            self._actualizar_historial(pregunta, respuesta)
            logger.info("✅ Respuesta OpenAI fallback generada exitosamente")
            return respuesta
        except Exception as e:
            logger.error(f"❌ Error en fallback OpenAI: {e}")
            return f"⚠️ Hubo un problema con la IA. Llámanos directamente: {self.datos_empresa.get('telefono', ['932203111'])[0]} 📞"
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
📧 Email o WhatsApp 👇"""
        
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

¿Te gustaría que un ingeniero te asesore GRATIS?

Solo déjanos tu WhatsApp o Email y te escribimos 👇"""
        
        return """¡Hola! 👋 Soy el asistente virtual de GEO CENTER LAB.

Puedo ayudarte con:
1. 🔬 Ensayos de laboratorio
2. 📐 Topografía
3. ⚙️ Perforación
4. 💰 Cotizaciones

¿Qué necesitas? Escribe el número 👇"""

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