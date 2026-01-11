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

        /* ===== 資料夾瀏覽器樣式 ===== */
        .folder-modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.2s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .folder-modal-content {
            background: linear-gradient(145deg, #1e1e3a, #16162e);
            border-radius: 16px;
            padding: 0;
            width: 560px;
            max-height: 75vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1);
            overflow: hidden;
        }
        .folder-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: linear-gradient(90deg, #3a7bd5, #00d4aa);
            color: white;
        }
        .folder-modal-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        .close-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            font-size: 20px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            transition: background 0.2s;
        }
        .close-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        /* 麵包屑導航 */
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 12px 20px;
            background: #0d0d1a;
            border-bottom: 1px solid #2a2a4e;
            flex-wrap: wrap;
            min-height: 44px;
        }
        .breadcrumb-item {
            padding: 4px 10px;
            background: #2a2a4e;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #9cd9ff;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .breadcrumb-item:hover {
            background: #3a7bd5;
            color: white;
        }
        .breadcrumb-sep {
            color: #555;
            font-size: 12px;
        }
        .breadcrumb-current {
            color: #69db7c;
            font-weight: 600;
            background: #1a4a2a;
        }

        /* 資料夾列表 */
        .folder-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            max-height: 350px;
        }
        .folder-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            margin: 4px 0;
            background: #1a1a2e;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.15s;
            border: 1px solid transparent;
        }
        .folder-item:hover {
            background: #252550;
            border-color: #3a7bd5;
            transform: translateX(4px);
        }
        .folder-item.drive {
            background: linear-gradient(135deg, #1a2a4a, #1a1a2e);
        }
        .folder-item.drive:hover {
            background: linear-gradient(135deg, #2a3a5a, #252550);
        }
        .folder-icon {
            font-size: 22px;
            min-width: 28px;
            text-align: center;
        }
        .folder-name {
            flex: 1;
            font-size: 14px;
            color: #e0e0e0;
        }
        .folder-arrow {
            color: #555;
            font-size: 16px;
        }

        /* 選中路徑顯示 */
        .selected-path {
            padding: 12px 20px;
            background: #0d0d1a;
            border-top: 1px solid #2a2a4e;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* 底部按鈕 */
        .folder-modal-footer {
            display: flex;
            gap: 12px;
            padding: 16px 20px;
            background: #16162e;
        }
        .btn-cancel {
            flex: 1;
            padding: 12px 20px;
            background: #3a3a5e;
            border: none;
            color: #aaa;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .btn-cancel:hover {
            background: #4a4a6e;
            color: #fff;
        }
        .btn-confirm {
            flex: 1;
            padding: 12px 20px;
            background: linear-gradient(135deg, #4caf50, #45a049);
            border: none;
            color: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .btn-confirm:hover {
            background: linear-gradient(135deg, #5cbf60, #4db051);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(76,175,80,0.4);
        }

        /* 空狀態提示 */
        .folder-empty {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }
        .folder-empty-icon {
            font-size: 48px;
            margin-bottom: 10px;
            opacity: 0.5;
        }
    </style>
</head>
<body>
    <h1>JYpymaker 工具箱</h1>

    <div class="tabs">
        <button class="tab active" onclick="showTab('transcribe')">語音辨識</button>
        <button class="tab" onclick="showTab('convert')">草稿轉換</button>
    </div>

    <!-- 資料夾瀏覽彈窗 -->
    <div id="folderModal" class="folder-modal">
        <div class="folder-modal-content">
            <div class="folder-modal-header">
                <h3>📁 選擇資料夾</h3>
                <button onclick="closeFolderModal()" class="close-btn">&times;</button>
            </div>

            <!-- 麵包屑導航 -->
            <div id="breadcrumb" class="breadcrumb">
                <span class="breadcrumb-item" onclick="browseTo('')">🖥️ 電腦</span>
            </div>

            <!-- 資料夾列表 -->
            <div id="folderList" class="folder-list"></div>

            <!-- 選中的路徑顯示 -->
            <div class="selected-path">
                <span style="color:#888;">已選擇：</span>
                <span id="selectedPathText" style="color:#69db7c;">尚未選擇</span>
            </div>

            <!-- 按鈕區 -->
            <div class="folder-modal-footer">
                <button onclick="closeFolderModal()" class="btn-cancel">取消</button>
                <button onclick="confirmFolder()" class="btn-confirm">✓ 選擇此資料夾</button>
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

// ===== 資料夾瀏覽器 =====
var currentBrowsePath = '';
var videoFiles = [];
var pathHistory = [];

function openFolderBrowser() {
    document.getElementById('folderModal').style.display = 'flex';
    browseTo('');  // 從根目錄（磁碟機列表）開始
}

function closeFolderModal() {
    document.getElementById('folderModal').style.display = 'none';
}

// 更新麵包屑導航
function updateBreadcrumb(path) {
    var breadcrumb = document.getElementById('breadcrumb');
    var html = '<span class="breadcrumb-item" onclick="browseTo(\\'\\')">🖥️ 電腦</span>';

    if (path) {
        // 解析路徑各層
        var normalized = path.replace(/\\\\/g, '/');
        var parts = normalized.split('/').filter(p => p);

        var currentPath = '';
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i];
            if (i === 0 && part.match(/^[A-Za-z]:$/)) {
                // Windows 磁碟機
                currentPath = part + '/';
                html += '<span class="breadcrumb-sep">›</span>';
                if (i === parts.length - 1) {
                    html += '<span class="breadcrumb-item breadcrumb-current">💿 ' + part + '</span>';
                } else {
                    html += '<span class="breadcrumb-item" onclick="browseTo(\\'' + escapeJS(currentPath) + '\\')">💿 ' + part + '</span>';
                }
            } else {
                currentPath += (i === 0 || (i === 1 && parts[0].match(/^[A-Za-z]:$/))) ? part : '/' + part;
                html += '<span class="breadcrumb-sep">›</span>';
                if (i === parts.length - 1) {
                    html += '<span class="breadcrumb-item breadcrumb-current">📁 ' + part + '</span>';
                } else {
                    html += '<span class="breadcrumb-item" onclick="browseTo(\\'' + escapeJS(currentPath) + '\\')">📁 ' + part + '</span>';
                }
            }
        }
    }

    breadcrumb.innerHTML = html;
}

// 跳脫 JS 字串中的特殊字元
function escapeJS(str) {
    return str.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'");
}

function browseTo(path) {
    currentBrowsePath = path;
    updateBreadcrumb(path);

    // 更新選中路徑顯示
    document.getElementById('selectedPathText').textContent = path || '尚未選擇';

    // 載入中動畫
    document.getElementById('folderList').innerHTML =
        '<div style="text-align:center;padding:40px;color:#888;">' +
        '<div style="font-size:32px;margin-bottom:10px;">⏳</div>' +
        '<div>載入中...</div></div>';

    fetch('/api/browse?path=' + encodeURIComponent(path))
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                document.getElementById('folderList').innerHTML =
                    '<div class="folder-empty">' +
                    '<div class="folder-empty-icon">⚠️</div>' +
                    '<div>' + data.error + '</div></div>';
                return;
            }

            var html = '';
            var isDriveList = !path;

            // 資料夾列表
            if (data.folders.length === 0) {
                html = '<div class="folder-empty">' +
                       '<div class="folder-empty-icon">📂</div>' +
                       '<div>此資料夾沒有子資料夾</div></div>';
            } else {
                for (var i = 0; i < data.folders.length; i++) {
                    var f = data.folders[i];
                    var icon = isDriveList ? '💿' : '📁';
                    var itemClass = isDriveList ? 'folder-item drive' : 'folder-item';

                    html += '<div class="' + itemClass + '" onclick="browseTo(\\'' + escapeJS(f.path) + '\\')">';
                    html += '<span class="folder-icon">' + icon + '</span>';
                    html += '<span class="folder-name">' + f.name + '</span>';
                    html += '<span class="folder-arrow">›</span>';
                    html += '</div>';
                }
            }

            document.getElementById('folderList').innerHTML = html;
        })
        .catch(e => {
            document.getElementById('folderList').innerHTML =
                '<div class="folder-empty">' +
                '<div class="folder-empty-icon">❌</div>' +
                '<div>載入失敗: ' + e + '</div></div>';
        });
}

function confirmFolder() {
    if (!currentBrowsePath) {
        alert('請先選擇一個資料夾');
        return;
    }
    document.getElementById('folderPath').value = currentBrowsePath;
    closeFolderModal();
    scanFolder();  // 自動掃描
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
