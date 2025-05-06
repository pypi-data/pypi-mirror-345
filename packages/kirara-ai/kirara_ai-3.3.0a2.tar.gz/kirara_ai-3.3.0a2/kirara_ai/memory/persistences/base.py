import threading
from abc import ABC, abstractmethod
from queue import Empty, Queue
from typing import List, Tuple

from kirara_ai.logger import get_logger
from kirara_ai.memory.entry import MemoryEntry


class MemoryPersistence(ABC):
    """持久化层抽象类"""

    @abstractmethod
    def save(self, scope_key: str, entries: List[MemoryEntry]) -> None:
        pass

    @abstractmethod
    def load(self, scope_key: str) -> List[MemoryEntry]:
        pass

    @abstractmethod
    def flush(self) -> None:
        """确保所有数据都已持久化"""

logger = get_logger("MemoryPersistence")
class AsyncMemoryPersistence:
    """异步持久化管理器"""

    def __init__(self, persistence: MemoryPersistence):
        self.persistence = persistence
        self.queue: Queue[Tuple[str, List[MemoryEntry]]] = Queue()
        self.running = True
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def _worker(self):
        while self.running:
            try:
                scope_key, entries = self.queue.get(timeout=1)
                self.persistence.save(scope_key, entries)
                self.queue.task_done()
                logger.info(f"Saved {scope_key} with {len(entries)} entries")
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error saving memory: {e}")
                continue

    def load(self, scope_key: str) -> List[MemoryEntry]:
        return self.persistence.load(scope_key)

    def save(self, scope_key: str, entries: List[MemoryEntry]):
        self.queue.put((scope_key, entries))

    def stop(self):
        self.running = False
        self.worker.join()
        self.persistence.flush()
