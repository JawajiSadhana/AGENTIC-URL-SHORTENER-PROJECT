class CostTracker:
    def __init__(self):
        self.cost_per_1k = {"gpt-4o": 0.03, "gpt-4o-mini": 0.00015}
        self.total_cost = 0.0
        self.usage_log = []

    def log(self, step, model, prompt_tokens, completion_tokens):
        tokens = prompt_tokens + completion_tokens
        cost = (tokens / 1000) * self.cost_per_1k.get(model, 0)
        self.total_cost += cost
        self.usage_log.append({"step": step, "model": model, "tokens": tokens, "cost": cost})
        print(f"[{step}] {model} | {tokens} tokens | ${cost:.5f}")

    def summary(self):
        return {"total_cost": round(self.total_cost, 5), "steps": self.usage_log}

cost_tracker = CostTracker()
MAX_RETRIES = 3
BUDGET_LIMIT = 1.00