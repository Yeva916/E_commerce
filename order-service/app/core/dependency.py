import httpx
from app.services.product_client import ProductClient

# The global singletons container dictionary
clients_state = {}

def get_http_client() -> httpx.AsyncClient:
    """Dependency injection target to fetch the open connection pool"""
    return clients_state["async_client"]

def get_product_client() -> ProductClient:
    """Dependency injection target to fetch the reusable ProductClient wrapper"""
    return clients_state["product_client"]