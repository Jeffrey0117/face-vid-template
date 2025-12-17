#!/usr/bin/env python3
"""
批量導出面相專案草稿腳本
根據面相專案名稱批量導出所有生成的 "面相專案_XYZ" 草稿

使用方法:
python batch_export_faces.py [output_path] [resolution] [framerate]

參數:
- output_path: 可選, 導出路徑, 默認為桌面
- resolution: 可選, 導出分辨率, 支持: 480P, 720P, 1080P, 2K, 4K, 8K, 默認1080P
- framerate: 可選, 導出幀率, 支持: 24fps, 25fps, 30fps, 50fps, 60fps, 默認30fps

範例:
python batch_export_faces.py
python batch_export_faces.py "C:\\Users\\Jeffrey\\Desktop\\exports"
python batch_export_faces.py "C:\\Users\\Jeffrey\\Desktop\\exports" 1080P 24fps
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Optional
from enum import Enum

# 添加專案路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from pyJianYingDraft.jianying_controller import JianyingController, ExportResolution, ExportFramerate


def get_jianying_draft_root() -> str:
    """動態獲取剪映草稿根路徑"""
    # 優先從 config.json 讀取
    config_path = os.path.join(current_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "jianying_draft_folder" in config:
                    return config["jianying_draft_folder"]
        except Exception:
            pass

    # 備用方案：使用當前用戶名動態生成路徑
    username = os.environ.get("USERNAME") or os.getlogin()
    return rf"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"


class BatchExporter:
    """批量導出器"""

    DRAFT_FOLDER_PREFIX = "面相專案_"

    def __init__(self, output_path: Optional[str] = None,
                 resolution: str = "1080P",
                 framerate: str = "30fps"):
        # 動態設置剪映草稿根路徑
        self.JIANYING_DRAFT_ROOT = get_jianying_draft_root()

        # 設置輸出路徑
        if output_path is None:
            # 默認輸出到桌面
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            self.output_path = os.path.join(desktop, "面相專案批量導出")
        else:
            self.output_path = output_path

        # 確保輸出路徑存在
        os.makedirs(self.output_path, exist_ok=True)

        # 設置解析度和幀率
        self.resolution = self._parse_resolution(resolution)
        self.framerate = self._parse_framerate(framerate)

        self.controller = JianyingController()

        print("🚀 初始化批量導出器成功")
        print(f"🎯 輸出路徑: {self.output_path}")
        print(f"📐 導出分辨率: {resolution}")
        print(f"🎬 導出幀率: {framerate}")
        print("-" * 60)

    def _parse_resolution(self, resolution: str) -> ExportResolution:
        """解析分辨率字串"""
        resolution_map = {
            "480P": ExportResolution.RES_480P,
            "720P": ExportResolution.RES_720P,
            "1080P": ExportResolution.RES_1080P,
            "2K": ExportResolution.RES_2K,
            "4K": ExportResolution.RES_4K,
            "8K": ExportResolution.RES_8K,
        }
        return resolution_map.get(resolution.upper(), ExportResolution.RES_1080P)

    def _parse_framerate(self, framerate: str) -> ExportFramerate:
        """解析幀率字串"""
        framerate_map = {
            "24fps": ExportFramerate.FR_24,
            "25fps": ExportFramerate.FR_25,
            "30fps": ExportFramerate.FR_30,
            "50fps": ExportFramerate.FR_50,
            "60fps": ExportFramerate.FR_60,
        }
        return framerate_map.get(framerate.lower(), ExportFramerate.FR_30)

    def find_face_drafts(self) -> List[str]:
        """掃描並找到所有面相專案草稿"""
        print("🔍 正在掃描面相專案草稿...")
        print(f"📁 掃描路徑: {self.JIANYING_DRAFT_ROOT}")

        if not os.path.exists(self.JIANYING_DRAFT_ROOT):
            print(f"❌ 找不到草稿資料夾: {self.JIANYING_DRAFT_ROOT}")
            return []

        drafts = []
        try:
            items = os.listdir(self.JIANYING_DRAFT_ROOT)
            print(f"📋 發現 {len(items)} 個項目")

            for item in items:
                if os.path.isdir(os.path.join(self.JIANYING_DRAFT_ROOT, item)):
                    if item.startswith(self.DRAFT_FOLDER_PREFIX):
                        drafts.append(item)
                        print(f"  ✅ 找到面相專案草稿: {item}")

            print(f"\n📊 共找到 {len(drafts)} 個面相專案草稿")
            for i, draft in enumerate(drafts, 1):
                print(f"  {i}. {draft}")

        except Exception as e:
            print(f"❌ 掃描草稿失敗: {e}")
            import traceback
            traceback.print_exc()
            return []

        return drafts

    def export_draft(self, draft_name: str) -> bool:
        """導出單個草稿"""
        try:
            print(f"\n🎬 開始導出: {draft_name}")
            start_time = time.time()

            # 設定輸出檔案名稱
            output_filename = f"{draft_name}.mp4"
            output_file_path = os.path.join(self.output_path, output_filename)

            # 確保路徑不重複
            counter = 1
            original_path = output_file_path
            while os.path.exists(output_file_path):
                base_name = os.path.splitext(output_filename)[0]
                ext = os.path.splitext(output_filename)[1]
                output_filename = f"{base_name}_{counter}{ext}"
                output_file_path = os.path.join(self.output_path, output_filename)
                counter += 1

                if counter > 100:  # 防止無限循環
                    print(f"⚠️  文件名稱重複太多，跳過: {draft_name}")
                    return False

            # 執行導出
            self.controller.export_draft(
                draft_name=draft_name,
                output_path=output_file_path,
                resolution=self.resolution,
                framerate=self.framerate
            )

            end_time = time.time()
            duration = end_time - start_time
            print(f"✅ 導出成功: {draft_name}")
            print(f"📁 保存位置: {output_file_path}")
            print(f"⏱️  耗時: {duration:.2f}秒")
            return True

        except Exception as e:
            print(f"❌ 導出失敗: {draft_name}")
            print(f"錯誤信息: {e}")
            return False

    def run_export(self) -> None:
        """執行批量導出"""
        print("🗂️ 開始批量導出面相專案")
        print("=" * 60)

        # 找到所有面相專案草稿
        drafts = self.find_face_drafts()
        if not drafts:
            print("❌ 未找到任何面相專案草稿，結束程序")
            return

        print("\n🚀 開始逐一導出...")
        print("=" * 60)

        success_count = 0
        total_count = len(drafts)

        for i, draft_name in enumerate(drafts, 1):
            print(f"\n Progress: {i}/{total_count}")

            if self.export_draft(draft_name):
                success_count += 1

            # 在每個導出之間添加延遲，避免剪映軟體響應過慢
            if i < total_count:
                print("⏱️  等待2秒後導出下一個...")
                time.sleep(2)

        print("\n" + "=" * 60)
        print("🎉 批量導出完成!")
        print(f"📊 統計: 成功 {success_count}/{total_count} 個")
        print(f"📁 輸出路徑: {self.output_path}")

        if success_count > 0:
            print("\n✅ 所有影片已導出到指定資料夾")
        else:
            print("\n❌ 無任何成功導出的影片")


def main():
    """主函數"""
    print("🎭 面相專案批量導出器 v1.0")
    print("=" * 60)

    # 從命令列參數獲取設定
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    resolution = sys.argv[2] if len(sys.argv) > 2 else "1080P"
    framerate = sys.argv[3] if len(sys.argv) > 3 else "30fps"

    # 創建批量導出器並執行
    try:
        exporter = BatchExporter(
            output_path=output_path,
            resolution=resolution,
            framerate=framerate
        )
        exporter.run_export()

    except Exception as e:
        print(f"❌ 程序執行錯誤: {e}")
        print("請確保:")
        print("1. 剪映專業版已開啟並處於主頁面")
        print("2. 剪映草稿路徑正確")
        print("3. 有足夠的輸出權限")


if __name__ == "__main__":
    main()