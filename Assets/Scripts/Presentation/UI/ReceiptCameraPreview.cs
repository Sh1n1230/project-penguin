using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UIElements;
#if UNITY_ANDROID && !UNITY_EDITOR
using UnityEngine.Android;
#endif

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// スキャン画面にカメラ映像を映す。映像はその場で表示するだけで、フレームの保存もログ出力もしない
    /// (レシートの扱いは .claude/rules/privacy.md に従う)。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class ReceiptCameraPreview : MonoBehaviour
    {
        private const string HiddenClass = "pp-hidden";
        private const int RequestedWidth = 1920;
        private const int RequestedHeight = 1080;

        // 起動直後の WebCamTexture は、実際の解像度が決まるまで 16x16 を返す。
        private const int PlaceholderSize = 16;

        private VisualElement _viewport;
        private Image _preview;
        private Label _status;

        private WebCamTexture _webcam;
        private Coroutine _startRoutine;
        private bool _wantsPreview;

        private int _appliedAngle;
        private bool _appliedMirrored;
        private Vector2 _appliedViewportSize;

        private void OnEnable()
        {
            var root = GetComponent<UIDocument>().rootVisualElement;
            _viewport = root.Q("previewViewport");
            _preview = root.Q<Image>("cameraPreview");
            _status = root.Q<Label>("cameraStatus");
            _preview.scaleMode = ScaleMode.ScaleAndCrop;
        }

        private void OnDisable()
        {
            _wantsPreview = false;
            ReleaseCamera();
        }

        private void Update()
        {
            if (_webcam != null && _webcam.width > PlaceholderSize)
            {
                ApplyOrientationIfChanged();
            }
        }

        // アプリが裏に回っている間はカメラを掴んだままにしない。戻ってきたときはスキャン画面にいる場合だけ再開する。
        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                ReleaseCamera();
            }
            else if (_wantsPreview)
            {
                StartPreview();
            }
        }

        public void StartPreview()
        {
            _wantsPreview = true;
            if (_webcam == null && _startRoutine == null)
            {
                _startRoutine = StartCoroutine(StartRoutine());
            }
        }

        public void StopPreview()
        {
            _wantsPreview = false;
            ReleaseCamera();
        }

        private IEnumerator StartRoutine()
        {
            SetStatus(null);

            var authorized = false;
            yield return RequestPermission(result => authorized = result);
            if (!authorized)
            {
                SetStatus("カメラの使用が許可されていません。\n端末の設定から許可してください。");
                _startRoutine = null;
                yield break;
            }

            var devices = WebCamTexture.devices;
            if (devices.Length == 0)
            {
                SetStatus("カメラが見つかりません");
                _startRoutine = null;
                yield break;
            }

            _webcam = new WebCamTexture(SelectBackCamera(devices).name, RequestedWidth, RequestedHeight);
            _webcam.Play();
            _preview.image = _webcam;
            _appliedViewportSize = Vector2.zero;
            _startRoutine = null;
        }

        private static IEnumerator RequestPermission(Action<bool> onResult)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (Permission.HasUserAuthorizedPermission(Permission.Camera))
            {
                onResult(true);
                yield break;
            }

            bool? granted = null;
            var callbacks = new PermissionCallbacks();
            callbacks.PermissionGranted += _ => granted = true;
            callbacks.PermissionDenied += _ => granted = false;
            callbacks.PermissionRequestDismissed += _ => granted = false;
            Permission.RequestUserPermission(Permission.Camera, callbacks);

            while (granted == null)
            {
                yield return null;
            }

            onResult(granted.Value);
#else
            if (!Application.HasUserAuthorization(UserAuthorization.WebCam))
            {
                yield return Application.RequestUserAuthorization(UserAuthorization.WebCam);
            }

            onResult(Application.HasUserAuthorization(UserAuthorization.WebCam));
#endif
        }

        // レシートを撮るので背面カメラを優先する。PC など背面カメラが無い環境では先頭のカメラを使う。
        private static WebCamDevice SelectBackCamera(WebCamDevice[] devices)
        {
            foreach (var device in devices)
            {
                if (!device.isFrontFacing)
                {
                    return device;
                }
            }

            return devices[0];
        }

        // モバイルのカメラ映像は横向きのまま届き、正しい向きは videoRotationAngle で渡される。
        // 90°/270° のときは縦横を入れ替えた箱に描いてから回すと、ちょうど画面を覆う。
        private void ApplyOrientationIfChanged()
        {
            var viewportSize = _viewport.layout.size;
            if (float.IsNaN(viewportSize.x) || float.IsNaN(viewportSize.y))
            {
                return;
            }

            var angle = _webcam.videoRotationAngle;
            var mirrored = _webcam.videoVerticallyMirrored;
            if (angle == _appliedAngle && mirrored == _appliedMirrored && viewportSize == _appliedViewportSize)
            {
                return;
            }

            _appliedAngle = angle;
            _appliedMirrored = mirrored;
            _appliedViewportSize = viewportSize;

            var quarterTurn = angle % 180 != 0;
            var width = quarterTurn ? viewportSize.y : viewportSize.x;
            var height = quarterTurn ? viewportSize.x : viewportSize.y;

            // 端末ごとに変わる実測値なので USS では表せず、インラインスタイルで入れる。
            var style = _preview.style;
            style.left = (viewportSize.x - width) / 2f;
            style.top = (viewportSize.y - height) / 2f;
            style.right = StyleKeyword.Auto;
            style.bottom = StyleKeyword.Auto;
            style.width = width;
            style.height = height;
            style.rotate = new Rotate(angle);
            style.scale = new Scale(new Vector3(1f, mirrored ? -1f : 1f, 1f));
        }

        private void ReleaseCamera()
        {
            if (_startRoutine != null)
            {
                StopCoroutine(_startRoutine);
                _startRoutine = null;
            }

            if (_preview != null)
            {
                _preview.image = null;
            }

            if (_webcam != null)
            {
                _webcam.Stop();
                Destroy(_webcam);
                _webcam = null;
            }
        }

        private void SetStatus(string message)
        {
            if (_status == null)
            {
                return;
            }

            _status.text = message ?? string.Empty;
            _status.EnableInClassList(HiddenClass, message == null);
        }
    }
}
