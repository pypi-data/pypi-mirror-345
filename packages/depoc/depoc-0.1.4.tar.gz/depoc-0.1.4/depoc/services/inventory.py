from depoc.resources.methods import Create, Retrieve, Update, Delete
from depoc.objects.inventory import InventoryObject, InventoryTransctionObject


class Inventory(Retrieve[InventoryObject]):
    obj = InventoryObject
    endpoint = 'products/inventory'
    label = 'inventory'


class ProductInventory(Retrieve[InventoryObject], Update[InventoryObject]):
    obj = InventoryObject
    endpoint = 'products/<id>/inventory'
    label = 'inventory'


class InventoryTransaction(
    Create[InventoryTransctionObject],
    Retrieve[InventoryTransctionObject],
    Update[InventoryTransctionObject],
    Delete[InventoryTransctionObject],
):
    obj = InventoryTransctionObject
    endpoint = 'products/<id>/inventory/transactions'
    label = 'transaction'
