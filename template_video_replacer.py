#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板影片替換工具 - 基於現有草稿模板批量替換影片
"""

import os
import json
import shutil
import getpass
import glob
from typing import Dict, List, Tuple
import pyJianYingDraft as draft
from pyJianYingDraft import trange
import re
import copy  # 添加deepcopy支援
from datetime import datetime  # 添加時間戳支援
import uuid  # 添加UUID支援用於生成唯一ID
from pathlib import Path

# 禁用所有debug日誌用於生產環境
DEBUG_MODE = False

def debug_print(*args, **kwargs):
    """條件調試輸出函數"""
    if DEBUG_MODE:
        print(*args, **kwargs)

class TemplateVideoReplacer:
    """模板影片替換系統"""

    # 預定義顏色 (RGB 0-1範圍)
    COLORS = {
        'yellow': [1.0, 1.0, 0.0],  # 黃色
        'black': [0.0, 0.0, 0.0],   # 黑色
        'white': [1.0, 1.0, 1.0],   # 白色
        'red': [1.0, 0.0, 0.0],     # 紅色
        'blue': [0.0, 0.0, 1.0],    # 藍色
        'green': [0.0, 1.0, 0.0],   # 綠色
    }

    def __init__(self):
        self.username = getpass.getuser()
        # 載入配置文件
        self.config = self.load_config()
        # 使用配置文件中的路徑設置
        self.template_folder_path = self.config.get("project_root", os.getcwd())
        self.draft_folder_path = self.config.get("jianying_draft_folder",
            f"C:\\Users\\{self.username}\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft")
        self.videos_folder = self.config.get("videos_raw_folder",
            os.path.join(self.template_folder_path, "videos", "raw"))
    
    def load_config(self):
        """載入配置文件"""
        config_path = os.path.join(os.getcwd(), "config.json")
        
        # 如果配置文件不存在，嘗試運行 setup_paths.py 生成
        if not os.path.exists(config_path):
            print("⚠️  配置文件不存在，嘗試自動生成...")
            try:
                # 嘗試自動運行路徑設置
                import setup_paths
                setup = setup_paths.PathSetup()
                if setup.setup():
                    print("✅ 配置文件生成成功")
                else:
                    print("❌ 配置文件生成失敗，使用預設設置")
                    return self.get_default_config()
            except ImportError:
                print("❌ 找不到 setup_paths.py，使用預設設置")
                return self.get_default_config()
            except Exception as e:
                print(f"❌ 自動設置失敗: {e}，使用預設設置")
                return self.get_default_config()
        
        # 讀取配置文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 載入配置文件: {config_path}")
            print(f"   項目根目錄: {config.get('project_root', 'N/A')}")
            print(f"   剪映草稿目錄: {config.get('jianying_draft_folder', 'N/A')}")
            return config
        except Exception as e:
            print(f"❌ 讀取配置文件失敗: {e}，使用預設設置")
            return self.get_default_config()
    
    def get_default_config(self):
        """獲取預設配置"""
        project_root = os.getcwd()
        return {
            "project_root": project_root,
            "template_folder": os.path.join(project_root, "面相專案"),
            "videos_folder": os.path.join(project_root, "videos"),
            "videos_raw_folder": os.path.join(project_root, "videos", "raw"),
            "jianying_draft_folder": f"C:\\Users\\{self.username}\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
            "username": self.username
        }

    def check_and_copy_template(self, template_name: str = "面相專案"):
        """檢查剪映草稿文件夾中是否有模板，如沒有則自動複製"""
        print(f"🔍 檢查剪映草稿文件夾中的模板: {template_name}")
        
        # 檢查剪映草稿文件夾中的模板路徑
        jianying_template_path = os.path.join(self.draft_folder_path, template_name)
        local_template_path = os.path.join(self.template_folder_path, template_name)
        
        # 如果剪映草稿文件夾中已有模板，直接返回
        if os.path.exists(jianying_template_path):
            print(f"✅ 剪映草稿文件夾中已存在模板: {jianying_template_path}")
            return True
        
        # 檢查本地是否有模板
        if not os.path.exists(local_template_path):
            print(f"❌ 本地找不到模板: {local_template_path}")
            print("💡 請確保本地項目文件夾中有「面相專案」模板")
            return False
        
        # 開始複製模板
        print(f"📋 開始複製模板到剪映草稿文件夾...")
        print(f"   來源: {local_template_path}")
        print(f"   目標: {jianying_template_path}")
        
        try:
            # 確保剪映草稿文件夾存在
            if not os.path.exists(self.draft_folder_path):
                print(f"📁 創建剪映草稿文件夾: {self.draft_folder_path}")
                os.makedirs(self.draft_folder_path, exist_ok=True)
            
            # 複製整個模板文件夾
            shutil.copytree(local_template_path, jianying_template_path)
            
            print(f"✅ 模板複製成功!")
            print(f"📁 已複製到: {jianying_template_path}")
            
            # 驗證複製結果
            if os.path.exists(os.path.join(jianying_template_path, "draft_content.json")):
                print(f"✅ 驗證成功: draft_content.json 已存在")
                return True
            else:
                print(f"❌ 驗證失敗: 找不到 draft_content.json")
                return False
                
        except Exception as e:
            print(f"❌ 複製模板失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    def find_template_draft(self, template_name: str = "面相專案"):
        # 🔧 Debug: 添加詳細的模板查找日誌
        print(f"🔍 [Debug] 正在尋找模板專案: {template_name}")
        print(f"🔍 [Debug] 本地模板文件夾路徑: {self.template_folder_path}")
        """尋找指定名稱的草稿模板，如果剪映草稿文件夾中沒有則自動複製"""
        print(f"🔍 尋找模板草稿: {template_name}")
        
        # 首先執行自動檢查和複製
        print(f"🔧 執行自動模板檢查和複製...")
        copy_success = self.check_and_copy_template(template_name)
        
        if not copy_success:
            print(f"❌ 模板準備失敗，無法繼續")
            return None
        
        # 優先在剪映草稿文件夾中查找模板（複製後應該存在）
        jianying_template_path = os.path.join(self.draft_folder_path, template_name)
        if os.path.exists(jianying_template_path):
            print(f"✅ 使用剪映模板: {jianying_template_path}")
            return jianying_template_path
        
        # 如果剪映草稿文件夾中還是沒有，再檢查本地
        local_template_path = os.path.join(self.template_folder_path, template_name)
        if os.path.exists(local_template_path):
            print(f"✅ 使用本地模板: {local_template_path}")
            return local_template_path
        
        # 如果都找不到，顯示錯誤信息
        print(f"❌ 找不到模板: {template_name}")
        print("📁 可用的本地模板:")
        
        if os.path.exists(self.template_folder_path):
            for item in os.listdir(self.template_folder_path):
                item_path = os.path.join(self.template_folder_path, item)
                if os.path.isdir(item_path):
                    print(f"   • {item}")
        
        print("📁 可用的剪映草稿專案:")
        if os.path.exists(self.draft_folder_path):
            for item in os.listdir(self.draft_folder_path):
                item_path = os.path.join(self.draft_folder_path, item)
                if os.path.isdir(item_path):
                    print(f"   • {item}")
        return None
    
    def replace_text_variables(self, json_data: Dict, variables: Dict[str, str]) -> Dict:
        """新的文字變數替換策略：創建新文字素材取代原文字素材，保持樣式完整性"""
        print("🎨 開始新的文字替換策略...")
        print("=" * 80)

        if not isinstance(json_data, dict) or 'materials' not in json_data:
            print("❌ 無效的JSON數據結構")
            return json_data

        # 初始化映射和統計
        material_id_mappings = {}  # 原ID -> 新ID
        new_text_materials = []    # 新創建的文字素材列表
        replaced_indices = []      # 被替換的文字素材索引

        # 第一階段：分析和創建新文字素材
        print("🔍 第一階段：分析文字內容並準備替換")
        replacements_count = 0

        if 'texts' in json_data['materials']:
            for i, text_item in enumerate(json_data['materials']['texts']):
                if 'content' in text_item and isinstance(text_item['content'], str):
                    try:
                        content_data = json.loads(text_item['content'])
                        if 'text' in content_data:
                            original_text = content_data['text']
                            new_text = original_text

                            # 替換所有變數（保持原有邏輯）
                            for var_name, var_value in variables.items():
                                if re.search(re.escape(var_name), new_text, re.IGNORECASE):
                                    new_text = re.sub(re.escape(var_name), str(var_value), new_text, flags=re.IGNORECASE)

                            # 如果文字內容有變化，創建新文字素材
                            if new_text != original_text:
                                print(f'✓ 文字替換: "{original_text}" -> "{new_text}"')

                                # 創建新的文字素材（保留所有樣式）
                                new_text_material = self.create_replacement_text_material(
                                    text_item, new_text, material_id_mappings
                                )

                                if new_text_material:
                                    new_text_materials.append(new_text_material)
                                    replaced_indices.append(i)
                                    replacements_count += 1
                                else:
                                    print(f'⚠️ 跳過替換 (創建失敗): "{original_text}"')

                    except Exception as e:
                        print(f'⚠️ 文字分析失敗 (索引{i}): {e}')
                        continue

        if replacements_count == 0:
            print("ℹ️  沒有需要替換的文字內容")
            return json_data

        print(f"\\n📊 第一階段完成:")
        print(f"   • 找到 {replacements_count} 個需要替換的文字")
        print(f"   • 創建了 {len(new_text_materials)} 個新文字素材")
        print(f"   • 建立 {len(material_id_mappings)} 個ID映射關聯")

        # 第二階段：添加新文字素材到素材列表
        print("\\n🔧 第二階段：整合新文字素材")
        if new_text_materials:
            # 將新文字素材添加到原素材列表中
            json_data['materials']['texts'].extend(new_text_materials)
            print(f"   ✅ 添加了 {len(new_text_materials)} 個新文字素材到列表")

        # 第三階段：更新軌道引用
        print("\\n🔄 第三階段：更新軌道引用")
        json_data = self.update_track_references(json_data, material_id_mappings)

        # 第四階段：清理原文字素材
        print("\\n🧹 第四階段：清理原文字素材")
        json_data = self.cleanup_original_material(json_data, material_id_mappings, replaced_indices)

        print("\\n" + "=" * 80)
        print("✅ 文字替換策略完成！")
        print("=" * 80)
        print(f"📈 處理結果:")
        print(f"   • 文字替換次數: {replacements_count}")
        print(f"   • 新增文字素材: {len(new_text_materials)}")
        print(f"   • 更新軌道引用: {len(material_id_mappings)}")
        print(f"   • 清理原素材: {len(replaced_indices)}")

        # 最終資源檢查
        final_text_count = len(json_data['materials'].get('texts', []))
        print(f"   • 最終文字素材總數: {final_text_count}")

        print("\\n🎯 新策略特色:")
        print("   ✅ 保留所有原始樣式 (顏色、描邊、字體等)")
        print("   ✅ 精確控制字體大小")
        print("   ✅ 避免樣式污染問題")
        print("   ✅ 維護軌道引用完整性")
        print("=" * 80)

        return json_data

    def calculate_optimal_font_size(self, text: str) -> float:
        """根據文字長度智能計算最佳字體大小"""
        text_length = len(text.strip())

        # 根據文字長度設定更保守的字體大小範圍（針對9:16螢幕比例優化）
        if text_length <= 3:
            # 短文字：進一步降低字體大小
            return 8.0
        elif text_length <= 8:
            # 中等文字：使用中等字體
            return 6.0
        elif text_length <= 12:
            # 較長文字：略小字體
            return 5.0
        else:
            # 長文字：使用最小字體確保完整顯示
            return 4.0

    def apply_text_styling(self, content_data: Dict, text_target: str = None) -> Dict:
        """應用文字樣式設定（簡化版本，只更新文字內容）"""
        try:
            # 只更新文字內容，保留模板原有的樣式設定
            if text_target:
                content_data['text'] = text_target

            debug_print(f'📝 文字內容已更新為: {text_target}')

            return content_data

        except Exception as e:
            debug_print(f'文字內容更新失敗: {e}')
            return content_data

    def rgb_to_hex(self, rgb: List[float]) -> str:
        """將RGB陣列轉換為HEX字串"""
        try:
            # 將0-1範圍轉換為0-255
            r = int(rgb[0] * 255)
            g = int(rgb[1] * 255)
            b = int(rgb[2] * 255)
            return f"#{r:02x}{g:02x}{b:02x}".upper()
        except:
            return "#FFFF00"  # 預設返回黃色HEX

    def adjust_font_size_in_content(self, content_str: str, new_text: str,
                                    apply_styling: bool = False) -> str:
        """在文字內容中調整字體大小，只專注於文字替換和大小調整"""
        try:
            content_data = json.loads(content_str)

            # 計算新的最佳字體大小
            optimal_size = self.calculate_optimal_font_size(new_text)

            # 更新主要的字體大小字段
            if 'font_size' in content_data:
                original_size = content_data['font_size']
                content_data['font_size'] = optimal_size
                debug_print(f'字體大小調整: {original_size} -> {optimal_size}')

            # 更新備用的text_size字段（如果存在）
            if 'text_size' in content_data:
                content_data['text_size'] = optimal_size

            # 更新styles中的size参数（這是最重要的）
            if 'styles' in content_data and isinstance(content_data['styles'], list):
                for style in content_data['styles']:
                    if 'size' in style:
                        style['size'] = optimal_size

            # 更新文字內容
            if 'text' in content_data:
                content_data['text'] = new_text

            # 移除樣式強制設置，只專注於文字內容替換
            # if apply_styling:
            #     content_data = self.apply_text_styling(content_data, new_text)

            return json.dumps(content_data, ensure_ascii=False)

        except Exception as e:
            debug_print(f'字體大小調整失敗: {e}')
            return content_str

    def create_replacement_text_material(self, original_text_item: Dict, new_text: str,
                                       material_id_mappings: Dict[str, str]) -> Dict:
        """創建新的文字素材來取代原文字素材，保留所有樣式屬性"""
        try:
            # 生成新的唯一素材ID
            new_material_id = str(uuid.uuid4())
            print(f'🔄 創建新文字素材: {new_material_id}')

            # 深度複製原文字素材的所有屬性
            new_text_item = copy.deepcopy(original_text_item)

            # 更新ID為新生成的唯一ID
            new_text_item['id'] = new_material_id
            if 'material_id' in new_text_item:
                new_text_item['material_id'] = new_material_id

            # 記錄原ID與新ID的映射
            original_id = original_text_item.get('id', '')
            material_id_mappings[original_id] = new_material_id

            # 更新文字內容
            if 'content' in new_text_item and isinstance(new_text_item['content'], str):
                try:
                    content_data = json.loads(new_text_item['content'])

                    # 只更新文字內容，保留所有其他樣式屬性
                    if 'text' in content_data:
                        content_data['text'] = new_text

                    # 轉回JSON字串
                    new_text_item['content'] = json.dumps(content_data, ensure_ascii=False)

                except json.JSONDecodeError as e:
                    debug_print(f'解析content失敗: {e}')
                    return None

            # 更新頂層的text字段（如果存在）
            if 'text' in new_text_item:
                new_text_item['text'] = new_text

            print(f'✅ 新文字素材創建完成: "{original_text_item.get("text", "")}" -> "{new_text}"')
            return new_text_item

        except Exception as e:
            print(f'❌ 創建新文字素材失敗: {e}')
            return None

    def update_track_references(self, json_data: Dict, material_id_mappings: Dict[str, str]) -> Dict:
        """更新軌道引用，將指向原文字素材的引用替換為新文字素材的引用"""
        if not isinstance(json_data, dict) or 'tracks' not in json_data:
            return json_data

        print('🔄 開始更新軌道引用...')
        updated_count = 0

        # 遍歷所有軌道
        for track_index, track in enumerate(json_data['tracks']):
            if 'segments' not in track:
                continue

            track_type = track.get('type', 'unknown')
            print(f'   檢查軌道 {track_index} ({track_type}): {len(track["segments"])} 個片段')

            # 遍歷軌道中的所有片段
            for segment_index, segment in enumerate(track['segments']):
                current_material_id = segment.get('material_id')
                if current_material_id and current_material_id in material_id_mappings:
                    # 找到需要更新的引用
                    new_material_id = material_id_mappings[current_material_id]
                    segment['material_id'] = new_material_id

                    print(f'     ✅ 更新片段 {segment_index}: {current_material_id} -> {new_material_id}')
                    updated_count += 1

        print(f'🎯 軌道引用更新完成，共更新 {updated_count} 個引用')
        return json_data

    def cleanup_original_material(self, json_data: Dict, material_id_mappings: Dict[str, str],
                                  replaced_text_indices: List[int]) -> Dict:
        """清理原文字素材，從素材列表中移除並確保沒有遺留引用"""
        if not isinstance(json_data, dict) or 'materials' not in json_data:
            return json_data

        if 'texts' not in json_data['materials']:
            return json_data

        print('🧹 清理原文字素材...')
        cleaned_count = 0

        # 創建新文字素材列表，不包含被替換的素材
        original_texts = json_data['materials']['texts']
        new_texts = []

        for i, text_item in enumerate(original_texts):
            text_id = text_item.get('id', '')
            if text_id in material_id_mappings.keys():
                # 這是被替換的原文字素材，不加入新列表
                print(f'     🗑️  移除原文字素材 (索引 {i}): ID {text_id}')
                cleaned_count += 1
            else:
                # 保留未被替換的文字素材
                new_texts.append(text_item)

        json_data['materials']['texts'] = new_texts
        print(f'🧹 清理完成，共移除 {cleaned_count} 個原文字素材')

        return json_data

    def get_video_title(self, video_path: str) -> str:
        """從影片文件路徑獲取影片標題"""
        filename = os.path.basename(video_path)
        # 移除文件副檔名，剩下的就是標題
        title = os.path.splitext(filename)[0]
        return title.strip()

    def analyze_template_structure(self, template_path: str):
        """分析模板結構，只識別真正的影片素材"""
        print("🔍 分析模板結構...")

        draft_content_path = os.path.join(template_path, "draft_content.json")
        if not os.path.exists(draft_content_path):
            print("❌ 找不到 draft_content.json")
            return None

        try:
            with open(draft_content_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            print("📊 模板結構分析:")
            print(f"   軌道數量: {len(template_data.get('tracks', []))}")

            # 創建素材ID到素材資訊的映射
            materials = template_data.get('materials', {})
            all_videos = materials.get('videos', [])

            # 建立素材ID到類型的映射
            material_types = {}
            video_materials = []
            image_materials = []

            for video in all_videos:
                material_id = video.get('id', '')
                video_type = video.get('type', 'unknown')
                material_types[material_id] = video_type

                if video_type == 'video':
                    video_materials.append(video)
                else:
                    image_materials.append(video)

            print(f"   影片素材數量: {len(video_materials)} (真正影片)")
            print(f"   圖片素材數量: {len(image_materials)} (圖片等)")

            for i, video in enumerate(video_materials):
                path = video.get('path', 'N/A')
                print(f"      影片{i}: {os.path.basename(path)} (id={video.get('id', 'N/A')})")

            for i, image in enumerate(image_materials):
                path = image.get('path', 'N/A')
                print(f"      圖片{i}: {os.path.basename(path)} (id={image.get('id', 'N/A')})")

            # 分析影片軌道片段，只選擇連結到真正影片素材的片段
            video_segments = []
            for i, track in enumerate(template_data.get('tracks', [])):
                track_type = track.get('type', 'unknown')
                segments = track.get('segments', [])
                print(f"   軌道{i}: {track_type} ({len(segments)}個片段)")

                if track_type == 'video':
                    for j, segment in enumerate(segments):
                        if 'material_id' in segment:
                            material_id = segment['material_id']
                            if material_id in material_types and material_types[material_id] == 'video':
                                video_segments.append({
                                    'track_index': i,
                                    'segment_index': j,
                                    'material_id': material_id,
                                    'segment': segment,
                                    'material_type': 'video'
                                })
                                print(f"      ✅ 影片片段{j}: material_id={material_id} (影片)")
                            else:
                                print(f"      ❌ 跳過片段{j}: material_id={material_id} (非影片素材)")

            print(f"   📝 總計有效影片片段: {len(video_segments)} 個")

            return {
                'template_data': template_data,
                'video_segments': video_segments,
                'video_materials': video_materials,
                'material_types': material_types
            }

        except Exception as e:
            print(f"❌ 分析失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_video_replaced_draft(self, template_info: Dict, new_video_path: str, output_name: str):
        """基於模板創建替換影片的新草稿，並自動替換文字"""
        print(f"🎬 創建影片替換草稿: {output_name}")

        if not os.path.exists(new_video_path):
            print(f"❌ 找不到新影片: {new_video_path}")
            return False

        try:
            # 🛠️ 關鍵修復：使用深度複製而不是淺複製，避免模板污染
            new_draft_data = copy.deepcopy(template_info['template_data'])

            print(f"🔧 用於debugging的數據檢查 [{output_name}]:")
            print(f"   [Debug] 模板數據深拷貝完成")
            print(f"   [Debug] 新影片路徑: {new_video_path}")

            # 創建新影片素材（確保每次都生成唯一ID）
            new_video_material = draft.VideoMaterial(new_video_path)

            print(f"🔧 [Debug] 新生成的素材ID: {new_video_material.material_id}")
            print(f"   [Debug] 影片時長: {new_video_material.duration} microseconds")

            # 獲取素材類型信息
            material_types = template_info.get('material_types', {})
            original_videos = new_draft_data['materials'].get('videos', [])

            print(f"🔍 素材分類分析:")
            print(f"   原有素材數量: {len(original_videos)} 個")

            # 分類原有素材
            preserved_materials = []
            replaced_materials = []
            replaced_ids = set()

            for material in original_videos:
                material_id = material.get('id', '')
                material_name = os.path.basename(material.get('path', ''))
                material_type = material_types.get(material_id, 'unknown')

                if material_type == 'video':
                    # 這是真正的影片素材，需要替換
                    replaced_materials.append(material.copy())
                    replaced_ids.add(material_id)
                    print(f"   📹 影片素材: {material_name} (id={material_id})")
                else:
                    # 這是圖片或其他素材，直接保留
                    preserved_materials.append(material)
                    print(f"   🖼️  保留素材: {material_name} (id={material_id}, 類型={material_type})")

            # 如果沒有找到影片素材，警告用戶
            if not replaced_materials:
                print("⚠️  警告：模板中沒有找到真正的影片素材，可能會導致影片替換失敗")

            # 創建新影片素材並添加到保留的素材列表中
            print("🎬 處理新影片素材:")
            print(f"   新影片: {os.path.basename(new_video_path)}")
            print(f"   素材ID: {new_video_material.material_id}")

            # 如果有影片素材需要替換，使用第一個作為模板
            if replaced_materials:
                video_template = replaced_materials[0].copy()
                video_template.update({
                    'id': new_video_material.material_id,
                    'path': new_video_path,
                    'duration': new_video_material.duration,
                    'material_id': new_video_material.material_id,  # 確保material_id字段也更新
                    # 保持其他屬性如crop, volume等
                })

                # 替換的素材列表：保留素材 + 新影片素材
                new_materials = preserved_materials + [video_template]

                print(f"   📋 新素材列表:")
                for material in new_materials:
                    mat_name = os.path.basename(material.get('path', ''))
                    mat_id = material.get('id', '')
                    print(f"      • {mat_name} (id={mat_id})")
            else:
                # 如果沒有影片素材需要替換，直接添加新影片到素材列表
                new_materials = preserved_materials + [{
                    'id': new_video_material.material_id,
                    'path': new_video_path,
                    'duration': new_video_material.duration,
                    'material_id': new_video_material.material_id,
                    'type': 'video',
                    'material_name': os.path.basename(new_video_path)
                }]

            # 更新素材列表
            new_draft_data['materials']['videos'] = new_materials

            # 只更新連結到影片素材的軌道片段，保留指向圖片素材的片段
            print("🎯 更新影片軌道片段:")

            # 🔧 Debug: 記錄素材ID映射
            material_id_mapping = {}
            for original_mat in replaced_materials:
                original_id = original_mat.get('id', '')
                material_id_mapping[original_id] = new_video_material.material_id
            print(f"   [Debug] 素材ID映射: {material_id_mapping}")

            segments_updated = 0
            segments_skipped = 0

            for segment_info in template_info['video_segments']:
                track_index = segment_info['track_index']
                segment_index = segment_info['segment_index']
                segment_material_id = segment_info['material_id']

                # 只替換連結到真正影片素材的片段
                if segment_material_id in replaced_ids:
                    new_material_id = material_id_mapping.get(segment_material_id, new_video_material.material_id)
                    # 確保不會重複設置相同的ID
                    current_material_id = new_draft_data['tracks'][track_index]['segments'][segment_index].get('material_id')

                    if current_material_id != new_material_id:
                        # 更新片段的material_id指向新的影片素材
                        new_draft_data['tracks'][track_index]['segments'][segment_index]['material_id'] = new_material_id

                        # 🔧 Debug: 記錄每次更新的詳細信息
                        old_path = "unknown"
                        for vid in original_videos:
                            if vid.get('id') == segment_material_id:
                                old_path = vid.get('path', 'unknown')
                                break

                        print(f"   ✅ 更新軌道{track_index}片段{segment_index}:")
                        print(f"      material_id {segment_material_id} -> {new_material_id}")
                        print(f"      影片路徑: {old_path} -> {new_video_path}")
                        segments_updated += 1
                    else:
                        print(f"   ⏭️  軌道{track_index}片段{segment_index} 已是正確ID {current_material_id}")
                        segments_skipped += 1
                else:
                    # 跳過沒有替換的片段（通常是圖片素材的片段）
                    segments_skipped += 1
                    print(f"   ⏭️  保留軌道{track_index}片段{segment_index}: material_id {segment_material_id} (非替換對象)")

            print(f"   📊 片段處理統計: 更新{segments_updated}個，保留{segments_skipped}個")
            print(f"   [Debug] 最終影片素材: {os.path.basename(new_video_path)} (ID: {new_video_material.material_id})")

            # 進行文字替換
            video_title = self.get_video_title(new_video_path)
            print(f"📝 影片標題: {video_title}")

            # 定義替換規則：只將「婊子無情」替換為影片標題
            replace_variables = {
                '婊子無情': video_title
            }

            print("🔄 進行文字替換...")
            new_draft_data = self.replace_text_variables(new_draft_data, replace_variables)

            # 創建新草稿專案文件夾
            new_draft_path = os.path.join(self.draft_folder_path, output_name)
            if os.path.exists(new_draft_path):
                shutil.rmtree(new_draft_path)
            os.makedirs(new_draft_path)

            # 寫入新的draft_content.json
            draft_content_path = os.path.join(new_draft_path, "draft_content.json")
            with open(draft_content_path, 'w', encoding='utf-8') as f:
                json.dump(new_draft_data, f, indent=2, ensure_ascii=False)

            # 複製draft_meta_info.json（如果存在）
            original_meta_path = os.path.join(os.path.dirname(draft_content_path.replace(output_name, "面相專案")), "draft_meta_info.json")
            new_meta_path = os.path.join(new_draft_path, "draft_meta_info.json")

            if os.path.exists(original_meta_path):
                shutil.copy2(original_meta_path, new_meta_path)
                # 更新meta info中的標題
                try:
                    with open(new_meta_path, 'r', encoding='utf-8') as f:
                        meta_data = json.load(f)
                    meta_data['draft_name'] = output_name
                    with open(new_meta_path, 'w', encoding='utf-8') as f:
                        json.dump(meta_data, f, indent=2, ensure_ascii=False)
                except:
                    pass

            print(f"✅ 成功創建: {output_name}")
            print(f"   新影片: {os.path.basename(new_video_path)}")
            print(f"   時長: {new_video_material.duration/1000000:.2f}秒")
            print(f"   替換片段: {segments_updated} 個")
            return True

        except Exception as e:
            print(f"❌ 創建失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def batch_replace_videos(self, template_name: str, video_folder: str):
        """批量替換多個影片 - 支援去重處理"""
        print("=" * 60)
        print(f"🚀 批量影片替換開始...")
        print(f"📁 模板: {template_name}")
        print(f"📁 影片文件夾: {video_folder}")
        print("=" * 60)

        # 🔧 Debug: 記錄批量處理開始時間
        batch_start_time = datetime.now()
        print(f"[Debug] 批處理開始時間: {batch_start_time}")

        all_generated_ids = set()  # 跟踪所有已生成的素材ID
        project_creations = []  # 記錄每個專案的創建信息

        # 尋找模板（包含自動檢查和複製）
        print(f"🔍 準備模板: {template_name}")
        template_path = self.find_template_draft(template_name)
        if not template_path:
            print(f"❌ 無法準備模板 {template_name}，批處理終止")
            return False
        
        print(f"✅ 模板準備完成，開始批處理...")

        # 🔧 CRITICAL FIX: 提前讀取並深度複製原始模板，防止模板污染
        try:
            with open(os.path.join(template_path, "draft_content.json"), 'r', encoding='utf-8') as f:
                original_template_data = json.load(f)
            # 使用深度複製確保原始模板不會被修改
            fresh_template_data = copy.deepcopy(original_template_data)
        except Exception as e:
            print(f"❌ 無法讀取原始模板: {e}")
            return False

        # 分析模板（使用fresh copy）
        template_info = self.analyze_template_structure(template_path)
        if not template_info:
            return False

        # 🔧 Debug: 記錄模板分析結果
        print(f"[Debug] 模板分析完成")
        print(f"[Debug] 模板素材數量: {len(template_info.get('video_materials', []))}")

        # 獲取已存在的草稿名單，用於去重判斷
        existing_drafts = set()
        if os.path.exists(self.draft_folder_path):
            for item in os.listdir(self.draft_folder_path):
                item_path = os.path.join(self.draft_folder_path, item)
                if os.path.isdir(item_path):
                    existing_drafts.add(item)

        # 尋找影片文件
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv']
        all_video_files = []

        for ext in video_extensions:
            all_video_files.extend(glob.glob(os.path.join(video_folder, ext)))
            all_video_files.extend(glob.glob(os.path.join(video_folder, ext.upper())))

        # 過濾掉模板占位影片和非影片文件（如圖片）
        skipped_template_files = []
        skipped_image_files = []
        video_files = []

        for video_file in all_video_files:
            filename = os.path.basename(video_file)
            if filename.lower() == "video_for_template.mp4":
                skipped_template_files.append(filename)
                print(f"⏭️ 跳過模板占位影片: {filename}")
            elif filename.lower() == "logo.jpg" or filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                skipped_image_files.append(filename)
                print(f"⏭️ 跳過圖片文件: {filename}")
            else:
                video_files.append(video_file)

        if skipped_template_files:
            print(f"📋 跳過了 {len(skipped_template_files)} 個模板占位影片")
        if skipped_image_files:
            print(f"🖼️  跳過了 {len(skipped_image_files)} 個圖片文件")

        if not video_files:
            print("❌ 在指定文件夾中找不到有效的影片文件")
            return False

        print(f"🎬 找到 {len(video_files)} 個有效影片文件")
        print(f"📂 已存在草稿: {len(existing_drafts)} 個")

        success_count = 0
        skipped_count = 0
        total_skipped = len(skipped_template_files) + len(skipped_image_files) + len([f for f in existing_drafts if f.startswith(template_name)])

        for i, video_file in enumerate(video_files, 1):
            filename = os.path.splitext(os.path.basename(video_file))[0]
            output_name = f"{template_name}_{filename}"

            print(f"\n📹 ({i}/{len(video_files)}) 處理: {filename}")

            # 檢查是否已處理過
            if output_name in existing_drafts:
                print(f"   ⏭️  已存在相同名稱草稿，跳過處理")
                skipped_count += 1
                continue

            # 記錄此影片處理開始時間
            video_start_time = datetime.now()
            print(f"   [Debug] 影片處理開始: {os.path.basename(video_file)} at {video_start_time.time()}")

            # 🔧 CRITICAL FIX: 為每個影片創建全新的模板副本
            if i > 1:
                print(f"   [Debug] 為處理第{i}個影片創建全新模板副本")
                # 重新創建模板info，使用fresh copy
                template_info['template_data'] = copy.deepcopy(fresh_template_data)
                # 重新分析模板結構
                template_info = self.analyze_template_structure(template_path)
                if not template_info:
                    print(f"   ❌ 重新分析模板失敗")
                    continue

            success = self.create_video_replaced_draft(template_info, video_file, output_name)

            # 處理完成後記錄詳細信息
            video_end_time = datetime.now()
            processing_time = video_end_time - video_start_time

            if success:
                success_count += 1
                print(f"   ✅ 創建成功 ({processing_time.total_seconds():.2f}秒)")

                # 檢查生成的專案是否有正確的素材ID
                project_path = os.path.join(self.draft_folder_path, output_name)
                draft_content_path = os.path.join(project_path, "draft_content.json")

                if os.path.exists(draft_content_path):
                    try:
                        with open(draft_content_path, 'r', encoding='utf-8') as f:
                            created_data = json.load(f)

                        videos_in_project = created_data.get('materials', {}).get('videos', [])
                        texts_in_project = created_data.get('materials', {}).get('texts', [])

                        print(f"   [Info] 專案 '{output_name}' 創建驗證:")

                        # 檢查影片素材
                        video_material_ids = [v.get('material_id', 'none') for v in videos_in_project]
                        print(f"      影片素材數量: {len(videos_in_project)}")
                        print(f"      素材IDs: {video_material_ids}")

                        # 檢查文字內容
                        for i, text_item in enumerate(texts_in_project):
                            if 'content' in text_item and isinstance(text_item['content'], str):
                                try:
                                    content_data = json.loads(text_item['content'])
                                    if 'text' in content_data:
                                        print(f"      文字{i}: \"{content_data['text']}\"")
                                except:
                                    pass

                        # 記錄統計
                        project_creations.append({
                            'output_name': output_name,
                            'video_file': video_file,
                            'video_material_ids': video_material_ids,
                            'processing_time': processing_time.total_seconds(),
                            'status': 'success'
                        })

                    except Exception as e:
                        print(f"   ⚠️ 專案驗證失敗: {e}")
                else:
                    print(f"   ⚠️ 找不到生成的文件: {draft_content_path}")

            else:
                print(f"   ❌ 創建失敗 ({processing_time.total_seconds():.2f}秒)")
                project_creations.append({
                    'output_name': output_name,
                    'video_file': video_file,
                    'status': 'failed',
                    'processing_time': processing_time.total_seconds()
                })

        total_videos = len(all_video_files)
        processed_count = success_count + skipped_count
        valid_processed = len(video_files)

        print(f"\n🎉 批量處理完成！")
        print(f"📊 原始文件總計: {total_videos} 個")
        print(f"   🎬 有效影片: {len(video_files)} 個")
        if skipped_template_files:
            print(f"   ⏭️  模板占位影片: {len(skipped_template_files)} 個")
        if skipped_image_files:
            print(f"   🖼️  圖片文件: {len(skipped_image_files)} 個")
        print(f"   ✅ 處理成功: {success_count} 個")
        print(f"   ⏭️  已存在跳過: {skipped_count} 個")
        print(f"   📈 處理率: {processed_count}/{valid_processed} ({processed_count/valid_processed*100:.1f}%)")

        # 🔧 Debug: 最終統計報告
        batch_end_time = datetime.now()
        total_batch_time = batch_end_time - batch_start_time

        print("\n" + "=" * 80)
        print("🔧 DEBUG 統計報告")
        print("=" * 80)
        print(f"[Debug] 總處理時間: {total_batch_time}")
        print(f"[Debug] 平均每影片時間: {total_batch_time.total_seconds()/len(video_files):.2f}秒" if video_files else "[Debug] 無影片處理")

        # 分析素材ID重複問題
        all_material_ids = []
        all_text_contents = []

        print(f"\n[Debug] 專案素材ID分析:")
        for creation in project_creations:
            if creation['status'] == 'success':
                material_ids = creation.get('video_material_ids', [])
                all_material_ids.extend(material_ids)
                print(f"  📹 '{creation['output_name']}': 素材IDs = {material_ids}")

                # 檢查文字內容是否也相同
                project_path = os.path.join(self.draft_folder_path, creation['output_name'])
                draft_content_path = os.path.join(project_path, "draft_content.json")
                if os.path.exists(draft_content_path):
                    try:
                        with open(draft_content_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        texts = []
                        for text_item in data.get('materials', {}).get('texts', []):
                            if 'content' in text_item and isinstance(text_item['content'], str):
                                try:
                                    content_data = json.loads(text_item['content'])
                                    if 'text' in content_data:
                                        texts.append(content_data['text'])
                                except:
                                    pass
                        if texts:
                            print(f"    📝 文字內容: {texts}")
                            all_text_contents.append(texts)
                    except Exception as e:
                        print(f"    ⚠️ 讀取失敗: {e}")

        # 檢查是否有重複的素材ID
        unique_ids = set(all_material_ids)
        duplicate_ids = [id for id in all_material_ids if all_material_ids.count(id) > 1]

        print(f"\n[Debug] 素材ID統計:")
        print(f"  總素材ID數量: {len(all_material_ids)}")
        print(f"  唯一素材ID數量: {len(unique_ids)}")
        if duplicate_ids:
            print(f"  ⚠️ 發現重複素材ID: {set(duplicate_ids)}")
        else:
            print(f"  ✅ 所有素材ID均為唯一")

        # 檢查是否有重複的文字內容
        print(f"\n[Debug] 文字內容分析:")
        if len(all_text_contents) > 1:
            first_text = all_text_contents[0] if all_text_contents else []
            duplicate_texts = []
            for texts in all_text_contents[1:]:
                if texts == first_text:
                    duplicate_texts.append(texts)

            if duplicate_texts:
                print(f"  ⚠️ 發現 {len(duplicate_texts)} 個專案有相同文字內容")
                print(f"  被複製的文字: {first_text[:3]}..." if len(first_text) > 3 else f"  被複製的文字: {first_text}")
            else:
                print(f"  ✅ 所有專案文字內容均為唯一")

        print("=" * 80)

        return success_count > 0 or skipped_count > 0

def direct_process_videos_to_template():
    """直接處理 videos 文件夹到面相專案模板"""
    print("🎯 面相專案影片替換 - 自動批處理模式")
    print("=" * 60)

    replacer = TemplateVideoReplacer()

    print("📋 第一步：檢查和準備模板...")
    print("=" * 40)
    
    # 🔧 自動檢查和複製模板
    template_path = replacer.find_template_draft("面相專案")

    if not template_path:
        print("❌ 模板準備失敗")
        print("💡 請檢查:")
        print("   1. 本地項目文件夾中是否有「面相專案」文件夾")
        print("   2. 「面相專案」文件夾中是否包含 draft_content.json")
        print("   3. 剪映是否正確安裝在預期位置")
        return False
    
    print("✅ 模板準備完成")
    print("=" * 40)

    # 分析模板結構
    template_info = replacer.analyze_template_structure(template_path)
    if not template_info:
        print("❌ 模板分析失敗")
        return False

    # 使用配置中的影片文件夾路徑
    video_folder = replacer.videos_folder

    if not os.path.exists(video_folder):
        print(f"❌ 找不到 videos 文件夾: {video_folder}")
        print("💡 請確保 videos 文件夾存在或運行 setup_paths.py 重新配置")
        return False

    print(f"📁 將使用模板: 面相專案")
    print(f"📁 批量處理文件夾: {video_folder}")

    # 批量替換處理
    success = replacer.batch_replace_videos("面相專案", video_folder)
    return success

def main():
    """主函數 - 自動模式優先"""
    print("🎯 模板影片替換工具 - ⚡ 一鍵批處理模式")
    print("=" * 60)

    replacer = TemplateVideoReplacer()

    # 自動檢測並處理配置的影片文件夾
    video_folder = replacer.videos_folder

    if os.path.exists(video_folder):
        print(f"✅ 發現 videos 文件夾: {video_folder}")
        direct_process_videos_to_template()
    else:
        print("⚠️  未找到 videos 文件夾，嘗試自動設置...")
        print("💡 請運行 setup_paths.py 來配置正確的路徑")
        print("=" * 60)

        # 嘗試自動運行路徑設置
        try:
            import setup_paths
            setup = setup_paths.PathSetup()
            if setup.setup():
                print("✅ 路徑設置完成，請重新運行程序")
            else:
                print("❌ 路徑設置失敗")
        except Exception as e:
            print(f"❌ 自動設置失敗: {e}")
            print("💡 請手動運行: python setup_paths.py")

    print("\n🎉 如果需要更多自定義選項，請編輯 config.json 配置文件")

if __name__ == "__main__":
    main()