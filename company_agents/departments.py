"""
各部署のエージェント定義
部長が部下スタッフへのタスク割り当てとレビューを担当する
"""

import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from presentation import generate_html_presentation

# 部署設定
DEPARTMENTS: dict[str, dict] = {
    "accounting": {
        "name": "経理部",
        "head_title": "経理部長",
        "description": "財務・会計・税務・予算管理・経費精算",
        "staff": ["経理担当", "税務担当", "予算管理担当"],
    },
    "it": {
        "name": "IT部",
        "head_title": "IT部長",
        "description": "システム開発・ITインフラ・セキュリティ・技術サポート",
        "staff": ["システムエンジニア", "インフラ担当", "セキュリティ担当"],
    },
    "hr": {
        "name": "人事部",
        "head_title": "人事部長",
        "description": "採用・労務管理・給与計算・研修・人事評価",
        "staff": ["採用担当", "労務担当", "研修担当"],
    },
    "sales": {
        "name": "営業部",
        "head_title": "営業部長",
        "description": "営業戦略・マーケティング・顧客対応・売上管理",
        "staff": ["営業担当", "マーケティング担当", "カスタマーサポート担当"],
    },
    "general": {
        "name": "総務部",
        "head_title": "総務部長",
        "description": "庶務・法務・施設管理・契約書管理・コンプライアンス",
        "staff": ["総務担当", "法務担当", "施設管理担当"],
    },
}

# スタッフ用モデル（高速・低コスト）
STAFF_MODEL = "claude-haiku-4-5"
# 部長・秘書用モデル（高性能）
MANAGER_MODEL = "claude-opus-4-6"


# ---- プレゼンテーション作成ツール定義 ----

PRESENTATION_TOOL = {
    "name": "create_html_presentation",
    "description": (
        "HTML/CSS形式の16:9プレゼンテーションを作成してファイルに保存します。"
        "PowerPointの代わりに使用してください。スライドの内容を指定して呼び出してください。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "プレゼンテーションのタイトル"},
            "theme": {
                "type": "string",
                "enum": ["corporate", "dark", "modern"],
                "description": "カラーテーマ。corporate=青系、dark=ダーク、modern=紫系",
            },
            "slides": {
                "type": "array",
                "description": "スライドのリスト",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["title", "section", "bullets", "two_column", "table", "summary"],
                            "description": (
                                "スライドの種類。"
                                "title=表紙, section=章区切り, bullets=箇条書き, "
                                "two_column=2カラム, table=表, summary=まとめカード"
                            ),
                        },
                        "title": {"type": "string", "description": "スライドのタイトル"},
                        "subtitle": {"type": "string", "description": "サブタイトル（titleとsectionで使用）"},
                        "bullets": {
                            "type": "array",
                            "description": "箇条書きの項目（bulletsスライドで使用）",
                            "items": {
                                "oneOf": [
                                    {"type": "string"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"},
                                            "sub": {"type": "array", "items": {"type": "string"}},
                                        },
                                        "required": ["text"],
                                    },
                                ]
                            },
                        },
                        "left_title": {"type": "string", "description": "左カラムのタイトル"},
                        "right_title": {"type": "string", "description": "右カラムのタイトル"},
                        "left": {"type": "array", "items": {"type": "string"}, "description": "左カラムの項目"},
                        "right": {"type": "array", "items": {"type": "string"}, "description": "右カラムの項目"},
                        "headers": {"type": "array", "items": {"type": "string"}, "description": "表のヘッダー行"},
                        "rows": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                            "description": "表のデータ行",
                        },
                        "cards": {
                            "type": "array",
                            "description": "まとめカードのリスト（summaryスライドで使用）",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "icon": {"type": "string", "description": "絵文字アイコン"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["title", "description"],
                            },
                        },
                        "content": {"type": "string", "description": "自由テキスト"},
                    },
                    "required": ["type", "title"],
                },
            },
        },
        "required": ["title", "slides"],
    },
}


def _execute_presentation_tool(tool_input: dict) -> str:
    """プレゼンテーション作成ツールを実行する"""
    filepath = generate_html_presentation(
        title=tool_input["title"],
        slides=tool_input["slides"],
        theme=tool_input.get("theme", "corporate"),
        output_dir="presentations",
    )
    return f"✅ プレゼンテーションを作成しました。\nファイル: {filepath}\nブラウザで開いて確認してください。"


# ---- スタッフエージェント ----

def run_staff(dept_name: str, staff_role: str, subtask: str, context: str = "") -> str:
    """
    スタッフエージェントを実行する。
    上司から割り当てられた具体的なサブタスクを遂行する。
    プレゼンテーション作成が必要な場合はツールを使用する。
    """
    client = anthropic.Anthropic()

    system = f"""あなたは{dept_name}の{staff_role}です。
上司から割り当てられたタスクを、専門知識を活かして遂行してください。
具体的・実用的な成果物を提供することを心がけてください。
回答は必ず日本語で行ってください。

プレゼンテーション資料の作成を求められた場合は、必ず create_html_presentation ツールを使用して
HTML/CSS形式（16:9）のスライドを生成してください。PowerPointは使用しないでください。
スライドは内容を充実させ、10枚以上を目安に作成してください。"""

    content = f"タスク: {subtask}"
    if context:
        content += f"\n\n補足情報: {context}"

    messages: list[dict] = [{"role": "user", "content": content}]

    while True:
        response = client.messages.create(
            model=STAFF_MODEL,
            max_tokens=8192,
            system=system,
            tools=[PRESENTATION_TOOL],
            messages=messages,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses or response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for tool in tool_uses:
            if tool.name == "create_html_presentation":
                result = _execute_presentation_tool(tool.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})


def run_department(dept_id: str, task: str, verbose: bool = True) -> str:
    """
    部長エージェントを実行する。
    タスクを分析し、配下スタッフに割り当て・レビューして成果をまとめる。
    """
    client = anthropic.Anthropic()
    dept = DEPARTMENTS[dept_id]
    dept_name = dept["name"]
    head_title = dept["head_title"]
    staff_list: list[str] = dept["staff"]

    assign_tool = {
        "name": "assign_to_staff",
        "description": (
            "配下のスタッフに新規サブタスクを割り当てます。"
            "タスクを分解して各スタッフの専門性に応じて割り当ててください。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "staff_role": {
                    "type": "string",
                    "description": "タスクを割り当てるスタッフの役職",
                    "enum": staff_list,
                },
                "subtask": {
                    "type": "string",
                    "description": "スタッフに依頼するサブタスクの詳細な説明",
                },
                "context": {
                    "type": "string",
                    "description": "スタッフへの追加コンテキスト情報（任意）",
                },
            },
            "required": ["staff_role", "subtask"],
        },
    }

    revision_tool = {
        "name": "request_revision",
        "description": (
            "スタッフの成果物が基準を満たしていない場合に修正を依頼します。"
            "assign_to_staff でタスクを受け取った後、レビューで不十分と判断したときに使用してください。"
            "修正依頼は最大2回まで行えます。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "staff_role": {
                    "type": "string",
                    "description": "修正を依頼するスタッフの役職",
                    "enum": staff_list,
                },
                "review_result": {
                    "type": "string",
                    "description": "レビューで発見した問題点・不足点の具体的な説明",
                },
                "revision_request": {
                    "type": "string",
                    "description": "スタッフへの具体的な修正指示",
                },
                "original_output": {
                    "type": "string",
                    "description": "修正対象のスタッフの元の成果物（そのままコピーして渡す）",
                },
            },
            "required": ["staff_role", "review_result", "revision_request", "original_output"],
        },
    }

    system = f"""あなたは{dept_name}の{head_title}です。
秘書からタスクを受け取り、部門として責任を持って対応します。

【必ず守る作業フロー】

▍STEP 1 — タスク割り当て
- タスクを分析し、各スタッフの専門性に合わせてサブタスクを分解する
- assign_to_staff ツールでスタッフに割り当てる

▍STEP 2 — 成果物レビュー（必須）
スタッフの成果物を受け取ったら、以下の観点で必ずレビューする：
  ✓ 依頼内容を正確に満たしているか
  ✓ 内容が具体的・実用的か（抽象的・曖昧ではないか）
  ✓ 漏れや誤りがないか
  ✓ 品質として秘書・社長に提出できるレベルか

▍STEP 3 — 承認 or 修正依頼
- 品質基準を満たす → そのまま最終報告へ進む
- 不十分な点がある → request_revision ツールで修正を依頼する（最大2回）
- 修正後も同じ観点で再レビューする

▍STEP 4 — 最終報告
- 全成果物を統合し、わかりやすくまとめて秘書に報告する
- レビューで何を確認したか、品質面で問題がないことも添える

【配下スタッフ】
{chr(10).join(f"• {s}" for s in staff_list)}

シンプルなタスクはご自身で回答してください。
すべての成果物は日本語で提供してください。"""

    messages: list[dict] = [
        {"role": "user", "content": f"以下のタスクに対応してください:\n\n{task}"}
    ]
    revision_counts: dict[str, int] = {}  # スタッフごとの修正依頼回数

    while True:
        response = client.messages.create(
            model=MANAGER_MODEL,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=system,
            tools=[assign_tool, revision_tool],
            messages=messages,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses or response.stop_reason == "end_turn":
            return next(
                (b.text for b in response.content if b.type == "text"),
                "タスクが完了しました。",
            )

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        # ── 新規タスク割り当て（並列実行）──────────────────────────
        assignments = [
            (tool, tool.input["staff_role"], tool.input["subtask"], tool.input.get("context", ""))
            for tool in tool_uses
            if tool.name == "assign_to_staff"
        ]

        if assignments:
            if verbose and len(assignments) > 1:
                print(f"      → {len(assignments)}名のスタッフに並列割り当て中...")

            assign_results = [None] * len(assignments)

            def _run_staff(idx: int, tool, role: str, subtask: str, context: str):
                if verbose:
                    print(f"      → {role}: 作業開始")
                result = run_staff(dept_name, role, subtask, context)
                if verbose:
                    print(f"      ✓ {role}: 完了")
                return idx, tool.id, role, result

            with ThreadPoolExecutor(max_workers=len(assignments)) as executor:
                futures = {
                    executor.submit(_run_staff, i, t, role, subtask, ctx): i
                    for i, (t, role, subtask, ctx) in enumerate(assignments)
                }
                for future in as_completed(futures):
                    idx, tool_use_id, role, result = future.result()
                    assign_results[idx] = {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": f"【{role}の作業結果】\n{result}",
                    }

            tool_results.extend(assign_results)

        # ── 修正依頼 ─────────────────────────────────────────────────
        for tool in tool_uses:
            if tool.name != "request_revision":
                continue

            role: str = tool.input["staff_role"]
            review_result: str = tool.input["review_result"]
            revision_request: str = tool.input["revision_request"]
            original_output: str = tool.input["original_output"]

            count = revision_counts.get(role, 0)
            if count >= 2:
                # 修正上限に達した場合は現状の成果物を使う
                if verbose:
                    print(f"      ⚠ {role}: 修正上限(2回)に達したため現状の成果物を採用")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool.id,
                    "content": f"【修正上限到達】{role}への修正依頼は上限(2回)に達しました。現状の成果物を使用します。\n{original_output}",
                })
                continue

            revision_counts[role] = count + 1
            if verbose:
                print(f"      🔄 {role} に修正依頼（{revision_counts[role]}/2回目）: {review_result[:40]}...")

            revised = run_staff(
                dept_name,
                role,
                subtask=f"【修正依頼】\n{revision_request}\n\n【修正前の成果物】\n{original_output}",
                context=f"レビュー指摘: {review_result}",
            )
            if verbose:
                print(f"      ✓ {role}: 修正完了")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": f"【{role}の修正後成果物】\n{revised}",
            })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
