import urllib.request
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

os.makedirs('static/images/ropa/hombre', exist_ok=True)
os.makedirs('static/images/ropa/mujer', exist_ok=True)

imagenes_hombre = {
    'camisa_oxford.png': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=400&fit=crop',
    'camisa_denim.png': 'https://images.unsplash.com/photo-1589310243389-96a5483213a8?w=300&h=400&fit=crop',
    'playera_negra.png': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=400&fit=crop',
    'playera_estampada.png': 'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=300&h=400&fit=crop',
    'jeans_slim.png': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=400&fit=crop',
    'chinos_caqui.png': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=300&h=400&fit=crop',
    'bomber.png': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=400&fit=crop',
    'derby.png': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=300&h=400&fit=crop',
}

imagenes_mujer = {
    'blusa_seda.png': 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=300&h=400&fit=crop',
    'camisa_oversize.png': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=400&fit=crop',
    'crop_top.png': 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=300&h=400&fit=crop',
    'vestido_floral.png': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300&h=400&fit=crop',
    'vestido_negro.png': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=300&h=400&fit=crop',
    'falda_midi.png': 'https://images.unsplash.com/photo-1583496661160-fb5886a0ujf1?w=300&h=400&fit=crop',
    'jeans_mom.png': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&h=400&fit=crop',
    'trench.png': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300&h=400&fit=crop',
    'zapatillas.png': 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=300&h=400&fit=crop',
    'tacones_nude.png': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=300&h=400&fit=crop',
}

def descargar(url, ruta):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(ruta, 'wb') as f:
                f.write(response.read())
        print(f"✅ {ruta}")
        return True
    except Exception as e:
        print(f"❌ Error: {ruta} - {e}")
        return False

print("🎨 Descargando imágenes...")

for nombre, url in imagenes_hombre.items():
    descargar(url, f'static/images/ropa/hombre/{nombre}')

for nombre, url in imagenes_mujer.items():
    descargar(url, f'static/images/ropa/mujer/{nombre}')

print("✅ ¡Listo!")