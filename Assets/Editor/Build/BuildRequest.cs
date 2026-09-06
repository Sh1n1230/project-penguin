using UnityEditor;
using UnityEditor.Build;

namespace ProjectPenguin.Editor.Build
{
    /// <summary>ビルド成果物の種類。</summary>
    public enum BuildKind
    {
        /// <summary>実機で直接動かして確認するための APK。</summary>
        AndroidApk,

        /// <summary>Google Play に上げるための AAB。署名必須。</summary>
        AndroidAab,

        /// <summary>Xcode プロジェクト。実機ビルドは macOS 上の Xcode で行う。</summary>
        IosXcode,
    }

    /// <summary>
    /// ビルド 1 回分の入力。MenuItem からも CLI 引数からもここに集約してから
    /// <see cref="ProjectBuilder"/> に渡す。分岐をこの型の中だけに閉じる。
    /// </summary>
    public sealed class BuildRequest
    {
        public BuildKind Kind { get; set; }

        /// <summary>Development Build (プロファイラ接続・デバッグシンボルあり)。</summary>
        public bool Development { get; set; }

        /// <summary>成果物を置くルート。リポジトリ直下からの相対パス。</summary>
        public string OutputRoot { get; set; } = "Builds";

        /// <summary>null なら ProjectSettings の bundleVersion をそのまま使う。</summary>
        public string BundleVersion { get; set; }

        /// <summary>null なら ProjectSettings の versionCode をそのまま使う。</summary>
        public int? AndroidVersionCode { get; set; }

        public bool IsAndroid => Kind != BuildKind.IosXcode;

        public BuildTarget Target => IsAndroid ? BuildTarget.Android : BuildTarget.iOS;

        public BuildTargetGroup Group => IsAndroid ? BuildTargetGroup.Android : BuildTargetGroup.iOS;

        public NamedBuildTarget NamedTarget => NamedBuildTarget.FromBuildTargetGroup(Group);

        /// <summary>ログと成果物名に使う短い識別子。</summary>
        public string Label => Kind switch
        {
            BuildKind.AndroidApk => "Android APK",
            BuildKind.AndroidAab => "Android AAB",
            _ => "iOS Xcode",
        };
    }
}
