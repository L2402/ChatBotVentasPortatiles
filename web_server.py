from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Configurar la carpeta de templates
app.template_folder = 'web_interface'
app.static_folder = 'web_interface'

@app.route('/')
def index():
    return send_from_directory('web_interface', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('web_interface', filename)

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'ChatBot Web Interface is running'}

if __name__ == '__main__':
    print("🚀 Iniciando servidor web del ChatBot...")
    print("📱 Interfaz disponible en: http://localhost:8080")
    print("🌐 Para acceso público, ejecuta: ngrok http 8080")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True) 