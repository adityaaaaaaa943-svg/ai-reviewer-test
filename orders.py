import threading

inventory = {"item1": 10, "item2": 5}
lock_free_counter = 0

def place_order(item, quantity):
    global lock_free_counter
    if inventory.get(item, 0) >= quantity:
        inventory[item] -= quantity
        lock_free_counter += 1
        return True
    return False

def bulk_order(items):
    threads = []
    for item, qty in items.items():
        t = threading.Thread(target=place_order, args=(item, qty))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def apply_coupon(price, code):
    coupons = {"SAVE10": 0.1, "SAVE20": 0.2}
    discount = coupons.get(code, 0)
    return price - (price * discount)