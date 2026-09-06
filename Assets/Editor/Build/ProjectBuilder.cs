using System;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace ProjectPenguin.Editor.Build
{
    /// <summary>
    /// ビルドの実行本体。MenuItem と CLI の両方がここを通る。
    /// 設定の書き換えは <see cref="PlayerSettingsScope"/> の中だけで行い、必ず元へ戻す。
    /// </summary>
    public static class ProjectBuilder
    {
        /// <summary>iOS の署名チーム ID。未設定なら Xcode 側で指定する。</summary>
        public const string AppleTeamIdEnv = "PENGUIN_IOS_TEAM_ID";

        public static BuildReport Run(BuildRequest request)
        {
            if (request == null)
            {
                throw new ArgumentNullException(nameof(request));
            }

            var scenes = EnabledScenes();
            if (scenes.Length == 0)
            {
                throw new BuildRequestException(
                    "Build Settings に有効なシーンが 1 つもありません。"
                    + "File > Build Profiles でシーンを追加してください。");
            }

            if (EditorUserBuildSettings.activeBuildTarget != request.Target)
            {
                if (!EditorUserBuildSettings.SwitchActiveBuildTarget(request.Group, request.Target))
                {
                    throw new BuildRequestException(
                        $"{request.Target} へ切り替えられませんでした。"
                        + "Unity Hub で該当プラットフォームのビルドモジュールを追加してください。");
                }
            }

            using (new PlayerSettingsScope())
            {
                if (!string.IsNullOrWhiteSpace(request.BundleVersion))
                {
                    PlayerSettings.bundleVersion = request.BundleVersion;
                }

                var signing = "—";
                if (request.IsAndroid)
                {
                    if (request.AndroidVersionCode.HasValue)
                    {
                        PlayerSettings.Android.bundleVersionCode = request.AndroidVersionCode.Value;
                    }

                    EditorUserBuildSettings.buildAppBundle = request.Kind == BuildKind.AndroidAab;
                    signing = AndroidSigning.Apply(request);
                }
                else
                {
                    var team = Environment.GetEnvironmentVariable(AppleTeamIdEnv);
                    if (!string.IsNullOrWhiteSpace(team))
                    {
                        PlayerSettings.iOS.appleDeveloperTeamID = team;
                        signing = $"team {team}";
                    }
                    else
                    {
                        signing = "未設定 (Xcode 側で指定する)";
                    }
                }

                var location = ResolveLocation(request);
                var parent = Path.GetDirectoryName(location);
                if (!string.IsNullOrEmpty(parent))
                {
                    Directory.CreateDirectory(parent);
                }

                Debug.Log(Describe(request, scenes, location, signing));

                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = scenes,
                    locationPathName = location,
                    target = request.Target,
                    targetGroup = request.Group,
                    options = request.Development
                        ? BuildOptions.Development | BuildOptions.AllowDebugging | BuildOptions.ConnectWithProfiler
                        : BuildOptions.None,
                });

                LogResult(request, report);
                return report;
            }
        }

        /// <summary>Build Settings で有効になっているシーンだけを、その並び順で返す。</summary>
        public static string[] EnabledScenes() =>
            EditorBuildSettings.scenes
                .Where(scene => scene.enabled && !string.IsNullOrEmpty(scene.path))
                .Select(scene => scene.path)
                .ToArray();

        /// <summary>成果物の出力先。Android はファイル、iOS は Xcode プロジェクトのディレクトリ。</summary>
        public static string ResolveLocation(BuildRequest request)
        {
            var root = string.IsNullOrWhiteSpace(request.OutputRoot) ? "Builds" : request.OutputRoot;

            if (!request.IsAndroid)
            {
                return Path.GetFullPath(Path.Combine(root, "iOS"));
            }

            var name = SafeFileName(PlayerSettings.productName);
            var version = SafeFileName(PlayerSettings.bundleVersion);
            var suffix = request.Development ? "-dev" : string.Empty;
            var extension = request.Kind == BuildKind.AndroidAab ? "aab" : "apk";

            return Path.GetFullPath(Path.Combine(root, "Android", $"{name}-{version}{suffix}.{extension}"));
        }

        private static string SafeFileName(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return "build";
            }

            var invalid = Path.GetInvalidFileNameChars();
            var builder = new StringBuilder(value.Length);
            foreach (var c in value)
            {
                builder.Append(invalid.Contains(c) || char.IsWhiteSpace(c) ? '-' : c);
            }

            return builder.ToString();
        }

        private static string Describe(BuildRequest request, string[] scenes, string location, string signing)
        {
            var builder = new StringBuilder();
            builder.AppendLine($"[Build] {request.Label} を開始します。");
            builder.AppendLine($"  出力先        : {location}");
            builder.AppendLine($"  バージョン    : {PlayerSettings.bundleVersion}"
                + (request.IsAndroid ? $" (versionCode {PlayerSettings.Android.bundleVersionCode})" : string.Empty));
            builder.AppendLine($"  Development   : {(request.Development ? "あり" : "なし")}");
            builder.AppendLine($"  署名          : {signing}");
            builder.AppendLine($"  スクリプト    : {PlayerSettings.GetScriptingBackend(request.NamedTarget)}");
            builder.AppendLine($"  シーン ({scenes.Length}) : {string.Join(", ", scenes)}");
            return builder.ToString().TrimEnd();
        }

        private static void LogResult(BuildRequest request, BuildReport report)
        {
            var summary = report.summary;
            // TimeSpan の書式指定子はコロンをエスケープする必要がある。補間文字列に
            // 直接書くとエスケープが二重になるため、先に文字列へ落とす。
            var elapsed = summary.totalTime.ToString(@"hh\:mm\:ss");
            var message =
                $"[Build] {request.Label} : {summary.result} / "
                + $"{summary.totalSize / (1024f * 1024f):F1} MB / {elapsed}\n"
                + $"  {summary.outputPath}";

            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log(message);
                return;
            }

            // 失敗の原因は BuildReport のログに入っている。要約だけでは追えないので抜き出す。
            var errors = report.steps
                .SelectMany(step => step.messages)
                .Where(m => m.type == LogType.Error || m.type == LogType.Exception)
                .Select(m => "  " + m.content)
                .Take(20);

            Debug.LogError(message + "\n" + string.Join("\n", errors));
        }
    }
}
