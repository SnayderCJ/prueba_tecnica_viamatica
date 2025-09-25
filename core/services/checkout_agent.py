import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END

# Importar modelos de Django
from core.models import Cart, Invoice, User

# Cargar variables de entorno
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# --- Definición del Estado del Grafo ---
class AgentState(TypedDict):
    user_id: int
    cart_id: int
    cart_total: float
    payment_successful: bool
    invoice_id: int | None # Puede ser un entero o None al inicio
    error: bool
    message: str

# --- Nodos del Grafo ---

def get_cart_details(state: AgentState) -> AgentState:
    print("--- 💵 Obteniendo detalles del carrito ---")
    try:
        cart = Cart.objects.get(id=state['cart_id'], user_id=state['user_id'], ordered=False)
        if not cart.items.exists():
            state['error'] = True
            state['message'] = "El carrito está vacío. No se puede procesar el pago."
            return state
        
        state['cart_total'] = float(cart.get_total())
        state['error'] = False
        state['message'] = "Detalles del carrito obtenidos."
        return state
    except Cart.DoesNotExist:
        state['error'] = True
        state['message'] = "No se encontró un carrito activo para este usuario."
        return state

def process_payment(state: AgentState) -> AgentState:
    print(f"--- 💳 Procesando pago por ${state['cart_total']} ---")
    # Simulación de un proceso de pago. En un caso real, aquí iría la
    # integración con una pasarela de pagos como Stripe o PayPal.
    if state['cart_total'] > 0:
        state['payment_successful'] = True
        state['message'] = "Pago procesado exitosamente."
    else:
        state['payment_successful'] = False
        state['error'] = True
        state['message'] = "El total del carrito es cero, no se puede procesar el pago."
    return state

def create_invoice(state: AgentState) -> AgentState:
    print("--- 🧾 Creando factura ---")
    try:
        user = User.objects.get(id=state['user_id'])
        cart = Cart.objects.get(id=state['cart_id'])
        
        # Crear la factura en la base de datos
        invoice = Invoice.objects.create(
            user=user,
            total_amount=state['cart_total']
        )
        
        # Marcar el carrito como "comprado"
        cart.ordered = True
        cart.save()
        
        # --- ESTA ES LA LÍNEA CLAVE QUE FALTABA ---
        state['invoice_id'] = invoice.id 
        
        state['message'] = f"Factura #{invoice.id} creada y carrito cerrado."
        return state
    except Exception as e:
        state['error'] = True
        state['message'] = f"Error al crear la factura: {e}"
        return state

def handle_error(state: AgentState) -> AgentState:
    print(f"--- ❌ Error manejado: {state['message']} ---")
    return state

# --- Lógica Condicional del Grafo ---

def decide_next_step(state: AgentState) -> str:
    if state.get('error'):
        return "handle_error"
    if not state.get('payment_successful'):
        return "process_payment"
    return "create_invoice"

# --- Construcción y Ejecución del Grafo ---

def run_checkout_agent(user_id: int, cart_id: int) -> dict:
    workflow = StateGraph(AgentState)

    workflow.add_node("get_cart_details", get_cart_details)
    workflow.add_node("process_payment", process_payment)
    workflow.add_node("create_invoice", create_invoice)
    workflow.add_node("handle_error", handle_error)

    workflow.set_entry_point("get_cart_details")

    workflow.add_conditional_edges(
        "get_cart_details",
        lambda state: "handle_error" if state.get("error") else "process_payment"
    )
    workflow.add_conditional_edges(
        "process_payment",
        lambda state: "handle_error" if state.get("error") else "create_invoice"
    )

    workflow.add_edge('create_invoice', END)
    workflow.add_edge('handle_error', END)

    app = workflow.compile()

    inputs = {"user_id": user_id, "cart_id": cart_id}
    final_state = app.invoke(inputs)

    return final_state