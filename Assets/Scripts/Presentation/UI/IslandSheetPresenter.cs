using System;
using System.Collections.Generic;
using System.Linq;
using ProjectPenguin.Domain.Island;
using ProjectPenguin.Presentation.World;
using ProjectPenguin.Systems;
using UnityEngine;
using UnityEngine.UIElements;

namespace ProjectPenguin.Presentation.UI
{
    /// <summary>
    /// ホームの道具ボタン (建てる・港・生産量) と、下から出るシート、置き場所を選ぶ間の帯を受け持つ。
    /// 島を広げるのは建てるシートの下のボタンから、図鑑はメニューから開く。
    /// シートの中身は開くたびに組み立て、開いている間は数字だけを更新する (押している途中のボタンを作り直さないため)。
    /// </summary>
    [RequireComponent(typeof(UIDocument))]
    public sealed class IslandSheetPresenter : MonoBehaviour
    {

        [SerializeField] private GameStateSystem _game;
        [SerializeField] private IslandInteraction _interaction;
        [SerializeField] private ScreenNavigator _navigator;
        [SerializeField] private IslandHudPresenter _hud;

        private VisualElement _home;
        private VisualElement _sheet;
        private Label _sheetTitle;
        private ScrollView _sheetBody;
        private VisualElement _sheetFooter;
        private VisualElement _banner;
        private Label _bannerText;
        private Button _bannerConfirm;
        private Button _bannerCancel;
        private VisualElement _bannerIcon;
        private readonly List<(Button Button, Action Handler)> _bindings = new List<(Button, Action)>();

        /// <summary>シートが開いている間、島が変わるたびに呼ぶ更新。</summary>
        private Action _refreshSheet;
        private bool _sheetOpen;
        private int _facilityId = -1;

        public bool IsSheetOpen => _sheetOpen;

        private void OnEnable()
        {
            if (_game == null || _interaction == null || _navigator == null)
            {
                Debug.LogError($"{nameof(IslandSheetPresenter)}: 参照が未設定です。", this);
                enabled = false;
                return;
            }

            _home = GetComponent<UIDocument>().rootVisualElement.Q(ScreenNavigator.ElementNameOf(AppScreen.Home));
            _sheet = _home.Q(UiNames.Home.Sheet);
            _sheetTitle = _home.Q<Label>(UiNames.Home.SheetTitle);
            _sheetBody = _home.Q<ScrollView>(UiNames.Home.SheetBody);
            _sheetFooter = _home.Q(UiNames.Home.SheetFooter);
            _banner = _home.Q(UiNames.Home.PlacementBanner);
            _bannerText = _home.Q<Label>(UiNames.Home.BannerText);
            _bannerConfirm = _home.Q<Button>(UiNames.Home.BannerConfirm);
            _bannerCancel = _home.Q<Button>(UiNames.Home.BannerCancel);
            _bannerIcon = _home.Q(UiNames.Home.BannerIcon);

            BindButton(UiNames.Home.ToolBuild, OpenBuild);
            BindButton(UiNames.Home.ToolHarbor, OpenHarbor);
            BindButton(UiNames.Home.ToolProduction, OpenProduction);
            BindButton(UiNames.Home.SheetClose, CloseSheet);
            BindButton(UiNames.Home.BannerConfirm, ConfirmPlacement);
            BindButton(UiNames.Home.BannerCancel, () => _interaction.Cancel());
            _home.Q(UiNames.Home.SheetScrim).RegisterCallback<PointerDownEvent>(OnScrim);
            _home.Q(UiNames.Home.IslandBar)?.RegisterCallback<ClickEvent>(OnResourceBar);

            _interaction.Changed += RefreshBanner;
            _interaction.FacilitySelected += OpenFacility;
            _interaction.HarborTapped += OpenHarbor;
            _interaction.ExpandAttempted += OnExpandAttempted;
            _game.IslandChanged += OnIslandChanged;
            RefreshBanner();
        }

        private void OnDisable()
        {
            foreach (var (button, handler) in _bindings)
            {
                button.clicked -= handler;
            }

            _bindings.Clear();
            _home?.Q(UiNames.Home.SheetScrim)?.UnregisterCallback<PointerDownEvent>(OnScrim);
            _home?.Q(UiNames.Home.IslandBar)?.UnregisterCallback<ClickEvent>(OnResourceBar);
            if (_interaction != null)
            {
                _interaction.Changed -= RefreshBanner;
                _interaction.FacilitySelected -= OpenFacility;
                _interaction.HarborTapped -= OpenHarbor;
                _interaction.ExpandAttempted -= OnExpandAttempted;
            }

            if (_game != null)
            {
                _game.IslandChanged -= OnIslandChanged;
            }
        }

        private void BindButton(string name, Action handler)
        {
            var b = _home.Q<Button>(name);
            if (b == null)
            {
                return;
            }

            b.clicked += handler;
            _bindings.Add((b, handler));
        }

        private void OnScrim(PointerDownEvent e) => CloseSheet();

        private void OnResourceBar(ClickEvent e) => OpenResources();

        private void OnIslandChanged()
        {
            if (_sheetOpen)
            {
                _refreshSheet?.Invoke();
            }

            if (_interaction.Mode == IslandMode.Expand)
            {
                RefreshBanner();
            }
        }

        // ------------------------------------------------------------------
        // シートの開け閉め
        // ------------------------------------------------------------------

        private void OpenSheet(string title, Action<VisualElement, VisualElement> build, Action refresh = null)
        {
            if (_interaction.Mode != IslandMode.Browse)
            {
                _interaction.Cancel();
            }

            _sheetTitle.text = title;
            _sheetBody.Clear();
            _sheetFooter.Clear();
            build(_sheetBody.contentContainer, _sheetFooter);
            IslandUi.SetVisible(_sheetFooter, _sheetFooter.childCount > 0);
            _refreshSheet = refresh;
            _refreshSheet?.Invoke();
            _sheetBody.scrollOffset = Vector2.zero;
            if (!_sheetOpen)
            {
                _sheetOpen = true;
                IslandUi.SetVisible(_sheet, true);
                _sheet.schedule.Execute(() => _sheet.RemoveFromClassList(UiClasses.Sheet.Closed)).StartingIn(16);
            }
        }

        public void CloseSheet()
        {
            if (!_sheetOpen)
            {
                return;
            }

            _sheetOpen = false;
            _refreshSheet = null;
            _facilityId = -1;
            _sheet.AddToClassList(UiClasses.Sheet.Closed);
            _sheet.schedule.Execute(() =>
            {
                if (!_sheetOpen)
                {
                    IslandUi.SetVisible(_sheet, false);
                }
            }).StartingIn(240);
            _interaction.ClearSelection();
        }

        // ------------------------------------------------------------------
        // 建てる
        // ------------------------------------------------------------------

        public void OpenBuild()
        {
            OpenSheet("建てる", (body, footer) =>
            {
                var island = _game.Island;
                var defs = IslandCatalog.Facilities.OrderBy(f => f.UnlockLevel).ToList();
                for (var i = 0; i < defs.Count; i++)
                {
                    var def = defs[i];
                    var unlocked = island.IsUnlocked(def.Kind);
                    var cost = IslandUi.Cost();
                    var trailing = unlocked
                        ? IslandUi.Text(def.MaxCount == int.MaxValue ? $"{island.CountOf(def.Kind)} 棟" : $"{island.CountOf(def.Kind)} / {def.MaxCount}",
                            UiClasses.Text.Caption, UiClasses.Text.Sub)
                        : IslandUi.Text($"Lv {def.UnlockLevel}", UiClasses.Badge.Root);
                    var row = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(def), IslandUi.TintClass(def)), def.Name,
                        Describe(def), trailing);
                    row.Q(className: UiClasses.Row.Body).Add(cost);
                    row.EnableInClassList(UiClasses.Row.Locked, !unlocked);
                    row.EnableInClassList(UiClasses.Row.Last, i == defs.Count - 1);
                    var kind = def.Kind;
                    row.RegisterCallback<ClickEvent>(_ => ChooseBuild(kind));
                    body.Add(row);

                    // 足りないコストは赤くする (お金はシートを開いている間も増減するので、開くときの値で十分)。
                    IslandUi.AddCost(cost, UiClasses.Icon.Electricity, UiClasses.Tint.Electricity, def.ElectricityCost,
                        island.Get(Resource.Electricity) + island.Get(Resource.AllMighty) < def.ElectricityCost);
                    IslandUi.AddCost(cost, UiClasses.Icon.Fish, UiClasses.Tint.Fish, def.FishCost, island.Fish < def.FishCost);
                    if (def.Workers > 0)
                    {
                        IslandUi.AddCost(cost, UiClasses.Icon.Penguin, UiClasses.Tint.Original, def.Workers, island.FreeWorkers < def.Workers);
                    }
                }

                footer.Add(IslandUi.Pill("島を広げる", StartExpand, UiClasses.Pill.Primary));
            });
        }

        private static string Describe(FacilityDef def)
        {
            var parts = new List<string> { def.Description };
            if (def.Recipes.Count > 0 && def.Role == FacilityRole.Producer)
            {
                var r = def.Recipes[0];
                var output = IslandCatalog.ProducesPearl(def.Kind) ? "真珠" : IslandCatalog.NameOf(r.Output.Item);
                var inputs = r.Inputs.Count == 0 ? "" : string.Join("＋", r.Inputs.Select(x => $"{IslandCatalog.NameOf(x.Item)}{x.Count}")) + " → ";
                parts.Add($"{inputs}{output}（{r.Seconds:0} 秒）");
            }

            return string.Join("\n", parts);
        }

        private void ChooseBuild(FacilityKind kind)
        {
            var can = _game.Island.CanBuild(kind);
            if (can != IslandActionResult.Ok)
            {
                _hud?.ShowToast(IslandUi.Message(can));
                return;
            }

            CloseSheet();
            _interaction.BeginPlace(kind);
        }

        private void ConfirmPlacement()
        {
            var name = IslandCatalog.Get(_interaction.PlacingKind).Name;
            var moving = _interaction.Mode == IslandMode.Move;
            var r = _interaction.Confirm();
            _hud?.ShowToast(r == IslandActionResult.Ok ? (moving ? $"{name}を移したよ" : $"{name}を建てたよ！") : IslandUi.Message(r));
        }

        // ------------------------------------------------------------------
        // 広げる
        // ------------------------------------------------------------------

        private void StartExpand()
        {
            CloseSheet();
            var island = _game.Island;
            var check = island.Board.SunkCount(island.Ice) > 0 || island.ExpandRoom == 0 ? island.CanExpand(new Cell(-1, -1)) : IslandActionResult.Ok;
            if (check == IslandActionResult.NotEnoughIce || check == IslandActionResult.LimitReached)
            {
                _hud?.ShowToast(check == IslandActionResult.LimitReached ? "今のレベルではこれ以上広げられないよ" : IslandUi.Message(check));
                return;
            }

            _interaction.BeginExpand();
        }

        private void OnExpandAttempted(Cell cell, IslandActionResult r)
        {
            if (r != IslandActionResult.Ok)
            {
                _hud?.ShowToast(IslandUi.Message(r));
                return;
            }

            if (_game.Island.ExpandRoom == 0)
            {
                _hud?.ShowToast("今はここまで広げられるよ");
                _interaction.Cancel();
            }
        }

        private void RefreshBanner()
        {
            var mode = _interaction.Mode;
            IslandUi.SetVisible(_banner, mode != IslandMode.Browse);
            if (mode == IslandMode.Browse)
            {
                return;
            }

            var island = _game.Island;
            _bannerIcon.EnableInClassList(UiClasses.Icon.Build, mode != IslandMode.Expand);
            _bannerIcon.EnableInClassList(UiClasses.Icon.ExpandIsland, mode == IslandMode.Expand);
            IslandUi.SetVisible(_bannerConfirm, mode != IslandMode.Expand);
            _bannerCancel.text = mode == IslandMode.Expand ? "おわる" : "やめる";
            if (mode == IslandMode.Expand)
            {
                _bannerText.text = $"光る海をタップ（水 {IslandUi.Number(island.ExpandWaterCost)}・お魚 {IslandUi.Number(island.ExpandFishCost)}）あと {island.ExpandRoom} マス";
                return;
            }

            var def = IslandCatalog.Get(_interaction.PlacingKind);
            var ok = _interaction.GhostResult == IslandActionResult.Ok;
            _bannerConfirm.SetEnabled(ok);
            _bannerConfirm.text = mode == IslandMode.Move ? "ここに移す" : "ここに建てる";
            _bannerText.text = ok
                ? $"{def.Name}：置く場所をタップ" + (def.NeedsCoast ? "（海ぞい）" : "")
                : $"{def.Name}：{IslandUi.Message(_interaction.GhostResult)}";
        }

        // ------------------------------------------------------------------
        // 施設
        // ------------------------------------------------------------------

        private void OpenFacility(int id)
        {
            var f = _game.Island.Find(id);
            if (f == null)
            {
                return;
            }

            _facilityId = id;
            VisualElement statusHolder = null;
            ProgressBar progress = null;
            Label workers = null;
            Label speed = null;
            Label pearls = null;
            Button minus = null, plus = null;
            var recipeButtons = new List<Button>();

            OpenSheet(f.Def.Name, (body, footer) =>
            {
                statusHolder = new VisualElement();
                body.Add(statusHolder);

                if (f.Def.Role == FacilityRole.Producer)
                {
                    progress = new ProgressBar { lowValue = 0, highValue = 1 };
                    progress.AddToClassList(UiClasses.Progress.Root);
                    progress.AddToClassList(UiClasses.Progress.Eco);
                    var recipeRow = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(f.Def), IslandUi.TintClass(f.Def), true),
                        "つくるもの", Describe(f.Def).Split('\n').Last());
                    recipeRow.Q(className: UiClasses.Row.Body).Add(progress);
                    body.Add(recipeRow);

                    if (f.Def.Recipes.Count > 1)
                    {
                        var choices = new VisualElement();
                        choices.AddToClassList(UiClasses.Cost.Root);
                        for (var i = 0; i < f.Def.Recipes.Count; i++)
                        {
                            var index = i;
                            var r = f.Def.Recipes[i];
                            var b = IslandUi.Pill($"{r.Name}（{r.Seconds:0} 秒・ガス {r.GasPerHour:0.#}/時）", () =>
                            {
                                _game.SetRecipe(id, index);
                                foreach (var other in recipeButtons)
                                {
                                    other.EnableInClassList(UiClasses.Pill.Selected, recipeButtons.IndexOf(other) == index);
                                }
                            });
                            recipeButtons.Add(b);
                            choices.Add(b);
                        }

                        body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.RecipeHigh, UiClasses.Tint.Gas), "作り方", null));
                        body.Add(choices);
                    }

                    speed = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                    body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.TimeForward, UiClasses.Tint.Primary), "速さ",
                        "質の良いマス・真珠・ペンギンの力で速くなる", speed));

                    pearls = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                    var pearlRow = IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Pearl, UiClasses.Tint.Pearl), "真珠",
                        $"1 つで 10% 速くなる（{_game.Island.Parameters.PearlsPerFacility} つまで）", pearls);
                    pearlRow.Add(IslandUi.Pill("入れる", () =>
                    {
                        var r = _game.AddPearl(id);
                        _hud?.ShowToast(r == IslandActionResult.Ok ? "真珠を入れたよ" : IslandUi.Message(r));
                    }));
                    body.Add(pearlRow);
                }

                if (f.Def.Workers > 0)
                {
                    var stepper = new VisualElement();
                    stepper.AddToClassList(UiClasses.Stepper.Root);
                    minus = new Button(() => ChangeWorkers(id, -1)) { text = "−" };
                    minus.AddToClassList(UiClasses.Stepper.Button);
                    workers = IslandUi.Text("", UiClasses.Stepper.Value);
                    plus = new Button(() => ChangeWorkers(id, +1)) { text = "＋" };
                    plus.AddToClassList(UiClasses.Stepper.Button);
                    stepper.Add(minus);
                    stepper.Add(workers);
                    stepper.Add(plus);
                    body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Penguin, UiClasses.Tint.Original), "はたらくペンギン",
                        "手のあいているペンギンを配属する", stepper));
                }
                else
                {
                    body.Add(IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(f.Def), IslandUi.TintClass(f.Def)), "効果", EffectText(f)));
                }

                footer.Add(IslandUi.Pill("移す", () =>
                {
                    CloseSheet();
                    _interaction.BeginMove(id);
                }));
                footer.Add(IslandUi.Pill("取り壊す", () => ConfirmDemolish(id), UiClasses.Pill.Danger));
            }, () =>
            {
                var cur = _game.Island.Find(id);
                if (cur == null)
                {
                    CloseSheet();
                    return;
                }

                statusHolder.Clear();
                statusHolder.Add(IslandUi.StatusPill(cur));
                if (progress != null)
                {
                    progress.value = (float)cur.ProgressRatio;
                }

                if (speed != null)
                {
                    speed.text = $"× {_game.Island.SpeedOf(cur):0.00}";
                }

                if (pearls != null)
                {
                    pearls.text = $"{cur.Pearls}（手もち {IslandUi.Number(_game.Island.Get(Resource.Pearl))}）";
                }

                if (workers != null)
                {
                    workers.text = $"{cur.Workers} / {cur.Def.Workers}";
                    minus.SetEnabled(cur.Workers > 0);
                    plus.SetEnabled(cur.Workers < cur.Def.Workers && _game.Island.FreeWorkers > 0);
                }

                for (var i = 0; i < recipeButtons.Count; i++)
                {
                    recipeButtons[i].EnableInClassList(UiClasses.Pill.Selected, i == cur.RecipeIndex);
                }
            });
        }

        private string EffectText(Facility f)
        {
            var p = _game.Island.Parameters;
            return f.Def.Role switch
            {
                FacilityRole.Storage => $"品物の置き場 +{p.StoragePerWarehouse}（今は {_game.Island.StorageLimit} 個まで）",
                FacilityRole.Housing => $"住めるペンギン +{p.HousingPerDormitory}（今は {_game.Island.Housing} 羽まで）",
                FacilityRole.Amplifier => $"{IslandCatalog.NameOf(f.Def.Amplifies.GetValueOrDefault())}を受け取る量 +{p.AmplifierBonus * 100:0}%",
                FacilityRole.AutoDeliver => "そろった注文を港へ自動で届ける",
                _ => "",
            };
        }

        private void ChangeWorkers(int id, int delta)
        {
            var f = _game.Island.Find(id);
            if (f == null)
            {
                return;
            }

            var r = _game.SetWorkers(id, f.Workers + delta);
            if (r != IslandActionResult.Ok)
            {
                _hud?.ShowToast(IslandUi.Message(r));
            }
        }

        private void ConfirmDemolish(int id)
        {
            var f = _game.Island.Find(id);
            if (f == null || _hud == null)
            {
                return;
            }

            _hud.ShowModal($"{f.Def.Name}を取り壊す？", "建てたときの半分が戻るよ", null, "取り壊す", () =>
            {
                if (_game.Demolish(id) == IslandActionResult.Ok)
                {
                    CloseSheet();
                    _hud.ShowToast($"{f.Def.Name}を取り壊したよ");
                }
            }, true);
        }

        // ------------------------------------------------------------------
        // 港
        // ------------------------------------------------------------------

        public void OpenHarbor()
        {
            var cards = new List<(Label Status, Button Deliver, Label Stock)>();
            Label stage = null;
            ProgressBar stageBar = null;
            OpenSheet("港の注文", (body, footer) =>
            {
                stage = IslandUi.Text("", UiClasses.Text.Caption, UiClasses.Text.Sub);
                stageBar = new ProgressBar { lowValue = 0, highValue = 1 };
                stageBar.AddToClassList(UiClasses.Progress.Root);
                stageBar.AddToClassList(UiClasses.Progress.Point);
                var stageRow = IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Flag, UiClasses.Tint.Point), "港の育ち具合", null);
                stageRow.Q(className: UiClasses.Row.Body).Add(stageBar);
                stageRow.Q(className: UiClasses.Row.Body).Add(stage);
                body.Add(stageRow);

                var island = _game.Island;
                for (var i = 0; i < island.Orders.Count; i++)
                {
                    var slot = i;
                    var o = island.Orders[i];
                    var status = IslandUi.Text("", UiClasses.Row.Sub);
                    var stock = IslandUi.Text("", UiClasses.Text.Caption, UiClasses.Text.Bold);
                    var deliver = IslandUi.Pill("届ける", () =>
                    {
                        var order = _game.Island.Orders[slot];
                        var r = _game.Deliver(slot);
                        _hud?.ShowToast(r == IslandActionResult.Ok ? $"お魚を {IslandUi.Number(order.Reward)} 匹もらったよ！" : IslandUi.Message(r));
                        if (r == IslandActionResult.Ok)
                        {
                            OpenHarbor();
                        }
                    }, UiClasses.Pill.Primary);
                    var reward = IslandUi.Cost();
                    IslandUi.AddCost(reward, UiClasses.Icon.Fish, UiClasses.Tint.Fish, o.Reward, false);
                    var row = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(o.Item), UiClasses.Tint.Fish),
                        $"{IslandCatalog.NameOf(o.Item)} × {o.Count}", null, deliver);
                    var rowBody = row.Q(className: UiClasses.Row.Body);
                    rowBody.Add(stock);
                    rowBody.Add(reward);
                    rowBody.Add(status);
                    row.EnableInClassList(UiClasses.Row.Last, i == island.Orders.Count - 1);
                    body.Add(row);
                    cards.Add((status, deliver, stock));
                }
            }, () =>
            {
                var island = _game.Island;
                var p = island.Parameters;
                var s = island.HarborStage;
                if (s >= p.HarborStageDeliveries.Length)
                {
                    stage.text = "完成！おでん祭りの港";
                    stageBar.value = 1;
                }
                else
                {
                    var prev = s == 0 ? 0 : p.HarborStageDeliveries[s - 1];
                    var next = p.HarborStageDeliveries[s];
                    stage.text = $"あと {next - island.Delivered} 回届けると港が育つ（{island.Delivered} 回）";
                    stageBar.value = (float)(island.Delivered - prev) / Math.Max(1, next - prev);
                }

                for (var i = 0; i < cards.Count && i < island.Orders.Count; i++)
                {
                    var o = island.Orders[i];
                    var ready = island.IsOrderReady(i);
                    var have = island.StockOf(o.Item);
                    cards[i].Stock.text = $"手もち {IslandUi.Number(have)} / {o.Count}";
                    cards[i].Status.text = ready ? "" : $"舟が向かっているよ（あと {Math.Ceiling(o.ArrivesAt - island.PlayTime):0} 秒）";
                    cards[i].Deliver.SetEnabled(ready && have >= o.Count);
                }
            });
        }

        // ------------------------------------------------------------------
        // 生産量
        // ------------------------------------------------------------------

        private void OpenProduction()
        {
            var rows = new Dictionary<Item, (Label Stock, Label Rates)>();
            Label gas = null, workers = null, storage = null;
            OpenSheet("生産量", (body, footer) =>
            {
                gas = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Gas, UiClasses.Tint.Gas), "ガスの使い方", "施設が動いている間に減る", gas));
                workers = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Penguin, UiClasses.Tint.Original), "はたらくペンギン",
                    "記録した日の数だけ増える（宿舎で住める数が増える）", workers));
                storage = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.StorageFull, UiClasses.Tint.Primary), "置き場", "お魚以外の品物 1 種類ごとの上限", storage));
                body.Add(IslandUi.Text("品物ごと（1 時間あたり）", UiClasses.SectionTitle));
                foreach (var item in IslandCatalog.Items)
                {
                    var stock = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy);
                    var rates = IslandUi.Text("", UiClasses.Row.Sub);
                    var row = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(item), UiClasses.Tint.Fish), IslandCatalog.NameOf(item), null, stock);
                    row.Q(className: UiClasses.Row.Body).Add(rates);
                    body.Add(row);
                    rows[item] = (stock, rates);
                }
            }, () =>
            {
                var island = _game.Island;
                var hours = island.GasHoursLeft;
                gas.text = island.GasPerHour <= 0 ? "使っていない" : $"{island.GasPerHour:0.##}/時・あと {(double.IsInfinity(hours) ? "∞" : hours >= 48 ? $"{hours / 24:0} 日" : $"{hours:0.#} 時間")}";
                workers.text = $"{island.AssignedWorkers} / {island.Population}";
                storage.text = $"{island.StorageLimit} 個";
                foreach (var rate in island.Rates())
                {
                    var (stock, text) = rows[rate.Item];
                    stock.text = IslandUi.Number(island.StockOf(rate.Item));
                    if (rate.ProducedPerHour <= 0 && rate.ConsumedPerHour <= 0)
                    {
                        text.text = "まだ作っていない";
                        continue;
                    }

                    var net = rate.NetPerHour;
                    var warn = net < 0 ? "　足りない！" : "";
                    text.text = $"作る {IslandUi.Rate(rate.ProducedPerHour)}・使う {IslandUi.Rate(rate.ConsumedPerHour)}・差 {(net >= 0 ? "+" : "")}{IslandUi.Rate(net)}{warn}";
                }
            });
        }

        // ------------------------------------------------------------------
        // 資源の集め方
        // ------------------------------------------------------------------

        /// <summary>
        /// 資源ごとに、どうすれば増えるか・今日どこまで受け取ったか・倍率の内訳・何に使うかを出す。
        /// 数値は <see cref="IslandParameters"/> から読むので、調整してもここを直す必要はない。
        /// </summary>
        public void OpenResources()
        {
            var today = new Dictionary<Resource, Label>();
            var multipliers = new Dictionary<Resource, Label>();
            var amounts = new Dictionary<Resource, Label>();
            OpenSheet("資源の集め方", (body, footer) =>
            {
                var p = _game.Island.Parameters;
                body.Add(IslandUi.Text("電気・水・ガス・オールマイティは、現実のエコな行動からだけ増える。島の中では作れない。",
                    UiClasses.Text.Caption, UiClasses.Text.Sub, UiClasses.IslandGuide.Lead));

                void Add(Resource r, string how, string use)
                {
                    var amount = IslandUi.Text("", UiClasses.Text.Label, UiClasses.Text.Heavy, UiClasses.IslandGuide.Amount);
                    var row = IslandUi.Row(IslandUi.IconBadge(IslandUi.IconClass(r), IslandUi.TintClass(r)), IslandCatalog.NameOf(r), how, amount);
                    var rowBody = row.Q(className: UiClasses.Row.Body);
                    var t = IslandUi.Text("", UiClasses.Text.Caption, UiClasses.Text.Bold, UiClasses.IslandGuide.Today);
                    var m = IslandUi.Text("", UiClasses.Text.Caption, UiClasses.Text.Sub);
                    rowBody.Add(t);
                    rowBody.Add(m);
                    rowBody.Add(IslandUi.Text("使い道：" + use, UiClasses.Text.Caption, UiClasses.Text.Sub));
                    today[r] = t;
                    multipliers[r] = m;
                    amounts[r] = amount;
                    body.Add(row);
                }

                Add(Resource.Electricity,
                    $"エコ写真で「電気の節約」と判定 +{p.PhotoMainGrant:0}、ほかの写真でも +{p.PhotoSideGrant:0}（1 日 {p.PhotosPerDay} 枚まで）",
                    "施設を建てる");
                Add(Resource.Water,
                    $"エコ写真で「水の節約」と判定 +{p.PhotoMainGrant:0}、ほかの写真でも +{p.PhotoSideGrant:0}（1 日 {p.PhotosPerDay} 枚まで）",
                    "海を凍らせて島を広げる");
                Add(Resource.Gas,
                    $"{p.StepsPerGas:N0} 歩ごとに +1（1 日 {p.StepGasPerDayMax:0} まで）。写真で「移動」と判定 +{p.PhotoMainGrant:0}、ほかの写真でも +{p.PhotoSideGrant:0}",
                    "施設を動かす（動いている間ずっと減る）");
                Add(Resource.AllMighty,
                    $"夜の振り返りで「できた」+{p.MissionAllMighty:0}、「できなかった」でも +{p.MissionTriedAllMighty:0}。写真で「食べ物」「物を大事に」と判定 +{p.PhotoMainGrant:0}、エコと判定できない写真 +{p.PhotoSideGrant:0}",
                    "電気・水・ガスが足りないとき、代わりに 1 対 1 で使われる");

                body.Add(IslandUi.Text("島の中で増えるもの", UiClasses.SectionTitle));
                body.Add(IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Fish, UiClasses.Tint.Fish), "お魚",
                    $"港の注文に品物を届ける（品物の値 × 個数 × {p.OrderRewardMultiplier:0.#}）。漁場でもとれる。使い道：建てる・広げる"));
                var pearl = IslandUi.Row(IslandUi.IconBadge(UiClasses.Icon.Pearl, UiClasses.Tint.Pearl), "真珠",
                    $"研究所で作る。使い道：施設 1 つに {p.PearlsPerFacility} 個まで入れて、1 個ごとに速さ +{p.PearlSpeed * 100:0}%");
                pearl.EnableInClassList(UiClasses.Row.Last, true);
                body.Add(pearl);
            }, () =>
            {
                var island = _game.Island;
                var p = island.Parameters;
                var session = _game.Session;
                foreach (var kv in amounts)
                {
                    kv.Value.text = IslandUi.Number(island.Get(kv.Key));
                }

                var photo = _game.CanReceivePhotoToday ? "今日：写真はまだ" : "今日：写真は受け取った";
                today[Resource.Electricity].text = photo;
                today[Resource.Water].text = photo;

                var steps = _game.StepsToday;
                var stepText = steps >= 0 ? $"今日：{steps:N0} 歩" : _game.StepsSupported ? "今日：歩数を読み込み中" : "今日：この端末では歩数を読めない";
                today[Resource.Gas].text = $"{stepText} → ガス {island.StepGasToday:0} / {p.StepGasPerDayMax:0}";

                var selected = session.SelectedOn(session.Today);
                var done = selected.Count(id => session.IsCheckedIn(session.Today, id));
                today[Resource.AllMighty].text = selected.Count == 0
                    ? "今日：ミッションをまだ選んでいない"
                    : $"今日：振り返り {done} / {selected.Count} 件";

                foreach (var kv in multipliers)
                {
                    kv.Value.text = MultiplierText(island, kv.Key);
                }
            });
        }

        /// <summary>受け取る量の倍率と、その内訳 (増幅施設・図鑑のペンギン)。</summary>
        private static string MultiplierText(IslandGame island, Resource r)
        {
            var amp = IslandCatalog.Facilities.FirstOrDefault(d => d.Amplifies == r);
            var amps = island.Facilities.Count(f => f.Def.Amplifies == r && f.Status == FacilityStatus.Running);
            var penguins = PenguinDex.Entries
                .Where(e => e.Bonus == BonusKind.ResourceGain && e.Resource == r && island.Species.Contains(e.Species))
                .Select(e => e.Species)
                .ToList();
            var parts = new List<string>();
            if (amps > 0 && amp != null)
            {
                parts.Add($"{amp.Name} {amps} 棟");
            }

            if (penguins.Count > 0)
            {
                parts.Add(string.Join("・", penguins));
            }

            if (parts.Count == 0)
            {
                return amp != null ? $"倍率 ×1（{amp.Name}を建てると増える）" : "倍率 ×1";
            }

            return $"倍率 ×{island.GainMultiplier(r):0.##}（{string.Join("、", parts)}）";
        }
    }
}
