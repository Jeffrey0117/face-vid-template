"""
JYpymaker Web UI - 語音辨識 + 簡繁轉換

使用方式：
    python -m JYpymaker.web

功能：
    1. 語音辨識 - 影片 → 繁體 SRT
    2. 草稿轉換 - 簡體草稿 → 繁體草稿
"""

import os
import json
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

from .converter import list_drafts, convert_draft_file

app = Flask(__name__)

# 全域變數追蹤辨識進度
transcribe_status = {"running": False, "progress": "", "result": None}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>JYpymaker 工具箱</title>
    <style>
        body { font-family: "Microsoft JhengHei", sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #1a1a2e; color: #fff; }
        h1 { color: #3a7bd5; text-align: center; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 12px 24px; background: #2a2a4e; border: none; color: #888; cursor: pointer; border-radius: 8px 8px 0 0; font-size: 16px; }
        .tab.active { background: #3a7bd5; color: white; }
        .tab-content { display: none; padding: 20px; background: #2a2a4e; border-radius: 0 8px 8px 8px; }
        .tab-content.active { display: block; }
        .section { margin-bottom: 20px; }
        .section h3 { color: #69db7c; margin-bottom: 10px; }
        label { display: block; margin: 10px 0 5px; color: #aaa; }
        input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #444; background: #1a1a2e; color: #fff; border-radius: 5px; font-size: 14px; }
        button { padding: 12px 24px; font-size: 16px; background: #3a7bd5; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #2a6bc5; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-green { background: #4caf50; }
        .btn-green:hover { background: #45a049; }
        .draft { padding: 10px; margin: 5px 0; background: #1a1a2e; border-radius: 5px; }
        .draft input { margin-right: 10px; }
        .draft-list { max-height: 300px; overflow-y: auto; }
        #result, #transcribeResult { margin-top: 20px; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        .success { background: #2e7d32; }
        .error { background: #c62828; }
        .info { background: #1565c0; }
        .progress { background: #f57c00; }
        .file-input-wrapper { position: relative; overflow: hidden; display: inline-block; }
        .file-input-wrapper input[type=file] { font-size: 100px; position: absolute; left: 0; top: 0; opacity: 0; cursor: pointer; }
        #selectedFile { margin: 10px 0; padding: 10px; background: #1a1a2e; border-radius: 5px; }

        /* ===== OS.js 風格資料夾瀏覽器 ===== */
        .folder-modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.4);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        /* OS.js 現代視窗 */
        .osjs-window {
            background: #ebebeb;
            border: 1px solid #716c6c;
            border-radius: 6px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 2px 8px rgba(0,0,0,0.2);
            font-family: 'Roboto', 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            font-size: 13px;
            color: #242424;
            width: 580px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* 標題列 - macOS 風格按鈕 */
        .osjs-titlebar {
            background: linear-gradient(to bottom, #f8f8f8 0%, #e8e8e8 100%);
            border-bottom: 1px solid #c1c1c1;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            user-select: none;
            min-height: 36px;
        }
        .osjs-titlebar-buttons {
            display: flex;
            gap: 8px;
        }
        .osjs-titlebar-btn {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 1px solid rgba(102,102,102,0.5);
            cursor: pointer;
            transition: all 0.1s ease-out;
        }
        .osjs-titlebar-btn.close {
            background: linear-gradient(to bottom, #e56c5c 0%, #f09c8d 100%);
        }
        .osjs-titlebar-btn.close:hover {
            background: linear-gradient(to bottom, #f09c8d 0%, #e56c5c 100%);
        }
        .osjs-titlebar-btn.maximize {
            background: linear-gradient(to bottom, #8dd22b 0%, #b1ec70 100%);
        }
        .osjs-titlebar-btn.minimize {
            background: linear-gradient(to bottom, #f9c435 0%, #fdd675 100%);
        }
        .osjs-titlebar-icon {
            font-size: 16px;
            margin-left: 4px;
        }
        .osjs-titlebar-text {
            flex: 1;
            text-align: center;
            font-weight: 500;
            font-size: 13px;
            color: #242424;
        }

        /* 工具列 / 路徑列 */
        .osjs-toolbar {
            background: #ebebeb;
            padding: 8px 12px;
            border-bottom: 1px solid #c1c1c1;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .osjs-toolbar-label {
            color: #242424;
            font-size: 13px;
            font-weight: 500;
        }
        .osjs-address-box {
            flex: 1;
            background: #fff;
            border: 1px solid #c1c1c1;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 13px;
            font-family: inherit;
            color: #242424;
            outline: none;
            transition: border-color 0.1s ease-out;
        }
        .osjs-address-box:focus {
            border-color: rgba(0,0,200,0.5);
        }
        .osjs-toolbar-btn {
            background: linear-gradient(to bottom, #f8f8f8 0%, #f4f4f4 100%);
            border: 1px solid #c1c1c1;
            border-radius: 4px;
            padding: 6px 10px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.1s ease-out;
        }
        .osjs-toolbar-btn:hover {
            background: linear-gradient(to bottom, #fff 0%, #f8f8f8 100%);
        }
        .osjs-toolbar-btn:active {
            background: linear-gradient(to bottom, #f4f4f4 0%, #f8f8f8 100%);
        }

        /* 主要內容區 - 雙欄 */
        .osjs-content {
            display: flex;
            flex: 1;
            min-height: 0;
            background: #d9d9d9;
            padding: 8px;
            gap: 8px;
        }

        /* 左側 Tree View */
        .osjs-tree {
            width: 180px;
            background: #fff;
            border: 1px solid #c1c1c1;
            border-radius: 4px;
            overflow-y: auto;
            max-height: 340px;
            font-size: 13px;
            color: #242424;
        }
        .osjs-tree ul {
            list-style: none;
            margin: 0;
            padding: 0 0 0 16px;
        }
        .osjs-tree > ul {
            padding: 4px;
        }
        .osjs-tree li {
            padding: 4px 8px;
            cursor: pointer;
            white-space: nowrap;
            border-radius: 3px;
            transition: all 0.1s ease-out;
        }
        .osjs-tree li:hover {
            background: rgba(0,0,200,0.1);
        }
        .osjs-tree li.selected {
            background: rgba(0,0,200,0.9);
            color: #fff;
        }
        .osjs-tree-icon {
            margin-right: 6px;
        }

        /* 右側檔案列表 */
        .osjs-filelist {
            flex: 1;
            background: #fff;
            border: 1px solid #c1c1c1;
            border-radius: 4px;
            overflow-y: auto;
            max-height: 340px;
            padding: 4px;
        }
        .osjs-file-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            cursor: pointer;
            color: #242424;
            font-size: 13px;
            border-radius: 3px;
            transition: all 0.1s ease-out;
        }
        .osjs-file-item:nth-child(even) {
            background: #f9f9f9;
        }
        .osjs-file-item:hover {
            background: rgba(0,0,200,0.1);
        }
        .osjs-file-item.selected {
            background: rgba(0,0,200,0.9);
            color: #fff;
        }
        .osjs-file-icon {
            font-size: 18px;
        }

        /* 狀態列 */
        .osjs-statusbar {
            background: #ebebeb;
            border-top: 1px solid #c1c1c1;
            padding: 6px 12px;
            font-size: 12px;
            color: #666;
            display: flex;
            gap: 12px;
        }

        /* 底部按鈕區 */
        .osjs-footer {
            background: #ebebeb;
            padding: 12px;
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            border-top: 1px solid #c1c1c1;
        }
        .osjs-btn {
            min-width: 80px;
            padding: 8px 16px;
            background: linear-gradient(to bottom, #f8f8f8 0%, #f4f4f4 100%);
            border: 1px solid #c1c1c1;
            border-radius: 4px;
            font-size: 13px;
            font-family: inherit;
            cursor: pointer;
            color: #242424;
            transition: all 0.1s ease-out;
        }
        .osjs-btn:hover {
            background: linear-gradient(to bottom, #fff 0%, #f8f8f8 100%);
            border-color: #999;
        }
        .osjs-btn:active {
            background: linear-gradient(to bottom, #f4f4f4 0%, #f8f8f8 100%);
        }
        .osjs-btn.primary {
            background: linear-gradient(to bottom, rgba(0,0,200,0.8) 0%, rgba(0,0,200,0.9) 100%);
            border-color: rgba(0,0,150,0.8);
            color: #fff;
        }
        .osjs-btn.primary:hover {
            background: linear-gradient(to bottom, rgba(0,0,200,0.9) 0%, rgba(0,0,200,1) 100%);
        }

        /* 空狀態 */
        .osjs-empty {
            text-align: center;
            padding: 40px 20px;
            color: #888;
            font-size: 13px;
        }

        /* 載入動畫 */
        .osjs-loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: #666;
        }
        .osjs-loading::after {
            content: '';
            width: 20px;
            height: 20px;
            border: 2px solid #c1c1c1;
            border-top-color: rgba(0,0,200,0.8);
            border-radius: 50%;
            animation: osjs-spin 0.8s linear infinite;
            margin-left: 10px;
        }
        @keyframes osjs-spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>JYpymaker 工具箱</h1>

    <div class="tabs">
        <button class="tab active" onclick="showTab('transcribe')">語音辨識</button>
        <button class="tab" onclick="showTab('convert')">草稿轉換</button>
    </div>

    <!-- OS.js 風格資料夾瀏覽器 -->
    <div id="folderModal" class="folder-modal">
        <div class="osjs-window">
            <!-- 標題列 - macOS 風格按鈕 -->
            <div class="osjs-titlebar">
                <div class="osjs-titlebar-buttons">
                    <div class="osjs-titlebar-btn close" onclick="closeFolderModal()"></div>
                    <div class="osjs-titlebar-btn minimize"></div>
                    <div class="osjs-titlebar-btn maximize"></div>
                </div>
                <span class="osjs-titlebar-icon">📁</span>
                <span class="osjs-titlebar-text">瀏覽資料夾</span>
            </div>

            <!-- 工具列 - 路徑與導航 -->
            <div class="osjs-toolbar">
                <button class="osjs-toolbar-btn" onclick="goBack()" title="上一層">⬆️</button>
                <button class="osjs-toolbar-btn" onclick="browseTo('')" title="根目錄">🏠</button>
                <input type="text" id="addressBox" class="osjs-address-box" placeholder="選擇路徑..." readonly>
            </div>

            <!-- 主要內容 -->
            <div class="osjs-content">
                <!-- 左側樹狀目錄 -->
                <div class="osjs-tree" id="treeView">
                    <ul id="treeRoot"></ul>
                </div>

                <!-- 右側資料夾列表 -->
                <div class="osjs-filelist" id="folderList"></div>
            </div>

            <!-- 狀態列 -->
            <div class="osjs-statusbar">
                <span id="statusText">請選擇資料夾</span>
            </div>

            <!-- 按鈕區 -->
            <div class="osjs-footer">
                <button class="osjs-btn" onclick="closeFolderModal()">取消</button>
                <button class="osjs-btn primary" onclick="confirmFolder()">選擇</button>
            </div>
        </div>
    </div>

    <!-- 語音辨識 Tab -->
    <div id="transcribe" class="tab-content active">
        <div class="section">
            <h3>1. 選擇影片檔案</h3>
            <div style="display:flex; gap:10px; margin-bottom:10px;">
                <button onclick="openFolderBrowser()" class="btn-green" style="padding:12px 20px;">📁 選擇資料夾</button>
                <input type="text" id="folderPath" placeholder="或手動輸入路徑" style="flex:1;" readonly>
            </div>
            <div id="videoList" class="draft-list" style="max-height:200px;"></div>
            <div style="margin-top:10px;">
                <label>已選擇的檔案：</label>
                <input type="text" id="videoPath" placeholder="請先選擇資料夾，再點選影片" style="font-size:14px;" readonly>
            </div>
        </div>

        <div class="section">
            <h3>2. 辨識設定</h3>
            <label>Whisper 模型：</label>
            <select id="whisperModel">
                <option value="tiny">tiny (最快，準確度低)</option>
                <option value="base">base (快速)</option>
                <option value="small">small (平衡)</option>
                <option value="medium" selected>medium (推薦)</option>
                <option value="large-v3">large-v3 (最準確，較慢)</option>
            </select>

            <label>語言：</label>
            <select id="language">
                <option value="zh" selected>中文</option>
                <option value="en">英文</option>
                <option value="ja">日文</option>
                <option value="ko">韓文</option>
            </select>

            <label>輸出格式：</label>
            <select id="outputFormat">
                <option value="traditional" selected>繁體中文 (自動轉換)</option>
                <option value="simplified">簡體中文 (原始輸出)</option>
            </select>
        </div>

        <div class="section" style="display:flex; gap:20px; justify-content:center;">
            <button class="btn-green" onclick="startTranscribe('srt')" id="srtBtn" style="font-size: 18px; padding: 20px 30px; min-width: 180px;">
                📝 產生字幕
            </button>
            <button class="btn-green" onclick="startTranscribe('draft')" id="draftBtn" style="font-size: 18px; padding: 20px 30px; min-width: 180px; background: linear-gradient(135deg, #f093fb, #f5576c);">
                🎬 一條龍草稿
            </button>
        </div>

        <div id="transcribeResult"></div>
    </div>

    <!-- 草稿轉換 Tab -->
    <div id="convert" class="tab-content">
        <div class="section">
            <h3>轉換模式</h3>
            <select id="mode" style="width: auto;">
                <option value="s2twp">簡體 → 台灣繁體（含慣用詞）</option>
                <option value="s2tw">簡體 → 台灣繁體</option>
                <option value="s2t">簡體 → 繁體</option>
                <option value="t2s">繁體 → 簡體</option>
            </select>
        </div>

        <div class="section">
            <h3>選擇草稿</h3>
            <div>
                <button onclick="selectAll()">全選</button>
                <button onclick="selectNone()">取消全選</button>
                <button onclick="loadDrafts()">重新整理</button>
            </div>
            <div class="draft-list" id="drafts">載入中...</div>
        </div>

        <div class="section">
            <button class="btn-green" onclick="convert()" style="font-size: 18px; padding: 15px 40px;">
                開始轉換
            </button>
        </div>

        <div id="result"></div>
    </div>

<script>
var draftsData = [];

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');

    if (tabId === 'convert') loadDrafts();
}

// ===== OS.js 風格資料夾瀏覽器 =====
var currentBrowsePath = '';
var pathHistory = [];  // 瀏覽歷史
var videoFiles = [];
var treeData = {};  // 快取樹狀資料

function openFolderBrowser() {
    document.getElementById('folderModal').style.display = 'flex';
    pathHistory = [];
    initTreeView();
    browseTo('');
}

function closeFolderModal() {
    document.getElementById('folderModal').style.display = 'none';
}

// 上一層
function goBack() {
    if (!currentBrowsePath) return;
    var parts = currentBrowsePath.replace(/\\/g, '/').split('/').filter(Boolean);
    if (parts.length <= 1) {
        browseTo('');
    } else {
        parts.pop();
        var newPath = parts.join('/');
        // Windows 磁碟機處理
        if (parts.length === 1 && parts[0].endsWith(':')) {
            newPath = parts[0] + '/';
        }
        browseTo(newPath);
    }
}

// 跳脫 JS 字串中的特殊字元
function escapeJS(str) {
    return str.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'");
}

// 初始化左側樹狀目錄
function initTreeView() {
    fetch('/api/browse?path=')
        .then(r => r.json())
        .then(data => {
            if (data.error) return;
            var html = '<li class="selected" onclick="browseTo(\\'\\')">' +
                       '<span class="osjs-tree-icon">🖥️</span>我的電腦</li>';
            for (var i = 0; i < data.folders.length; i++) {
                var f = data.folders[i];
                html += '<li onclick="browseTo(\\'' + escapeJS(f.path) + '\\'); event.stopPropagation();">' +
                        '<span class="osjs-tree-icon">💿</span>' + f.name + '</li>';
            }
            document.getElementById('treeRoot').innerHTML = html;
        });
}

// 瀏覽到指定路徑
function browseTo(path) {
    currentBrowsePath = path;

    // 更新位址列
    document.getElementById('addressBox').value = path || '我的電腦';

    // 更新狀態列
    document.getElementById('statusText').textContent = path ? '📂 ' + path : '請選擇資料夾';

    // 載入中
    document.getElementById('folderList').innerHTML =
        '<div class="osjs-loading">載入中</div>';

    fetch('/api/browse?path=' + encodeURIComponent(path))
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                document.getElementById('folderList').innerHTML =
                    '<div class="osjs-empty">⚠️ ' + data.error + '</div>';
                return;
            }

            var html = '';
            var isDriveList = !path;

            if (data.folders.length === 0) {
                html = '<div class="osjs-empty">📭 此資料夾沒有子資料夾</div>';
            } else {
                for (var i = 0; i < data.folders.length; i++) {
                    var f = data.folders[i];
                    var icon = isDriveList ? '💿' : '📁';

                    html += '<div class="osjs-file-item" ondblclick="browseTo(\\'' + escapeJS(f.path) + '\\')" onclick="selectFolder(this, \\'' + escapeJS(f.path) + '\\')">';
                    html += '<span class="osjs-file-icon">' + icon + '</span>';
                    html += '<span>' + f.name + '</span>';
                    html += '</div>';
                }
            }

            document.getElementById('folderList').innerHTML = html;

            // 更新樹狀目錄的選中狀態
            updateTreeSelection(path);
        })
        .catch(e => {
            document.getElementById('folderList').innerHTML =
                '<div class="osjs-empty">❌ 載入失敗: ' + e + '</div>';
        });
}

// 選擇資料夾（單擊）
function selectFolder(elem, path) {
    // 移除其他選中狀態
    document.querySelectorAll('.osjs-file-item').forEach(function(el) {
        el.classList.remove('selected');
    });
    // 設定當前選中
    elem.classList.add('selected');
    currentBrowsePath = path;

    // 更新位址列和狀態列
    document.getElementById('addressBox').value = path;
    document.getElementById('statusText').textContent = '📂 已選擇: ' + path;
}

// 更新樹狀目錄選中狀態
function updateTreeSelection(path) {
    document.querySelectorAll('#treeRoot li').forEach(function(li) {
        li.classList.remove('selected');
    });
    // 簡單匹配：如果是根目錄，選中「我的電腦」
    if (!path) {
        var first = document.querySelector('#treeRoot li');
        if (first) first.classList.add('selected');
    }
}

function confirmFolder() {
    if (!currentBrowsePath) {
        alert('請先選擇一個資料夾');
        return;
    }
    document.getElementById('folderPath').value = currentBrowsePath;
    closeFolderModal();
    scanFolder();
}

// ===== 語音辨識 =====
function scanFolder() {
    var folder = document.getElementById('folderPath').value.trim();
    var listDiv = document.getElementById('videoList');

    if (!folder) {
        listDiv.innerHTML = '<p style="color:#888;padding:10px;">請先選擇資料夾</p>';
        return;
    }

    listDiv.innerHTML = '<p style="padding:10px;">掃描中...</p>';

    fetch('/api/scan_folder?path=' + encodeURIComponent(folder))
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                listDiv.innerHTML = '<p style="color:#ff6b6b;padding:10px;">' + data.error + '</p>';
                return;
            }
            videoFiles = data.files;
            if (videoFiles.length === 0) {
                listDiv.innerHTML = '<p style="color:#888;padding:10px;">此資料夾沒有影片檔案</p>';
                return;
            }
            var html = '';
            for (var i = 0; i < videoFiles.length; i++) {
                var f = videoFiles[i];
                html += '<div class="draft" onclick="selectVideo(' + i + ')" id="vf' + i + '">';
                html += '<span style="color:#69db7c;">▶</span> ' + f.name + ' <span style="color:#888;">(' + f.size + ')</span>';
                html += '</div>';
            }
            listDiv.innerHTML = html;
        })
        .catch(e => {
            listDiv.innerHTML = '<p style="color:#ff6b6b;padding:10px;">掃描失敗: ' + e + '</p>';
        });
}

function selectVideo(idx) {
    document.getElementById('videoPath').value = videoFiles[idx].path;
    // 高亮選中項目
    document.querySelectorAll('#videoList .draft').forEach(d => d.style.background = '#1a1a2e');
    document.getElementById('vf' + idx).style.background = '#3a7bd5';
}

function startTranscribe(outputMode) {
    var pathInput = document.getElementById('videoPath').value.trim();
    var result = document.getElementById('transcribeResult');
    var srtBtn = document.getElementById('srtBtn');
    var draftBtn = document.getElementById('draftBtn');

    if (!pathInput) {
        result.className = 'error';
        result.textContent = '請選擇或輸入影片檔案路徑！';
        return;
    }

    // 禁用兩個按鈕
    srtBtn.disabled = true;
    draftBtn.disabled = true;
    result.className = 'progress';

    if (outputMode === 'draft') {
        srtBtn.textContent = '處理中...';
        draftBtn.textContent = '🎬 處理中...';
        result.textContent = '一條龍處理中...\\n\\n1. Whisper 語音辨識\\n2. 轉換繁體中文\\n3. 產生剪映草稿\\n\\n請耐心等候...';
    } else {
        srtBtn.textContent = '📝 處理中...';
        draftBtn.textContent = '處理中...';
        result.textContent = '語音辨識中...\\n\\n請耐心等候，時間取決於影片長度。';
    }

    var data = {
        path: pathInput,
        model: document.getElementById('whisperModel').value,
        language: document.getElementById('language').value,
        traditional: document.getElementById('outputFormat').value === 'traditional',
        output_mode: outputMode
    };

    fetch('/api/transcribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            result.className = 'error';
            result.textContent = '錯誤: ' + data.error;
        } else if (data.draft_path) {
            result.className = 'success';
            result.textContent = '✅ 剪映草稿已建立！\\n\\n' +
                '草稿: ' + data.draft_name + '\\n' +
                '字幕: ' + data.srt_path + '\\n' +
                '耗時: ' + data.duration + ' 秒\\n\\n' +
                '重新開啟剪映即可看到！';
        } else {
            result.className = 'success';
            result.textContent = '✅ 字幕產生完成！\\n\\n' +
                '檔案: ' + data.output + '\\n' +
                '片段: ' + data.segments + ' 段\\n' +
                '耗時: ' + data.duration + ' 秒';
        }
        resetButtons();
    })
    .catch(e => {
        result.className = 'error';
        result.textContent = '請求失敗: ' + e;
        resetButtons();
    });
}

function resetButtons() {
    document.getElementById('srtBtn').disabled = false;
    document.getElementById('draftBtn').disabled = false;
    document.getElementById('srtBtn').textContent = '📝 產生字幕';
    document.getElementById('draftBtn').textContent = '🎬 一條龍草稿';
}

// ===== 草稿轉換 =====
function loadDrafts() {
    document.getElementById('drafts').innerHTML = '載入中...';
    fetch('/api/drafts')
        .then(r => r.json())
        .then(data => {
            draftsData = data.drafts || [];
            var html = '';
            for (var i = 0; i < draftsData.length; i++) {
                var d = draftsData[i];
                var encTag = d.encrypted ? ' <span style="color:#ff6b6b;">[已加密]</span>' : ' <span style="color:#69db7c;">[可轉換]</span>';
                var disabled = d.encrypted ? ' disabled' : '';
                html += '<div class="draft" style="' + (d.encrypted ? 'opacity:0.5;' : '') + '">';
                html += '<input type="checkbox" id="cb' + i + '" value="' + i + '"' + disabled + '>';
                html += '<label for="cb' + i + '">' + d.name + encTag + ' (' + d.mtime_str + ')</label>';
                html += '</div>';
            }
            document.getElementById('drafts').innerHTML = html || '沒有找到草稿';
        })
        .catch(e => {
            document.getElementById('drafts').innerHTML = '載入失敗: ' + e;
        });
}

function selectAll() {
    var cbs = document.querySelectorAll('#drafts input[type=checkbox]:not(:disabled)');
    for (var i = 0; i < cbs.length; i++) cbs[i].checked = true;
}

function selectNone() {
    var cbs = document.querySelectorAll('#drafts input[type=checkbox]');
    for (var i = 0; i < cbs.length; i++) cbs[i].checked = false;
}

function convert() {
    var result = document.getElementById('result');
    var cbs = document.querySelectorAll('#drafts input[type=checkbox]:checked');

    if (cbs.length === 0) {
        result.className = 'error';
        result.textContent = '請先選擇至少一個草稿！';
        return;
    }

    var paths = [];
    for (var i = 0; i < cbs.length; i++) {
        var idx = parseInt(cbs[i].value);
        paths.push(draftsData[idx].path);
    }

    var mode = document.getElementById('mode').value;

    result.className = 'info';
    result.textContent = '轉換中... 請稍候';

    fetch('/api/convert', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({paths: paths, mode: mode})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            result.className = 'error';
            result.textContent = '錯誤: ' + data.error;
        } else {
            var text = '轉換完成！\\n\\n';
            for (var i = 0; i < data.results.length; i++) {
                var r = data.results[i];
                if (r.success) {
                    text += '[OK] ' + r.name + ': 轉換了 ' + r.count + ' 個文字片段\\n';
                } else {
                    text += '[FAIL] ' + r.name + ': ' + r.error + '\\n';
                }
            }
            result.className = 'success';
            result.textContent = text;
        }
    })
    .catch(e => {
        result.className = 'error';
        result.textContent = '請求失敗: ' + e;
    });
}

// 初始載入
// loadDrafts();  // 等切換到 tab 再載入
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/drafts')
def api_drafts():
    try:
        drafts = list_drafts(limit=50)
        result = []
        for d in drafts:
            draft_file = Path(d['path'])
            is_encrypted = False
            if draft_file.exists():
                with open(draft_file, 'r', encoding='utf-8') as f:
                    first_char = f.read(1)
                    is_encrypted = (first_char != '{')

            result.append({
                'name': d['name'],
                'path': str(d['path']),
                'mtime_str': datetime.fromtimestamp(d['mtime']).strftime('%Y-%m-%d %H:%M'),
                'encrypted': is_encrypted
            })
        return jsonify({'drafts': result})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/convert', methods=['POST'])
def api_convert():
    data = request.json
    paths = data.get('paths', [])
    mode = data.get('mode', 's2tw')

    results = []
    for path in paths:
        try:
            count = convert_draft_file(path, mode, verbose=False)
            name = Path(path).parent.name
            results.append({'name': name, 'success': True, 'count': count})
        except Exception as e:
            results.append({'name': path, 'success': False, 'error': str(e)})

    return jsonify({'results': results})


@app.route('/api/browse')
def api_browse():
    """瀏覽資料夾結構"""
    import string
    path = request.args.get('path', '')

    folders = []

    if not path:
        # 列出所有磁碟機 (Windows)
        import platform
        if platform.system() == 'Windows':
            for letter in string.ascii_uppercase:
                drive = f"{letter}:/"
                if Path(drive).exists():
                    folders.append({'name': f"{letter}: 磁碟機", 'path': drive})
        else:
            # macOS/Linux: 列出常用目錄
            home = Path.home()
            common_paths = [
                (home, '家目錄'),
                (home / 'Desktop', '桌面'),
                (home / 'Downloads', '下載'),
                (home / 'Documents', '文件'),
                (home / 'Movies', '影片'),
                (home / 'Videos', '影片'),
            ]
            for p, name in common_paths:
                if p.exists():
                    folders.append({'name': name, 'path': str(p)})
    else:
        # 列出指定路徑下的子資料夾
        folder_path = Path(path)
        if not folder_path.exists():
            return jsonify({'error': f'路徑不存在: {path}'})
        if not folder_path.is_dir():
            return jsonify({'error': f'不是資料夾: {path}'})

        try:
            for f in sorted(folder_path.iterdir(), key=lambda x: x.name.lower()):
                if f.is_dir() and not f.name.startswith('.'):
                    folders.append({'name': f.name, 'path': str(f)})
        except PermissionError:
            return jsonify({'error': '沒有權限存取此資料夾'})
        except Exception as e:
            return jsonify({'error': str(e)})

    return jsonify({'folders': folders})


@app.route('/api/scan_folder')
def api_scan_folder():
    folder = request.args.get('path', '')
    if not folder:
        return jsonify({'error': '請提供資料夾路徑'})

    folder_path = Path(folder)
    if not folder_path.exists():
        return jsonify({'error': f'資料夾不存在: {folder}'})
    if not folder_path.is_dir():
        return jsonify({'error': f'這不是資料夾: {folder}'})

    # 支援的影片/音訊格式
    video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v',
                  '.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma'}

    files = []
    try:
        for f in folder_path.iterdir():
            if f.is_file() and f.suffix.lower() in video_exts:
                size = f.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f} MB"
                else:
                    size_str = f"{size / 1024:.0f} KB"
                files.append({
                    'name': f.name,
                    'path': str(f),
                    'size': size_str
                })
        # 按名稱排序
        files.sort(key=lambda x: x['name'].lower())
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify({'files': files})


@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    data = request.json
    file_path = data.get('path', '')
    model = data.get('model', 'medium')
    language = data.get('language', 'zh')
    traditional = data.get('traditional', True)
    output_mode = data.get('output_mode', 'srt')

    if not file_path:
        return jsonify({'error': '請提供檔案路徑'})

    if not Path(file_path).exists():
        return jsonify({'error': f'找不到檔案: {file_path}'})

    try:
        import time
        start_time = time.time()

        if output_mode == 'draft':
            # 一條龍：影片 → 辨識 → SRT → 剪映草稿
            from .transcribe import transcribe_to_draft
            draft_path = transcribe_to_draft(
                file_path,
                model=model,
                language=language,
                traditional=traditional
            )

            duration = round(time.time() - start_time, 1)
            draft_name = Path(draft_path).name
            srt_path = str(Path(file_path).with_suffix('')) + ('_zh-TW' if traditional else '_zh-CN') + '.srt'

            return jsonify({
                'success': True,
                'draft_path': draft_path,
                'draft_name': draft_name,
                'srt_path': srt_path,
                'duration': duration
            })
        else:
            # 只產生 SRT
            from .transcribe import transcribe_to_srt
            output = transcribe_to_srt(
                file_path,
                model=model,
                language=language,
                traditional=traditional
            )

            duration = round(time.time() - start_time, 1)

            # 計算片段數
            with open(output, 'r', encoding='utf-8') as f:
                content = f.read()
                segments = content.count('\n\n')

            return jsonify({
                'success': True,
                'output': output,
                'segments': segments,
                'duration': duration
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)})


def main():
    import webbrowser
    import threading
    import sys

    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("=" * 50)
    print("  JYpymaker 工具箱")
    print("  語音辨識 + 簡繁轉換")
    print("=" * 50)
    print()
    print("Open: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()

    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open('http://localhost:5000')

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    main()
