import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DiscountStrategy(ABC):
    @abstractmethod
    def rate(self) -> float:
        ...

class NoDiscount(DiscountStrategy):
    def rate(self) -> float:
        return 0.0

class StudentDiscount(DiscountStrategy):
    def rate(self) -> float:
        return 0.10

class BlackFridayDiscount(DiscountStrategy):
    def rate(self) -> float:
        return 0.30

def make_discount_strategy(name: str) -> DiscountStrategy:
    discounts = {
        None: NoDiscount(),
        "student": StudentDiscount(),
        "black_friday": BlackFridayDiscount(),
    }
    return discounts.get(name, NoDiscount())

# --------- Tax Strategies ---------
class TaxStrategy(ABC):
    @abstractmethod
    def tax_for(self, price: float, category: str) -> float:
        ...

class VATStrategy(TaxStrategy):
    """IVA 20% excepto food_item."""
    VAT_RATE = 0.20
    def tax_for(self, price: float, category: str) -> float:
        if category == "food_item":
            return 0.0
        return price * self.VAT_RATE

class ImportDutyStrategy(TaxStrategy):
    """Derechos 30% para imported_car, cellphone, computer."""
    DUTY_RATE = 0.30
    IMPORTED = {"imported_car", "cellphone", "computer"}
    def tax_for(self, price: float, category: str) -> float:
        return price * self.DUTY_RATE if category in self.IMPORTED else 0.0

class CompositeTaxStrategy(TaxStrategy):
    def __init__(self, strategies: List[TaxStrategy]):
        self._strategies = strategies
    def tax_for(self, price: float, category: str) -> float:
        return sum(s.tax_for(price, category) for s in self._strategies)

def make_tax_strategy() -> TaxStrategy:
    # Podés agregar más estrategias sin tocar el core
    return CompositeTaxStrategy([VATStrategy(), ImportDutyStrategy()])

# --------- Core billing (orquestador) ---------
def facturacion(compra: Dict[str, Any]) -> Dict[str, Any]:
    items = compra.get("items", [])
    discount_strategy = make_discount_strategy(compra.get("discount"))
    tax_strategy = make_tax_strategy()

    # 1) Subtotal
    subtotal = sum(float(i["price"]) for i in items)

    # 2) Descuento (monto)
    disc_rate = discount_strategy.rate()
    applied_discount = subtotal * disc_rate

    # 3) Precio descontado por ítem (proporcional)
    #    Si quisieras impuestos ANTES del descuento, reemplazá 'price_after_disc' por 'price'
    item_taxes = []
    total_taxes = 0.0

    for it in items:
        price = float(it["price"])
        category = it["product_category"]
        price_after_disc = price * (1.0 - disc_rate)
        tax_amount = tax_strategy.tax_for(price_after_disc, category)
        total_taxes += tax_amount
        item_taxes.append({"id": it["id"], "tax": round(tax_amount, 2)})

    final_total = (subtotal - applied_discount) + total_taxes

    return {
        "subtotal": round(subtotal, 2),
        "applied_discount": round(applied_discount, 2),
        "item_taxes": item_taxes,
        "total_taxes": round(total_taxes, 2),
        "final_total": round(final_total, 2),
    }

# --------- Demo ---------
if __name__ == "__main__":
    with open("./data/compra_1.json", "r") as f:
        compra = json.load(f)
    factura = facturacion(compra)
    print(json.dumps(factura, indent=2, ensure_ascii=False))
