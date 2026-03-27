"""
会社エージェントシステム - エントリーポイント

使い方:
    python main.py

秘書が会話の受付窓口となり、必要に応じて各部署の部長に業務を委任します。
各部長は配下のスタッフにサブタスクを割り当て、レビューしてまとめます。

組織構造:
    秘書
    ├── 経理部長 → [経理担当、税務担当、予算管理担当]
    ├── IT部長   → [システムエンジニア、インフラ担当、セキュリティ担当]
    ├── 人事部長 → [採用担当、労務担当、研修担当]
    ├── 営業部長 → [営業担当、マーケティング担当、カスタマーサポート担当]
    └── 総務部長 → [総務担当、法務担当、施設管理担当]
"""

import os
import sys
from secretary import run_secretary_turn


def print_header() -> None:
    print()
    print("=" * 60)
    print("        🏢 会社エージェントシステム")
    print("=" * 60)
    print("  秘書が各部署と連携してご依頼にお応えします。")
    print("  終了: 'quit' または 'exit' と入力")
    print("=" * 60)
    print()


def check_api_key() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ エラー: ANTHROPIC_API_KEY が設定されていません。")
        print("   環境変数を設定してから再度実行してください。")
        print("   例: export ANTHROPIC_API_KEY='your-api-key'")
        return False
    return True


def main() -> None:
    if not check_api_key():
        sys.exit(1)

    print_header()

    history: list[dict] = []

    while True:
        try:
            user_input = input("👤 あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n秘書: ありがとうございました。またいつでもお声がけください。")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "終了", "bye", "さようなら"):
            print("\n🤵 秘書: ありがとうございました。またいつでもお気軽にお声がけください。")
            break

        print("\n🤵 秘書: 承りました。処理中です...\n")

        try:
            response, history = run_secretary_turn(user_input, history, verbose=True)
            print(f"\n🤵 秘書: {response}\n")

        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback

            traceback.print_exc()
            print()


if __name__ == "__main__":
    main()
