"""PreToolUse(Bash): 取り返しのつかない git 操作をブロックする。

確認を挟めば済む操作 (commit / push / rebase など) は settings.json の
permissions.ask に任せ、ここでは「確認しても許可しない」ものだけを deny する。
"""

import json
import os
import re
import shlex
import subprocess
import sys

# シェルの区切りでコマンドを分割する。$(...) や `...` の中身も 1 セグメントとして拾う。
_SPLIT = re.compile(r"\|\||&&|[;|&\n]|\$\(|`|\)")
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# git 本体のグローバルオプション。サブコマンドを探すときに読み飛ばす。
_GLOBAL_OPT_WITH_ARG = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def deny(reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )
    sys.exit(0)


def tokenize(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def git_invocations(command: str) -> list[tuple[str, list[str]]]:
    """コマンド文字列から (サブコマンド, 残りの引数) を全部拾う。"""
    found = []
    for segment in _SPLIT.split(command):
        tokens = tokenize(segment.strip())
        while tokens and _ASSIGN.match(tokens[0]):  # FOO=bar git ... を剥がす
            tokens.pop(0)
        if not tokens or os.path.basename(tokens[0]).removesuffix(".exe") != "git":
            continue
        rest = tokens[1:]
        while rest:
            if rest[0] in _GLOBAL_OPT_WITH_ARG:
                rest = rest[2:]
            elif rest[0].startswith("-"):
                rest = rest[1:]
            else:
                break
        if rest:
            found.append((rest[0], rest[1:]))
    return found


def current_branch(cwd: str) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    command = (payload.get("tool_input") or {}).get("command") or ""
    if not command:
        return
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or ""

    for sub, args in git_invocations(command):
        if sub in ("filter-branch", "filter-repo"):
            deny(
                "履歴の一括改変 (git " + sub + ") は禁止しています。"
                "LFS ポインタと Unity アセットの GUID を巻き込んで壊れます。"
                "必要なら手順の提示だけ行い、実行はユーザーに任せてください。"
            )

        if sub == "push":
            if any(a in ("-f", "--force") or a.startswith("--force-with-lease") or a.startswith("--force-if-includes") for a in args):
                deny(
                    "force push は禁止しています。公開リポジトリで履歴を書き換えると "
                    "LFS オブジェクトの参照も壊れます。手順の提示にとどめてください。"
                )
            refs = [a for a in args if not a.startswith("-")]
            targets = " ".join(refs)
            if re.search(r"(^|[\s:])(main|master)($|[\s:])", targets) or (
                len(refs) <= 1 and current_branch(cwd) in ("main", "master")
            ):
                deny(
                    "main への直接 push は禁止しています。"
                    "feat/ fix/ chore/ などの作業ブランチを切って PR 経由でマージしてください。"
                )

        if sub == "commit":
            if any(a in ("-n", "--no-verify") for a in args):
                deny("--no-verify はフックを迂回するため禁止しています。失敗の原因を直してからコミットしてください。")

        if sub == "add":
            for a in args:
                if a.startswith("-"):
                    continue
                base = os.path.basename(a)
                if base == ".env" or re.search(r"\.(db|sqlite3?|pem|key)$", base):
                    deny(
                        f"`{a}` は秘密情報またはローカル DB (購買履歴) です。"
                        "public リポジトリのためコミットは回復不能な事故になります。"
                    )

    return


if __name__ == "__main__":
    main()
