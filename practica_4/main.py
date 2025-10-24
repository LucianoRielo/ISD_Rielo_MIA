import json

def facturacion(compra):

    taxes = {
        "food_item"     :   [],
        "cellphone"     :   [0.2, 0.3],
        "computer"      :   [0.2, 0.3],
        "car"           :   [0.2],
        "imported_car"  :   [0.2, 0.3],
    }

    discounts = {
        "student"     :   0.1,
        "black_friday":   0.3
    }

    factura = {
            "subtotal": 0.0,               ###
            "applied_discount": 0.0,       ###
            "item_taxes": [],              ###
            "total_taxes": 0.0,            ###
            "final_total": 0.0
            }
    

    for item in compra["items"]:

        item_id = item["id"]
        item_price = item["price"]
        item_category = item["product_category"]
        item_taxes_per = sum(tax for tax in taxes[item_category])
        item_tax = item_taxes_per * item_price

        factura["subtotal"] += item_price
        factura["total_taxes"] += item_tax
        factura["item_taxes"].append({"id": item_id, "taxes": item_tax})

    factura["applied_discount"] = discounts[compra["discount"]]
    factura["final_total"]     = factura["subtotal"] + factura["total_taxes"]



    return factura


if __name__ == "__main__":


    with open("./data/compra_1.json", "r") as file:
        compra = json.load(file)
    
    factura = facturacion(compra)

    print(factura)