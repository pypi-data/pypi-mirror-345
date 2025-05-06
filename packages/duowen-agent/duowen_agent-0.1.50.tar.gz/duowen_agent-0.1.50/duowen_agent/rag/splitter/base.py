from abc import ABC, abstractmethod
from typing import List

from duowen_agent.rag.models import Document
from duowen_agent.utils.concurrency import run_in_threadpool


class BaseChunk(ABC):

    @abstractmethod
    def chunk(self, text: str) -> List[Document]:
        raise NotImplementedError

    async def achunk(self, text: str) -> List[Document]:
        result = await run_in_threadpool(self.chunk, text)  # 折中方案，建议继承重写
        return result
