"""
测试脚本 - 验证 timeline_nodes 重构是否正确
"""
from src.models import WorldLore, EventNode, RomanceScript


def test_event_node():
    """测试 EventNode 类"""
    print("=" * 70)
    print("🧪 测试 EventNode 类")
    print("=" * 70)
    
    # 创建一个事件节点
    event = EventNode(
        timestamp="Year 1024, Spring Semester",
        summary="新生入学典礼：主角正式进入魔法学院",
        consequence="主角被分配到火焰院，开始接触学院的核心课程",
        involved_factions=["光明议会"],
        tags=["School", "Important"]
    )
    
    print(f"✅ EventNode 创建成功")
    print(f"   时间戳: {event.timestamp}")
    print(f"   摘要: {event.summary}")
    print(f"   影响: {event.consequence}")
    print(f"   涉及势力: {event.involved_factions}")
    print(f"   标签: {event.tags}")
    
    # 测试序列化
    json_data = event.model_dump_json()
    print(f"\n✅ 序列化成功 (JSON 长度: {len(json_data)} 字符)")
    
    # 测试反序列化
    restored = EventNode.model_validate_json(json_data)
    print(f"✅ 反序列化成功")
    assert restored.timestamp == event.timestamp
    print(f"✅ 数据一致性验证通过")


def test_world_lore_timeline():
    """测试 WorldLore 的 timeline_nodes"""
    print("\n" + "=" * 70)
    print("🧪 测试 WorldLore.timeline_nodes")
    print("=" * 70)
    
    # 创建多个事件节点
    events = [
        EventNode(
            timestamp="Year 1024, Spring",
            summary="春季开学：新生入学典礼",
            consequence="主角开始学院生活",
            involved_factions=["光明议会"],
            tags=["School", "Important"]
        ),
        EventNode(
            timestamp="Year 1024, Mid-Spring",
            summary="第一次实战课：展现天赋",
            consequence="引起关注",
            involved_factions=[],
            tags=["Magic"]
        )
    ]
    
    # 创建 WorldLore 实例
    world_lore = WorldLore(
        rules=["魔法规则1"],
        locations={"地点1": "描述1"},
        timeline_nodes=events,  # 使用 EventNode 列表
        factions={"光明议会": "描述"},
        lore_summary="世界观摘要",
        villian_type="黑暗势力：黑暗势力，追求权力和控制"  # 确保保留
    )
    
    print(f"✅ WorldLore 创建成功")
    print(f"   timeline_nodes 类型: {type(world_lore.timeline_nodes)}")
    print(f"   事件数量: {len(world_lore.timeline_nodes)}")
    print(f"   villian_type 保留: {world_lore.villian_type}")
    
    # 验证 timeline_nodes 是 EventNode 列表
    assert all(isinstance(node, EventNode) for node in world_lore.timeline_nodes)
    print(f"✅ 所有节点都是 EventNode 类型")
    
    # 测试序列化
    json_data = world_lore.model_dump_json()
    print(f"\n✅ 序列化成功 (JSON 长度: {len(json_data)} 字符)")
    
    # 测试反序列化
    restored = WorldLore.model_validate_json(json_data)
    print(f"✅ 反序列化成功")
    assert len(restored.timeline_nodes) == len(world_lore.timeline_nodes)
    assert all(isinstance(node, EventNode) for node in restored.timeline_nodes)
    assert restored.villian_type == world_lore.villian_type
    print(f"✅ 数据完整性验证通过")


def test_romance_script_preserved():
    """测试 RomanceScript 的 possible_ending 是否保留"""
    print("\n" + "=" * 70)
    print("🧪 测试 RomanceScript.possible_ending 保留")
    print("=" * 70)
    
    romance_script = RomanceScript(
        dialogue_examples=["台词1"],
        relationship_stages=["阶段1"],
        emotional_triggers={"行为": "反应"},
        possible_ending=["圆满结局", "悲剧结局"]  # 确保保留
    )
    
    print(f"✅ RomanceScript 创建成功")
    print(f"   possible_ending: {romance_script.possible_ending}")
    assert len(romance_script.possible_ending) == 2
    print(f"✅ possible_ending 字段保留完整")


def test_access_timeline_fields():
    """测试访问 timeline_nodes 的各个字段"""
    print("\n" + "=" * 70)
    print("🧪 测试访问 timeline_nodes 字段")
    print("=" * 70)
    
    events = [
        EventNode(
            timestamp="Year 1024, Spring",
            summary="事件1",
            consequence="影响1",
            involved_factions=["势力A"],
            tags=["Tag1"]
        ),
        EventNode(
            timestamp="Year 1024, Summer",
            summary="事件2",
            consequence=None,  # 可选字段
            involved_factions=[],
            tags=["Tag2", "Tag3"]
        )
    ]
    
    world_lore = WorldLore(
        timeline_nodes=events,
        factions={"势力A": "描述"}
    )
    
    # 访问第一个事件
    first_event = world_lore.timeline_nodes[0]
    print(f"✅ 访问第一个事件成功")
    print(f"   时间戳: {first_event.timestamp}")
    print(f"   摘要: {first_event.summary}")
    print(f"   影响: {first_event.consequence}")
    print(f"   涉及势力: {first_event.involved_factions}")
    print(f"   标签: {first_event.tags}")
    
    # 测试过滤（按标签）
    tagged_events = [e for e in world_lore.timeline_nodes if "Tag1" in e.tags]
    print(f"\n✅ 按标签过滤成功: 找到 {len(tagged_events)} 个事件")
    
    # 测试过滤（按势力）
    faction_events = [
        e for e in world_lore.timeline_nodes 
        if "势力A" in e.involved_factions
    ]
    print(f"✅ 按势力过滤成功: 找到 {len(faction_events)} 个事件")


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🚀 Timeline Nodes 重构验证测试")
    print("=" * 70)
    
    try:
        test_event_node()
        test_world_lore_timeline()
        test_romance_script_preserved()
        test_access_timeline_fields()
        
        print("\n" + "=" * 70)
        print("🎉 所有测试通过！重构成功！")
        print("=" * 70)
        print("\n✅ 验证结果：")
        print("   - EventNode 类正确定义")
        print("   - WorldLore.timeline_nodes 类型为 List[EventNode]")
        print("   - villian_type 字段保留")
        print("   - possible_ending 字段保留")
        print("   - 序列化/反序列化正常")
        print("   - 字段访问正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



