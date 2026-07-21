class Memory:
    def __init__(self):
        self._facts: list[str] = []

    def add(self, fact: str) -> None:
        self._facts.append(fact)

    def get_all(self) -> str:
        if not self._facts:
            return ""
        return "\n".join(f"- {f}" for f in self._facts)
