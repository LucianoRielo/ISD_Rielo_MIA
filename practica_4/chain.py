import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any

# =========================
# Strategy: descuentos
# =========================
class DiscountStrategy(ABC):
    @abstractmethod
    def compute_amount(self, subtotal: float) -> float:
        ...

class NoDiscount(DiscountStrategy):
    def compute_amount(self, subtotal: float) -> float:
        return 0.0

class Student10(DiscountStrategy):
    def compute_amount(self, subtotal: float) -> float:
        return 0.10 * subtotal

class BlackFriday30(DiscountStrategy):
    def compute_amount(self, subtotal: float) -> float:
        return 0.30 * subtotal

def discount_factory(code: str) -> DiscountStrategy:
    mapping = {
        "": NoDiscount(),
        None: NoDiscount(),
        "student": Student10(),
        "black_friday": BlackFriday30(),
    }
    return mapping.get(code, NoDiscount())

# =========================
# Chain of Responsibility: impuestos por ítem
# =========================
class TaxHandler(ABC):
    def __init__(self):
        self._next: Optional["TaxHandler"] = None

    def set_next(self, nxt: "TaxHandler") -> "TaxHandler":
        self._next = nxt
        return nxt

    def handle(self, item: Dict[str, Any], net_price: float) -> float:
        """Devuelve el impuesto TOTAL del ítem tras pasar por toda la cadena."""
        tax_here = self._apply(item, net_price)
        if self._next:
            return tax_here + self._next.handle(item, net_price)
        return tax_here

    @abstractmethod
    def _apply(self, item: Dict[str, Any], net_price: float) -> float:
        ...

class VAT20Handler(TaxHandler):
    """IVA 20% a todo excepto food_item."""
    def _apply(self, item: Dict[str, Any], net_price: float) -> float:
        if item["product_category"] != "food_item":
            return 0.20 * net_price
        return 0.0

class ImportDuty30Handler(TaxHandler):
    """Derechos de importación 30% para imported_car, cellphone, computer."""
    IMPORTED = {"imported_car", "cellphone", "computer"}

    def _apply(self, item: Dict[str, Any], net_price: float) -> float:
        if item["product_category"] in self.IMPORTED:
            return 0.30 * net_price
        return 0.0

def build_tax_chain() -> TaxHandler:
    head = VAT20Handler()
    head.set_next(ImportDuty30Handler())
    return head

# =========================
# Facturación principal
# =========================
def facturar(compra: Dict[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = compra["items"]
    discount_code = compra.get("discount", "")

    # 1) Subtotal bruto
    subtotal = sum(float(it["price"]) for it in items)

    # 2) Descuento (Strategy)
    disc_strategy = discount_factory(discount_code)
    applied_discount = disc_strategy.compute_amount(subtotal)

    # 3) Precio neto total tras descuento
    net_total = subtotal - applied_discount
    if net_total < 0:
        net_total = 0.0

    # 4) Prorratear el descuento por ítem (para calcular impuestos sobre neto)
    #    (Si prefieres impuestos sobre bruto, usa item_net_price = item_price)
    tax_chain = build_tax_chain()
    item_taxes = []
    total_taxes = 0.0

    # evitar división por cero
    if subtotal == 0:
        shares = [0.0 for _ in items]
    else:
        shares = [float(it["price"]) / subtotal for it in items]

    for it, share in zip(items, shares):
        item_price = float(it["price"])
        item_net_price = net_total * share  # <- calcula impuesto sobre precio neto con descuento
        tax_amount = tax_chain.handle(it, item_net_price)
        item_taxes.append({"id": it["id"], "tax": round(tax_amount, 2)})
        total_taxes += tax_amount

    final_total = net_total + total_taxes

    return {
        "subtotal": round(subtotal, 2),
        "applied_discount": round(applied_discount, 2),
        "item_taxes": item_taxes,
        "total_taxes": round(total_taxes, 2),
        "final_total": round(final_total, 2),
    }

# =========================
# Ejecución ejemplo
# =========================
if __name__ == "__main__":
    # Ejemplo de lectura (ajusta la ruta)
    with open("./data/compra_1.json", "r") as f:
        compra = json.load(f)
    factura = facturar(compra)
    print(json.dumps(factura, indent=2, ensure_ascii=False))
