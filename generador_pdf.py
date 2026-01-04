# -*- coding: utf-8 -*-
"""
Generador de Cotizaciones PDF - GEO CENTER LAB
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime, timedelta
import os
from precios_servicios import calcular_precio_con_descuento, PRECIOS_SERVICIOS

class GeneradorPDF:
    def __init__(self):
        self.width, self.height = A4
        self.estilos = getSampleStyleSheet()
        self._configurar_estilos()
        
        # Ruta del logo
        self.logo_path = os.path.join(os.path.dirname(__file__), 'imagenes', 'logo.jpeg')
        if not os.path.exists(self.logo_path):
            # Fallback a extensión JPG en mayúsculas si es necesario
            temp_path = os.path.join(os.path.dirname(__file__), 'imagenes', 'logo.JPG')
            if os.path.exists(temp_path):
                self.logo_path = temp_path

    def _configurar_estilos(self):
        """Configura estilos personalizados para el PDF"""
        # Estilo para Título Principal
        self.estilos.add(ParagraphStyle(
            name='TituloEmpresa',
            parent=self.estilos['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1E3A8A'), # Azul oscuro corporativo
            alignment=1, # Centro
            spaceAfter=6
        ))
        
        # Estilo para Subtítulo
        self.estilos.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.estilos['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1,
            spaceAfter=20
        ))

        # Estilo para celdas de tabla
        self.estilos.add(ParagraphStyle(
            name='CeldaTabla',
            parent=self.estilos['Normal'],
            fontSize=9,
            alignment=0 # Izquierda
        ))
        
        self.estilos.add(ParagraphStyle(
            name='CeldaTablaDerecha',
            parent=self.estilos['Normal'],
            fontSize=9,
            alignment=2 # Derecha
        ))

    def generar_cotizacion(self, cliente_nombre, servicios, numero_cotizacion, output_filename):
        """
        Genera el PDF de la cotización
        """
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elementos = []

        # 1. HEADER (Logo y Membrete)
        self._agregar_header(elementos)
        
        # 2. DATOS COTIZACION
        self._agregar_info_cliente(elementos, cliente_nombre, numero_cotizacion)

        # 3. TABLA DE SERVICIOS
        total_pagar = self._agregar_tabla_servicios(elementos, servicios)

        # 4. CONDICIONES Y PIE
        self._agregar_condiciones(elementos)

        # Generar PDF
        doc.build(elementos)
        return output_filename

    def _agregar_header(self, elementos):
        """Agrega logo y datos de empresa"""
        # Logo
        if os.path.exists(self.logo_path):
            im = Image(self.logo_path, width=4*cm, height=2*cm)
            im.hAlign = 'CENTER'
            elementos.append(im)
        
        elementos.append(Spacer(1, 0.5*cm))
        
        # Nombre Empresa
        elementos.append(Paragraph("GEO CENTER LAB PEYTON COMPANY S.A.C.", self.estilos['TituloEmpresa']))
        elementos.append(Paragraph("RUC: 20610467866 | VILLÓN ALTO MZ. C. LOTE 7 - HUARAZ", self.estilos['Subtitulo']))
        elementos.append(Spacer(1, 1*cm))

    def _agregar_info_cliente(self, elementos, nombre, numero):
        """Datos del cliente y fecha"""
        fecha = datetime.now().strftime("%d/%m/%Y")
        vence = (datetime.now() + timedelta(days=15)).strftime("%d/%m/%Y")
        
        data = [
            [Paragraph(f"<b>CLIENTE:</b> {nombre}", self.estilos['Normal']), 
             Paragraph(f"<b>N° COTIZACIÓN:</b> {numero}", self.estilos['Normal'])],
            [Paragraph(f"<b>FECHA:</b> {fecha}", self.estilos['Normal']),
             Paragraph(f"<b>VALIDEZ:</b> Hasta {vence}", self.estilos['Normal'])]
        ]
        
        t = Table(data, colWidths=[10*cm, 8*cm])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 0.5*cm))

    def _agregar_tabla_servicios(self, elementos, servicios):
        """Crea la tabla detallada de servicios"""
        
        # Headers
        data = [['ITEM', 'DESCRIPCIÓN', 'CANT.', 'UND.', 'P. UNIT', 'TOTAL S/.']]
        
        subtotal = 0.0
        
        for idx, s in enumerate(servicios, 1):
            nombre = s.get('nombre', 'Servicio')
            cantidad = s.get('cantidad', 1)
            urgente = s.get('urgente', False)
            
            # Obtener precio base
            precio_base = 0.0
            unidad = "und"
            
            if nombre in PRECIOS_SERVICIOS:
                info = PRECIOS_SERVICIOS[nombre]
                precio_base = info['precio_base']
                unidad = info['unidad'].split(" ")[0] # "por muestra" -> "por" (simplificar)
            
            # Calcular
            p_unit, p_total, desc = calcular_precio_con_descuento(precio_base, cantidad, False, urgente)
            
            subtotal += p_total
            
            # Descripción detallada
            desc_text = nombre
            if urgente:
                desc_text += " (URGENTE)"
            if desc > 0:
                desc_text += f" (Desc. {desc*100:.0f}%)"
                
            row = [
                str(idx),
                Paragraph(desc_text, self.estilos['CeldaTabla']),
                str(cantidad),
                unidad,
                f"{p_unit:.2f}",
                f"{p_total:.2f}"
            ]
            data.append(row)
        
        # Totales
        igv = subtotal * 0.18
        total = subtotal + igv
        
        data.append(['', '', '', '', 'SUBTOTAL', f"{subtotal:.2f}"])
        data.append(['', '', '', '', 'IGV (18%)', f"{igv:.2f}"])
        data.append(['', '', '', '', 'TOTAL', f"{total:.2f}"])
        
        # Estilo Tabla
        t = Table(data, colWidths=[1.5*cm, 8.5*cm, 1.5*cm, 2*cm, 2.5*cm, 2.5*cm])
        t.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            
            # Body
            ('ALIGN', (0,1), (-1,-4), 'CENTER'), # Todo centrado por defecto
            ('ALIGN', (1,1), (1,-4), 'LEFT'),   # Descripcion izquierda
            ('ALIGN', (-2,1), (-1,-1), 'RIGHT'), # Numeros derecha
            
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('GRID', (0,0), (-1,-4), 0.5, colors.grey),
            
            # Totales
            ('LINEBELOW', (-2,-3), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (-2,-3), (-1,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (-2,-1), (-1,-1), colors.HexColor('#E5E7EB')), # Fondo gris total
        ]))
        
        elementos.append(t)
        elementos.append(Spacer(1, 1*cm))
        return total

    def _agregar_condiciones(self, elementos):
        """Terminos y footer"""
        texto = """<b>CONDICIONES COMERCIALES:</b><br/>
        1. Validez de la oferta: 15 días calendario.<br/>
        2. Forma de pago: 50% Adelanto, 50% contra entrega de informe.<br/>
        3. Tiempo de entrega: Contado a partir del pago del adelanto y recepción de muestras.<br/>
        <br/>
        <b>CUENTAS BANCARIAS:</b><br/>
        BCP Soles: 375-xxxxxxxx-0-xx<br/>
        CCI: 002-375-xxxxxxxxxxxx-xx<br/>
        <br/>
        Atentamente,<br/>
        <b>GEO CENTER LAB</b>
        """
        elementos.append(Paragraph(texto, self.estilos['Normal']))

if __name__ == "__main__":
    # Prueba individual
    gen = GeneradorPDF()
    servicios = [
        {'nombre': 'Análisis granulométrico', 'cantidad': 5, 'urgente': False},
        {'nombre': 'CBR (California Bearing Ratio)', 'cantidad': 2, 'urgente': True}
    ]
    gen.generar_cotizacion("Cliente Prueba SAC", servicios, "COT-001", "test_cotizacion.pdf")
    print("PDF Generado: test_cotizacion.pdf")
