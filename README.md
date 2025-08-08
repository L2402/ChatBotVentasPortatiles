# 🤖 Documentación Completa: ChatBot con Interfaz Web

**Desarrollado por:** Reyes Vinces Jeremy Daniel, Muñoz Miranda Felix Anthony, Anchundia Lucas Eduardo Jesus
**Fecha:** Agosto 2025  
**Tecnologías:** Rasa, PostgreSQL, Flask, HTML/CSS/JavaScript

---

## 📋 Instalación y Configuración

### 1. Prerrequisitos
```bash
# Python 3.10, PostgreSQL
python --version
psql --version
```

### 2. Instalación
```bash
# Crear proyecto
mkdir ChatBot && cd ChatBot
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install rasa psycopg2-binary flask requests

# Inicializar Rasa
rasa init
```

### 3. Base de Datos PostgreSQL
```sql
-- Crear base de datos
CREATE DATABASE chatbot_db;
CREATE USER chatbot_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;

-- Tabla productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    procesador VARCHAR(100),
    ram VARCHAR(50),
    uso VARCHAR(100),
    marca VARCHAR(100),
    precio DECIMAL(10,2)
);

-- Insertar datos (ver archivo completo para datos completos)
INSERT INTO productos VALUES 
(1, 'IdeaPad 3 Lenovo', 'I5 11ava Generacion', '12GB', 'programación', 'Lenovo', 598.00),
(2, 'Asus TUF Asus', 'i7 13ava Generacion', '32GB', 'gaming', 'Asus', 999.00);
```

---

## ⚙️ Archivos de Configuración Rasa

### 1. config.yml
```yaml
recipe: default.v1
language: es
pipeline:
  - name: "WhitespaceTokenizer"
  - name: "RegexFeaturizer"
  - name: "LexicalSyntacticFeaturizer"
  - name: "CountVectorsFeaturizer"
  - name: "DIETClassifier"
    epochs: 100
  - name: "EntitySynonymMapper"
  - name: "FallbackClassifier"
    threshold: 0.3
policies:
  - name: "MemoizationPolicy"
  - name: "RulePolicy"
  - name: "TEDPolicy"
    max_history: 5
    epochs: 100
```

### 2. domain.yml
```yaml
version: "3.1"
intents:
  - greet
  - goodbye
  - ask_for_product
  - ask_for_recommendation

entities:
  - uso
  - marca
  - procesador
  - ram

responses:
  utter_greet:
  - text: "¡Hola! 👋 Soy tu asistente virtual especializado en laptops y accesorios."

  utter_goodbye:
  - text: "¡Adiós! 👋 ¡Que tengas un excelente día!"

actions:
  - action_query_products
  - action_recommend_accessories
  - action_compare_laptops
  - action_specific_recommendation
```

### 3. data/nlu.yml
```yaml
version: "3.1"
nlu:
- intent: greet
  examples: |
    - ¡Hola!
    - Hola, ¿cómo estás?
    - Buenas tardes

- intent: ask_for_product
  examples: |
    - ¿Tienes laptop para programación?
    - Busco una laptop para [gaming](uso)
    - ¿Tienes laptops de la marca [Dell](marca)?
    - Necesito una laptop con [16GB](ram) de RAM
    - Quiero una laptop con procesador [i7](procesador)

- intent: ask_for_recommendation
  examples: |
    - ¿Cuál me recomiendas?
    - Recomiéndame una laptop
    - ¿Cuál es la mejor opción?
```

### 4. data/rules.yml
```yaml
version: "3.1"
rules:
- rule: Consultar productos
  steps:
  - intent: ask_for_product
  - action: action_query_products

- rule: Recomendación
  steps:
  - intent: ask_for_recommendation
  - action: action_specific_recommendation
```

### 5. endpoints.yml
```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

---

## 💻 Código del Proyecto

### 1. actions/actions.py
```python
import psycopg2
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

class ActionQueryProducts(Action):
    def name(self) -> Text:
        return "action_query_products"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        connection_params = {
            'host': 'localhost',
            'database': 'chatbot_db',
            'user': 'chatbot_user',
            'password': 'tu_password'
        }
        
        try:
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            
            entities = tracker.latest_message.get('entities', [])
            query = "SELECT * FROM productos WHERE 1=1"
            params = []
            
            for entity in entities:
                if entity['entity'] == 'uso':
                    query += " AND uso ILIKE %s"
                    params.append(f"%{entity['value']}%")
                elif entity['entity'] == 'marca':
                    query += " AND marca ILIKE %s"
                    params.append(f"%{entity['value']}%")
                elif entity['entity'] == 'procesador':
                    query += " AND procesador ILIKE %s"
                    params.append(f"%{entity['value']}%")
                elif entity['entity'] == 'ram':
                    query += " AND ram ILIKE %s"
                    params.append(f"%{entity['value']}%")
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            if products:
                response = "🎯 **Aquí tienes nuestras mejores opciones:**\n\n"
                for product in products:
                    response += f"💻 **{product[1]}** • RAM: {product[3]} • Procesador: {product[2]} • Precio: ${product[4]:.2f}\n\n"
                response += "✨ **¿Te gustaría conocer más detalles?**"
            else:
                response = "😔 No encontré productos que coincidan con tu búsqueda."
            
            dispatcher.utter_message(text=response)
            
        except Exception as e:
            dispatcher.utter_message(text="Lo siento, hubo un error al consultar los productos.")
        finally:
            if 'conn' in locals():
                conn.close()
        
        return []

class ActionSpecificRecommendation(Action):
    def name(self) -> Text:
        return "action_specific_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        response = """🏆 **Mis mejores recomendaciones:**

🥇 **Mejor relación calidad-precio:** IdeaPad 3 Lenovo ($598)
🥈 **Mejor para gaming:** Asus TUF ($999)
🥉 **Mejor económica:** Aspire 3 Acer ($299.99)
💎 **Mejor premium:** MacBook Pro ($1899.99)

¿Cuál te interesa más?"""
        
        dispatcher.utter_message(text=response)
        return []
```

### 2. web_server.py
```python
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
app.template_folder = 'web_interface'
app.static_folder = 'web_interface'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    print("🚀 Servidor web iniciado en: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## 3. accesories.py
```python
from rasa_sdk import Action
import psycopg2

class ActionRecommendAccessories(Action):
    def name(self) -> str:
        return "action_recommend_accessories"

    def run(self, dispatcher, tracker, domain):
        try:
            conn = psycopg2.connect(
                dbname='tienda_computadoras_accesorios',
                user='postgres',
                password='2005',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            user_input = tracker.latest_message.get('text').lower()
            
            # Detectar el tipo de uso o producto principal
            usos_profesionales = ["programacion", "gaming", "diseño", "edicion", "arquitectura", "ingenieria"]
            usos_basicos = ["ofimatica", "ver peliculas", "navegar", "clases"]
            
            uso_detectado = None
            for uso in usos_profesionales + usos_basicos:
                if uso in user_input:
                    uso_detectado = uso
                    break

            response = "🎧 **¡Perfecto! Te recomiendo estos accesorios complementarios:**\n\n"

            if uso_detectado in usos_profesionales:
                # Accesorios para usos profesionales
                cursor.execute("""
                    SELECT nombre, caracteristicas, precio FROM accesorios 
                    WHERE nombre ILIKE '%mouse%' OR nombre ILIKE '%teclado%' OR nombre ILIKE '%monitor%'
                    ORDER BY precio DESC
                """)
                accesorios = cursor.fetchall()
                
                response += "💼 **Para trabajo profesional:**\n"
                for nombre, caracteristicas, precio in accesorios:
                    response += f"   • {nombre}: {caracteristicas} - ${precio}\n"
                
                response += "\n💡 **Recomendación especial:** Un mouse ergonómico y un teclado mecánico mejorarán significativamente tu productividad.\n"

            elif uso_detectado in usos_basicos:
                # Accesorios para usos básicos
                cursor.execute("""
                    SELECT nombre, caracteristicas, precio FROM accesorios 
                    WHERE nombre ILIKE '%mouse%' OR nombre ILIKE '%auriculares%'
                    ORDER BY precio ASC
                """)
                accesorios = cursor.fetchall()
                
                response += "🏠 **Para uso doméstico:**\n"
                for nombre, caracteristicas, precio in accesorios:
                    response += f"   • {nombre}: {caracteristicas} - ${precio}\n"
                
                response += "\n💡 **Recomendación especial:** Un mouse inalámbrico y auriculares con micrófono son ideales para clases virtuales.\n"

            else:
                # Accesorios generales
                cursor.execute("""
                    SELECT nombre, caracteristicas, precio FROM accesorios 
                    ORDER BY precio ASC
                """)
                accesorios = cursor.fetchall()
                
                response += "🛒 **Accesorios populares:**\n"
                for nombre, caracteristicas, precio in accesorios:
                    response += f"   • {nombre}: {caracteristicas} - ${precio}\n"

            response += "\n🚀 **¿Te gustaría que te ayude a elegir el accesorio perfecto o tienes alguna pregunta específica?**"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al consultar los accesorios: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return [] 
## 4. comparisons.py
```python
from rasa_sdk import Action
import psycopg2

class ActionCompareLaptops(Action):
    def name(self) -> str:
        return "action_compare_laptops"

    def run(self, dispatcher, tracker, domain):
        try:
            conn = psycopg2.connect(
                dbname='tienda_computadoras_accesorios',
                user='postgres',
                password='2005',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            user_input = tracker.latest_message.get('text').lower()
            
            # Detectar marcas mencionadas
            marcas = ["lenovo", "dell", "hp", "asus", "acer", "apple", "samsung", "microsoft"]
            marcas_mencionadas = [marca for marca in marcas if marca in user_input]
            
            # Detectar rangos de precio
            rangos_precio = {
                "económico": (0, 600),
                "medio": (600, 1200),
                "alto": (1200, 2000),
                "premium": (2000, 9999)
            }
            
            rango_detectado = None
            for rango, (min_precio, max_precio) in rangos_precio.items():
                if rango in user_input:
                    rango_detectado = (min_precio, max_precio)
                    break

            response = "📊 **Comparación de laptops:**\n\n"

            if marcas_mencionadas:
                # Comparar marcas específicas
                placeholders = ','.join(['%s'] * len(marcas_mencionadas))
                query = f"""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE LOWER(marca) IN ({placeholders})
                    ORDER BY precio ASC
                """
                cursor.execute(query, marcas_mencionadas)
                laptops = cursor.fetchall()
                
                response += f"🔍 **Comparando {', '.join(marcas_mencionadas).title()}:**\n\n"
                
                for nombre, marca, ram, procesador, precio in laptops:
                    response += f"💻 **{nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n"
                    response += f"   • 💰 **Relación calidad-precio:** {'Excelente' if precio < 800 else 'Buena' if precio < 1500 else 'Premium'}\n\n"

            elif rango_detectado:
                # Comparar por rango de precio
                min_precio, max_precio = rango_detectado
                cursor.execute("""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE precio BETWEEN %s AND %s
                    ORDER BY precio ASC
                """, (min_precio, max_precio))
                laptops = cursor.fetchall()
                
                response += f"💰 **Laptops entre ${min_precio} y ${max_precio}:**\n\n"
                
                for nombre, marca, ram, procesador, precio in laptops:
                    response += f"💻 **{nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n\n"

            else:
                # Comparación general por categorías
                response += "📈 **Comparación por categorías:**\n\n"
                
                # Económicas
                cursor.execute("SELECT COUNT(*), MIN(precio), MAX(precio) FROM laptops WHERE precio < 600")
                count, min_precio, max_precio = cursor.fetchone()
                response += f"💰 **Económicas (< $600):** {count} opciones desde ${min_precio} hasta ${max_precio}\n"
                
                # Medias
                cursor.execute("SELECT COUNT(*), MIN(precio), MAX(precio) FROM laptops WHERE precio BETWEEN 600 AND 1200")
                count, min_precio, max_precio = cursor.fetchone()
                response += f"⚡ **Medias ($600-$1200):** {count} opciones desde ${min_precio} hasta ${max_precio}\n"
                
                # Altas
                cursor.execute("SELECT COUNT(*), MIN(precio), MAX(precio) FROM laptops WHERE precio BETWEEN 1200 AND 2000")
                count, min_precio, max_precio = cursor.fetchone()
                response += f"🚀 **Altas ($1200-$2000):** {count} opciones desde ${min_precio} hasta ${max_precio}\n"
                
                # Premium
                cursor.execute("SELECT COUNT(*), MIN(precio), MAX(precio) FROM laptops WHERE precio > 2000")
                count, min_precio, max_precio = cursor.fetchone()
                response += f"👑 **Premium (> $2000):** {count} opciones desde ${min_precio} hasta ${max_precio}\n"

            response += "\n💡 **¿Te gustaría que compare modelos específicos o te ayude a elegir según tu presupuesto?**"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al comparar laptops: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return [] 
## 5. recommendations.py
```python
from rasa_sdk import Action
import psycopg2

class ActionSpecificRecommendation(Action):
    def name(self) -> str:
        return "action_specific_recommendation"

    def run(self, dispatcher, tracker, domain):
        try:
            conn = psycopg2.connect(
                dbname='tienda_computadoras_accesorios',
                user='postgres',
                password='2005',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            user_input = tracker.latest_message.get('text').lower()
            
            # Detectar palabras clave para recomendaciones específicas
            palabras_clave = {
                "mejor": "best",
                "recomienda": "recommend", 
                "cual": "which",
                "cuál": "which",
                "sugiere": "suggest",
                "opcion": "option",
                "opción": "option"
            }
            
            # Detectar presupuesto
            presupuesto_detectado = None
            if "barato" in user_input or "económico" in user_input or "bajo" in user_input:
                presupuesto_detectado = "bajo"
            elif "medio" in user_input or "intermedio" in user_input:
                presupuesto_detectado = "medio"
            elif "alto" in user_input or "caro" in user_input or "premium" in user_input:
                presupuesto_detectado = "alto"

            response = "🎯 **Mi recomendación personalizada:**\n\n"

            if presupuesto_detectado == "bajo":
                # Recomendación económica
                cursor.execute("""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE precio < 600
                    ORDER BY ram DESC, precio ASC
                    LIMIT 3
                """)
                laptops = cursor.fetchall()
                
                response += "💰 **Para presupuesto económico, te recomiendo:**\n\n"
                for i, (nombre, marca, ram, procesador, precio) in enumerate(laptops, 1):
                    response += f"🥇 **Opción {i} - {nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n"
                    response += f"   • ⭐ **Ventaja:** Mejor relación calidad-precio en su rango\n\n"

            elif presupuesto_detectado == "medio":
                # Recomendación intermedia
                cursor.execute("""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE precio BETWEEN 600 AND 1200
                    ORDER BY ram DESC, precio ASC
                    LIMIT 3
                """)
                laptops = cursor.fetchall()
                
                response += "⚡ **Para presupuesto medio, te recomiendo:**\n\n"
                for i, (nombre, marca, ram, procesador, precio) in enumerate(laptops, 1):
                    response += f"🥇 **Opción {i} - {nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n"
                    response += f"   • ⭐ **Ventaja:** Equilibrio perfecto entre rendimiento y precio\n\n"

            elif presupuesto_detectado == "alto":
                # Recomendación premium
                cursor.execute("""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE precio > 1200
                    ORDER BY ram DESC, precio DESC
                    LIMIT 3
                """)
                laptops = cursor.fetchall()
                
                response += "🚀 **Para presupuesto alto, te recomiendo:**\n\n"
                for i, (nombre, marca, ram, procesador, precio) in enumerate(laptops, 1):
                    response += f"🥇 **Opción {i} - {nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n"
                    response += f"   • ⭐ **Ventaja:** Máximo rendimiento y calidad premium\n\n"

            else:
                # Recomendación general (mejor relación calidad-precio)
                cursor.execute("""
                    SELECT nombre, marca, ram, procesador, precio 
                    FROM laptops 
                    WHERE precio BETWEEN 600 AND 1000
                    ORDER BY ram DESC, precio ASC
                    LIMIT 1
                """)
                laptop = cursor.fetchone()
                
                if laptop:
                    nombre, marca, ram, procesador, precio = laptop
                    response += f"🏆 **Mi TOP recomendación:**\n\n"
                    response += f"💻 **{nombre} {marca}**\n"
                    response += f"   • RAM: {ram}GB\n"
                    response += f"   • Procesador: {procesador}\n"
                    response += f"   • Precio: ${precio}\n"
                    response += f"   • ⭐ **¿Por qué esta?** Mejor relación calidad-precio del catálogo\n"
                    response += f"   • 🎯 **Ideal para:** Programación, diseño, gaming moderado, trabajo profesional\n\n"

            response += "💡 **¿Te gustaría que te ayude con la compra o tienes alguna pregunta específica sobre estas opciones?**"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Hubo un error al generar la recomendación: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return [] 

## 6. usos.json
```json

{
    "maquinas virtuales": {"ram": 16, "procesador": ["i5", "i7", "i9", "ryzen 5", "ryzen 7", "ryzen 9"]},
    "virtualizacion": {"ram": 16, "procesador": ["i5", "i7", "i9", "ryzen 5", "ryzen 7", "ryzen 9"]},
    "servidores": {"ram": 16, "procesador": ["i5", "i7", "i9", "ryzen 5", "ryzen 7", "ryzen 9"]},
    "bases de datos": {"ram": 16, "procesador": ["i5", "i7", "i9", "ryzen 5", "ryzen 7", "ryzen 9"]},
    "gaming": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "videojuegos": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "juegos": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "diseño grafico": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "diseño": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "photoshop": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "illustrator": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "edicion de video": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "edicion video": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "premiere": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "after effects": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "renderizado": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "render": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "arquitectura": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "autocad": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "revit": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "solidworks": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "ingenieria": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "data science": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "ciencia de datos": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "machine learning": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "inteligencia artificial": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "ai": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "mineria de datos": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "analisis de datos": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "estadistica": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "investigacion": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "investigador": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "modelado 3d": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "3d": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "blender": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "maya": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]},
    "3ds max": {"ram": 16, "procesador": ["i7", "i9", "ryzen 7", "ryzen 9"]}
}

## 🎨 Interfaz Web

### 1. web_interface/index.html
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatBot - Asistente Virtual</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="bot-avatar">🤖</div>
            <div class="header-info">
                <h1>Asistente Virtual</h1>
                <p>Especializado en laptops y accesorios</p>
            </div>
        </div>

        <div class="chat-messages" id="chatMessages"></div>

        <div class="quick-actions">
            <button class="quick-btn" onclick="sendQuickMessage('Busco una laptop para programación')">
                💻 Programación
            </button>
            <button class="quick-btn" onclick="sendQuickMessage('¿Cuál me recomiendas?')">
                🏆 Recomendación
            </button>
        </div>

        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Escribe tu mensaje...">
            <button id="sendButton" onclick="sendMessage()">
                <span>📤</span>
            </button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>
```

### 2. web_interface/style.css
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --chat-bg: #ffffff;
    --bot-message-bg: #667eea;
    --user-message-bg: #f8f9fa;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.chat-container {
    background: var(--chat-bg);
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    width: 100%;
    max-width: 500px;
    height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chat-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.bot-avatar {
    font-size: 2.5rem;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.message {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    word-wrap: break-word;
    animation: messageSlide 0.3s ease-out;
}

.message.bot {
    background: var(--bot-message-bg);
    color: white;
    align-self: flex-start;
    border-bottom-left-radius: 5px;
}

.message.user {
    background: var(--user-message-bg);
    color: #333;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
    border: 1px solid #e9ecef;
}

.quick-actions {
    padding: 15px 20px;
    display: flex;
    gap: 10px;
    overflow-x: auto;
    border-top: 1px solid #e9ecef;
}

.quick-btn {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    cursor: pointer;
    white-space: nowrap;
    transition: transform 0.2s;
}

.quick-btn:hover {
    transform: translateY(-2px);
}

.chat-input {
    padding: 20px;
    display: flex;
    gap: 10px;
    border-top: 1px solid #e9ecef;
}

#messageInput {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #e9ecef;
    border-radius: 25px;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.3s;
}

#messageInput:focus {
    border-color: var(--primary-color);
}

#sendButton {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    transition: transform 0.2s;
}

#sendButton:hover {
    transform: scale(1.1);
}

@keyframes messageSlide {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 600px) {
    .chat-container {
        height: 100vh;
        border-radius: 0;
    }
    body {
        padding: 0;
    }
}
```

### 3. web_interface/script.js
```javascript
const RASA_ENDPOINT = 'http://localhost:5005/webhooks/rest/webhook';
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
let isLoading = false;

document.addEventListener('DOMContentLoaded', function() {
    addBotMessage('¡Hola! 👋 Soy tu asistente virtual especializado en laptops y accesorios. ¿En qué puedo ayudarte hoy?');
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;
    
    addUserMessage(message);
    messageInput.value = '';
    showLoading();
    
    try {
        const response = await fetch(RASA_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: 'user',
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error('Error en la comunicación con el bot');
        }
        
        const data = await response.json();
        hideLoading();
        
        if (data && data.length > 0) {
            data.forEach(item => {
                if (item.text) {
                    addBotMessage(item.text);
                }
            });
        } else {
            addBotMessage('Lo siento, no pude procesar tu mensaje. ¿Podrías intentarlo de nuevo?');
        }
        
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        addBotMessage('Lo siento, hubo un error en la comunicación. Por favor, intenta de nuevo.');
    }
}

function sendQuickMessage(message) {
    messageInput.value = message;
    sendMessage();
}

function addBotMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = formatMessage(text);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessage(text) {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

function showLoading() {
    isLoading = true;
    sendButton.innerHTML = '<span>⏳</span>';
    sendButton.disabled = true;
}

function hideLoading() {
    isLoading = false;
    sendButton.innerHTML = '<span>📤</span>';
    sendButton.disabled = false;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
```

---

## 🚀 Instrucciones de Uso

### 1. Entrenar el Modelo
```bash
rasa train
```

### 2. Iniciar Servicios
```bash
# Terminal 1: Servidor de acciones
rasa run actions

# Terminal 2: Servidor Rasa
rasa shell

# Terminal 3: Servidor web
python web_server.py
```

### 3. Probar
- Abrir `http://localhost:8080`
- Probar consultas como:
  - "Busco una laptop para programación"
  - "¿Cuál me recomiendas?"
  - "¿Tienes laptops de Dell?"

---

## 📁 Estructura del Proyecto
```
ChatBot/
├── actions/
│   ├── __init__.py
│   └── accesories.py
│   ├── actions.py
│   └── comparisons.py
│   ├── recommendations.py
│   └── usos.json
├── data/
│   ├── nlu.yml
│   ├── rules.yml
│   └── stories.yml
├── web_interface/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── config.yml
├── domain.yml
├── endpoints.yml
├── web_server.py
└── README.md
```

---

**Documento preparado por:** Reyes Vinces Jeremy Daniel, Muñoz Miranda Felix Anthony, Anchundia Lucas Eduardo Jesus 
**Fecha:** Agosto 2025
**Versión:** 2.0 - Completa 