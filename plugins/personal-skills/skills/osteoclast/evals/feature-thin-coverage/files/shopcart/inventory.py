from abc import ABC, abstractmethod


class InventoryRepository(ABC):
    @abstractmethod
    def on_hand(self, sku):
        ...


class InMemoryInventory(InventoryRepository):
    def __init__(self, counts=None):
        self._counts = dict(counts or {})

    def on_hand(self, sku):
        return self._counts.get(sku, 0)


def can_fulfil(inventory, lines):
    return all(inventory.on_hand(line.sku) >= line.qty for line in lines)
