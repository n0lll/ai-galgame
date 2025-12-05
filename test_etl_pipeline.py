"""
ETL Pipeline 测试脚本
用于验证 Pipeline 的各个组件是否正常工作
"""
import asyncio
from pathlib import Path
from src.etl_pipeline import (
    NovelLoader,
    DeepSeekExtractor,
    DataAggregator,
    PartialWorldLore,
    PartialRomanceData
)
from src.models import EventNode


def test_novel_loader():
    """测试文本切片器"""
    print("=" * 70)
    print("🧪 测试 NovelLoader")
    print("=" * 70)
    
    # 创建测试文本
    test_text = "这是一段测试文本。\n" * 1000  # 约 8000 字符
    
    loader = NovelLoader()
    chunks = loader.split_into_chunks(test_text)
    
    print(f"✅ 文本切分成功: {len(chunks)} 个块")
    print(f"   第一个块长度: {len(chunks[0])} 字符")
    if len(chunks) > 1:
        print(f"   第二个块长度: {len(chunks[1])} 字符")
        # 检查重叠
        overlap = len(chunks[0]) + len(chunks[1]) - len(test_text)
        print(f"   重叠大小: ~{overlap} 字符")
    
    return True


def test_data_models():
    """测试数据模型"""
    print("\n" + "=" * 70)
    print("🧪 测试数据模型")
    print("=" * 70)
    
    # 测试 EventNode
    event = EventNode(
        timestamp="Year 1024",
        summary="测试事件",
        consequence="测试影响",
        involved_factions=["测试势力"],
        tags=["Test"]
    )
    print(f"✅ EventNode 创建成功")
    
    # 测试 PartialWorldLore
    partial_lore = PartialWorldLore(
        rules=["规则1"],
        locations={"地点1": "描述1"},
        timeline_nodes=[event],
        factions={"势力1": "描述"},
        villian_type="测试反派类型"
    )
    print(f"✅ PartialWorldLore 创建成功")
    print(f"   反派类型保留: {partial_lore.villian_type}")
    
    # 测试 PartialRomanceData
    partial_romance = PartialRomanceData(
        interaction_events=[{"event_name": "测试事件"}],
        dialogue_snippets=["测试台词"],
        psychology_clues=["测试心理线索"],
        possible_ending=["测试结局"]
    )
    print(f"✅ PartialRomanceData 创建成功")
    print(f"   可能结局保留: {partial_romance.possible_ending}")
    
    return True


def test_data_aggregator():
    """测试数据聚合器"""
    print("\n" + "=" * 70)
    print("🧪 测试 DataAggregator")
    print("=" * 70)
    
    # 创建测试数据
    partial_lores = [
        PartialWorldLore(
            rules=["规则1", "规则2"],
            locations={"地点1": "描述1"},
            timeline_nodes=[
                EventNode(
                    timestamp="Year 1024",
                    summary="事件1",
                    involved_factions=["势力1"],
                    tags=["Tag1"]
                )
            ],
            factions={"势力1": "描述1"},
            villian_type="反派类型A"
        ),
        PartialWorldLore(
            rules=["规则2", "规则3"],
            locations={"地点1": "更详细的描述1", "地点2": "描述2"},
            timeline_nodes=[
                EventNode(
                    timestamp="Year 1025",
                    summary="事件2",
                    involved_factions=["势力2"],
                    tags=["Tag2"]
                )
            ],
            factions={"势力1": "更详细的描述1", "势力2": "描述2"},
            villian_type="反派类型B（更详细）"
        )
    ]
    
    # 测试聚合
    world_lore = DataAggregator.aggregate_world_lore(partial_lores)
    
    print(f"✅ 世界观数据聚合成功")
    print(f"   规则数量: {len(world_lore.rules)} (去重后)")
    print(f"   地点数量: {len(world_lore.locations)}")
    print(f"   事件数量: {len(world_lore.timeline_nodes)}")
    print(f"   势力数量: {len(world_lore.factions)}")
    print(f"   反派类型: {world_lore.villian_type}")
    
    # 验证去重和合并
    assert len(world_lore.rules) == 3  # 去重后应该只有3个规则
    assert world_lore.locations["地点1"] == "更详细的描述1"  # 保留更详细的
    assert len(world_lore.timeline_nodes) == 2  # 两个不同的事件
    
    return True


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 70)
    print("🧪 测试文件结构")
    print("=" * 70)
    
    data_dir = Path("data")
    output_dir = Path("output")
    
    # 检查数据目录
    if data_dir.exists():
        print(f"✅ 数据目录存在: {data_dir}")
        
        world_file = data_dir / "world_novel_cleaned.txt"
        romance_file = data_dir / "romance_novel_cleaned.txt"
        
        if world_file.exists():
            size = world_file.stat().st_size
            print(f"✅ 世界观小说文件存在: {world_file} ({size:,} 字节)")
        else:
            print(f"⚠️  世界观小说文件不存在: {world_file}")
        
        if romance_file.exists():
            size = romance_file.stat().st_size
            print(f"✅ 恋爱小说文件存在: {romance_file} ({size:,} 字节)")
        else:
            print(f"⚠️  恋爱小说文件不存在: {romance_file}")
    else:
        print(f"⚠️  数据目录不存在: {data_dir}")
        print(f"   将自动创建")
    
    # 检查输出目录
    if output_dir.exists():
        print(f"✅ 输出目录存在: {output_dir}")
    else:
        print(f"⚠️  输出目录不存在: {output_dir}")
        print(f"   将自动创建")
    
    return True


async def test_extractor_initialization():
    """测试提取器初始化（不调用 API）"""
    print("\n" + "=" * 70)
    print("🧪 测试 DeepSeekExtractor 初始化")
    print("=" * 70)
    
    import os
    
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            extractor = DeepSeekExtractor(api_key)
            print(f"✅ DeepSeekExtractor 初始化成功")
            print(f"   模型: {extractor.model}")
            print(f"   并发限制: {extractor.semaphore._value}")
            return True
        except Exception as e:
            print(f"❌ DeepSeekExtractor 初始化失败: {e}")
            return False
    else:
        print(f"⚠️  未设置 API Key，跳过测试")
        print(f"   设置 SILICONFLOW_API_KEY 或 OPENAI_API_KEY 后可以测试 API 调用")
        return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🚀 ETL Pipeline 组件测试")
    print("=" * 70)
    
    tests = [
        ("文本切片器", test_novel_loader),
        ("数据模型", test_data_models),
        ("数据聚合器", test_data_aggregator),
        ("文件结构", test_file_structure),
    ]
    
    results = {}
    
    # 运行同步测试
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # 运行异步测试
    try:
        result = asyncio.run(test_extractor_initialization())
        results["提取器初始化"] = result
    except Exception as e:
        print(f"\n❌ 提取器初始化测试失败: {e}")
        results["提取器初始化"] = False
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        print("\n💡 下一步：")
        print("  1. 准备输入文件（data/world_novel_cleaned.txt 和 data/romance_novel_cleaned.txt）")
        print("  2. 设置 API Key（SILICONFLOW_API_KEY 或 OPENAI_API_KEY）")
        print("  3. 运行: python src/etl_pipeline.py")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
    
    print("=" * 70)


if __name__ == "__main__":
    main()



