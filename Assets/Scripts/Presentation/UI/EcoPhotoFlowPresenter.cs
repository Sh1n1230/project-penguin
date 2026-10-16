using System;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using ProjectPenguin.Backend;
using ProjectPenguin.Domain.Island;
using ProjectPenguin.Systems;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// エコ写真の流れ: スキャン画面のシャッター → 解析中 (判定を待つ) → 結果 → 島へ。
    /// 写真の JPEG はメモリ上だけで判定に渡し、結果を受け取ったら捨てる (保存もログ出力もしない)。
    /// 判定は今はモック (<see cref="MockEcoPhotoJudge"/>)。Hack Day に backend の判定へ差し替える。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class EcoPhotoFlowPresenter : MonoBehaviour
    {
        private static readonly string[] Tips =
        {
            "小さな行動でも、毎日続けると大きな差になるよ",
            "電気・水・ガスを大事にすると、島の施設がよく動くよ",
            "写真は毎日 1 枚で十分。続けることがいちばん大事",
            "歩いた歩数もガスになるよ。ちょっと遠回りしてみよう",
            "ミッションを振り返ると、どの資源にもなるオールマイティがもらえるよ",
        };

        [SerializeField] private GameStateSystem _game;
        [SerializeField] private ScreenNavigator _navigator;
        [SerializeField] private ReceiptCameraPreview _camera;
        [SerializeField] private AnalyzingScreenPresenter _analyzing;
        [SerializeField] private IslandHudPresenter _hud;

        private IEcoPhotoJudge _judge;
        private CancellationTokenSource _cts;
        private Button _shutter;
        private VisualElement _result;
        private bool _busy;

        /// <summary>判定の差し替え口 (テストと Hack Day の backend 用)。</summary>
        public void SetJudge(IEcoPhotoJudge judge) => _judge = judge;

        private void Awake() => _judge ??= new MockEcoPhotoJudge();

        private void OnEnable()
        {
            if (_game == null || _navigator == null || _analyzing == null)
            {
                Debug.LogError($"{nameof(EcoPhotoFlowPresenter)}: 参照が未設定です。", this);
                enabled = false;
                return;
            }

            var root = GetComponent<UIDocument>().rootVisualElement;
            _shutter = root.Q(ScreenNavigator.ElementNameOf(AppScreen.Scan)).Q<Button>(UiNames.Scan.ShutterButton);
            _result = root.Q(ScreenNavigator.ElementNameOf(AppScreen.Result));
            _shutter.clicked += OnShutter;
            _navigator.ScreenShown += OnScreenShown;
        }

        private void OnDisable()
        {
            if (_shutter != null)
            {
                _shutter.clicked -= OnShutter;
            }

            if (_navigator != null)
            {
                _navigator.ScreenShown -= OnScreenShown;
            }

            CancelJudge();
        }

        private void OnScreenShown(AppScreen screen, AppScreen previous)
        {
            // 解析中に閉じたら判定もやめる。
            if (previous == AppScreen.Analyzing && screen != AppScreen.Analyzing && screen != AppScreen.Result)
            {
                CancelJudge();
                _analyzing.Cancel();
            }
        }

        private void OnShutter()
        {
            if (_busy)
            {
                return;
            }

            var jpeg = _camera != null ? _camera.CaptureJpeg() : null;
            if (jpeg == null)
            {
                if (!Application.isEditor && !Debug.isDebugBuild)
                {
                    _hud?.ShowToast("カメラが使えないみたい。メニューの「カメラの許可」を確かめてね");
                    return;
                }

                // Editor や開発ビルドでカメラが無いときは、見本の写真で流れを確かめられるようにする。
                jpeg = SampleJpeg();
            }

            _ = RunAsync(jpeg);
        }

        private async Task RunAsync(byte[] jpeg)
        {
            _busy = true;
            CancelJudge();
            _cts = new CancellationTokenSource();
            var token = _cts.Token;
            _navigator.Show(AppScreen.Analyzing);
            _analyzing.Begin();
            try
            {
                var verdict = await _judge.JudgeAsync(jpeg, token);
                jpeg = null;
                if (token.IsCancellationRequested)
                {
                    return;
                }

                var result = _game.RecordEcoPhoto(verdict);
                _analyzing.Finish(() =>
                {
                    Fill(result);
                    _navigator.Show(AppScreen.Result);
                });
            }
            catch (OperationCanceledException)
            {
                // 画面を閉じた。何もしない。
            }
            catch (Exception e)
            {
                // 写真の中身はメッセージに含めない (.claude/rules/privacy.md)。
                Debug.LogWarning($"{nameof(EcoPhotoFlowPresenter)}: 判定に失敗しました ({e.GetType().Name})");
                _analyzing.Cancel();
                _navigator.Show(AppScreen.Scan);
                _hud?.ShowToast("うまく見分けられなかったよ。もう一度撮ってみてね");
            }
            finally
            {
                _busy = false;
            }
        }

        private void CancelJudge()
        {
            if (_cts == null)
            {
                return;
            }

            _cts.Cancel();
            _cts.Dispose();
            _cts = null;
        }

        private void Fill(EcoPhotoResult result)
        {
            var v = result.Verdict;
            var now = _game.Now.ToOffset(TimeSpan.FromHours(9));
            _result.Q<Label>(UiNames.Result.ScannedAt).text = now.ToString("yyyy/MM/dd HH:mm", CultureInfo.InvariantCulture);
            _result.Q<Label>(UiNames.Result.PhotoLabel).text = string.IsNullOrEmpty(v.Label) ? EcoCategories.NameOf(v.Category) : v.Label;
            _result.Q<Label>(UiNames.Result.CategoryName).text = EcoCategories.NameOf(v.Category);
            _result.Q<Label>(UiNames.Result.CommentText).text = string.IsNullOrEmpty(v.Comment) ? "撮ってくれてありがとう！" : v.Comment;

            var main = EcoCategories.MainResource(v.Category);
            var icon = _result.Q(UiNames.Result.CategoryIcon);
            foreach (var c in new[] { UiClasses.Icon.Leaf, UiClasses.Icon.Electricity, UiClasses.Icon.Water, UiClasses.Icon.Gas, UiClasses.Icon.AllMighty })
            {
                icon.RemoveFromClassList(c);
            }

            foreach (var c in new[] { UiClasses.Tint.Eco, UiClasses.Tint.Electricity, UiClasses.Tint.Water, UiClasses.Tint.Gas, UiClasses.Tint.AllMighty })
            {
                icon.RemoveFromClassList(c);
            }

            icon.AddToClassList(v.IsEco ? IslandUi.IconClass(main) : UiClasses.Icon.Leaf);
            icon.AddToClassList(v.IsEco ? IslandUi.TintClass(main) : UiClasses.Tint.Eco);

            var list = _result.Q(UiNames.Result.GrantList);
            list.Clear();
            var title = _result.Q<Label>(UiNames.Result.GrantTitle);
            if (result.Granted == null)
            {
                title.text = "今日の資源はもう受け取ったよ";
                list.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Check, UiClasses.Tint.Eco, true), "また明日撮ってね",
                    "資源がもらえるのは 1 日 1 枚まで。記録は何枚撮っても同じだよ"));
            }
            else
            {
                title.text = "島に届いた資源";
                foreach (var kv in result.Granted.NonZero())
                {
                    var row = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(kv.Key), IslandUi.TintClass(kv.Key)),
                        IslandCatalog.NameOf(kv.Key), Purpose(kv.Key), IslandUi.Text("+" + IslandUi.Number(kv.Value), UiClasses.Text.Title, UiClasses.Text.Heavy));
                    list.Add(row);
                }

                if (list.childCount > 0)
                {
                    list[list.childCount - 1].AddToClassList(UiClasses.Row.Last);
                }
            }

            var recordCard = _result.Q(UiNames.Result.RecordCard);
            IslandUi.SetVisible(recordCard, result.NewRecordDay);
            if (result.NewRecordDay)
            {
                var gain = result.After.Ice - result.Before.Ice;
                _result.Q<Label>(UiNames.Result.IceGain).text = (gain >= 0 ? "+" : "") + gain.ToString("0.#", CultureInfo.InvariantCulture);
            }

            _result.Q<Label>(UiNames.Result.TipText).text = Tips[Mathf.Abs(_game.Today) % Tips.Length];
        }

        private static string Purpose(Resource r) => r switch
        {
            Resource.Electricity => "施設を建てるのに使う",
            Resource.Water => "海を凍らせて島を広げるのに使う",
            Resource.Gas => "施設を動かすのに使う",
            Resource.AllMighty => "電気・水・ガスのどれにもなる",
            _ => "",
        };

        /// <summary>カメラが無い環境で流れを確かめるための見本の写真 (毎回少し違う色)。</summary>
        private static byte[] SampleJpeg()
        {
            var texture = new Texture2D(64, 64, TextureFormat.RGB24, false);
            try
            {
                var color = Color.HSVToRGB(UnityEngine.Random.value, 0.5f, 0.9f);
                var pixels = new Color[64 * 64];
                for (var i = 0; i < pixels.Length; i++)
                {
                    pixels[i] = color * (0.8f + 0.2f * ((i % 64) / 64f));
                }

                texture.SetPixels(pixels);
                texture.Apply(false);
                return texture.EncodeToJPG(70);
            }
            finally
            {
                Destroy(texture);
            }
        }
    }
}
