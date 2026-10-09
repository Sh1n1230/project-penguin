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


# git push のうち、次の引数を値として取るオプション。値を refspec と取り違えないよう読み飛ばす。
_PUSH_OPT_WITH_ARG = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
_PROTECTED = ("main", "master")


def parse_push(args: list[str]) -> tuple[list[str], list[str]]:
    """git push の引数を (オプション, refspec) に分ける。最初の位置引数はリモート名なので捨てる。"""
    options: list[str] = []
    positionals: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            positionals.extend(args[i + 1:])
            break
        if arg.startswith("-"):
            options.append(arg)
            if arg in _PUSH_OPT_WITH_ARG:
                i += 1
        else:
            positionals.append(arg)
        i += 1
    return options, positionals[1:]


def is_force_option(option: str) -> bool:
    """force push になるオプションか。-uf のような短いオプションのまとめ書きも見る。"""
    if option in ("--force", "--mirror"):
        return True
    if option.startswith(("--force-with-lease", "--force-if-includes")):
        return True
    # git push の短いオプションで f を含むのは -f (--force) だけ。
    return re.fullmatch(r"-[A-Za-z0-9]*f[A-Za-z0-9]*", option) is not None


def push_target(refspec: str, cwd: str) -> str:
    """refspec の push 先のブランチ名。HEAD は今のブランチに、refs/heads/ は外して返す。"""
    src, sep, dst = refspec.lstrip("+").partition(":")
    target = dst if sep else src
    if target in ("HEAD", "@"):
        target = current_branch(cwd)
    return target.removeprefix("refs/heads/")


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
            options, refspecs = parse_push(args)
            # refspec 先頭の + も、そのブランチだけの force push になる。
            if any(is_force_option(o) for o in options) or any(r.startswith("+") for r in refspecs):
                deny(
                    "force push は禁止しています。公開リポジトリで履歴を書き換えると "
                    "LFS オブジェクトの参照も壊れます。手順の提示にとどめてください。"
                )
            # --all はローカルの main も、refspec の省略は今のブランチを push する。
            # ":" だけの refspec は同名のブランチをすべて push する。
            pushes_main = (
                any(o in ("--all", "--branches") for o in options)
                or (not refspecs and current_branch(cwd) in _PROTECTED)
                or any(r.lstrip("+") == ":" or push_target(r, cwd) in _PROTECTED for r in refspecs)
            )
            if pushes_main:
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
