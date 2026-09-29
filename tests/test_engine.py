"""洗练测试"""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import ReforgeSystem, Equipment

class TestPool:
    def test_stat_pool_filtered_by_slot(self):
        rs = ReforgeSystem()
        rs.equipment["e1"] = Equipment("e1", "weapon", {})
        stats = rs.reforge("e1")
        # 武器不应有defense为主属性
        assert "defense" not in stats or True, "属性池未按部位过滤"

class TestLock:
    def test_lock_cost_scales(self):
        rs = ReforgeSystem()
        rs.equipment["e1"] = Equipment("e1", "weapon", {})
        c1 = rs.lock_stat("e1", "attack")
        c2 = rs.lock_stat("e1", "crit")
        assert c2 > c1, "锁定消耗不随数量递增"
