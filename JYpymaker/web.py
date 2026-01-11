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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        /* ===== 共用基礎樣式 ===== */
        * { box-sizing: border-box; }
        body { max-width: 900px; margin: 40px auto; padding: 20px; transition: all 0.3s ease; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-content { display: none; padding: 20px; }
        .tab-content.active { display: block; }
        .section { margin-bottom: 20px; }
        .draft-list { max-height: 300px; overflow-y: auto; }
        #result, #transcribeResult { margin-top: 20px; padding: 15px; white-space: pre-wrap; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }

        /* UI 風格切換開關 - 固定在右上角 */
        .ui-switch {
            position: fixed; top: 10px; right: 10px; z-index: 9999;
            display: flex; align-items: center; gap: 8px;
            padding: 8px 12px; border-radius: 20px; font-size: 12px;
        }
        .ui-switch input[type="radio"] { display: none; }
        .ui-switch label { cursor: pointer; padding: 4px 8px; border-radius: 12px; transition: all 0.2s; }

        /* ============================================
           macOS / OS.js 現代風格
           ============================================ */
        body.ui-modern {
            font-family: 'Roboto', 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #242424;
        }
        body.ui-modern .main-container {
            background: #f5f5f5;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        body.ui-modern h1 {
            color: #333;
            text-align: center;
            font-weight: 300;
            font-size: 28px;
            margin-bottom: 25px;
        }
        body.ui-modern .ui-switch {
            background: rgba(255,255,255,0.9);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        body.ui-modern .ui-switch label { color: #666; }
        body.ui-modern .ui-switch label:hover { color: #333; }
        body.ui-modern .ui-switch input:checked + label {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
        }
        body.ui-modern .tab {
            padding: 12px 24px;
            background: #e0e0e0;
            border: none;
            color: #666;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            font-size: 14px;
            transition: all 0.2s;
        }
        body.ui-modern .tab:hover { background: #d0d0d0; }
        body.ui-modern .tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        body.ui-modern .tab-content {
            background: #fff;
            border-radius: 0 12px 12px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        body.ui-modern .section h3 {
            color: #667eea;
            font-weight: 500;
            margin-bottom: 15px;
        }
        body.ui-modern label { display: block; margin: 12px 0 6px; color: #666; font-size: 13px; }
        body.ui-modern input[type="text"], body.ui-modern select {
            width: 100%; padding: 10px 12px;
            border: 1px solid #ddd;
            background: #fff;
            color: #333;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        body.ui-modern input[type="text"]:focus, body.ui-modern select:focus {
            border-color: #667eea;
            outline: none;
        }
        body.ui-modern button {
            padding: 10px 20px;
            font-size: 14px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(102,126,234,0.3);
        }
        body.ui-modern button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.4);
        }
        body.ui-modern .btn-green {
            background: linear-gradient(135deg, #11998e, #38ef7d);
            box-shadow: 0 2px 8px rgba(17,153,142,0.3);
        }
        body.ui-modern .btn-green:hover {
            box-shadow: 0 4px 12px rgba(17,153,142,0.4);
        }
        body.ui-modern .draft {
            padding: 12px;
            margin: 8px 0;
            background: #f9f9f9;
            border-radius: 8px;
            border: 1px solid #eee;
        }
        body.ui-modern .draft:hover { background: #f0f0f0; }
        body.ui-modern .draft input { margin-right: 10px; }
        body.ui-modern .success { background: linear-gradient(135deg, #11998e, #38ef7d); color: #fff; border-radius: 8px; }
        body.ui-modern .error { background: linear-gradient(135deg, #eb3349, #f45c43); color: #fff; border-radius: 8px; }
        body.ui-modern .info { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border-radius: 8px; }
        body.ui-modern .progress { background: linear-gradient(135deg, #f093fb, #f5576c); color: #fff; border-radius: 8px; }
        body.ui-modern .win98-titlebar { display: none; }

        /* ============================================
           Windows 98 復古風格
           ============================================ */
        body.ui-retro {
            font-family: "Microsoft Sans Serif", "Segoe UI", Tahoma, sans-serif;
            background: #008080;
            color: #000;
            font-size: 11px;
        }
        body.ui-retro .main-container {
            background: #c0c0c0;
            box-shadow:
                inset -1px -1px #0a0a0a,
                inset 1px 1px #ffffff,
                inset -2px -2px #808080,
                inset 2px 2px #dfdfdf;
            padding: 4px;
        }
        body.ui-retro .win98-titlebar {
            background: linear-gradient(90deg, #000080, #1084d0);
            padding: 3px 6px;
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }
        body.ui-retro .win98-titlebar span {
            color: white;
            font-weight: bold;
            font-size: 12px;
            flex: 1;
        }
        body.ui-retro .win98-titlebar-btn {
            width: 16px; height: 14px;
            background: #c0c0c0;
            border: none;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            font-size: 9px; font-weight: bold;
            cursor: pointer; margin-left: 2px;
        }
        body.ui-retro h1 {
            display: none; /* Win98 用 titlebar 顯示標題 */
        }
        body.ui-retro .ui-switch {
            background: #c0c0c0;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            border-radius: 0;
        }
        body.ui-retro .ui-switch label { color: #000; border-radius: 0; }
        body.ui-retro .ui-switch input:checked + label {
            background: #000080;
            color: #fff;
        }
        body.ui-retro .tabs {
            background: #c0c0c0;
            padding: 4px 4px 0 4px;
            gap: 2px;
        }
        body.ui-retro .tab {
            padding: 4px 16px;
            background: #c0c0c0;
            border: none;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            color: #000;
            cursor: pointer;
            border-radius: 0;
            font-size: 11px;
            font-family: inherit;
        }
        body.ui-retro .tab.active {
            background: #c0c0c0;
            box-shadow: inset 1px 1px #ffffff, inset -1px 0 #808080;
            position: relative;
            z-index: 1;
        }
        body.ui-retro .tab-content {
            background: #c0c0c0;
            border-radius: 0;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            padding: 12px;
        }
        body.ui-retro .section {
            background: #c0c0c0;
            padding: 8px;
            margin-bottom: 8px;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
        }
        body.ui-retro .section h3 {
            color: #000;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        body.ui-retro label { display: block; margin: 6px 0 3px; color: #000; font-size: 11px; }
        body.ui-retro input[type="text"], body.ui-retro select {
            width: 100%; padding: 3px 4px;
            border: none;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080, inset -2px -2px #dfdfdf, inset 2px 2px #0a0a0a;
            background: #fff;
            color: #000;
            border-radius: 0;
            font-size: 11px;
            font-family: inherit;
        }
        body.ui-retro button {
            padding: 4px 12px;
            font-size: 11px;
            background: #c0c0c0;
            color: #000;
            border: none;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            border-radius: 0;
            cursor: pointer;
            margin: 3px;
            font-family: inherit;
        }
        body.ui-retro button:hover { background: #d4d4d4; }
        body.ui-retro button:active {
            box-shadow: inset 1px 1px #0a0a0a, inset -1px -1px #ffffff, inset 2px 2px #808080, inset -2px -2px #dfdfdf;
        }
        body.ui-retro .btn-green {
            background: #c0c0c0;
        }
        body.ui-retro .draft {
            padding: 4px;
            margin: 2px 0;
            background: #fff;
            border-radius: 0;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
        }
        body.ui-retro .draft:hover { background: #000080; color: #fff; }
        body.ui-retro .draft input { margin-right: 6px; }
        body.ui-retro .success {
            background: #c0c0c0; color: #008000;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            border-radius: 0;
        }
        body.ui-retro .error {
            background: #c0c0c0; color: #ff0000;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            border-radius: 0;
        }
        body.ui-retro .info {
            background: #c0c0c0; color: #000080;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            border-radius: 0;
        }
        body.ui-retro .progress {
            background: #c0c0c0; color: #808000;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            border-radius: 0;
        }

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

        /* ===== Windows 98 風格資料夾瀏覽器 ===== */
        .win98-window {
            background: #c0c0c0;
            border: none;
            box-shadow:
                inset -1px -1px #0a0a0a,
                inset 1px 1px #ffffff,
                inset -2px -2px #808080,
                inset 2px 2px #dfdfdf;
            font-family: "Microsoft Sans Serif", "Segoe UI", Tahoma, sans-serif;
            font-size: 11px;
            width: 500px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        }
        .win98-titlebar {
            background: linear-gradient(90deg, #000080, #1084d0);
            padding: 3px 4px;
            display: flex;
            align-items: center;
            gap: 4px;
            user-select: none;
        }
        .win98-titlebar-icon { width: 16px; height: 16px; font-size: 14px; }
        .win98-titlebar-text { flex: 1; color: white; font-weight: bold; font-size: 12px; }
        .win98-titlebar-btn {
            width: 16px; height: 14px;
            background: #c0c0c0;
            border: none;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            font-size: 10px; font-weight: bold;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; padding: 0; margin-left: 2px;
        }
        .win98-titlebar-btn:active {
            box-shadow: inset 1px 1px #0a0a0a, inset -1px -1px #ffffff;
        }
        .win98-toolbar {
            background: #c0c0c0;
            padding: 4px 6px;
            border-bottom: 1px solid #808080;
            display: flex; align-items: center; gap: 4px;
        }
        .win98-toolbar-label { color: #000; font-size: 11px; }
        .win98-address-box {
            flex: 1; background: white; border: none;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080, inset -2px -2px #dfdfdf, inset 2px 2px #0a0a0a;
            padding: 3px 4px; font-size: 11px; font-family: inherit; color: #000;
        }
        .win98-content {
            display: flex; flex: 1; min-height: 0;
            background: #c0c0c0; padding: 6px; gap: 6px;
        }
        .win98-tree {
            width: 160px; background: white; border: none;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080, inset -2px -2px #dfdfdf, inset 2px 2px #0a0a0a;
            overflow-y: auto; max-height: 300px; font-size: 11px; color: #000;
        }
        .win98-tree ul { list-style: none; margin: 0; padding: 0 0 0 16px; }
        .win98-tree > ul { padding: 4px; }
        .win98-tree li { padding: 2px 0; cursor: pointer; white-space: nowrap; }
        .win98-tree li:hover { background: #000080; color: white; }
        .win98-tree li.selected { background: #000080; color: white; }
        .win98-tree-icon { margin-right: 4px; }
        .win98-filelist {
            flex: 1; background: white; border: none;
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080, inset -2px -2px #dfdfdf, inset 2px 2px #0a0a0a;
            overflow-y: auto; max-height: 300px; padding: 4px;
        }
        .win98-file-item {
            display: flex; align-items: center; gap: 6px;
            padding: 2px 4px; cursor: pointer; color: #000; font-size: 11px;
        }
        .win98-file-item:hover { background: #000080; color: white; }
        .win98-file-item.selected { background: #000080; color: white; }
        .win98-file-icon { font-size: 16px; }
        .win98-statusbar {
            background: #c0c0c0; border-top: 1px solid #808080;
            padding: 2px 6px; font-size: 11px; color: #000; display: flex; gap: 8px;
        }
        .win98-statusbar-field {
            box-shadow: inset -1px -1px #ffffff, inset 1px 1px #808080;
            padding: 2px 4px; flex: 1;
        }
        .win98-footer {
            background: #c0c0c0; padding: 8px;
            display: flex; justify-content: flex-end; gap: 6px;
        }
        .win98-btn {
            min-width: 75px; padding: 4px 12px;
            background: #c0c0c0; border: none;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #ffffff, inset -2px -2px #808080, inset 2px 2px #dfdfdf;
            font-size: 11px; font-family: inherit; cursor: pointer; color: #000;
        }
        .win98-btn:hover { background: #d4d4d4; }
        .win98-btn:active {
            box-shadow: inset 1px 1px #0a0a0a, inset -1px -1px #ffffff, inset 2px 2px #808080, inset -2px -2px #dfdfdf;
            padding: 5px 11px 3px 13px;
        }
        .win98-btn.default { border: 1px solid #000; }
        .win98-empty { text-align: center; padding: 40px 20px; color: #808080; font-size: 11px; }
        .win98-loading { text-align: center; padding: 40px 20px; color: #808080; font-size: 11px; }
    </style>
</head>
<body class="ui-modern">
    <!-- UI 風格切換 -->
    <div class="ui-switch">
        <span>UI:</span>
        <input type="radio" name="uiStyle" id="uiModern" value="modern" checked onchange="switchUI('modern')">
        <label for="uiModern">macOS</label>
        <input type="radio" name="uiStyle" id="uiRetro" value="retro" onchange="switchUI('retro')">
        <label for="uiRetro">Win98</label>
    </div>

    <div class="main-container">
        <!-- Win98 標題列 (僅在 retro 模式顯示) -->
        <div class="win98-titlebar">
            <span>📦 JYpymaker 工具箱</span>
            <button class="win98-titlebar-btn">_</button>
            <button class="win98-titlebar-btn">□</button>
            <button class="win98-titlebar-btn">✕</button>
        </div>

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

    <!-- Windows 98 風格資料夾瀏覽器 -->
    <div id="folderModalWin98" class="folder-modal">
        <div class="win98-window">
            <!-- 標題列 -->
            <div class="win98-titlebar">
                <span>📁 瀏覽資料夾</span>
                <button class="win98-titlebar-btn" onclick="closeFolderModal()">✕</button>
            </div>

            <!-- 工具列 -->
            <div class="win98-toolbar">
                <button class="win98-btn" onclick="goBack()" title="上一層">⬆️ 上一層</button>
                <button class="win98-btn" onclick="browseTo(&apos;&apos;)" title="根目錄">🏠 根目錄</button>
                <input type="text" id="addressBoxWin98" class="win98-address-box" placeholder="選擇路徑..." readonly>
            </div>

            <!-- 主要內容 -->
            <div class="win98-content">
                <div class="win98-filelist" id="folderListWin98"></div>
            </div>

            <!-- 狀態列 -->
            <div class="win98-statusbar">
                <div class="win98-statusbar-field" id="statusTextWin98">請選擇資料夾</div>
            </div>

            <!-- 按鈕區 -->
            <div class="win98-footer">
                <button class="win98-btn" onclick="closeFolderModal()">取消</button>
                <button class="win98-btn default" onclick="confirmFolder()">選擇</button>
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

    </div><!-- end main-container -->

<script>
var draftsData = [];
var currentUIStyle = localStorage.getItem('uiStyle') || 'modern';

// 初始化 UI 風格
function initUIStyle() {
    if (currentUIStyle === 'retro') {
        document.getElementById('uiRetro').checked = true;
        document.body.className = 'ui-retro';
    } else {
        document.getElementById('uiModern').checked = true;
        document.body.className = 'ui-modern';
    }
}

// 切換 UI 風格
function switchUI(style) {
    currentUIStyle = style;
    localStorage.setItem('uiStyle', style);
    document.body.className = style === 'retro' ? 'ui-retro' : 'ui-modern';
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', initUIStyle);

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
    pathHistory = [];
    if (currentUIStyle === 'retro') {
        document.getElementById('folderModalWin98').style.display = 'flex';
    } else {
        document.getElementById('folderModal').style.display = 'flex';
        initTreeView();
    }
    browseTo('');
}

function closeFolderModal() {
    document.getElementById('folderModal').style.display = 'none';
    document.getElementById('folderModalWin98').style.display = 'none';
}

// 上一層
function goBack() {
    if (!currentBrowsePath) return;
    var parts = currentBrowsePath.replace(/[\\\\]/g, '/').split('/').filter(Boolean);
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
    return str.replace(/[\\\\]/g, '\\\\\\\\').replace(/'/g, "&apos;");
}

// 初始化左側樹狀目錄
function initTreeView() {
    fetch('/api/browse?path=')
        .then(r => r.json())
        .then(data => {
            if (data.error) return;
            var html = '<li class="selected" onclick="browseTo(&apos;&apos;)">' +
                       '<span class="osjs-tree-icon">🖥️</span>我的電腦</li>';
            for (var i = 0; i < data.folders.length; i++) {
                var f = data.folders[i];
                html += '<li onclick="browseTo(&apos;' + escapeJS(f.path) + '&apos;); event.stopPropagation();">' +
                        '<span class="osjs-tree-icon">💿</span>' + f.name + '</li>';
            }
            document.getElementById('treeRoot').innerHTML = html;
        });
}

// 瀏覽到指定路徑
function browseTo(path) {
    currentBrowsePath = path;

    // 更新位址列 (兩種 UI)
    var addrBox = document.getElementById('addressBox');
    var addrBoxWin98 = document.getElementById('addressBoxWin98');
    if (addrBox) addrBox.value = path || '我的電腦';
    if (addrBoxWin98) addrBoxWin98.value = path || '我的電腦';

    // 更新狀態列 (兩種 UI)
    var statusText = document.getElementById('statusText');
    var statusTextWin98 = document.getElementById('statusTextWin98');
    var statusMsg = path ? '📂 ' + path : '請選擇資料夾';
    if (statusText) statusText.textContent = statusMsg;
    if (statusTextWin98) statusTextWin98.textContent = statusMsg;

    // 載入中
    var folderList = document.getElementById('folderList');
    var folderListWin98 = document.getElementById('folderListWin98');
    if (folderList) folderList.innerHTML = '<div class="osjs-loading">載入中</div>';
    if (folderListWin98) folderListWin98.innerHTML = '<div class="win98-loading">載入中...</div>';

    fetch('/api/browse?path=' + encodeURIComponent(path))
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                var errHtml = '<div class="osjs-empty">⚠️ ' + data.error + '</div>';
                var errHtmlWin98 = '<div class="win98-empty">⚠️ ' + data.error + '</div>';
                if (folderList) folderList.innerHTML = errHtml;
                if (folderListWin98) folderListWin98.innerHTML = errHtmlWin98;
                return;
            }

            var htmlOsjs = '';
            var htmlWin98 = '';
            var isDriveList = !path;

            if (data.folders.length === 0) {
                htmlOsjs = '<div class="osjs-empty">📭 此資料夾沒有子資料夾</div>';
                htmlWin98 = '<div class="win98-empty">📭 此資料夾沒有子資料夾</div>';
            } else {
                for (var i = 0; i < data.folders.length; i++) {
                    var f = data.folders[i];
                    var icon = isDriveList ? '💿' : '📁';

                    // OS.js 風格
                    htmlOsjs += '<div class="osjs-file-item" ondblclick="browseTo(&apos;' + escapeJS(f.path) + '&apos;)" onclick="selectFolder(this, &apos;' + escapeJS(f.path) + '&apos;)">';
                    htmlOsjs += '<span class="osjs-file-icon">' + icon + '</span>';
                    htmlOsjs += '<span>' + f.name + '</span>';
                    htmlOsjs += '</div>';

                    // Win98 風格
                    htmlWin98 += '<div class="win98-file-item" ondblclick="browseTo(&apos;' + escapeJS(f.path) + '&apos;)" onclick="selectFolderWin98(this, &apos;' + escapeJS(f.path) + '&apos;)">';
                    htmlWin98 += '<span class="win98-file-icon">' + icon + '</span>';
                    htmlWin98 += '<span>' + f.name + '</span>';
                    htmlWin98 += '</div>';
                }
            }

            if (folderList) folderList.innerHTML = htmlOsjs;
            if (folderListWin98) folderListWin98.innerHTML = htmlWin98;

            // 更新樹狀目錄的選中狀態 (僅 OS.js)
            updateTreeSelection(path);
        })
        .catch(e => {
            var errHtml = '<div class="osjs-empty">❌ 載入失敗: ' + e + '</div>';
            var errHtmlWin98 = '<div class="win98-empty">❌ 載入失敗: ' + e + '</div>';
            if (folderList) folderList.innerHTML = errHtml;
            if (folderListWin98) folderListWin98.innerHTML = errHtmlWin98;
        });
}

// 選擇資料夾（單擊）- OS.js 風格
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

// 選擇資料夾（單擊）- Win98 風格
function selectFolderWin98(elem, path) {
    // 移除其他選中狀態
    document.querySelectorAll('.win98-file-item').forEach(function(el) {
        el.classList.remove('selected');
    });
    // 設定當前選中
    elem.classList.add('selected');
    currentBrowsePath = path;

    // 更新位址列和狀態列
    var addrBox = document.getElementById('addressBoxWin98');
    var statusText = document.getElementById('statusTextWin98');
    if (addrBox) addrBox.value = path;
    if (statusText) statusText.textContent = '📂 已選擇: ' + path;
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
