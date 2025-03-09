import threading

from services.IDGenerator import IDGenerator


class IDPool:
    def __init__(self, generator: IDGenerator):
        self.generator = generator
        self.next_id = 0
        self.recycled = set()
        self.lock = threading.Lock()

    def acquire(self):
        """获取一个可用的 ID，优先使用回收池中的 ID"""
        with self.lock:
            if self.recycled:
                return self.recycled.pop()  # 取出一个回收的 ID（无序）
            else:
                next_id = self.generator.encode(self.next_id)
                self.next_id += 1
                return next_id

    def release(self, recycled_id: str):
        """释放一个 ID，放入回收池"""
        with self.lock:
            if recycled_id not in self.recycled:
                self.recycled.add(recycled_id)

    def release_batch(self, ids):
        """批量释放多个 ID"""
        with self.lock:
            valid_ids = {recycled_id for recycled_id in ids if recycled_id not in self.recycled}
            self.recycled.update(valid_ids)
