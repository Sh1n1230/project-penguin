using System;
using NUnit.Framework;
using ProjectPenguin.Presentation.UI;
using UnityEditor;
using UnityEngine.UIElements;

namespace ProjectPenguin.Tests.EditMode
{
    /// <summary>
    /// ScreenNavigator が名前で探す要素が App.uxml にそろっているかを確かめる。
    /// UXML の name を変えただけでは画面遷移が実行時まで壊れたことに気づけないため。
    /// </summary>
    public sealed class AppLayoutTests
    {
        private const string AppUxmlPath = "Assets/UI/App/App.uxml";

        private VisualElement _root;

        [SetUp]
        public void SetUp()
        {
            var tree = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(AppUxmlPath);
            Assert.That(tree, Is.Not.Null, $"{AppUxmlPath} が読み込めません");
            _root = tree.Instantiate();
        }

        [Test]
        public void EveryScreenExistsInApp()
        {
            foreach (AppScreen screen in Enum.GetValues(typeof(AppScreen)))
            {
                var name = ScreenNavigator.ElementNameOf(screen);
                Assert.That(_root.Q(name), Is.Not.Null, $"{screen} の要素 '{name}' がありません");
            }
        }

        [Test]
        public void EveryTabScreenHasTabButton()
        {
            var tabBar = _root.Q(ScreenNavigator.TabBarName);
            Assert.That(tabBar, Is.Not.Null);

            foreach (AppScreen screen in Enum.GetValues(typeof(AppScreen)))
            {
                var tabName = ScreenNavigator.TabButtonOf(screen);
                if (tabName != null)
                {
                    Assert.That(tabBar.Q<Button>(tabName), Is.Not.Null, $"{screen} のタブ '{tabName}' がありません");
                }
            }
        }

        [Test]
        public void EveryRouteButtonExistsInItsScope()
        {
            foreach (var route in ScreenNavigator.Routes)
            {
                var scope = _root.Q(route.Scope);
                Assert.That(scope, Is.Not.Null, $"'{route.Scope}' がありません");
                Assert.That(scope.Q<Button>(route.Button), Is.Not.Null, $"'{route.Scope}' に Button '{route.Button}' がありません");
            }
        }
    }
}
