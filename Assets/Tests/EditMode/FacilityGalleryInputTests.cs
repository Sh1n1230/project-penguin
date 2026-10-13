using NUnit.Framework;
using ProjectPenguin.Presentation.World;
using UnityEngine;
using UnityEngine.InputSystem;

namespace ProjectPenguin.Tests.EditMode
{
    public sealed class FacilityGalleryInputTests
    {
        [Test]
        public void EnablingAndDisablingGalleryPreservesSettingsAndMouseState()
        {
            var settings = InputSystem.settings;
            var original = JsonUtility.ToJson(settings);
            var mouse = Mouse.current;
            var enabled = mouse?.enabled;
            var root = new GameObject("ReviewGallery");
            root.SetActive(false);
            try
            {
                root.AddComponent<FacilityDesignGallery>();
                root.SetActive(true);
                root.SetActive(false);
                Assert.That(InputSystem.settings, Is.SameAs(settings));
                Assert.That(JsonUtility.ToJson(settings), Is.EqualTo(original));
                Assert.That(mouse?.enabled, Is.EqualTo(enabled));
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
