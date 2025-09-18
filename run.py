#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台啟動腳本 - 面相專案影片替換工具
自動執行路徑設置和主程序
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """打印標題"""
    print("🚀 面相專案影片替換工具 - 跨平台啟動腳本")
    print("=" * 60)

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 7):
        print("❌ Python 版本過低")
        print(f"   當前版本: {sys.version}")
        print("💡 請使用 Python 3.7 或更高版本")
        return False
    
    print(f"✅ Python 版本檢查完成: {sys.version}")
    return True

def check_required_modules():
    """檢查必要的模組"""
    print("\n🔍 檢查必要的 Python 模組...")
    
    required_modules = [
        'pyJianYingDraft',
        'pathlib',
        'json',
        'uuid',
        'getpass'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ 缺少必要模組: {', '.join(missing_modules)}")
        if 'pyJianYingDraft' in missing_modules:
            print("💡 請確保 pyJianYingDraft 文件夾在當前目錄中")
        return False
    
    print("✅ 所有必要模組檢查完成")
    return True

def check_and_setup_config():
    """檢查並設置配置文件"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("\n⚠️  配置文件不存在，正在自動生成...")
        try:
            import setup_paths
            setup = setup_paths.PathSetup()
            if setup.setup():
                print("✅ 配置文件生成完成")
                return True
            else:
                print("❌ 配置文件生成失敗")
                return False
        except ImportError:
            print("❌ 找不到 setup_paths.py")
            return False
        except Exception as e:
            print(f"❌ 配置文件生成失敗: {e}")
            return False
    else:
        print("\n✅ 配置文件已存在")
        
        # 驗證配置文件內容
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_keys = ['project_root', 'videos_raw_folder', 'jianying_draft_folder']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                print(f"⚠️  配置文件缺少必要字段: {', '.join(missing_keys)}")
                print("🔄 重新生成配置文件...")
                import setup_paths
                setup = setup_paths.PathSetup()
                return setup.setup()
            
            print("✅ 配置文件驗證完成")
            return True
            
        except Exception as e:
            print(f"❌ 配置文件驗證失敗: {e}")
            print("🔄 重新生成配置文件...")
            try:
                import setup_paths
                setup = setup_paths.PathSetup()
                return setup.setup()
            except Exception as e2:
                print(f"❌ 重新生成失敗: {e2}")
                return False

def check_project_structure():
    """檢查項目結構"""
    print("\n🔍 檢查項目結構...")
    
    # 檢查模板文件夾
    template_folder = Path("面相專案")
    if not template_folder.exists():
        print("⚠️  找不到模板文件夾 \"面相專案\"")
        print("💡 請確保模板文件夾存在於當前目錄")
    else:
        print("✅ 模板文件夾存在")
    
    # 檢查並創建影片文件夾
    videos_folder = Path("videos") / "raw"
    if not videos_folder.exists():
        print("⚠️  找不到影片文件夾 \"videos/raw\"")
        print("📁 正在創建影片文件夾...")
        try:
            videos_folder.mkdir(parents=True, exist_ok=True)
            print("✅ 影片文件夾創建完成")
            print("💡 請將待處理的影片文件放入 videos/raw 文件夾")
        except Exception as e:
            print(f"❌ 創建影片文件夾失敗: {e}")
    else:
        print("✅ 影片文件夾存在")
    
    # 檢查主程序文件
    main_script = Path("template_video_replacer.py")
    if not main_script.exists():
        print("❌ 找不到主程序文件 template_video_replacer.py")
        return False
    else:
        print("✅ 主程序文件存在")
    
    return True

def run_main_program():
    """運行主程序"""
    print("\n🎬 啟動影片替換程序...")
    print("=" * 60)
    print()
    
    try:
        # 直接運行模組而不是子進程，保持控制台輸出
        import template_video_replacer
        template_video_replacer.main()
        return True
    except Exception as e:
        print(f"\n❌ 程序執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_footer(success):
    """打印結束信息"""
    print("\n" + "=" * 60)
    if success:
        print("✅ 程序執行完成")
    else:
        print("❌ 程序執行過程中發生錯誤")
    
    print("🎉 腳本執行完成")
    print("💡 提示：")
    print("   - 如需修改設置，請編輯 config.json 文件")
    print("   - 如需重新配置路徑，請運行 setup_paths.py")
    print("   - 生成的剪映草稿位於剪映軟體的草稿文件夾中")

def main():
    """主函數"""
    # 切換到腳本所在目錄
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print_header()
    
    # 檢查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 檢查必要模組
    if not check_required_modules():
        sys.exit(1)
    
    # 檢查並設置配置文件
    if not check_and_setup_config():
        print("❌ 配置設置失敗")
        sys.exit(1)
    
    # 檢查項目結構
    if not check_project_structure():
        print("❌ 項目結構檢查失敗")
        sys.exit(1)
    
    # 運行主程序
    success = run_main_program()
    
    # 打印結束信息
    print_footer(success)
    
    # 在 Windows 上暫停，讓用戶看到結果
    if os.name == 'nt':
        input("\n按 Enter 鍵退出...")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()