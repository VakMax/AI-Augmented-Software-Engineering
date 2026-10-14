import pytest

from shopcart import Cart


def test_empty_cart_total_is_zero():
    assert Cart().total() == 0


def test_add_single_item():
    cart = Cart()
    cart.add_item("MUG")
    assert cart.items == {"MUG": 1}
    assert cart.subtotal() == 1200


def test_add_same_item_twice_increments_quantity():
    cart = Cart()
    cart.add_item("MUG")
    cart.add_item("MUG", 2)
    assert cart.items == {"MUG": 3}


def test_remove_item_decrements_then_deletes():
    cart = Cart()
    cart.add_item("CAP", 2)
    cart.remove_item("CAP")
    assert cart.items == {"CAP": 1}
    cart.remove_item("CAP")
    assert cart.items == {}


def test_unknown_sku_raises():
    with pytest.raises(ValueError):
        Cart().add_item("NOPE")


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        Cart().apply_code("FREESTUFF")


def test_total_includes_tax():
    cart = Cart()
    cart.add_item("TEE")
    assert cart.total() == 2759  # (2000 + 8% tax) + $5.99 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + $5.99 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + $5.99 shipping


def test_free_shipping_threshold():
    cart = Cart()
    cart.add_item("TEE", 3)  # 6000 cents >= $50.00 threshold
    assert cart.subtotal() == 6000
    # 6000 + 8% tax = 6480, shipping is free (0)
    assert cart.total() == 6480


def test_empty_cart_shipping_is_zero():
    cart = Cart()
    assert cart.total() == 0


def test_shipping_is_not_taxed():
    cart = Cart()
    cart.add_item("MUG")  # 1200 cents, subtotal < 5000 -> $5.99 (599 cents) shipping
    # subtotal = 1200, taxed = round(1200 * 1.08) = 1296
    # shipping = 599 (not taxed)
    # total = 1296 + 599 = 1895
    assert cart.total() == 1895
