class Agent:
    def __init__(self, name: str, wallet):
        self.name = name
        self.wallet = wallet

    def handle_request(self, task):
        if task["action"] == "translate":
            return {"result": f"Translated({task['text']}) to {task['lang']}"}
        return {"result": "Unknown task."}

    def request_task(self, target_agent, task, price: int):
        result = target_agent.handle_request(task)
        self.wallet.send(target_agent.wallet, price, memo="Payment for task")
        return result
