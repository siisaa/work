"""
顧客提案管理モジュール

顧客への提案内容を保存・検索し、過去事例を新規提案に活用する。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

PROPOSALS_DIR = Path(__file__).parent / "proposals_db"
PROPOSALS_FILE = PROPOSALS_DIR / "proposals.json"


# ---------------------------------------------------------------------------
# 保存
# ---------------------------------------------------------------------------

def save_proposal(
    company_name: str,
    industry: str,
    challenges: str,
    approach: str,
    proposal_content: str,
    presentation_file: str = "",
    tags: Optional[list] = None,
) -> str:
    """
    新規顧客提案を保存する。

    Returns:
        proposal_id (例: "2026-03-28_001")
    """
    _ensure_dirs()
    proposals = _load_proposals()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    seq = sum(1 for k in proposals if k.startswith(date_str)) + 1
    proposal_id = f"{date_str}_{seq:03d}"

    proposals[proposal_id] = {
        "proposal_id": proposal_id,
        "date": date_str,
        "company_name": company_name,
        "industry": industry,
        "challenges": challenges,
        "approach": approach,
        "proposal_content": proposal_content,
        "presentation_file": presentation_file,
        "result": "pending",
        "win_reason": "",
        "loss_reason": "",
        "tags": tags or [],
        "created_at": now.isoformat(),
    }
    _save_proposals(proposals)
    return proposal_id


# ---------------------------------------------------------------------------
# 受注結果の更新
# ---------------------------------------------------------------------------

def update_proposal_result(
    proposal_id: str,
    result: str,
    reason: str,
) -> bool:
    """
    提案の受注結果（won / lost）と理由を更新する。

    Args:
        proposal_id: 更新対象の提案ID
        result: "won"（受注）または "lost"（失注）
        reason: 受注 or 失注の理由

    Returns:
        True: 更新成功 / False: 該当IDなし
    """
    proposals = _load_proposals()
    if proposal_id not in proposals:
        return False

    proposals[proposal_id]["result"] = result
    if result == "won":
        proposals[proposal_id]["win_reason"] = reason
        proposals[proposal_id]["loss_reason"] = ""
    else:
        proposals[proposal_id]["loss_reason"] = reason
        proposals[proposal_id]["win_reason"] = ""
    proposals[proposal_id]["updated_at"] = datetime.now().isoformat()

    _save_proposals(proposals)
    return True


# ---------------------------------------------------------------------------
# 検索
# ---------------------------------------------------------------------------

def search_proposals(
    query: str,
    top_k: int = 3,
    result_filter: str = "",
) -> list:
    """
    キーワードで過去提案を検索する。

    Args:
        query: 検索キーワード（スペース区切りで複数可）
        top_k: 返す件数上限
        result_filter: "" = 全件 / "won" = 受注のみ / "lost" = 失注のみ

    Returns:
        関連度スコア順の提案リスト（最大 top_k 件）
    """
    proposals = _load_proposals()
    if not proposals:
        return []

    query_terms = set(query.lower().split())
    scored = []

    for info in proposals.values():
        if result_filter and info["result"] != result_filter:
            continue

        search_text = " ".join([
            info["company_name"],
            info["industry"],
            info["challenges"],
            info["approach"],
            info["proposal_content"][:500],
            " ".join(info.get("tags", [])),
        ]).lower()

        score = sum(1 for term in query_terms if term in search_text)
        if score > 0:
            scored.append((score, info))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [info for _, info in scored[:top_k]]


def get_proposal(proposal_id: str) -> Optional[dict]:
    """提案の全内容を返す。見つからない場合は None。"""
    proposals = _load_proposals()
    return proposals.get(proposal_id)


def list_proposals(result_filter: str = "") -> list:
    """
    提案一覧を返す（新しい順）。

    Args:
        result_filter: "" = 全件 / "won" / "lost" / "pending"
    """
    proposals = _load_proposals()
    items = list(proposals.values())
    if result_filter:
        items = [p for p in items if p["result"] == result_filter]
    return sorted(items, key=lambda x: x["date"], reverse=True)


def format_search_results(results: list, include_full: bool = False) -> str:
    """検索結果を読みやすいテキストに整形する。"""
    if not results:
        return "該当する過去提案は見つかりませんでした。"

    result_labels = {"won": "受注", "lost": "失注", "pending": "結果待ち"}
    lines = [f"【過去提案 {len(results)} 件が見つかりました】\n"]

    for i, p in enumerate(results, 1):
        result_label = result_labels.get(p["result"], p["result"])

        reason_line = ""
        if p["result"] == "won" and p.get("win_reason"):
            reason_line = f"受注理由: {p['win_reason']}\n"
        elif p["result"] == "lost" and p.get("loss_reason"):
            reason_line = f"失注理由: {p['loss_reason']}\n"

        lines.append(
            f"─── 提案 {i}: {p['proposal_id']} ───\n"
            f"日付: {p['date']}  会社名: {p['company_name']}\n"
            f"業種: {p['industry']}  結果: {result_label}\n"
            f"課題: {p['challenges'][:200]}\n"
            f"アプローチ: {p['approach'][:200]}\n"
            + reason_line
        )

        if include_full:
            lines.append(f"提案内容:\n{p['proposal_content']}\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)


def _load_proposals() -> dict:
    if not PROPOSALS_FILE.exists():
        return {}
    return json.loads(PROPOSALS_FILE.read_text(encoding="utf-8"))


def _save_proposals(proposals: dict) -> None:
    PROPOSALS_FILE.write_text(
        json.dumps(proposals, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
