"""装备洗练系统"""
from dataclasses import dataclass, field
import random

# 各装备部位可用的属性池（按部位严格过滤）
SLOT_STAT_POOLS = {
    "weapon": ["attack", "crit", "speed"],
    "necklace": ["attack", "crit", "hp"],
    "ring": ["attack", "crit", "speed"],
    "armor": ["defense", "hp", "speed"],
    "helmet": ["defense", "hp"],
    "boots": ["defense", "hp", "speed"],
}
DEFAULT_STAT_POOL = ["attack", "defense", "hp", "crit", "speed"]

# 条目数配置范围
MIN_ENTRIES = 2
MAX_ENTRIES = 4

# 属性值范围与高品质线
VALUE_MIN = 1
VALUE_MAX = 100
HIGH_VALUE = 80

# 锁定消耗：第 n 条锁定的费用 = LOCK_BASE_COST * n
LOCK_BASE_COST = 10

# 保底：连续 PITY_THRESHOLD 次未出高品质属性则必出一条（按装备独立计数）
PITY_THRESHOLD = 10


@dataclass
class Equipment:
    eid: str
    slot: str
    stats: dict
    reforge_count: int = 0


class ReforgeSystem:
    def __init__(self):
        self.equipment: dict[str, Equipment] = {}
        self.pity: dict[str, int] = {}  # 保底按装备独立计数
        self.locked_stats: dict[str, set] = {}  # 每件装备各自锁定的属性
        self._pending: dict[str, dict] = {}  # 洗练预览（未确认前不生效）

    def _pool_for(self, eq: Equipment) -> list:
        return list(SLOT_STAT_POOLS.get(eq.slot, DEFAULT_STAT_POOL))

    def _roll_value(self, force_high: bool = False) -> int:
        if force_high:
            return random.randint(HIGH_VALUE, VALUE_MAX)
        # 正态分布：中间值概率高，极值概率低
        mean = (VALUE_MIN + VALUE_MAX) / 2
        std = (VALUE_MAX - VALUE_MIN) / 6
        value = int(round(random.gauss(mean, std)))
        return max(VALUE_MIN, min(VALUE_MAX, value))

    def _generate(self, eq: Equipment) -> dict:
        locked = self.locked_stats.get(eq.eid, set())
        new_stats = {s: v for s, v in eq.stats.items() if s in locked}
        # 可用池：按部位过滤，且排除已锁定/已有的属性，保证不重复
        available = [s for s in self._pool_for(eq) if s not in new_stats]
        # 条目数在配置范围内随机（含已锁定条目）
        total = random.randint(MIN_ENTRIES, MAX_ENTRIES)
        total = max(total, len(locked))
        total = min(total, len(locked) + len(available))
        count = total - len(new_stats)
        # 保底判定：连续未出高品质达到阈值则必出一条
        force_high = self.pity.get(eq.eid, 0) + 1 >= PITY_THRESHOLD
        chosen = random.sample(available, min(count, len(available)))
        for i, stat in enumerate(chosen):
            new_stats[stat] = self._roll_value(force_high and i == 0)
        return new_stats

    def preview_reforge(self, eid) -> dict:
        """生成洗练预览，玩家确认前不影响装备当前属性"""
        eq = self.equipment[eid]
        candidate = self._generate(eq)
        self._pending[eid] = candidate
        return candidate

    def confirm_reforge(self, eid) -> dict:
        """接受预览结果，替换装备属性"""
        eq = self.equipment[eid]
        new_stats = self._pending.pop(eid, None)
        if new_stats is None:
            new_stats = self._generate(eq)
        eq.stats = new_stats
        eq.reforge_count += 1
        if any(v >= HIGH_VALUE for v in new_stats.values()):
            self.pity[eid] = 0
        else:
            self.pity[eid] = self.pity.get(eid, 0) + 1
        return new_stats

    def cancel_reforge(self, eid) -> dict:
        """放弃预览结果，保留原属性"""
        self._pending.pop(eid, None)
        return self.equipment[eid].stats

    def reforge(self, eid) -> dict:
        """预览并直接确认（等价于 preview + confirm）"""
        self.preview_reforge(eid)
        return self.confirm_reforge(eid)

    def lock_stat(self, eid, stat) -> int:
        locked = self.locked_stats.setdefault(eid, set())
        locked.add(stat)
        # 消耗随该装备已锁定数量递增
        return LOCK_BASE_COST * len(locked)

    def unlock_stat(self, eid, stat):
        self.locked_stats.get(eid, set()).discard(stat)

    def get_pity(self, eid) -> int:
        return self.pity.get(eid, 0)
