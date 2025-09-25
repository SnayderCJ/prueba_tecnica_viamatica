# 🛒 E-commerce con Agente IA 🤖

✨ *Descripción*

¡Bienvenido a la tienda online inteligente! Este proyecto es una aplicación full-stack de e-commerce desarrollada con Django, que va más allá de una tienda tradicional al integrar un **agente de IA con LangGraph** para gestionar de forma autónoma y robusta todo el proceso de checkout. 🚀

Con este sistema, he puesto en práctica conocimientos avanzados en desarrollo web con Python, creando no solo un frontend interactivo con **Tailwind CSS**, sino también un backend con una API RESTful y una capa de lógica inteligente que simula procesos de negocio complejos.

---
🚀 *Características Principales*

* **Gestión de Usuarios:** Sistema completo de registro e inicio de sesión.
* **Catálogo de Productos:** Visualización de productos con imágenes, búsqueda por nombre y filtro por categorías.
* **Carrito de Compras Interactivo:** Añade productos, incrementa/decrementa la cantidad y elimina items, todo con una interfaz fluida.
* **Checkout con IA:** Al proceder al pago, un agente de LangGraph orquesta la validación, simula el procesamiento del pago y genera la factura final.
* **Confirmación de Compra:** Tras un pago exitoso, el usuario es redirigido a una página de confirmación con los detalles de su factura.
* **Diseño Responsivo:** La interfaz se adapta perfectamente a dispositivos móviles y de escritorio gracias a Tailwind CSS.

---
🛠️ *Tecnologías Utilizadas*

* **Backend:**
    * **Django:** El sólido framework web de Python que impulsa la aplicación.
    * **Django REST Framework:** Para la construcción de la API.
    * **LangChain & LangGraph:** Para la creación del agente de IA que maneja el checkout.
* **Frontend:**
    * **HTML & Django Templates:** Para la estructura y renderizado del contenido.
    * **Tailwind CSS:** Para un diseño moderno, personalizable y responsivo.
    * **Alpine.js:** Para añadir interactividad en el frontend, como los modales animados.
* **Base de Datos:**
    * **SQLite 3:** La base de datos por defecto de Django, ideal para desarrollo.
* **Librerías Clave:**
    * `djangorestframework-simplejwt` para autenticación por tokens.
    * `pillow` para el manejo de imágenes.
    * `python-dotenv` para la gestión de variables de entorno.

---
## ⚙️ Cómo Ejecutar la Aplicación

Sigue estos pasos para levantar el proyecto en un entorno local.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/SnayderCJ/prueba_tecnica_viamatica.git
    cd prueba_tecnica_viamatica
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # En Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # En Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    # Dependencias de Python
    pip install -r requirements.txt

    # Dependencias de Node.js (para Tailwind)
    npm install
    ```

4.  **Configurar las variables de entorno:**
    * Crea un archivo llamado `.env` en la raíz del proyecto.
    * Abre el archivo y añade tu clave de API de LangSmith:
    ```env
    LANGCHAIN_API_KEY="tu_api_key_de_langsmith_aqui" (Como es de prueba mande el .env)
    ```

5.  **Aplicar las migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **(Opcional) Crear un superusuario:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ejecutar los servidores (¡Necesitas 2 terminales!)**

    * **En la Terminal 1, inicia el servidor de Django:**
    ```bash
    python manage.py runserver
    ```

    * **En la Terminal 2, inicia el compilador de Tailwind:**
    ```bash
    npx @tailwindcss/cli -i core/static/css/input.css -o core/static/css/output.css --watch
    ```

8.  **¡Accede a la aplicación!**
    * Abre tu navegador web y visita: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---
## 🚀 Explora la tienda, prueba el flujo de compra y observa cómo el agente de IA gestiona el checkout. Si tienes alguna duda, ¡no dudes en contactarme! 😊