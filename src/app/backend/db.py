#!/usr/bin/env python3
"""
数据库模块 - 诊断历史记录管理
使用 SQLite 存储每次诊断结果
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

from config import DB_PATH


def get_db_path():
    """确保数据库目录存在并返回路径"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            image_size TEXT,
            predicted_class TEXT NOT NULL,
            predicted_class_cn TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities TEXT NOT NULL,
            gradcam_path TEXT,
            model_type TEXT DEFAULT 'efficientnet_b0',
            use_tta INTEGER DEFAULT 1,
            inference_time_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 批量记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batch_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_name TEXT,
            total_count INTEGER,
            class_distribution TEXT,
            malignant_ratio REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ==================== CRUD 操作 ====================

def save_diagnosis(result: dict, filename: str = '', image_size: str = '',
                   gradcam_path: str = '', inference_time_ms: float = 0) -> int:
    """保存单次诊断记录，返回新记录 ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO diagnosis_history 
        (filename, image_size, predicted_class, predicted_class_cn, confidence,
         probabilities, gradcam_path, model_type, use_tta, inference_time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        image_size,
        result.get('predicted_class', ''),
        result.get('predicted_class_cn', ''),
        result.get('confidence', 0),
        json.dumps(result.get('probabilities', {}), ensure_ascii=False),
        gradcam_path,
        result.get('model_type', 'efficientnet_b0'),
        1 if result.get('tta_augments') else 0,
        inference_time_ms,
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def save_batch_record(summary: dict, batch_name: str = '') -> int:
    """保存批量诊断摘要"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO batch_records (batch_name, total_count, class_distribution, malignant_ratio)
        VALUES (?, ?, ?, ?)
    ''', (
        batch_name or f"批量_{datetime.now().strftime('%m%d_%H%M')}",
        summary.get('total', 0),
        json.dumps(summary.get('class_distribution', {}), ensure_ascii=False),
        summary.get('malignant_ratio', 0),
    ))
    record_id = cursor.lastrowid
    # 同时将每条结果存入 history
    for r in summary.get('results', []):
        save_diagnosis(r, filename=r.get('filename', ''))
    conn.commit()
    conn.close()
    return record_id


def get_recent_history(limit: int = 50, offset: int = 0) -> list:
    """获取最近的历史记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM diagnosis_history 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    # 解析 JSON 字段
    for row in rows:
        row['probabilities'] = json.loads(row['probabilities']) if isinstance(row['probabilities'], str) else {}
    return rows


def get_history_stats() -> dict:
    """获取统计信息"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM diagnosis_history')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT predicted_class, COUNT(*) as cnt 
        FROM diagnosis_history GROUP BY predicted_class
    ''')
    class_dist = {row['predicted_class']: row['cnt'] for row in cursor.fetchall()}

    cursor.execute('SELECT AVG(inference_time_ms) FROM diagnosis_history WHERE inference_time_ms > 0')
    avg_time = cursor.fetchone()[0] or 0

    cursor.execute('SELECT DATE(created_at) as d, COUNT(*) FROM diagnosis_history GROUP BY d ORDER BY d DESC LIMIT 7')
    daily = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

    conn.close()
    return {
        'total': total,
        'class_distribution': class_dist,
        'avg_inference_time': round(avg_time, 1),
        'daily_counts': daily,
    }


def delete_history(record_id: int) -> bool:
    """删除单条记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM diagnosis_history WHERE id = ?', (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def clear_all_history() -> int:
    """清空所有历史记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM diagnosis_history')
    count = cursor.fetchone()[0]
    cursor.execute('DELETE FROM diagnosis_history')
    conn.commit()
    conn.close()
    return count


# 初始化
init_db()
