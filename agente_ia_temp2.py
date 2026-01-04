
    def _detectar_intencion(self, pregunta):
        """Detecta la intención del usuario para personalizar respuesta"""
        pregunta_lower = pregunta.lower()
        
        if any(word in pregunta_lower for word in ['cotiza', 'precio', 'costo', 'presupuesto', 'cuanto']):
            return 'cotizacion'
        elif any(word in pregunta_lower for word in ['contacto', 'llamar', 'visitar', 'direccion', 'ubicacion', 'whatsapp', 'watsapp', 'wasap', 'telefono', 'celular', 'mail', 'correo']):
            return 'contacto'
        elif any(word in pregunta_lower for word in ['servicio', 'ofrece', 'hacen', 'tienen', 'que hacen']):
            return 'informacion_general'
        elif any(word in pregunta_lower for word in ['proyecto', 'experiencia', 'obra', 'referencia']):
            return 'proyectos'
        elif any(word in pregunta_lower for word in ['gracias', 'adios', 'chao']):
            return 'despedida'
        return 'otros'

    def _respuesta_demo_mejorada(self, pregunta):
        """Modo demo con lógica conversacional avanzada"""
        pregunta_lower = pregunta.lower()
        pregunta_stripped = pregunta.strip()
        
        # Detectar contacto primero (prioridad máxima)
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
        """Genera respuesta cuando el usuario proporciona contacto"""
        es_email = '@' in contacto
        
        if es_email:
            return f"""✅ Email confirmado: {contacto}

📧 Enviaremos a tu bandeja:
• Catálogo completo de servicios
• Precios actualizados 2024
• Casos de éxito de proyectos
• 10% DESCUENTO en tu primer servicio

⏰ Revisa tu correo en 15-30 minutos

¿Mientras tanto, qué servicio te interesa? (Laboratorio, Geotecnia, Hidráulica, Perforación)"""
        else:
            whatsapp = self.datos_empresa['redes_sociales']['whatsapp']
            return f"""✅ Número guardado: {contacto}

📱 WHATSAPP: Contáctanos ahora:
https://wa.me/{whatsapp}

💡 Te responderemos al instante con:
• Información detallada
• Cotización personalizada
• Asesoría técnica GRATIS

¿Qué necesitas exactamente? Cuéntanos 👇"""

    def _manejar_seleccion_numero(self, num):
        """Maneja selección numérica del menú"""
        # Menú principal (1-7)
        if self.ultima_opcion is None:
            return self._menu_principal(num)
        
        # Submenús
        return self._submenu_opciones(num)

    def _menu_principal(self, num):
        """Menú principal con opciones ampliadas"""
        menus = {
            1: ('laboratorio', self._menu_laboratorio()),
            2: ('geotecnia', self._menu_geotecnia()),
            3: ('hidraulica', self._menu_hidraulica()),
            4: ('perforacion', self._menu_perforacion()),
            5: ('topografia', self._menu_topografia()),
            6: ('cotizacion', self._menu_cotizacion()),
            7: ('contacto', self._menu_contacto())
        }
        
        if num in menus:
            opcion, respuesta = menus[num]
            # Para cotizacion y contacto, no hay submenu
            if num in [6, 7]:
                self.solicito_contacto = True
                self.ultima_opcion = None
            else:
                self.ultima_opcion = opcion
            return respuesta
        
        return "❌ Opción no válida. Escribe 1-7 para continuar 👇"

    def _submenu_opciones(self, num):
        """Maneja submenús según última opción"""
        opciones = {
            'laboratorio': {
                1: "🔬 SUELOS: Granulometría, Límites, Humedad, Clasificación SUCS/AASHTO. ¿Cuántas muestras tienes? 📝",
                2: "🏗️ RESISTENCIA: CBR, Proctor, Corte Directo, Compresión Simple. Normas ASTM garantizadas. ✅",
                3: "🧪 CONCRETO: Rotura de probetas, Diseño de mezclas, Esclerometría. Control de calidad en obra. 🏢",
                4: "⚗️ ESPECIALES: Triaxial, Consolidación, Permeabilidad. Para proyectos de alta ingeniería. 🎯"
            },
            'geotecnia': {
                1: "🔨 SPT/DPL: Ensayos de penetración estándar y ligera. Perfil estratigráfico completo. ¿Ubicación del proyecto? 📍",
                2: "📉 GEOFÍSICA: Refracción Sísmica, MASW (Vs30), Tomografía Eléctrica. Estudios no destructivos. ⚡",
                3: "⛰️ ESTABILIDAD: Análisis de taludes, muros de contención, capacidad portante. Software especializado. 💻",
                4: "📋 ESTUDIOS: Informes técnicos para licencias, edificaciones y carreteras. Firmados por especialistas. ✒️"
            },
            'hidraulica': {
                1: "💧 HIDROLOGÍA: Estudios de cuencas, caudales máximos, diseño de drenaje. 🌧️",
                2: "🌊 MODELACIÓN: Simulación de inundaciones, rotura de presas (Hec-RAS). Mapas de riesgo. 🗺️",
                3: "🚰 PRUEBAS: Pruebas hidrostáticas en tuberías, permeabilidad de campo. 🔧",
                4: "🏗️ DISEÑO: Canales, presas, defensas ribereñas. Ingeniería de detalle. 📐"
            },
            'perforacion': {
                1: "💎 DIAMANTINA: Recuperación de núcleos (Core) BQ, NQ, HQ, PQ. Hasta 500m. 🏔️",
                2: "🌍 GEOTÉCNICA: Instalación de piezómetros, inclinómetros. Muestras inalteradas. 📊",
                3: "⛏️ MINERÍA: Exploración, validación de reservas. Servicio en interior mina y superficie. 👷",
                4: "💧 POZOS: Perforación para agua subterránea. Mantenimiento y limpieza. 🚰"
            },
            'topografia': {
                1: "📍 LEVANTAMIENTO: Estación total + GPS Diferencial. Precisión milimétrica. 📏",
                2: "🚁 DRONES: Fotogrametría, curvas de nivel, ortofotos de alta resolución. 📸",
                3: "📐 REPLANTEO: Ejes, niveles, control de obra civil y movimiento de tierras. 🚜",
                4: "🌊 BATIMETRÍA: Topografía de fondos marinos, lagunas y ríos. 🚤"
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

Escribe el número de la opción que deseas (1-4)
O escríbeme tu consulta y te ayudo 💬"""

    def _menu_laboratorio(self):
        return """🔬 LABORATORIO - ¿Qué área te interesa?

1. Ensayos Estándar (Granulometría, Límites)
2. Ensayos de Resistencia (CBR, Proctor)
3. Concreto y Materiales
4. Ensayos Especiales (Triaxial, Consolidación)

Escribe el número 👇"""

    def _menu_geotecnia(self):
        return """🌍 GEOTECNIA Y GEOFÍSICA - ¿Qué servicio?

1. Ensayos de Campo (SPT, DPL)
2. Geofísica (Refracción, MASW)
3. Estabilidad y Diseño
4. Estudios Geotécnicos Completos

Escribe el número 👇"""

    def _menu_hidraulica(self):
        return """💧 HIDRÁULICA E HIDROLOGÍA - ¿Qué necesitas?

1. Estudios Hidrológicos
2. Modelación Hidráulica
3. Pruebas de Campo
4. Diseño de Obras Hidráulicas

Escribe el número 👇"""

    def _menu_perforacion(self):
        return """⚙️ PERFORACIÓN DIAMANTINA - ¿Qué tipo?

1. Perforación Diamantina (Core)
2. Perforación Geotécnica
3. Exploración Minera
4. Pozos de Agua

Escribe el número 👇"""

    def _menu_topografia(self):
        return """📐 TOPOGRAFÍA - ¿Qué servicio?

1. Levantamiento Topográfico
2. Fotogrametría con Drones
3. Replanteo de Obra
4. Batimetría

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
        # Contacto directo (WhatsApp, Email, etc.) - PRIORIDAD ALTA
        if any(word in pregunta_lower for word in ['whatsapp', 'watsapp', 'wasap', 'telefono', 'celular', 'llamar', 'contacto', 'direccion', 'ubicacion', 'donde estan', 'donde se encuentran']):
            self.solicito_contacto = True
            return self._menu_contacto()
        
        # Servicios
        if any(word in pregunta_lower for word in ['servicio', 'ofrece', 'hacen', 'tienen', 'hola', 'buenos', 'buenas', 'info']):
            self.ultima_opcion = None
            return """¡Hola! 👋 Somos GEO CENTER LAB, especialistas en ingeniería.

1. 🔬 Laboratorio de Suelos y Materiales
2. 🌍 Geotecnia y Geofísica
3. 💧 Hidráulica e Hidrología
4. ⚙️ Perforación Diamantina
5. 📐 Topografía y Drones
6. 💰 Cotización
7. 📞 Contacto

¿Qué necesitas? Escribe el número 👇"""
        
        # Precios (nunca dar cifras exactas)
        if any(word in pregunta_lower for word in ['precio', 'costo', 'cuanto', 'cotiza', 'tarifa']):
            self.solicito_contacto = True
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
            proyectos_list = '\n• '.join([p['nombre'] for p in self.proyectos[:10]])
            return f"""🏗️ PROYECTOS REALIZADOS EN HUARAZ Y ANCASH

• {proyectos_list}

Total: {len(self.proyectos)} proyectos entregados con éxito ✅

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
2. 🌍 Geotecnia y geofísica
3. 💧 Hidráulica
4. ⚙️ Perforación
5. 📐 Topografía
6. 💰 Cotizaciones

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
