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
    print("=" * 70)
    print("🚀 面相專案影片替換工具 - 跨平台啟動腳本 v2.3".center(70))
    print("=" * 70)
    print()

def print_step_header(step_num, total_steps, title):
    """打印步驟標題"""
    print(f"\n【步驟 {step_num}/{total_steps}】{title}")
    print("-" * 50)

def print_success(message, indent=0):
    """打印成功訊息"""
    prefix = "  " * indent
    print(f"{prefix}✅ {message}")

def print_error(message, indent=0):
    """打印錯誤訊息"""
    prefix = "  " * indent
    print(f"{prefix}❌ {message}")

def print_info(message, indent=1):
    """打印資訊訊息"""
    prefix = "  " * indent
    print(f"{prefix}{message}")

def print_warning(message, indent=0):
    """打印警告訊息"""
    prefix = "  " * indent
    print(f"{prefix}⚠️  {message}")

def check_python_version():
    """檢查 Python 版本"""
    print_info("正在檢查 Python 版本...", 0)
    
    if sys.version_info < (3, 7):
        print_error("Python 版本過低")
        print_info(f"當前版本: {sys.version}", 1)
        print_info("請使用 Python 3.7 或更高版本", 1)
        return False
    
    version_info = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_success(f"Python 版本檢查完成: {version_info}")
    return True

def check_required_modules():
    """檢查必要的模組"""
    print_info("正在檢查必要的 Python 模組...", 0)
    
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
            print_success(f"{module}", 1)
        except ImportError:
            print_error(f"{module}", 1)
            missing_modules.append(module)
    
    if missing_modules:
        print()
        print_error(f"缺少必要模組: {', '.join(missing_modules)}")
        if 'pyJianYingDraft' in missing_modules:
            print_info("請確保 pyJianYingDraft 文件夾在當前目錄中", 1)
        return False
    
    print_success("所有必要模組檢查完成")
    return True

def check_and_setup_config():
    """檢查並設置配置文件"""
    config_path = Path("config.json")
    
    print_info("正在檢查配置文件...", 0)
    
    if not config_path.exists():
        print_warning("配置文件不存在，正在自動生成...")
        print_info("執行配置文件生成程序...", 1)
        try:
            import setup_paths
            setup = setup_paths.PathSetup()
            if setup.setup():
                print_success("配置文件生成完成")
                return True
            else:
                print_error("配置文件生成失敗")
                return False
        except ImportError:
            print_error("找不到 setup_paths.py")
            return False
        except Exception as e:
            print_error(f"配置文件生成失敗: {e}")
            return False
    else:
        print_success("配置文件已存在")
        
        # 驗證配置文件內容
        print_info("正在驗證配置文件內容...", 1)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_keys = ['project_root', 'videos_raw_folder', 'jianying_draft_folder']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                print_warning(f"配置文件缺少必要字段: {', '.join(missing_keys)}")
                print_info("正在重新生成配置文件...", 1)
                import setup_paths
                setup = setup_paths.PathSetup()
                return setup.setup()
            
            print_success("配置文件驗證完成")
            print_info(f"配置項目數: {len(config)}", 1)
            return True
            
        except Exception as e:
            print_error(f"配置文件驗證失敗: {e}")
            print_info("正在重新生成配置文件...", 1)
            try:
                import setup_paths
                setup = setup_paths.PathSetup()
                return setup.setup()
            except Exception as e2:
                print_error(f"重新生成失敗: {e2}")
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
        print("⚠️  找不到 raw 資料夾 \"videos/raw\"")
        print("📁 正在創建 raw 資料夾...")
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

def auto_execute_setup_paths():
    """自動執行 setup_paths.py 進行路徑設置"""
    print("\n🔧 自動執行路徑設置...")
    print("-" * 40)
    
    try:
        # 導入並執行 setup_paths
        import setup_paths
        
        # 創建 PathSetup 實例並執行設置
        setup = setup_paths.PathSetup()
        
        # 執行路徑設置
        success = setup.setup()
        
        print("-" * 40)
        if success:
            print("✅ 路徑設置自動執行完成！")
        else:
            print("⚠️  路徑設置執行完成，但可能存在問題")
        
        return success
        
    except ImportError as e:
        print(f"❌ 錯誤：無法導入 setup_paths.py - {e}")
        print("💡 請確保 setup_paths.py 文件存在於當前目錄中")
        return False
    except Exception as e:
        print(f"❌ 錯誤：執行 setup_paths.py 時發生錯誤 - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    # 切換到腳本所在目錄
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print_header()
    
    # 🚀 自動執行 setup_paths.py (在所有其他檢查之前)
    if not auto_execute_setup_paths():
        print("\n⚠️  路徑設置失敗，但程序將繼續執行...")
        print("💡 您可以稍後手動運行 setup_paths.py 來重新配置路徑")
    
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