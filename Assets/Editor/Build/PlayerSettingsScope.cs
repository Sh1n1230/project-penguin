using System;
using UnityEditor;

namespace ProjectPenguin.Editor.Build
{
    /// <summary>
    /// ビルドのために書き換えた PlayerSettings / EditorUserBuildSettings を元へ戻す。
    ///
    /// これらの API はプロジェクト設定そのものを書き換えるため、戻さないと
    /// ProjectSettings.asset に差分が残り、署名パスワードまでコミットされうる。
    /// ビルドが失敗した場合も必ず戻すこと。
    /// </summary>
    internal sealed class PlayerSettingsScope : IDisposable
    {
        private readonly string _bundleVersion;
        private readonly int _androidVersionCode;
        private readonly bool _useCustomKeystore;
        private readonly string _keystoreName;
        private readonly string _keystorePass;
        private readonly string _keyaliasName;
        private readonly string _keyaliasPass;
        private readonly string _appleTeamId;
        private readonly bool _buildAppBundle;

        public PlayerSettingsScope()
        {
            _bundleVersion = PlayerSettings.bundleVersion;
            _androidVersionCode = PlayerSettings.Android.bundleVersionCode;
            _useCustomKeystore = PlayerSettings.Android.useCustomKeystore;
            _keystoreName = PlayerSettings.Android.keystoreName;
            _keystorePass = PlayerSettings.Android.keystorePass;
            _keyaliasName = PlayerSettings.Android.keyaliasName;
            _keyaliasPass = PlayerSettings.Android.keyaliasPass;
            _appleTeamId = PlayerSettings.iOS.appleDeveloperTeamID;
            _buildAppBundle = EditorUserBuildSettings.buildAppBundle;
        }

        public void Dispose()
        {
            PlayerSettings.bundleVersion = _bundleVersion;
            PlayerSettings.Android.bundleVersionCode = _androidVersionCode;
            PlayerSettings.Android.useCustomKeystore = _useCustomKeystore;
            PlayerSettings.Android.keystoreName = _keystoreName;
            PlayerSettings.Android.keystorePass = _keystorePass;
            PlayerSettings.Android.keyaliasName = _keyaliasName;
            PlayerSettings.Android.keyaliasPass = _keyaliasPass;
            PlayerSettings.iOS.appleDeveloperTeamID = _appleTeamId;
            EditorUserBuildSettings.buildAppBundle = _buildAppBundle;
        }
    }

    /// <summary>ビルドを始める前の入力不備。Unity のビルド失敗とは区別する。</summary>
    public sealed class BuildRequestException : Exception
    {
        public BuildRequestException(string message) : base(message)
        {
        }
    }
}
