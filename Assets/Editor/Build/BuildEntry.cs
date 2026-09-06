using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ProjectPenguin.Editor.Build
{
    /// <summary>
    /// ビルドの入口。Editor のメニューと CLI の -executeMethod が両方ここに来る。
    ///
    ///   Unity -quit なしで実行し、終了コードはこちらの EditorApplication.Exit で返す:
    ///     Unity -batchmode -nographics -projectPath . -logFile - \
    ///           -executeMethod ProjectPenguin.Editor.Build.BuildEntry.AndroidApk -- --dev
    /// </summary>
    public static class BuildEntry
    {
        private const string MenuRoot = "Build/";

        // ---- Editor メニュー -------------------------------------------------

        [MenuItem(MenuRoot + "Android APK (Development)", priority = 10)]
        public static void MenuAndroidApkDevelopment() =>
            RunFromMenu(new BuildRequest { Kind = BuildKind.AndroidApk, Development = true });

        [MenuItem(MenuRoot + "Android APK", priority = 11)]
        public static void MenuAndroidApk() =>
            RunFromMenu(new BuildRequest { Kind = BuildKind.AndroidApk });

        [MenuItem(MenuRoot + "Android AAB (配布用)", priority = 12)]
        public static void MenuAndroidAab() =>
            RunFromMenu(new BuildRequest { Kind = BuildKind.AndroidAab });

        [MenuItem(MenuRoot + "iOS Xcode プロジェクト", priority = 30)]
        public static void MenuIos() =>
            RunFromMenu(new BuildRequest { Kind = BuildKind.IosXcode });

        [MenuItem(MenuRoot + "出力先を開く", priority = 100)]
        public static void MenuRevealOutput()
        {
            var root = Path.GetFullPath("Builds");
            Directory.CreateDirectory(root);
            EditorUtility.RevealInFinder(root);
        }

        // ---- CLI (-executeMethod) -------------------------------------------

        public static void AndroidApk() => RunFromCommandLine(BuildKind.AndroidApk);

        public static void AndroidAab() => RunFromCommandLine(BuildKind.AndroidAab);

        public static void IosXcode() => RunFromCommandLine(BuildKind.IosXcode);

        // ---- 実行 -------------------------------------------------------------

        private static void RunFromMenu(BuildRequest request)
        {
            // 未保存のシーンはビルドに含まれない。取りこぼしを防ぐため先に確認する。
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            {
                return;
            }

            try
            {
                var report = ProjectBuilder.Run(request);
                if (report.summary.result == BuildResult.Succeeded)
                {
                    EditorUtility.RevealInFinder(report.summary.outputPath);
                }
            }
            catch (BuildRequestException e)
            {
                // 入力不備はダイアログで直接伝える。Console だけだと気付かれない。
                EditorUtility.DisplayDialog("ビルドできません", e.Message, "OK");
            }
        }

        private static void RunFromCommandLine(BuildKind kind)
        {
            var succeeded = false;
            try
            {
                var request = Parse(kind, Environment.GetCommandLineArgs());
                succeeded = ProjectBuilder.Run(request).summary.result == BuildResult.Succeeded;
            }
            catch (BuildRequestException e)
            {
                Debug.LogError($"[Build] {e.Message}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Build] 予期しない失敗: {e}");
            }

            if (Application.isBatchMode)
            {
                EditorApplication.Exit(succeeded ? 0 : 1);
            }
        }

        /// <summary>
        /// CLI 引数を <see cref="BuildRequest"/> にする。Unity 自身のオプションと
        /// 混ざるため、認識できない引数は黙って読み飛ばす。
        /// </summary>
        internal static BuildRequest Parse(BuildKind kind, string[] args)
        {
            var request = new BuildRequest { Kind = kind };

            for (var i = 0; i < args.Length; i++)
            {
                switch (args[i])
                {
                    case "--dev":
                    case "--development":
                        request.Development = true;
                        break;
                    case "--output":
                        request.OutputRoot = Next(args, i++, "--output");
                        break;
                    case "--bundle-version":
                        request.BundleVersion = Next(args, i++, "--bundle-version");
                        break;
                    case "--version-code":
                        var raw = Next(args, i++, "--version-code");
                        if (!int.TryParse(raw, out var code))
                        {
                            throw new BuildRequestException($"--version-code に整数以外が渡されました: {raw}");
                        }

                        request.AndroidVersionCode = code;
                        break;
                }
            }

            return request;
        }

        private static string Next(string[] args, int index, string option)
        {
            if (index + 1 >= args.Length || args[index + 1].StartsWith("-", StringComparison.Ordinal))
            {
                throw new BuildRequestException($"{option} に値が指定されていません。");
            }

            return args[index + 1];
        }
    }
}
