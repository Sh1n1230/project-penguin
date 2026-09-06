using UnityEngine;
using UnityEngine.UI;

public class CameraController : MonoBehaviour
{
    [SerializeField] private RawImage preview;
    [SerializeField] private RawImage capturedPreview;

    private WebCamTexture webcam;
    private Texture2D capturedImage;

    private void Start()
    {
        var devices = WebCamTexture.devices;

        if (devices.Length == 0)
        {
            Debug.LogError("カメラが見つかりません");
            return;
        }

        webcam = new WebCamTexture(devices[0].name, 640, 480, 30);
        preview.texture = webcam;
        webcam.Play();

        Debug.Log("カメラ起動: " + devices[0].name);
    }

    public void Capture()
    {
        Debug.Log("CAPTURE FIRED");

        if (webcam == null || !webcam.isPlaying)
        {
            Debug.LogError("カメラが起動していません");
            return;
        }

        if (capturedImage != null)
        {
            Destroy(capturedImage);
        }

        capturedImage = new Texture2D(
            webcam.width,
            webcam.height,
            TextureFormat.RGB24,
            false
        );

        capturedImage.SetPixels(webcam.GetPixels());
        capturedImage.Apply();

        capturedPreview.texture = capturedImage;

        Debug.Log($"撮影成功 {capturedImage.width}x{capturedImage.height}");
    }

    private void OnDestroy()
    {
        if (webcam != null && webcam.isPlaying)
            webcam.Stop();

        if (capturedImage != null)
            Destroy(capturedImage);
    }
}
