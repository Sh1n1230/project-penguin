using System;
using System.Linq;
using ProjectPenguin.Presentation.UI;
using ProjectPenguin.Presentation.World;
using ProjectPenguin.Systems;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UIElements;
using IslandKind = ProjectPenguin.Domain.Island.FacilityKind;

namespace ProjectPenguin.Editor.ProductionIsland
{
    /// <summary>
    /// 生産の島のホーム (ProductionIslandHome.unity) を組み立てる。シーンが無ければ HomeWorld.unity を複製して作る
    /// (HomeWorld.unity 自体は変えない)。シーンの YAML を手で書かずに済むよう、参照の設定もすべてここで行う。
    /// 何度実行しても同じ状態になる。
    /// </summary>
    public static class HomeIslandSetup
    {
        public const string ScenePath = "Assets/Scenes/ProductionIslandHome.unity";
        private const string SourceScenePath = "Assets/Scenes/HomeWorld.unity";
        private const string MaterialFolder = "Assets/ProductionIsland/Materials";

        [MenuItem("Production Island/Setup Home Island")]
        public static void Run()
        {
            if (EditorApplication.isPlaying)
            {
                throw new InvalidOperationException("Play Mode を止めてから実行してください。");
            }

            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null && !AssetDatabase.CopyAsset(SourceScenePath, ScenePath))
            {
                throw new InvalidOperationException($"{SourceScenePath} を {ScenePath} に複製できませんでした。");
            }

            var scene = EditorSceneManager.GetActiveScene();
            if (scene.path != ScenePath)
            {
                scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            }

            var game = UnityEngine.Object.FindAnyObjectByType<GameStateSystem>();
            var appUi = GameObject.Find("AppUI");
            var camera = Camera.main;
            if (game == null || appUi == null || camera == null)
            {
                throw new InvalidOperationException("GameState・AppUI・Main Camera が見つかりません。");
            }

            HideOldWorld();
            var island = SetupIsland(game);
            var rig = Ensure<IslandCameraRig>(camera.gameObject);
            Set(rig, "_island", island.transform);
            var rigSo = new SerializedObject(rig);
            rigSo.FindProperty("_distance").floatValue = 16f;
            rigSo.FindProperty("_homeOffset").vector3Value = new Vector3(0f, 0f, 0.4f);
            rigSo.ApplyModifiedPropertiesWithoutUndo();

            var interaction = Ensure<IslandInteraction>(island.gameObject);
            Set(interaction, "_game", game);
            Set(interaction, "_board", island);
            Set(interaction, "_rig", rig);
            Set(interaction, "_ui", appUi.GetComponent<UIDocument>());
            Set(interaction, "_okMaterial", Highlight("IslandHighlight_Ok", new Color(0.18f, 0.72f, 0.45f, 0.55f)));
            Set(interaction, "_ngMaterial", Highlight("IslandHighlight_Ng", new Color(0.9f, 0.33f, 0.29f, 0.55f)));
            Set(interaction, "_selectMaterial", Highlight("IslandHighlight_Select", new Color(1f, 0.79f, 0.16f, 0.6f)));

            var penguins = Ensure<IslandPenguinsView>(island.gameObject);
            Set(penguins, "_game", game);
            Set(penguins, "_board", island);
            var template = GameObject.Find("World")?.transform.Find("Penguins")?.GetChild(0);
            Set(penguins, "_template", template != null ? template.gameObject : null);

            SetupIce(island, game, interaction);
            SetupUi(appUi, game, interaction);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log("HomeIslandSetup: ホームに生産の島を組み込みました。");
        }

        private static void HideOldWorld()
        {
            var world = GameObject.Find("World");
            if (world == null)
            {
                return;
            }

            var iceView = world.GetComponent<IceWorldView>();
            if (iceView != null)
            {
                UnityEngine.Object.DestroyImmediate(iceView);
            }

            foreach (var name in new[] { "IcebergWithCabin", "House", "Penguins", "IceFloes" })
            {
                var t = world.transform.Find(name);
                if (t != null)
                {
                    t.gameObject.SetActive(false);
                }
            }

            // 海の板は陸 (0) より下げ、氷の崖が見えるようにする (IslandBoardView._waterLevel と同じ高さ)。
            var sea = world.transform.Find("Sea");
            if (sea != null)
            {
                sea.localPosition = new Vector3(0f, -0.35f, 0f);
                sea.localScale = new Vector3(60f, 1f, 60f);
            }
        }

        private static IslandBoardView SetupIsland(GameStateSystem game)
        {
            var go = GameObject.Find("Island");
            if (go == null)
            {
                go = new GameObject("Island");
            }

            go.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            var view = Ensure<IslandBoardView>(go);
            Set(view, "_game", game);
            Set(view, "_baseTile", Model("Tile_Ice_Core_v001"));
            Set(view, "_expandedTile", Model("Tile_Ice_Expanded_v001"));
            Set(view, "_crackSmallTile", Model("Tile_Ice_CrackSmall_v001"));
            Set(view, "_crackLargeTile", Model("Tile_Ice_CrackLarge_v001"));
            Set(view, "_sinkingTile", Model("Tile_Ice_Sinking_v001"));
            // 普通の海はシーンの海の板に任せ、タイルを置かない (盤面の境目が箱のように見えないように)。
            Set(view, "_seaTile", null);
            Set(view, "_seaExpandableTile", Model("Tile_Sea_Expandable_v001"));
            Set(view, "_canalTile", Model("Tile_Canal_TwoBanks_v001"));
            Set(view, "_qualityFish", Model("Marker_Fishing_v001"));
            Set(view, "_qualitySalt", Model("Marker_Salt_v001"));
            Set(view, "_qualityKelp", Model("Marker_Kelp_v001"));
            Set(view, "_buildVfxSmall", Vfx("BuildSnow_1x1"));
            Set(view, "_buildVfxLarge", Vfx("BuildSnow_2x2"));
            Set(view, "_sinkVfx", Vfx("IceMelt"));
            Set(view, "_plusOneVfx", Vfx("ProductionPlusOne"));
            Set(view, "_confettiVfx", Vfx("MilestoneConfetti"));
            Set(view, "_pearlVfx", Vfx("PearlRing"));

            var so = new SerializedObject(view);
            var harbors = so.FindProperty("_harborStages");
            harbors.arraySize = 6;
            for (var i = 0; i < 6; i++)
            {
                harbors.GetArrayElementAtIndex(i).objectReferenceValue = Model($"Harbor_Stage{i}_v002");
            }

            var kinds = (IslandKind[])Enum.GetValues(typeof(IslandKind));
            var facilities = so.FindProperty("_facilityPrefabs");
            facilities.arraySize = kinds.Length;
            for (var i = 0; i < kinds.Length; i++)
            {
                var element = facilities.GetArrayElementAtIndex(i);
                element.FindPropertyRelative("Kind").enumValueIndex = (int)kinds[i];
                element.FindPropertyRelative("Prefab").objectReferenceValue = FacilityModel(kinds[i]);
            }

            so.ApplyModifiedPropertiesWithoutUndo();
            return view;
        }

        private static GameObject FacilityModel(IslandKind kind)
        {
            var name = kind.ToString();
            var small = kind == IslandKind.Warehouse || kind == IslandKind.Dormitory || kind == IslandKind.Sorter;
            var model = Model($"Building_{name}_{(small ? "1x1" : "2x2")}_v002");
            if (model == null)
            {
                Debug.LogWarning($"HomeIslandSetup: {kind} のモデルが見つかりません。");
            }

            return model;
        }

        private static void SetupUi(GameObject appUi, GameStateSystem game, IslandInteraction interaction)
        {
            var navigator = appUi.GetComponent<ScreenNavigator>();
            Set(navigator, "_islandInteraction", interaction);

            var hud = Ensure<IslandHudPresenter>(appUi);
            var sheets = Ensure<IslandSheetPresenter>(appUi);
            var photo = Ensure<EcoPhotoFlowPresenter>(appUi);
            var mission = Ensure<MissionScreenPresenter>(appUi);
            var dex = Ensure<DexScreenPresenter>(appUi);
            var onboarding = Ensure<OnboardingPresenter>(appUi);
            var menu = Ensure<MenuScreenPresenter>(appUi);
            var record = Ensure<RecordScreenPresenter>(appUi);

            Set(hud, "_game", game);
            Set(hud, "_navigator", navigator);
            Set(hud, "_sheets", sheets);

            Set(sheets, "_game", game);
            Set(sheets, "_interaction", interaction);
            Set(sheets, "_navigator", navigator);
            Set(sheets, "_hud", hud);

            Set(photo, "_game", game);
            Set(photo, "_navigator", navigator);
            Set(photo, "_camera", appUi.GetComponent<ReceiptCameraPreview>());
            Set(photo, "_analyzing", appUi.GetComponent<AnalyzingScreenPresenter>());
            Set(photo, "_hud", hud);

            Set(mission, "_game", game);
            Set(mission, "_navigator", navigator);
            Set(mission, "_hud", hud);

            Set(dex, "_game", game);
            Set(dex, "_navigator", navigator);

            Set(onboarding, "_game", game);
            Set(onboarding, "_navigator", navigator);

            Set(menu, "_game", game);
            Set(menu, "_navigator", navigator);
            Set(menu, "_onboarding", onboarding);

            Set(record, "_game", game);
            Set(record, "_navigator", navigator);
        }

        private static T Ensure<T>(GameObject go) where T : Component
        {
            // Editor の GetComponent は「無い」ときに偽の null を返すことがあるので ?? は使わない。
            var c = go.GetComponent<T>();
            return c != null ? c : go.AddComponent<T>();
        }

        private static void Set(UnityEngine.Object target, string field, UnityEngine.Object value)
        {
            var so = new SerializedObject(target);
            var p = so.FindProperty(field);
            if (p == null)
            {
                throw new InvalidOperationException($"{target.GetType().Name}.{field} がありません。");
            }

            p.objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static GameObject Model(string name) =>
            AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/3Dmodel/{name}/{name}.prefab");

        private static GameObject Vfx(string name) =>
            AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/VFX/ProductionIsland/Prefabs/{name}.prefab");

        private const string IcebergPath = "Assets/3Dmodel/Cabin_Field_v001/Iceberg_With_Cabin_v001.fbx";

        /// <summary>陸を HomeWorld の氷山と同じ見た目の 1 枚の氷で描く。島の外には遠くの氷山と浮かぶ氷を置く。</summary>
        private static void SetupIce(IslandBoardView island, GameStateSystem game, IslandInteraction interaction)
        {
            var boardSo = new SerializedObject(island);
            boardSo.FindProperty("_drawLandTiles").boolValue = false;
            boardSo.FindProperty("_waterLevel").floatValue = -0.35f;
            boardSo.FindProperty("_submergedDepth").floatValue = 0.8f;
            boardSo.ApplyModifiedPropertiesWithoutUndo();

            var ice = Ensure<IslandIceView>(island.gameObject);
            Set(ice, "_game", game);
            Set(ice, "_interaction", interaction);
            Set(ice, "_snow", IcebergMaterial("Snow_CoolFacet"));
            Set(ice, "_snowShade", IcebergMaterial("Snow_WindBlue"));
            Set(ice, "_gridLine", Highlight("IslandGridLine", new Color(1f, 1f, 1f, 0.7f)));

            var so = new SerializedObject(ice);
            var bands = new[] { "Snow_Porcelain", "Ice_Frosted", "Ice_Aqua", "Ice_Underwater" };
            var bandsProp = so.FindProperty("_cliffBands");
            bandsProp.arraySize = bands.Length;
            for (var i = 0; i < bands.Length; i++)
            {
                bandsProp.GetArrayElementAtIndex(i).objectReferenceValue = IcebergMaterial(bands[i]);
            }

            SetPiece(so.FindProperty("_fissure"), "SurfaceFissure_02");

            var decor = new (string Piece, Vector3 Position, float Scale, float Yaw)[]
            {
                // 奥の水路 (港の左右) に遠くの氷山、島の外の海に浮かぶ氷。どちらも建てられないマスか盤の外。
                ("IcePeak_02", new Vector3(-3.9f, -0.2f, 5.3f), 0.32f, 15f),
                ("IcePeak_01", new Vector3(-2.4f, -0.2f, 6.2f), 0.22f, -20f),
                ("IcePeak_03", new Vector3(3.7f, -0.2f, 5.5f), 0.3f, 40f),
                ("IcePeak_04", new Vector3(4.8f, -0.2f, 4.1f), 0.22f, 0f),
                ("IceBoulder_03", new Vector3(-5.7f, -0.3f, -1.6f), 0.5f, 30f),
                ("IceBoulder_06", new Vector3(5.8f, -0.3f, -3.0f), 0.45f, -50f),
                ("IceBoulder_02", new Vector3(3.9f, -0.3f, -5.9f), 0.5f, 80f),
                ("IceBoulder_07", new Vector3(-4.3f, -0.3f, -5.8f), 0.4f, 10f),
            };
            var decorProp = so.FindProperty("_decor");
            decorProp.arraySize = decor.Length;
            for (var i = 0; i < decor.Length; i++)
            {
                var e = decorProp.GetArrayElementAtIndex(i);
                SetPiece(e.FindPropertyRelative("Piece"), decor[i].Piece);
                e.FindPropertyRelative("Position").vector3Value = decor[i].Position;
                e.FindPropertyRelative("Scale").floatValue = decor[i].Scale;
                e.FindPropertyRelative("Yaw").floatValue = decor[i].Yaw;
            }

            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static Material IcebergMaterial(string name)
        {
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath(IcebergPath))
            {
                if (o is Material m && m.name == name)
                {
                    return m;
                }
            }

            throw new InvalidOperationException($"{IcebergPath} にマテリアル {name} がありません。");
        }

        /// <summary>氷山の FBX の子 (形とマテリアル) を <see cref="IslandIceView.Piece"/> に入れる。</summary>
        private static void SetPiece(SerializedProperty piece, string childName)
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(IcebergPath);
            var child = model.transform.Find(childName);
            if (child == null)
            {
                throw new InvalidOperationException($"{IcebergPath} に {childName} がありません。");
            }

            piece.FindPropertyRelative("Mesh").objectReferenceValue = child.GetComponent<MeshFilter>().sharedMesh;
            var materials = child.GetComponent<MeshRenderer>().sharedMaterials;
            var prop = piece.FindPropertyRelative("Materials");
            prop.arraySize = materials.Length;
            for (var i = 0; i < materials.Length; i++)
            {
                prop.GetArrayElementAtIndex(i).objectReferenceValue = materials[i];
            }
        }

        /// <summary>マスの強調に使う半透明の色 (URP Unlit)。無ければ作る。</summary>
        private static Material Highlight(string name, Color color)
        {
            var path = $"{MaterialFolder}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                AssetDatabase.CreateAsset(mat, path);
            }

            // 半透明 (Surface Type = Transparent, Blend = Alpha)。
            mat.SetFloat("_Surface", 1f);
            mat.SetFloat("_Blend", 0f);
            mat.SetOverrideTag("RenderType", "Transparent");
            mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            mat.SetInt("_ZWrite", 0);
            mat.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Transparent;
            mat.SetColor(ShaderIds.BaseColor, color);
            EditorUtility.SetDirty(mat);
            AssetDatabase.SaveAssets();
            return mat;
        }
    }
}
