using System;
using System.IO;
using UnityEngine;

namespace ProjectPenguin.Data
{
    /// <summary>プレイヤーの状態の置き場。今は JSON のファイル。Hack Day に SQLite の実装へ差し替える。</summary>
    public interface IGameStore
    {
        /// <summary>保存が無い・読めないときは null。</summary>
        GameSave Load();

        void Save(GameSave save);

        /// <summary>設定の「データを消す」。</summary>
        void Delete();
    }

    /// <summary>
    /// <c>Application.persistentDataPath</c> に JSON で保存する。書き込みは一時ファイルを経由し、
    /// 途中でアプリが落ちても前の保存が壊れないようにする。
    /// </summary>
    public sealed class JsonGameStore : IGameStore
    {
        private const string FileName = "penguin-save.json";

        private readonly string _path;

        public JsonGameStore(string directory = null)
        {
            _path = Path.Combine(directory ?? Application.persistentDataPath, FileName);
        }

        public string FilePath => _path;

        public GameSave Load()
        {
            if (!File.Exists(_path))
            {
                return null;
            }

            try
            {
                var save = JsonUtility.FromJson<GameSave>(File.ReadAllText(_path));
                return save != null && save.createdUnixMs > 0 ? save : null;
            }
            catch (Exception e)
            {
                // 読めない保存は消さずに退避し、最初から始める (原因を後で調べられるように)。
                Debug.LogWarning($"{nameof(JsonGameStore)}: 保存を読めませんでした ({e.GetType().Name})。最初から始めます。");
                TryBackup();
                return null;
            }
        }

        public void Save(GameSave save)
        {
            if (save == null)
            {
                return;
            }

            var tmp = _path + ".tmp";
            File.WriteAllText(tmp, JsonUtility.ToJson(save));
            if (File.Exists(_path))
            {
                File.Replace(tmp, _path, null);
            }
            else
            {
                File.Move(tmp, _path);
            }
        }

        public void Delete()
        {
            if (File.Exists(_path))
            {
                File.Delete(_path);
            }
        }

        private void TryBackup()
        {
            try
            {
                File.Copy(_path, _path + ".broken", true);
            }
            catch (IOException)
            {
                // 退避できなくても起動は続ける。
            }
        }
    }

    /// <summary>テストと、保存したくない場面 (確認用のシーン) のための置き場。</summary>
    public sealed class MemoryGameStore : IGameStore
    {
        private string _json;

        public GameSave Load() => string.IsNullOrEmpty(_json) ? null : JsonUtility.FromJson<GameSave>(_json);

        public void Save(GameSave save) => _json = save == null ? null : JsonUtility.ToJson(save);

        public void Delete() => _json = null;
    }
}
