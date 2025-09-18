#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動路徑偵測和配置系統
自動偵測項目根目錄位置並生成路徑配置文件
"""

import os
import json
import getpass
import sys
from pathlib import Path

class PathSetup:
    """自動路徑偵測和配置類"""
    
    def __init__(self):
        self.username = getpass.getuser()
        self.config_file = "config.json"
        self.project_root = self.detect_project_root()
        
    def detect_project_root(self):
        """自動偵測項目根目錄"""
        # 從當前腳本所在目錄開始查找
        current_path = Path(__file__).parent.absolute()
        
        # 項目標識文件列表（存在其中任一即認為是項目根目錄）
        project_markers = [
            "template_video_replacer.py",
            "pyJianYingDraft",
            "面相專案",
            "videos"
        ]
        
        # 向上搜索最多5層目錄
        for i in range(5):
            print(f"🔍 檢查目錄: {current_path}")
            
            # 檢查是否存在項目標識文件
            markers_found = []
            for marker in project_markers:
                marker_path = current_path / marker
                if marker_path.exists():
                    markers_found.append(marker)
            
            if markers_found:
                print(f"✅ 找到項目根目錄: {current_path}")
                print(f"   發現標識: {', '.join(markers_found)}")
                return str(current_path)
            
            # 向上一層目錄繼續查找
            parent = current_path.parent
            if parent == current_path:  # 已到達文件系統根目錄
                break
            current_path = parent
        
        # 如果找不到，使用腳本所在目錄
        fallback_path = str(Path(__file__).parent.absolute())
        print(f"⚠️  無法自動偵測項目根目錄，使用腳本所在目錄: {fallback_path}")
        return fallback_path
    
    def detect_jianying_path(self):
        """偵測剪映草稿目錄"""
        # 常見的剪映安裝路徑
        possible_paths = [
            f"C:\\Users\\{self.username}\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
            f"C:\\Users\\{self.username}\\AppData\\Roaming\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
            f"D:\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
            f"C:\\Program Files\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ 找到剪映草稿目錄: {path}")
                return path
        
        # 如果都找不到，使用預設路徑（即使不存在）
        default_path = f"C:\\Users\\{self.username}\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
        print(f"⚠️  未找到剪映安裝目錄，使用預設路徑: {default_path}")
        return default_path
    
    def create_directories(self, paths_config):
        """創建必要的目錄"""
        directories_to_create = [
            paths_config["videos_folder"],
            paths_config["videos_raw_folder"],
            paths_config["template_folder"]
        ]
        
        created_dirs = []
        for dir_path in directories_to_create:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    created_dirs.append(dir_path)
                    print(f"📁 創建目錄: {dir_path}")
                except Exception as e:
                    print(f"❌ 創建目錄失敗 {dir_path}: {e}")
        
        if created_dirs:
            print(f"✅ 成功創建 {len(created_dirs)} 個目錄")
        else:
            print("ℹ️  所有必要目錄已存在")
    
    def verify_paths(self, paths_config):
        """驗證路徑配置"""
        print("\n🔍 驗證路徑配置...")
        
        verification_results = {}
        
        # 檢查必要路徑
        essential_paths = {
            "項目根目錄": paths_config["project_root"],
            "模板文件夾": paths_config["template_folder"],
            "影片文件夾": paths_config["videos_folder"],
            "原始影片文件夾": paths_config["videos_raw_folder"]
        }
        
        for name, path in essential_paths.items():
            exists = os.path.exists(path)
            verification_results[name] = {
                "path": path,
                "exists": exists,
                "is_dir": os.path.isdir(path) if exists else False
            }
            
            status = "✅" if exists else "❌"
            print(f"   {status} {name}: {path}")
        
        # 檢查剪映路徑（可選）
        jianying_exists = os.path.exists(paths_config["jianying_draft_folder"])
        verification_results["剪映草稿目錄"] = {
            "path": paths_config["jianying_draft_folder"],
            "exists": jianying_exists,
            "is_dir": os.path.isdir(paths_config["jianying_draft_folder"]) if jianying_exists else False
        }
        
        jianying_status = "✅" if jianying_exists else "⚠️ "
        print(f"   {jianying_status} 剪映草稿目錄: {paths_config['jianying_draft_folder']}")
        if not jianying_exists:
            print("      (剪映未安裝或路徑不同，程序仍可正常運行)")
        
        return verification_results
    
    def generate_config(self):
        """生成完整的路徑配置"""
        print(f"\n🔧 生成路徑配置...")
        
        # 基本路徑配置
        config = {
            "version": "1.0",
            "generated_at": str(__import__('datetime').datetime.now()),
            "project_root": self.project_root,
            "template_folder": os.path.join(self.project_root, "面相專案"),
            "videos_folder": os.path.join(self.project_root, "videos"),
            "videos_raw_folder": os.path.join(self.project_root, "videos", "raw"),
            "jianying_draft_folder": self.detect_jianying_path(),
            "username": self.username,
            "config_file": self.config_file
        }
        
        # 添加相對路徑（供跨平台使用）
        config["relative_paths"] = {
            "template_folder": "面相專案",
            "videos_folder": "videos",
            "videos_raw_folder": os.path.join("videos", "raw")
        }
        
        return config
    
    def save_config(self, config):
        """保存配置到文件"""
        config_path = os.path.join(self.project_root, self.config_file)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置文件已保存: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置文件失敗: {e}")
            return False
    
    def setup(self):
        """執行完整的路徑設置流程"""
        print("🚀 自動路徑偵測和配置系統")
        print("=" * 60)
        
        # 生成配置
        config = self.generate_config()
        
        # 創建必要目錄
        self.create_directories(config)
        
        # 驗證路徑
        verification_results = self.verify_paths(config)
        
        # 保存配置
        if self.save_config(config):
            print("\n✅ 路徑設置完成！")
            print(f"📄 配置文件: {os.path.join(self.project_root, self.config_file)}")
            
            # 顯示摘要
            print("\n📋 路徑配置摘要:")
            print(f"   項目根目錄: {config['project_root']}")
            print(f"   影片文件夾: {config['videos_raw_folder']}")
            print(f"   模板文件夾: {config['template_folder']}")
            print(f"   剪映草稿: {config['jianying_draft_folder']}")
            
            return True
        else:
            print("\n❌ 路徑設置失敗！")
            return False

def main():
    """主函數"""
    print("🎯 自動路徑偵測和配置工具")
    
    try:
        setup = PathSetup()
        success = setup.setup()
        
        if success:
            print("\n🎉 設置完成！現在可以運行主程序了。")
            print("💡 提示：您可以編輯 config.json 來自定義路徑設置")
        else:
            print("\n💥 設置過程中出現錯誤，請檢查上述錯誤信息")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()