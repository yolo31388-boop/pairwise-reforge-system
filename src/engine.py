"""装备洗练 - 带7个bug"""
from dataclasses import dataclass, field
import random

@dataclass
class Equipment:
    eid: str
    slot: str
    stats: dict
    reforge_count: int = 0

class ReforgeSystem:
    def __init__(self):
        self.equipment: dict[str, Equipment] = {}
        self.stat_pool = ["attack", "defense", "hp", "crit", "speed"]  # bug1: 全局池
        self.pity = {}  # bug3: 全局保底
        self.locked_stats = set()

    def reforge(self, eid):
        eq = self.equipment[eid]
        # bug1: 不按部位过滤
        new_stats = {}
        for i in range(3):
            stat = random.choice(self.stat_pool)
            # bug7: 可重复
            new_stats[stat] = random.randint(1, 100)
        # bug4: 均匀随机
        # bug5: 无预览
        eq.stats = new_stats
        eq.reforge_count += 1
        return new_stats

    def lock_stat(self, eid, stat):
        self.locked_stats.add(stat)
        # bug2: 固定消耗
        return 10

    def get_pity(self, eid):
        # bug3: 全局
        return self.pity.get("global", 0)
