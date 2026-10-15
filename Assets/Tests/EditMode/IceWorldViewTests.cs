using NUnit.Framework;
using ProjectPenguin.Presentation.World;
using UnityEngine;

namespace ProjectPenguin.Tests.EditMode
{
    public sealed class IceWorldViewTests
    {
        [Test]
        public void ScaleAroundMovesOnlyHorizontally()
        {
            var center = new Vector3(1f, 5f, -2f);
            var point = new Vector3(3f, 0.5f, 2f);

            var moved = IceWorldView.ScaleAround(center, point, 0.5f);

            Assert.That(moved.x, Is.EqualTo(2f).Within(1e-5));
            Assert.That(moved.y, Is.EqualTo(0.5f).Within(1e-5));
            Assert.That(moved.z, Is.EqualTo(0f).Within(1e-5));
        }

        [Test]
        public void ScaleOfOneKeepsThePoint()
        {
            var point = new Vector3(3f, 0.5f, 2f);
            Assert.That(IceWorldView.ScaleAround(Vector3.zero, point, 1f), Is.EqualTo(point));
        }
    }
}
