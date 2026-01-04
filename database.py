import sqlite3
import json
from datetime import datetime
import os

DB_NAME = "geocenter_leads.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos si no existe"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabla de LEADS (Clientes Potenciales)
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT DEFAULT 'Anónimo',
            contacto TEXT,
            tipo_contacto TEXT, -- 'whatsapp' o 'email'
            servicios_interes TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'NUEVO' -- NUEVO, CONTACTADO, CERRADO
        )
    ''')
    
    # Tabla de MENSAJES (Historial - Opcional)
    c.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            rol TEXT, -- 'user' o 'bot'
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"📁 Base de datos '{DB_NAME}' inicializada.")

def guardar_lead(contacto, nombre="Desconocido", servicios=[], tipo="whatsapp"):
    """Guarda o actualiza un lead"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verificar si ya existe por contacto
    c.execute("SELECT id FROM leads WHERE contacto = ?", (contacto,))
    row = c.fetchone()
    
    servicios_str = ", ".join(servicios) if isinstance(servicios, list) else servicios
    
    if row:
        lead_id = row['id']
        # Actualizar interés y fecha
        c.execute('''
            UPDATE leads 
            SET servicios_interes = ?, fecha_creacion = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (servicios_str, lead_id))
    else:
        # Insertar nuevo
        c.execute('''
            INSERT INTO leads (nombre, contacto, tipo_contacto, servicios_interes)
            VALUES (?, ?, ?, ?)
        ''', (nombre, contacto, tipo, servicios_str))
        lead_id = c.lastrowid
        
    conn.commit()
    conn.close()
    return lead_id

def obtener_leads():
    """Devuelve todos los leads ordenados por fecha"""
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM leads ORDER BY fecha_creacion DESC').fetchall()
    conn.close()
    return [dict(lead) for lead in leads]

# Inicializar al importar
if not os.path.exists(DB_NAME):
    init_db()
