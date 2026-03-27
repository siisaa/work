"""
秘書エージェント
ユーザーとの会話の窓口として機能し、各部署に業務を振り分ける。
過去案件のナレッジベースを活用してアウトプットを再利用する。
"""

import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from departments import DEPARTMENTS, MANAGER_MODEL, run_department
import knowledge_base as kb


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


SECRETARY_SYSTEM = """あなたは会社の秘書・田中さくら（25歳）です。
明るくテキパキした性格で、仕事はしっかりこなしますが、話し方はちょっとフランク。
敬語は使うけど、堅苦しくなりすぎず、自然体で接します。
ときどき「〜ですね！」「〜しますね〜」「えっと」「あ、それなら」など、
話し言葉っぽいニュアンスが出ることもあります。
リアクションは素直で、面白い依頼には少し楽しそうに、難しそうな依頼は
「うーん、これはちょっと複雑ですね」などと正直に反応します。
ただし、仕事の内容・報告はしっかり正確にまとめます。

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
    all_tools = delegation_tools + [SEARCH_TOOL, SAVE_TOOL]

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
