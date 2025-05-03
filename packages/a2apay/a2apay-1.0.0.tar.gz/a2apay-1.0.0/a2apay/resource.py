class ResourceProvider:
    def __init__(self, name: str, wallet):
        self.name = name
        self.wallet = wallet
        self.resources = {}

    def set_resource(self, resource_id: str, price: int, data):
        self.resources[resource_id] = {"price": price, "data": data}

    def get_price(self, resource_id):
        return self.resources[resource_id]["price"]

    def provide(self, resource_id):
        return self.resources[resource_id]["data"]
