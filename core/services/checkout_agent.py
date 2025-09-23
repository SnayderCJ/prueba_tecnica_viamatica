import os
import django
from ..models import Cart, Invoice, User, CartItem
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'viamatica_project.settings')
django.setup()

class AgentState(TypedDict):
    user_id: int
    cart_id: int
    invoice_id: int | None # Puede que al inicio no exista
    message: str           # Mensaje final para el usuario
    error: bool            # Para saber si ocurrió un error

# --- 2. Definición de los Nodos (Funciones) ---
# Cada nodo es un paso en nuestro proceso de checkout.

def validate_cart(state: AgentState):
    """
    Nodo 1: Valida que el carrito exista, pertenezca al usuario y no esté vacío.
    """
    print("--- NODO: Validando Carrito ---")
    cart_id = state['cart_id']
    user_id = state['user_id']
    error_message = ""
    
    try:
        cart = Cart.objects.get(id=cart_id, user_id=user_id)
        if cart.ordered:
            error_message = "Este carrito ya fue procesado."
        elif not cart.items.exists():
            error_message = "El carrito está vacío."
    except Cart.DoesNotExist:
        error_message = "El carrito no fue encontrado."

    if error_message:
        print(f"Error de validación: {error_message}")
        return {"error": True, "message": error_message}
    
    print("Validación exitosa.")
    return {"error": False}

def create_invoice(state: AgentState):
    """
    Nodo 2: Crea la factura en la base de datos.
    """
    print("--- NODO: Creando Factura ---")
    cart = Cart.objects.get(id=state['cart_id'])
    
    # Creamos la factura con los datos del carrito
    invoice = Invoice.objects.create(
        user_id=state['user_id'],
        total_amount=cart.get_total()
    )
    
    # Aquí podrías agregar lógica para guardar los InvoiceItems si los tuvieras.
    
    print(f"Factura #{invoice.id} creada.")
    return {"invoice_id": invoice.id}

def update_cart_status(state: AgentState):
    """
    Nodo 3: Marca el carrito como "procesado" para que no se pueda volver a usar.
    """
    print("--- NODO: Actualizando Estado del Carrito ---")
    cart = Cart.objects.get(id=state['cart_id'])
    cart.ordered = True
    cart.save()
    print(f"Carrito #{cart.id} marcado como 'ordenado'.")
    return {} # No es necesario actualizar el estado aquí

def generate_final_response(state: AgentState):
    """
    Nodo 4: Genera el mensaje final que se devolverá al usuario.
    """
    print("--- NODO: Generando Respuesta Final ---")
    if state['error']:
        # Si hubo un error en la validación, el mensaje ya está en el estado.
        return {"message": state['message']}

    message = f"Compra completada con éxito. Factura #{state['invoice_id']} generada."
    return {"message": message}

# --- 3. Definición de las Conexiones (Edges) ---

def decide_next_step(state: AgentState):
    """
    Esta función decide a qué nodo ir después de la validación.
    Si hay un error, va directo al final. Si no, continúa el proceso.
    """
    print("--- DECISIÓN: ¿Hubo un error en la validación? ---")
    if state['error']:
        print("Resultado: SÍ. Yendo a generar respuesta de error.")
        return "end_process" # Nombre de la ruta hacia el final
    else:
        print("Resultado: NO. Continuando para crear factura.")
        return "continue_process" # Nombre de la ruta para continuar

# --- 4. Construcción del Grafo ---

# Creamos una instancia del grafo y le decimos cuál es nuestro objeto de estado.
workflow = StateGraph(AgentState)

# Añadimos los nodos
workflow.add_node("validate_cart", validate_cart)
workflow.add_node("create_invoice", create_invoice)
workflow.add_node("update_cart_status", update_cart_status)
workflow.add_node("generate_response", generate_final_response)

# Definimos el flujo
workflow.set_entry_point("validate_cart")

# Creamos la conexión condicional (la bifurcación)
workflow.add_conditional_edges(
    "validate_cart",
    decide_next_step,
    {
        "continue_process": "create_invoice",
        "end_process": "generate_response"
    }
)

# Conectamos el resto de los pasos en secuencia
workflow.add_edge('create_invoice', 'update_cart_status')
workflow.add_edge('update_cart_status', 'generate_response')
workflow.add_edge('generate_response', END) # El final del flujo

# Compilamos el grafo para poder usarlo
app = workflow.compile()

# --- 5. Función Principal para Llamar desde Django ---

def run_checkout_agent(user_id: int, cart_id: int):
    """
    Esta es la función que importarás y llamarás desde tu `views.py`.
    """
    inputs = {"user_id": user_id, "cart_id": cart_id}
    # .stream() ejecuta el grafo y devuelve los resultados de cada paso.
    # El último resultado es el estado final.
    final_state = None
    for s in app.stream(inputs):
        final_state = s
    
    # Devolvemos el último estado que contiene el mensaje final
    # Accedemos a la clave del primer (y único) nodo en el estado final
    key, value = list(final_state.items())[0]
    return value