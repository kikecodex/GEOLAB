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
                'titulo': 'Ensayos de Resistencia',
                'items': [
                    {'nombre': 'CBR (California Bearing Ratio)', 'descripcion': 'Resistencia para pavimentos (ASTM D1883)'},
                    {'nombre': 'Proctor Modificado', 'descripcion': 'Compactación y densidad máxima (ASTM D1557)'},
                    {'nombre': 'Proctor Estándar', 'descripcion': 'Densidad óptima (ASTM D698)'},
                    {'nombre': 'Corte Directo', 'descripcion': 'Resistencia al corte (ASTM D3080)'},
                    {'nombre': 'Compresión No Confinada', 'descripcion': 'Resistencia simple (ASTM D2166)'}
                ]
            },
            {
                'titulo': 'Ensayos Mecánicos Avanzados',
                'items': [
                    {'nombre': 'Ensayo Triaxial (UU, CU, CD)', 'descripcion': 'Parámetros de resistencia

 (ASTM D2850)'},
                    {'nombre': 'Consolidación', 'descripcion': 'Compresibilidad del suelo (ASTM D2435)'},
                    {'nombre': 'Permeabilidad', 'descripcion': 'Conductividad hidráulica (ASTM D2434)'},
                    {'nombre': 'Expansión', 'descripcion': 'Potencial de expansión (ASTM D4546)'}
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
                    {'nombre': 'SPT (Standard Penetration Test)', 'descripcion': 'Compacidad y resistencia in situ'},
                    {'nombre': 'DPL (Dynamic Probe Light)', 'descripcion': 'Penetración dinámica ligera'},
                    {'nombre': 'Cono de Arena', 'descripcion': 'Densidad de campo (ASTM D1556)'},
                    {'nombre': 'Placa de Carga', 'descripcion': 'Módulo de reacción de subrasante'},
                    {'nombre': 'Vane Test', 'descripcion': 'Resistencia al corte de suelos cohesivos'}
                ]
            },
            {
                'titulo': 'Estudios Geofísicos',
                'items': [
                    {'nombre': 'Refracción Sísmica', 'descripcion': 'Estratigrafía y ripabilidad'},
                    {'nombre': 'MASW (Análisis Vs30)', 'descripcion': 'Clasificación sísmica del suelo'},
                    {'nombre': 'SEV (Sondeo Eléctrico Vertical)', 'descripcion': 'Estructura del subsuelo'},
                    {'nombre': 'Tomografía Eléctrica', 'descripcion': 'Anomalías y estructuras 2D/3D'},
                    {'nombre': 'Estudios de Ripabilidad', 'descripcion': 'Excavabilidad de rocas'}
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
                    {'nombre': 'Permeabilidad de campo (Lefranc, Lugeon)', 'descripcion': 'Conductividad hidráulica in situ'},
                    {'nombre': 'Pruebas de infiltración', 'descripcion': 'Capacidad de absorción del suelo'},
                    {'nombre': 'Pruebas hidrostáticas en tuberías', 'descripcion': 'Control de calidad de redes'},
                    {'nombre': 'Aforos de caudales', 'descripcion': 'Medición de flujo en canales y ríos'}
                ]
            },
            {
                'titulo': 'Estudios Hidrológicos',
                'items': [
                    {'nombre': 'Análisis de cuencas hidrográficas', 'descripcion': 'Caracterización hidrológica'},
                    {'nombre': 'Modelación hidráulica (Hec-RAS, SWMM)', 'descripcion': 'Simulación de flujos'},
                    {'nombre': 'Diseño de sistemas de drenaje', 'descripcion': 'Drenaje pluvial y sanitario'},
                    {'nombre': 'Diseño de presas y canales', 'descripcion': 'Ingeniería de detalle hidráulico'}
                ]
            }
        ]
    },
    {
        'categoria': 'Perforación Diamantina',
        'subsecciones': [
            {
                'titulo': 'Perforación Geotécnica',
                'items': [
                    {'nombre': 'Perforación Diamantina Core BQ, NQ, HQ, PQ', 'descripcion': 'Recuperación de testigos hasta 500m'},
                    {'nombre': 'Instalación de piezómetros', 'descripcion': 'Monitoreo de nivel freático'},
                    {'nombre': 'Instalación de inclinómetros', 'descripcion': 'Control de deformaciones'},
                    {'nombre': 'Muestras inalteradas', 'descripcion': 'Recuperación de muestras intactas'}
                ]
            },
            {
                'titulo': 'Aplicaciones Especializadas',
                'items': [
                    {'nombre': 'Exploración minera', 'descripcion': 'Reconocimiento de reservas'},
                    {'nombre': 'Perforación en interior mina', 'descripcion': 'Servicio subterráneo'},
                    {'nombre': 'Pozos de agua subterránea', 'descripcion': 'Perforación y desarrollo de pozos'},
                    {'nombre': 'Mantenimiento de pozos', 'descripcion': 'Limpieza y rehabilitación'}
                ]
            }
        ]
    },
    {
        'categoria': 'Análisis de Materiales',
        'subsecciones': [
            {
                'titulo': 'Concreto',
                'items': [
                    {'nombre': 'Resistencia a compresión de cilindros', 'descripcion': 'Control de calidad (ASTM C39)'},
                    {'nombre': 'Diseño de mezclas de concreto', 'descripcion': 'Dosificaciones optimizadas'},
                    {'nombre': 'Esclerometría', 'descripcion': 'Dureza superficial no destructiva'},
                    {'nombre': 'Resistencia a flexión', 'descripcion': 'Vigas y losas (ASTM C78)'}
                ]
            },
            {
                'titulo': 'Agregados',
                'items': [
                    {'nombre': 'Granulometría de agregados', 'descripcion': 'Distribución de tamaños (ASTM C136)'},
                    {'nombre': 'Abrasión Los Ángeles', 'descripcion': 'Resistencia al desgaste (ASTM C131)'},
                    {'nombre': 'Peso específico y absorción', 'descripcion': 'Propiedades físicas (ASTM C127/C128)'},
                    {'nombre': 'Ensayo de sanidad', 'descripcion': 'Durabilidad química (ASTM C88)'}
                ]
            }
        ]
    },
    {
        'categoria': 'Topografía y Geodesia',
        'subsecciones': [
            {
                'titulo': 'Levantamientos Topográficos',
                'items': [
                    {'nombre': 'Levantamiento con estación total', 'descripcion': 'Precisión milimétrica'},
                    {'nombre': 'GPS Diferencial', 'descripcion': 'Georreferenciación de alta precisión'},
                    {'nombre': 'Replanteo de obra', 'descripcion': 'Control de ejes y niveles'},
                    {'nombre': 'Cálculo de volúmenes', 'descripcion': 'Movimiento de tierras'}
                ]
            },
            {
                'titulo': 'Tecnologías Avanzadas',
                'items': [
                    {'nombre': 'Fotogrametría con drones', 'descripcion': 'Ortofotos y curvas de nivel'},
                    {'nombre': 'Geodesia satelital', 'descripcion': 'Redes geodésicas'},
                    {'nombre': 'Batimetría', 'descripcion': 'Levantamiento de fondos acuáticos'},
                    {'nombre': 'Modelos digitales de terreno', 'descripcion': 'MDT y MDS de alta resolución'}
                ]
            }
        ]
    }
]

PROYECTOS_REALES = [
    {'nombre': 'Estudio Geotécnico Edificio Residencial Huaraz', 'descripcion': 'Análisis completo de suelos y diseño de cimentación'},
    {'nombre': 'Control de Calidad Carretera Huaraz-Caraz', 'descripcion': 'Ensayos de laboratorio y campo para pavimentación'},
    {'nombre': 'Diseño de Presa Proyecto Chingas', 'descripcion': 'Estudios geotécnicos e hidrológicos'},
    {'nombre': 'Perforación Diamantina Mina Pierina', 'descripcion': 'Recuperación de testigos para exploración'},
    {'nombre': 'Estudio Hidrológico Río Santa', 'descripcion': 'Modelación hidráulica y análisis de caudales'},
    {'nombre': 'Refracción Sísmica Parque Industrial Huaraz', 'descripcion': 'Caracterización geofísica del terreno'},
    {'nombre': 'Topografía con Drones - Proyecto Inmobiliario Monterrey', 'descripcion': 'Levantamiento aerofotogramétrico'},
    {'nombre': 'Análisis de Suelos para Planta de Tratamiento', 'descripcion': 'Ensayos químicos y mecánicos'},
    {'nombre': 'Instalación de Piezómetros - Proyecto Minero', 'descripcion': 'Monitoreo de aguas subterráneas'},
    {'nombre': 'Estudio de Estabilidad de Taludes - Carretera Pativilca', 'descripcion': 'Análisis geotécnico y diseño de estabilización'},
    {'nombre': 'Control de Compactación Aeropuerto Anta', 'descripcion': 'Ensayos de densidad de campo'},
    {'nombre': 'Análisis de Agua Potable - Municipalidades de Ancash', 'descripcion': 'Parámetros físico-químicos y bacteriológicos'},
    {'nombre': 'Diseño de Mezclas Concreto f\'c=280kg/cm² - Obra Múltiple', 'descripcion': 'Dosificaciones y control de calidad'}
]
