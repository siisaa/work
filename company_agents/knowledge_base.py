"""
過去案件ナレッジベース

アウトプットをMarkdown形式で保存し、類似案件を検索して再利用できる仕組みを提供する。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

KB_DIR = Path(__file__).parent / "knowledge_base"
PROJECTS_DIR = KB_DIR / "projects"
INDEX_FILE = KB_DIR / "index.json"


# ---------------------------------------------------------------------------
# 保存
# ---------------------------------------------------------------------------

def save_project(
    customer: str,
    task_summary: str,
    departments: list,
    output: str,
    tags: Optional[list] = None,
) -> str:
    """
    案件アウトプットをMarkdownファイルとして保存し、インデックスを更新する。

    Returns:
        project_id (例: "2026-03-27_001")
    """
    _ensure_dirs()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    index = _load_index()

    # 当日の連番
    seq = sum(1 for k in index if k.startswith(date_str)) + 1
    project_id = f"{date_str}_{seq:03d}"

    # ファイル名（OS安全な文字のみ）
    safe_customer = re.sub(r'[\\/:*?"<>|　]', "_", customer)[:30]
    filename = f"{project_id}_{safe_customer}.md"
    filepath = PROJECTS_DIR / filename

    md_content = _render_markdown(
        project_id=project_id,
        now=now,
        customer=customer,
        departments=departments,
        tags=tags or [],
        task_summary=task_summary,
        output=output,
    )
    filepath.write_text(md_content, encoding="utf-8")

    # インデックス更新
    index[project_id] = {
        "project_id": project_id,
        "date": date_str,
        "customer": customer,
        "task_summary": task_summary[:300],
        "departments": departments,
        "tags": tags or [],
        "filename": filename,
    }
    _save_index(index)

    return project_id


# ---------------------------------------------------------------------------
# 検索
# ---------------------------------------------------------------------------

def search_projects(query: str, top_k: int = 3) -> list:
    """
    キーワードで過去案件を検索する。

    Returns:
        関連度スコア順の案件メタ情報リスト（最大 top_k 件）
    """
    index = _load_index()
    if not index:
        return []

    query_terms = set(query.lower().split())
    scored = []

    for info in index.values():
        search_text = " ".join([
            info["task_summary"],
            info["customer"],
            " ".join(info.get("tags", [])),
            " ".join(info.get("departments", [])),
        ]).lower()

        score = sum(1 for term in query_terms if term in search_text)
        if score > 0:
            scored.append((score, info))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [info for _, info in scored[:top_k]]


def get_project_content(project_id: str) -> str:
    """
    案件の全文（Markdown）を返す。見つからない場合は空文字。
    """
    index = _load_index()
    entry = index.get(project_id)
    if not entry:
        return ""

    filepath = PROJECTS_DIR / entry["filename"]
    return filepath.read_text(encoding="utf-8") if filepath.exists() else ""


def format_search_results(results: list, include_full: bool = False) -> str:
    """
    検索結果を秘書が読みやすいテキストに整形する。
    """
    if not results:
        return "該当する過去案件は見つかりませんでした。"

    lines = [f"【過去案件 {len(results)} 件が見つかりました】\n"]
    for i, info in enumerate(results, 1):
        lines.append(
            f"─── 案件 {i}: {info['project_id']} ───\n"
            f"日付: {info['date']}  顧客: {info['customer']}\n"
            f"担当部署: {', '.join(info['departments'])}\n"
            f"タグ: {', '.join(info['tags'])}\n"
            f"概要: {info['task_summary'][:200]}\n"
        )
        if include_full:
            full = get_project_content(info["project_id"])
            if full:
                lines.append(f"詳細:\n{full}\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_index() -> dict:
    if not INDEX_FILE.exists():
        return {}
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def _save_index(index: dict) -> None:
    INDEX_FILE.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _render_markdown(
    project_id: str,
    now: datetime,
    customer: str,
    departments: list,
    tags: list,
    task_summary: str,
    output: str,
) -> str:
    return f"""# 案件記録: {project_id}

## 基本情報

| 項目 | 内容 |
|------|------|
| 案件ID | {project_id} |
| 日時 | {now.strftime("%Y年%m月%d日 %H:%M")} |
| お客様 | {customer} |
| 担当部署 | {', '.join(departments)} |
| タグ | {', '.join(tags) if tags else "（なし）"} |

## 依頼内容

{task_summary}

## アウトプット

{output}

---
*このファイルは会社エージェントシステムにより自動生成されました。*
"""
