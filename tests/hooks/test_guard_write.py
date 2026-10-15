"""guard_write.py: Unity YAML・生成物・.env・API キーの実値への書き込みを止めること。"""

from __future__ import annotations

import pytest
from conftest import ROOT, run_hook

CWD = str(ROOT)


def decide(path: str, content: str = "") -> str | None:
    return run_hook(
        "guard_write.py",
        {"cwd": CWD, "tool_input": {"file_path": path, "content": content}},
    )


@pytest.mark.parametrize(
    "path",
    [
        "Assets/Scenes/HomeWorld.unity",
        "Assets/Scripts/Domain/Game.meta",
        "ProjectSettings/ProjectSettings.asset",
        "Assets/Settings/Lighting.lighting",
        "Assets/UI/Atlas.spriteatlasv2",
        "Assets/Audio/Main.mixer",
        "Assets/Render/Mirror.renderTexture",
        "Assets/Presets/Texture.preset",
        "Assets/Shaders/Warmup.shadervariants",
        "Assets/Fonts/Legacy.fontsettings",
    ],
)
def test_unity_yaml_is_denied(path: str) -> None:
    reason = decide(f"{CWD}/{path}")
    assert reason is not None and "Unity が管理する YAML" in reason


@pytest.mark.parametrize(
    "path",
    [
        "Library/ScriptAssemblies/x.dll.txt",
        "Temp/x.txt",
        "Assembly-CSharp.csproj",
        "backend/.venv/lib/x.py",
        "tools/__pycache__/x.pyc",
    ],
)
def test_generated_files_are_denied(path: str) -> None:
    reason = decide(f"{CWD}/{path}")
    assert reason is not None and "生成物" in reason


def test_build_source_directory_is_not_generated() -> None:
    # Assets/Editor/Build/ はソース。リポジトリ直下の Build/ と取り違えない。
    assert decide(f"{CWD}/Assets/Editor/Build/BuildEntry.cs") is None


@pytest.mark.parametrize("path", [".env", "backend/.env", "backend/.env.local"])
def test_env_is_denied(path: str) -> None:
    reason = decide(f"{CWD}/{path}")
    assert reason is not None and ".env" in reason


@pytest.mark.parametrize(
    "content",
    [
        "key = 'AIza" + "x" * 35 + "'",
        "GEMINI_API_KEY=" + "a1b2c3d4" * 4,
        "sk-ant-" + "A" * 40,
    ],
)
def test_api_key_values_are_denied(content: str) -> None:
    assert decide(f"{CWD}/backend/src/penguin_backend/config.py", content) is not None


@pytest.mark.parametrize(
    "content",
    [
        "GEMINI_API_KEY=",
        "GEMINI_API_KEY=your-gemini-api-key",
        "GEMINI_API_KEY=${GEMINI_API_KEY}",
    ],
)
def test_env_example_placeholders_pass(content: str) -> None:
    assert decide(f"{CWD}/backend/.env.example", content) is None


def test_ordinary_source_passes() -> None:
    assert (
        decide(
            f"{CWD}/Assets/Scripts/Domain/Game/GameSession.cs",
            "public sealed class X {}",
        )
        is None
    )
