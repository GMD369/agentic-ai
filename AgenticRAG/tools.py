# tools.py
from typing import Optional
from crewai.tools import BaseTool

class TextTool(BaseTool):
    """Concrete BaseTool for a local text knowledge base."""

    # Annotated overrides (pydantic requires annotations when overriding)
    name: str = "local_knowledge_base"
    description: str = "Local text file used as a knowledge base"

    # Model fields
    content: str
    max_return_chars: int = 2000

    def __init__(self, content: str, max_return_chars: int = 2000, **data):
        """
        Pass required model fields into super().__init__ so pydantic validates them.
        Any additional BaseTool fields can be provided via **data.
        """
        # Provide model fields to pydantic's initializer
        super().__init__(content=content, max_return_chars=max_return_chars, **data)
        # If you need to ensure attributes are set explicitly, you could still use:
        # object.__setattr__(self, "content", content)
        # object.__setattr__(self, "max_return_chars", max_return_chars)

    def _run(self, query: str) -> str:
        if not query or not query.strip():
            return self.content[: self.max_return_chars]

        qtokens = [t.lower() for t in query.split() if t.strip()]
        paras = [p.strip() for p in self.content.split("\n\n") if p.strip()]

        matched = []
        for p in paras:
            pl = p.lower()
            if any(q in pl for q in qtokens):
                matched.append(p)

        if matched:
            return ("\n\n".join(matched))[: self.max_return_chars]

        return self.content[: self.max_return_chars]

    async def _arun(self, query: str) -> str:
        return self._run(query)

    # Optional wrappers some SDK variants expect
    def run(self, query: str) -> str:
        return self._run(query)

    async def arun(self, query: str) -> str:
        return await self._arun(query)
 