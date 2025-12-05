"""
测试脚本 - 验证项目骨架是否正常工作
"""
import sys
from pathlib import Path


def test_imports():
    """测试所有核心模块是否可以正常导入"""
    print("=" * 60)
    print("🧪 测试项目骨架")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # 测试 1: 导入核心模块
    print("\n[测试 1] 导入核心模块...")
    try:
        from src import models, database, config
        print("✅ 成功导入 src.models")
        print("✅ 成功导入 src.database")
        print("✅ 成功导入 src.config")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        tests_failed += 1
        return
    
    # 测试 2: 创建数据模型
    print("\n[测试 2] 创建数据模型...")
    try:
        # 创建角色
        character = models.Character(
            id="test_char",
            name="测试角色",
            visual_traits={
                "hair_color": "黑色",
                "eye_color": "棕色"
            },
            stats={"affection": 50}
        )
        print(f"✅ 成功创建角色: {character.name}")
        
        # 创建游戏状态
        game_state = models.GameState(
            turn_count=1,
            current_location="起始点",
            player_name="测试玩家"
        )
        print(f"✅ 成功创建游戏状态: 回合 {game_state.turn_count}")
        
        # 创建游戏配置
        game_config = models.GameConfig(
            visual_backend=models.VisualBackend.SILICONFLOW,
            difficulty="normal"
        )
        print(f"✅ 成功创建游戏配置: {game_config.visual_backend}")
        
        tests_passed += 1
    except Exception as e:
        print(f"❌ 创建数据模型失败: {e}")
        tests_failed += 1
    
    # 测试 3: 数据库操作
    print("\n[测试 3] 数据库操作...")
    try:
        # 测试保存和加载
        slot_id = 999  # 使用测试槽位
        
        # 保存游戏
        success = database.save_game(slot_id, game_state)
        if success:
            print("✅ 成功保存游戏")
        else:
            print("❌ 保存游戏失败")
            tests_failed += 1
            return
        
        # 加载游戏
        loaded_state = database.load_game(slot_id)
        if loaded_state:
            print(f"✅ 成功加载游戏: 回合 {loaded_state.turn_count}")
        else:
            print("❌ 加载游戏失败")
            tests_failed += 1
            return
        
        # 清理测试数据
        database.delete_save(slot_id)
        print("✅ 清理测试数据")
        
        tests_passed += 1
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        tests_failed += 1
    
    # 测试 4: 配置加载
    print("\n[测试 4] 配置加载...")
    try:
        cfg = config.get_config()
        print(f"✅ 应用名称: {cfg.app.app_name}")
        print(f"✅ 版本: {cfg.app.version}")
        print(f"✅ API 基础 URL: {cfg.api.base_url}")
        
        # 验证配置
        is_valid = cfg.validate()
        if is_valid:
            print("✅ 配置验证通过")
        else:
            print("⚠️  配置验证失败（可能缺少 API 密钥，这是正常的）")
        
        tests_passed += 1
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        tests_failed += 1
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果")
    print("=" * 60)
    print(f"✅ 通过: {tests_passed}")
    print(f"❌ 失败: {tests_failed}")
    print(f"📈 成功率: {tests_passed}/{tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 所有测试通过！项目骨架运行正常。")
        print("\n📝 下一步：")
        print("1. 编辑 .env 文件，填入你的 API 密钥")
        print("2. 运行 streamlit run app.py 启动应用")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
    
    print("=" * 60)


if __name__ == "__main__":
    test_imports()




