# -*- coding: utf-8 -*-
"""
Generador de Cotizaciones - GEO CENTER LAB
Genera cotizaciones profesionales formateadas para WhatsApp
"""

from datetime import datetime, timedelta
from precios_servicios import PRECIOS_SERVICIOS, calcular_precio_con_descuento, SERVICIOS_POPULARES


class GeneradorCotizacion:
    def __init__(self):
        self.numero_cotizacion = self._generar_numero_cotizacion()
        self.fecha = datetime.now()
        self.vigencia = self.fecha + timedelta(days=15)  # 15 días de vigencia
        
    def _generar_numero_cotizacion(self):
        """Genera número de cotización único"""
        fecha_actual = datetime.now()
        return f"COT-{fecha_actual.strftime('%Y%m%d')}-{fecha_actual.strftime('%H%M%S')}"
    
    def generar_cotizacion_whatsapp(self, cliente_nombre, servicios_solicitados, 
                                   ubicacion="", es_primer_servicio=False, 
                                   notas_adicionales=""):
        """
        Genera cotización formateada para WhatsApp
        
        Args:
            cliente_nombre: Nombre del cliente
            servicios_solicitados: Lista de dict con {nombre, cantidad, urgente}
            ubicacion: Ubicación del proyecto
            es_primer_servicio: Si es el primer servicio del cliente
            notas_adicionales: Notas adicionales del cliente
            
        Returns:
            str: Cotización formateada para WhatsApp
        """
        
        # Header
        mensaje = f"""📋 *COTIZACIÓN PROFESIONAL*
🏢 GEO CENTER LAB PEYTON COMPANY S.A.C.

━━━━━━━━━━━━━━━━━━━━━━━

📌 *DATOS DE LA COTIZACIÓN*
N° Cotización: `{self.numero_cotizacion}`
Fecha: {self.fecha.strftime('%d/%m/%Y')}
Válido hasta: {self.vigencia.strftime('%d/%m/%Y')}

👤 *CLIENTE*
Nombre: {cliente_nombre}"""

        if ubicacion:
            mensaje += f"\n📍 Ubicación: {ubicacion}"
        
        mensaje += "\n\n━━━━━━━━━━━━━━━━━━━━━━━\n\n📊 *SERVICIOS SOLICITADOS*\n"
        
        # Listar servicios y calcular totales
        subtotal = 0.0
        descuento_total_monto = 0.0
        items_cotizados = []
        
        for idx, servicio_data in enumerate(servicios_solicitados, 1):
            nombre_servicio = servicio_data.get('nombre', '')
            cantidad = servicio_data.get('cantidad', 1)
            urgente = servicio_data.get('urgente', False)
            
            if nombre_servicio in PRECIOS_SERVICIOS:
                info_precio = PRECIOS_SERVICIOS[nombre_servicio]
                precio_base = info_precio['precio_base']
                unidad = info_precio['unidad']
                tiempo = info_precio['tiempo']
                
                # Calcular precio con descuentos
                precio_unitario, precio_total_item, descuento = calcular_precio_con_descuento(
                    precio_base, cantidad, es_primer_servicio, urgente
                )
                
                subtotal += precio_total_item
                descuento_aplicado_monto = (precio_base * cantidad) - precio_total_item
                descuento_total_monto += descuento_aplicado_monto
                
                # Formatear item
                mensaje += f"\n*{idx}. {nombre_servicio}*\n"
                mensaje += f"   • Cantidad: {cantidad} {unidad}\n"
                mensaje += f"   • Precio unitario: S/. {precio_unitario:.2f}\n"
                if urgente:
                    mensaje += f"   • ⚡ URGENTE (+30%)\n"
                mensaje += f"   • Tiempo: {tiempo}\n"
                if descuento > 0:
                    mensaje += f"   • Descuento: {descuento*100:.0f}%\n"
                mensaje += f"   • *Subtotal: S/. {precio_total_item:.2f}*\n"
                
                items_cotizados.append({
                    'nombre': nombre_servicio,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': precio_total_item
                })
        
        # Calcular totales finales
        igv = subtotal * 0.18  # 18% IGV
        total = subtotal + igv
        
        # Resumen de costos
        mensaje += f"""\n━━━━━━━━━━━━━━━━━━━━━━━

💰 *RESUMEN DE COSTOS*

Subtotal:        S/. {subtotal:.2f}"""
        
        if descuento_total_monto > 0:
            mensaje += f"\nDescuento:      -S/. {descuento_total_monto:.2f}"
        
        if es_primer_servicio:
            mensaje += f"\n🎁 ¡DESCUENTO BIENVENIDA! 10%"
        
        mensaje += f"""\nIGV (18%):       S/. {igv:.2f}
━━━━━━━━━━━━━━━
*TOTAL:          S/. {total:.2f}*

━━━━━━━━━━━━━━━━━━━━━━━

✅ *INCLUYE:*
• Informe técnico profesional
• Resultados certificados
• Asesoría técnica sin costo
• Garantía de calidad

⏱ *CONDICIONES:*
• Anticipo: 50% al iniciar
• Saldo: Contra entrega de resultados
• Plazo de pago: 7 días calendario
• Vigencia: 15 días"""

        if ubicacion and "huaraz" not in ubicacion.lower():
            mensaje += f"\n\n🚗 *NOTA:* Fuera de Huaraz incluye movilidad"
        
        mensaje += f"""\n\n━━━━━━━━━━━━━━━━━━━━━━━

📞 *CONTACTO*
WhatsApp: +51 932 203 111
Email: geocenter.lab@gmail.com
Dirección: Villón Alto Mz. C Lote 7
Huaraz - Ancash

━━━━━━━━━━━━━━━━━━━━━━━

✨ *GEO CENTER LAB* - Precisión y Confiabilidad desde 2015

_¿Deseas proceder con esta cotización?_
_Responde "ACEPTO" para coordinar inicio de trabajos_"""

        if notas_adicionales:
            mensaje += f"\n\n💬 *Notas adicionales:*\n{notas_adicionales}"
        
        return mensaje
    
    def generar_lista_servicios_disponibles(self, categoria=None):
        """
        Genera lista de servicios disponibles para mostrar al cliente
        
        Args:
            categoria: Filtrar por categoría específica (opcional)
            
        Returns:
            str: Lista formateada de servicios
        """
        mensaje = "*📋 SERVICIOS DISPONIBLES*\n\n"
        
        if categoria:
            mensaje += f"*Categoría: {categoria}*\n\n"
        
        # Servicios más solicitados primero
        mensaje += "*⭐ MÁS SOLICITADOS:*\n"
        for idx, servicio in enumerate(SERVICIOS_POPULARES[:6], 1):
            if servicio in PRECIOS_SERVICIOS:
                info = PRECIOS_SERVICIOS[servicio]
                mensaje += f"{idx}. {servicio}\n   💰 Desde S/. {info['precio_base']:.2f} {info['unidad']}\n"
        
        mensaje += "\n_Escribe el número o nombre del servicio que necesitas_"
        
        return mensaje


# Función de utilidad para uso rápido
def crear_cotizacion_rapida(cliente, servicios):
    """
    Crear cotización rápida con valores por defecto
    
    Args:
        cliente: Nombre del cliente
        servicios: Lista de nombres de servicios o dict completos
        
    Returns:
        str: Cotización formateada
    """
    generador = GeneradorCotizacion()
    
    # Convertir lista simple a formato completo
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
    
    return generador.generar_cotizacion_whatsapp(
        cliente_nombre=cliente,
        servicios_solicitados=servicios_formateados,
        es_primer_servicio=True
    )


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== GENERADOR DE COTIZACIONES ===\n")
    
    # Ejemplo 1: Cotización simple
    servicios_ejemplo = [
        {'nombre': 'Análisis granulométrico', 'cantidad': 5, 'urgente': False},
        {'nombre': 'CBR (California Bearing Ratio)', 'cantidad': 2, 'urgente': False},
        {'nombre': 'Perforación diamantina', 'cantidad': 15, 'urgente': False}
    ]
    
    generador = GeneradorCotizacion()
    cotizacion = generador.generar_cotizacion_whatsapp(
        cliente_nombre="Juan Pérez - Constructora ABC",
        servicios_solicitados=servicios_ejemplo,
        ubicacion="Huaraz, Ancash",
        es_primer_servicio=True,
        notas_adicionales="Proyecto de vivienda multifamiliar - 3 pisos"
    )
    
    print(cotizacion)
    print("\n" + "="*50)
    print(f"Longitud del mensaje: {len(cotizacion)} caracteres")
