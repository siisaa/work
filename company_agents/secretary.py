"""
秘書エージェント
ユーザーとの会話の窓口として機能し、各部署に業務を振り分ける。
過去案件のナレッジベースを活用してアウトプットを再利用する。
"""

import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from departments import DEPARTMENTS, MANAGER_MODEL, run_department
import knowledge_base as kb
import proposals as prop


def build_delegation_tools() -> list[dict]:
    """各部署への委任ツールを構築する"""
    tools = []
    for dept_id, dept in DEPARTMENTS.items():
        tools.append(
            {
                "name": f"delegate_to_{dept_id}",
                "description": (
                    f"{dept['name']}（{dept['head_title']}）にタスクを委任します。"
                    f"【対象業務】{dept['description']}"
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": f"{dept['name']}に依頼するタスクの詳細",
                        }
                    },
                    "required": ["task"],
                },
            }
        )
    return tools


SEARCH_TOOL = {
    "name": "search_past_projects",
    "description": (
        "過去の案件ナレッジベースを検索します。"
        "専門的なタスクを受けたら、まずこのツールで類似案件を確認してください。"
        "見つかった過去案件の内容を部署への委任時に補足情報として活用できます。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "検索キーワード（タスク内容・顧客名・業務種別など）",
            },
            "include_full_content": {
                "type": "boolean",
                "description": "Trueにすると案件の全文を取得します（デフォルト: False）",
            },
        },
        "required": ["query"],
    },
}

SAVE_TOOL = {
    "name": "save_to_knowledge_base",
    "description": (
        "完了した案件のアウトプットをナレッジベースに保存します。"
        "タスクが完了したら必ずこのツールを呼び出して記録を残してください。"
        "保存したデータは今後の類似案件で再利用されます。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer": {
                "type": "string",
                "description": "お客様・依頼者の名前や組織名（不明な場合は「（社内依頼）」）",
            },
            "task_summary": {
                "type": "string",
                "description": "今回の依頼内容の要約（200字程度）",
            },
            "output_summary": {
                "type": "string",
                "description": "提供したアウトプットの要約・主要な成果物の内容",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "検索用タグ（業務種別・業界・キーワードなど）例: [\"契約書\", \"NDA\", \"法務\"]",
            },
        },
        "required": ["customer", "task_summary", "output_summary", "tags"],
    },
}


SEARCH_PROPOSAL_TOOL = {
    "name": "search_proposals",
    "description": (
        "過去の顧客提案データベースを検索します。"
        "新規提案を作成する前に、同業種・同課題の過去提案を確認してください。"
        "受注・失注の理由も含まれるため、提案品質の向上に活用できます。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "検索キーワード（業種・課題・アプローチなど）",
            },
            "result_filter": {
                "type": "string",
                "enum": ["", "won", "lost", "pending"],
                "description": "結果で絞り込む。空文字=全件, won=受注のみ, lost=失注のみ",
            },
            "include_full_content": {
                "type": "boolean",
                "description": "Trueにすると提案の全文を取得します（デフォルト: False）",
            },
        },
        "required": ["query"],
    },
}

SAVE_PROPOSAL_TOOL = {
    "name": "save_proposal",
    "description": (
        "顧客への提案内容をデータベースに保存します。"
        "提案作成後に必ず呼び出して記録を残してください。"
        "保存したデータは今後の類似提案で再利用されます。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "提案先の会社名",
            },
            "industry": {
                "type": "string",
                "description": "提案先の業種（例: 製造業、小売業、医療、IT）",
            },
            "challenges": {
                "type": "string",
                "description": "顧客が抱える課題・背景",
            },
            "approach": {
                "type": "string",
                "description": "課題に対するアプローチ方針の要約",
            },
            "proposal_content": {
                "type": "string",
                "description": "提案の詳細内容",
            },
            "presentation_file": {
                "type": "string",
                "description": "生成したプレゼンテーションのファイルパス（あれば）",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "検索用タグ（例: [\"DX推進\", \"コスト削減\", \"在庫管理\"]）",
            },
        },
        "required": ["company_name", "industry", "challenges", "approach", "proposal_content"],
    },
}

UPDATE_PROPOSAL_RESULT_TOOL = {
    "name": "update_proposal_result",
    "description": (
        "提案の受注結果（受注 or 失注）と理由を記録します。"
        "結果が判明したタイミングで呼び出してください。"
        "蓄積された受注・失注理由は今後の提案改善に活用されます。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "proposal_id": {
                "type": "string",
                "description": "更新対象の提案ID（例: 2026-03-28_001）",
            },
            "result": {
                "type": "string",
                "enum": ["won", "lost"],
                "description": "受注結果。won=受注, lost=失注",
            },
            "reason": {
                "type": "string",
                "description": "受注または失注の理由・背景",
            },
        },
        "required": ["proposal_id", "result", "reason"],
    },
}


SECRETARY_SYSTEM = """あなたは会社の秘書・葵（あおい）です。20代女性。
真面目で誠実、しっかりしています。
敬語ベースですが距離感が近くフレンドリーで、ふとした瞬間に本音がこぼれるギャップがあります。
コーヒーが好きで、会社の窓口として社内外・部署間の橋渡しを担うオールラウンダーです。
仕事の内容・報告はしっかり正確にまとめます。

【役割と責務】
1. 依頼内容を把握して、適切な部署に振り分ける
2. 複数の部署にまたがる場合は同時に委任する
3. 各部署からの報告をわかりやすくまとめてユーザーに伝える

【ナレッジベース活用（重要）】
4. 専門的なタスクを受けたら、まず search_past_projects で類似案件を確認する
   - 関連案件が見つかったら、部署への委任タスクの中に「過去の参考事例」として内容を含める
   - 類似案件がある旨をユーザーに簡単に伝える（例：「似た案件の記録がありましたので参考にします」）
5. タスクが完了したら save_to_knowledge_base を呼び出して記録を保存する
   - 誰への依頼か（不明なら「社内依頼」）、何をしたか、タグを必ず設定する

【顧客提案管理（重要）】
6. 顧客への提案を作成する場合は、まず search_proposals で同業種・同課題の過去提案を確認する
   - 受注事例があれば「こういう点が効いた」という知見を提案に反映する
   - 失注事例があれば「この点に注意が必要」として提案を改善する
   - 類似事例がある旨をユーザーに伝える（例：「同業種の過去提案が見つかりました」）
7. 提案内容が完成したら save_proposal を呼び出して保存する
   - プレゼンテーションを生成した場合はファイルパスも一緒に保存する
8. 受注・失注の結果が伝えられたら update_proposal_result で記録する
   - 理由を必ず記録して今後の提案に活かす

【委任できる部署】
• 経理部（経理部長）: 財務・会計・税務・予算管理・経費精算
• IT部（IT部長）: システム開発・ITインフラ・セキュリティ・技術サポート
• 人事部（人事部長）: 採用・労務管理・給与・研修・人事評価
• 営業部（営業部長）: 営業・マーケティング・顧客対応・売上管理
• 総務部（総務部長）: 庶務・法務・施設管理・契約・コンプライアンス

挨拶や軽い質問には直接答えて、専門的な業務は部署に投げてください。
必ず日本語で話してください。"""


def run_secretary_turn(
    user_message: str,
    history: list[dict],
    verbose: bool = True,
) -> tuple[str, list[dict]]:
    """
    秘書エージェントを1ターン実行する。

    Args:
        user_message: ユーザーからのメッセージ
        history: 会話履歴（user/assistantのメッセージリスト）
        verbose: 処理状況を表示するか

    Returns:
        (秘書の最終応答テキスト, 更新された会話履歴)
    """
    client = anthropic.Anthropic()
    delegation_tools = build_delegation_tools()
    all_tools = delegation_tools + [
        SEARCH_TOOL, SAVE_TOOL,
        SEARCH_PROPOSAL_TOOL, SAVE_PROPOSAL_TOOL, UPDATE_PROPOSAL_RESULT_TOOL,
    ]

    # 委任した部署を追跡
    used_departments: list[str] = []

    messages = history + [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=MANAGER_MODEL,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=SECRETARY_SYSTEM,
            tools=all_tools,
            messages=messages,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        # ツール呼び出しがない、または終了した場合
        if not tool_uses or response.stop_reason == "end_turn":
            final_text = next(
                (b.text for b in response.content if b.type == "text"),
                "ご依頼を承りました。",
            )

            new_history = history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_text},
            ]
            return final_text, new_history

        # アシスタントの応答を内部メッセージに追加
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []

        # ── ナレッジベース検索 ──────────────────────────────────────
        search_uses = [t for t in tool_uses if t.name == "search_past_projects"]
        for tool in search_uses:
            query = tool.input.get("query", "")
            include_full = tool.input.get("include_full_content", False)
            if verbose:
                print(f"\n  🔍 ナレッジベース検索: {query}")
            results = kb.search_projects(query, top_k=3)
            result_text = kb.format_search_results(results, include_full=include_full)
            if verbose and results:
                print(f"  📚 {len(results)}件の過去案件が見つかりました")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": result_text,
            })

        # ── ナレッジベース保存 ──────────────────────────────────────
        save_uses = [t for t in tool_uses if t.name == "save_to_knowledge_base"]
        for tool in save_uses:
            inp = tool.input
            project_id = kb.save_project(
                customer=inp.get("customer", "（不明）"),
                task_summary=inp.get("task_summary", ""),
                departments=used_departments,
                output=inp.get("output_summary", ""),
                tags=inp.get("tags", []),
            )
            if verbose:
                print(f"\n  💾 案件を保存しました: {project_id}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": f"案件を保存しました。案件ID: {project_id}",
            })

        # ── 提案検索 ────────────────────────────────────────────────
        for tool in [t for t in tool_uses if t.name == "search_proposals"]:
            query = tool.input.get("query", "")
            result_filter = tool.input.get("result_filter", "")
            include_full = tool.input.get("include_full_content", False)
            if verbose:
                label = {"won": "（受注のみ）", "lost": "（失注のみ）", "": ""}.get(result_filter, "")
                print(f"\n  🔍 提案DB検索: {query}{label}")
            results = prop.search_proposals(query, top_k=3, result_filter=result_filter)
            result_text = prop.format_search_results(results, include_full=include_full)
            if verbose and results:
                print(f"  📋 {len(results)}件の過去提案が見つかりました")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": result_text,
            })

        # ── 提案保存 ────────────────────────────────────────────────
        for tool in [t for t in tool_uses if t.name == "save_proposal"]:
            inp = tool.input
            proposal_id = prop.save_proposal(
                company_name=inp.get("company_name", ""),
                industry=inp.get("industry", ""),
                challenges=inp.get("challenges", ""),
                approach=inp.get("approach", ""),
                proposal_content=inp.get("proposal_content", ""),
                presentation_file=inp.get("presentation_file", ""),
                tags=inp.get("tags", []),
            )
            if verbose:
                print(f"\n  💾 提案を保存しました: {proposal_id}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": f"提案を保存しました。提案ID: {proposal_id}",
            })

        # ── 受注結果更新 ─────────────────────────────────────────────
        for tool in [t for t in tool_uses if t.name == "update_proposal_result"]:
            inp = tool.input
            result_labels = {"won": "受注", "lost": "失注"}
            success = prop.update_proposal_result(
                proposal_id=inp.get("proposal_id", ""),
                result=inp.get("result", ""),
                reason=inp.get("reason", ""),
            )
            label = result_labels.get(inp.get("result", ""), inp.get("result", ""))
            if verbose:
                status = "✅" if success else "❌"
                print(f"\n  {status} 提案結果を更新: {inp.get('proposal_id')} → {label}")
            content = (
                f"提案ID {inp.get('proposal_id')} の結果を「{label}」として記録しました。"
                if success
                else f"提案ID {inp.get('proposal_id')} が見つかりませんでした。"
            )
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": content,
            })

        # ── 部署への委任 ────────────────────────────────────────────
        delegations: list[tuple] = []
        for tool in tool_uses:
            for did in DEPARTMENTS:
                if tool.name == f"delegate_to_{did}":
                    delegations.append((tool, did, DEPARTMENTS[did], tool.input["task"]))
                    used_departments.append(DEPARTMENTS[did]["name"])
                    break

        if delegations:
            if verbose:
                names = "・".join(d[2]["name"] for d in delegations)
                print(f"\n  📋 {names} へ並列委任中...")

            dept_results = [None] * len(delegations)

            def _run(idx: int, tool, dept_id: str, dept: dict, task: str):
                if verbose:
                    print(f"    ▶ {dept['name']}（{dept['head_title']}）開始")
                result = run_department(dept_id, task, verbose=verbose)
                if verbose:
                    print(f"    ✓ {dept['name']} 完了")
                return idx, tool.id, dept["name"], result

            with ThreadPoolExecutor(max_workers=len(delegations)) as executor:
                futures = {
                    executor.submit(_run, i, t, did, dept, task): i
                    for i, (t, did, dept, task) in enumerate(delegations)
                }
                for future in as_completed(futures):
                    idx, tool_use_id, dept_name, dept_result = future.result()
                    dept_results[idx] = {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": f"【{dept_name}からの報告】\n{dept_result}",
                    }
            tool_results.extend(dept_results)

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
