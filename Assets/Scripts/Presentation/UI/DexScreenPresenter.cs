using System.Collections.Generic;
using System.Linq;
using ProjectPenguin.Domain.Game;
using ProjectPenguin.Domain.Island;
using ProjectPenguin.Systems;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// ペンギン図鑑。来たペンギンは事実の一行と島へのボーナスを、まだのペンギンは「？」で出す。
    /// 来る順と条件は氷の状態機械 (<see cref="GameSession"/>) が決める (docs/game-logic.md §5)。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class DexScreenPresenter : MonoBehaviour
    {
        [SerializeField] private GameStateSystem _game;
        [SerializeField] private ScreenNavigator _navigator;

        private VisualElement _screen;

        private void OnEnable()
        {
            _screen = GetComponent<UIDocument>().rootVisualElement.Q(ScreenNavigator.ElementNameOf(AppScreen.Dex));
            if (_navigator != null)
            {
                _navigator.ScreenShown += OnScreenShown;
            }
        }

        private void OnDisable()
        {
            if (_navigator != null)
            {
                _navigator.ScreenShown -= OnScreenShown;
            }
        }

        private void OnScreenShown(AppScreen screen, AppScreen previous)
        {
            if (screen == AppScreen.Dex)
            {
                Refresh();
            }
        }

        private void Refresh()
        {
            if (_game == null || _screen == null)
            {
                return;
            }

            var arrived = new HashSet<string>(_game.Session.Arrivals.Select(a => a.Species));
            _screen.Q<Label>(UiNames.Dex.DexCount).text = $"{arrived.Count} / {PenguinDex.Entries.Count} 種";

            // 来た順に並べ、まだのペンギンは後ろにまとめる。
            var order = _game.Session.Arrivals.Select(a => a.Species)
                .Concat(PenguinCatalog.MilestoneOrder).Concat(PenguinCatalog.WeeklyOrder).Distinct().ToList();
            var grid = _screen.Q(UiNames.Dex.DexGrid);
            grid.Clear();
            foreach (var species in order)
            {
                var entry = PenguinDex.Find(species);
                if (entry != null)
                {
                    grid.Add(Card(entry, arrived.Contains(species)));
                }
            }
        }

        private static VisualElement Card(PenguinEntry entry, bool arrived)
        {
            var card = new VisualElement();
            card.AddToClassList(UiClasses.DexCard.Root);
            card.EnableInClassList(UiClasses.DexCard.Locked, !arrived);
            var image = IslandUi.Icon(UiClasses.Icon.Penguin, arrived ? UiClasses.Tint.Original : null);
            image.AddToClassList(UiClasses.DexCard.Image);
            card.Add(image);
            card.Add(IslandUi.Text(arrived ? entry.Name : "？？？", UiClasses.DexCard.Name));
            card.Add(IslandUi.Text(arrived ? entry.Fact : "記録を続けると会えるかも", UiClasses.DexCard.Fact));
            if (arrived)
            {
                var bonus = IslandUi.Text(entry.BonusText, UiClasses.Badge.Root, UiClasses.Badge.Eco);
                bonus.AddToClassList(UiClasses.DexCard.Bonus);
                card.Add(bonus);
            }

            return card;
        }
    }
}
