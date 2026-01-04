# -*- coding: utf-8 -*-
"""
Catálogo de Precios - GEO CENTER LAB
Precios referenciales para cotizaciones automáticas
"""

# Precios en Soles (S/.)
# Nota: Estos son precios BASE. Pueden variar según cantidad, urgencia y ubicación

PRECIOS_SERVICIOS = {
    # LABORATORIO DE MECÁNICA DE SUELOS
    "Análisis granulométrico": {
        "precio_base": 45.00,
        "unidad": "por muestra",
        "tiempo": "2-3 días",
        "descuento_volumen": 0.10  # 10% descuento en 10+ muestras
    },
    "Límites de Atterberg": {
        "precio_base": 35.00,
        "unidad": "por muestra",
        "tiempo": "2-3 días",
        "descuento_volumen": 0.10
    },
    "Contenido de humedad": {
        "precio_base": 20.00,
        "unidad": "por muestra",
        "tiempo": "1-2 días",
        "descuento_volumen": 0.15
    },
    "CBR (California Bearing Ratio)": {
        "precio_base": 280.00,
        "unidad": "por ensayo completo",
        "tiempo": "5-7 días",
        "descuento_volumen": 0.05
    },
    "Proctor modificado": {
        "precio_base": 180.00,
        "unidad": "por ensayo",
        "tiempo": "3-4 días",
        "descuento_volumen": 0.08
    },
    "Corte directo": {
        "precio_base": 350.00,
        "unidad": "por ensayo (3 especímenes)",
        "tiempo": "7-10 días",
        "descuento_volumen": 0.05
    },
    "Consolidación": {
        "precio_base": 400.00,
        "unidad": "por ensayo",
        "tiempo": "15-20 días",
        "descuento_volumen": 0.05
    },
    
    # MATERIALES DE CONSTRUCCIÓN
    "Resistencia a compresión": {
        "precio_base": 25.00,
        "unidad": "por cilindro/probeta",
        "tiempo": "Según edad (7, 14, 28 días)",
        "descuento_volumen": 0.15
    },
    "Granulometría de agregados": {
        "precio_base": 40.00,
        "unidad": "por muestra",
        "tiempo": "2-3 días",
        "descuento_volumen": 0.10
    },
    
    # PERFORACIÓN Y CAMPO
    "Perforación diamantina": {
        "precio_base": 180.00,
        "unidad": "por metro lineal",
        "tiempo": "Según proyecto",
        "descuento_volumen": 0.08,
        "nota": "Incluye muestreo y registro estratigráfico"
    },
    "Calicatas y test-pits": {
        "precio_base": 250.00,
        "unidad": "por calicata (hasta 3m)",
        "tiempo": "1-2 días",
        "descuento_volumen": 0.10,
        "nota": "Incluye excavación, descripción y muestreo"
    },
    "Ensayos in-situ": {
        "precio_base": 80.00,
        "unidad": "por punto",
        "tiempo": "Inmediato",
        "descuento_volumen": 0.12,
        "nota": "Densidad de campo, CBR in-situ"
    },
    "SPT (Standard Penetration Test)": {
        "precio_base": 120.00,
        "unidad": "por punto (cada 1.5m)",
        "tiempo": "Durante perforación",
        "descuento_volumen": 0.08
    },
    
    # ANÁLISIS AMBIENTAL
    "Análisis de calidad de agua": {
        "precio_base": 150.00,
        "unidad": "por muestra (físico-químico básico)",
        "tiempo": "5-7 días",
        "descuento_volumen": 0.10,
        "nota": "Análisis microbiológico: +S/. 80"
    },
    "Contaminación de suelos": {
        "precio_base": 220.00,
        "unidad": "por muestra",
        "tiempo": "7-10 días",
        "descuento_volumen": 0.08
    },
    
    # TOPOGRAFÍA
    "Levantamiento planimétrico y altimétrico": {
        "precio_base": 1200.00,
        "unidad": "por hectárea",
        "tiempo": "3-5 días",
        "descuento_volumen": 0.15,
        "nota": "Incluye planos CAD y memoria descriptiva"
    },
    "Fotogrametría con drones": {
        "precio_base": 1800.00,
        "unidad": "por proyecto (hasta 10 ha)",
        "tiempo": "7-10 días",
        "descuento_volumen": 0.10,
        "nota": "Incluye modelo 3D, ortofoto y cálculo de volúmenes"
    },
    "Replanteo de obras": {
        "precio_base": 800.00,
        "unidad": "por día",
        "tiempo": "Según avance de obra",
        "descuento_volumen": 0.08
    },
    
    # PAQUETES ESPECIALES
    "Estudio de Mecánica de Suelos Completo": {
        "precio_base": 2500.00,
        "unidad": "por proyecto (incluye 3 calicatas + ensayos básicos)",
        "tiempo": "15-20 días",
        "descuento_volumen": 0.00,
        "nota": "Incluye informe técnico y recomendaciones de diseño"
    }
}

# Descuentos adicionales
DESCUENTOS = {
    "primer_servicio": 0.10,  # 10% descuento primera vez
    "paquete_corporativo": 0.15,  # 15% para empresas con convenio
    "pago_adelantado": 0.05,  # 5% por pago adelantado
    "emergencia": -0.30  # +30% por servicio urgente (< 48h)
}

# Servicios más solicitados (para sugerencias)
SERVICIOS_POPULARES = [
    "Análisis granulométrico",
    "Contenido de humedad",
    "CBR (California Bearing Ratio)",
    "Resistencia a compresión",
    "Perforación diamantina",
    "Levantamiento planimétrico y altimétrico"
]

def calcular_precio_con_descuento(precio_base, cantidad=1, es_primer_servicio=False, es_urgente=False):
    """
    Calcula el precio final aplicando descuentos
    
    Args:
        precio_base: Precio base del servicio
        cantidad: Cantidad de muestras/ensayos
        es_primer_servicio: Si es el primer servicio del cliente
        es_urgente: Si requiere entrega urgente
    
    Returns:
        tuple: (precio_unitario_final, precio_total, descuento_aplicado)
    """
    precio_unitario = precio_base
    descuento_total = 0.0
    
    # Descuento por volumen
    if cantidad >= 10:
        descuento_total += 0.10
    elif cantidad >= 5:
        descuento_total += 0.05
    
    # Descuento primer servicio
    if es_primer_servicio:
        descuento_total += DESCUENTOS["primer_servicio"]
    
    # Cargo por urgencia
    if es_urgente:
        descuento_total += DESCUENTOS["emergencia"]  # Negativo = incremento
    
    # Aplicar descuento
    precio_unitario_final = precio_base * (1 - descuento_total)
    precio_total = precio_unitario_final * cantidad
    
    return (precio_unitario_final, precio_total, descuento_total)


if __name__ == "__main__":
    # Prueba
    print("=== CATÁLOGO DE PRECIOS GEO CENTER LAB ===\n")
    print(f"Total de servicios: {len(PRECIOS_SERVICIOS)}")
    print("\nServicios más solicitados:")
    for servicio in SERVICIOS_POPULARES:
        if servicio in PRECIOS_SERVICIOS:
            info = PRECIOS_SERVICIOS[servicio]
            print(f"  - {servicio}: S/. {info['precio_base']:.2f} {info['unidad']}")
