# 生産の島 動作サンプリング結果

UTC: 2026-10-07T00:16:52.0094742Z / Unity 6000.6.0f1

PreviewScene: manually invoke production lifecycle methods; Animator.Update engine evaluation. Not a PlayMode/render acceptance test.

| ID | 結果 | 実測 |
|---|---|---|
| MOTION:Building_Chikuwa_2x2_v001 | PASS | parts=3; phase=4; poseDelta=11.41992 |
| STOP:Building_Chikuwa_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Chikuwa_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Chikuwa_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Chikuwa_2x2_v001 | PASS | poseDelta=-3.667969 |
| FLAME | PASS | lowParts=1; highParts=1 |
| MOTION:Building_Collection_1x1_v001 | FAIL | parts=1; phase=4; poseDelta=0 |
| STOP:Building_Collection_1x1_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Collection_1x1_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Collection_1x1_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Collection_1x1_v001 | PASS | poseDelta=-3 |
| MOTION:Building_Dormitory_1x1_v001 | PASS | parts=1; phase=4; poseDelta=-0.3925781 |
| STOP:Building_Dormitory_1x1_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Dormitory_1x1_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Dormitory_1x1_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Dormitory_1x1_v001 | PASS | poseDelta=-0.15625 |
| MOTION:Building_Drying_2x2_v001 | FAIL | parts=1; phase=4; poseDelta=0 |
| STOP:Building_Drying_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Drying_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Drying_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Drying_2x2_v001 | FAIL | poseDelta=0 |
| MOTION:Building_Fishery_2x2_v001 | PASS | parts=2; phase=4; poseDelta=-0.2070313 |
| STOP:Building_Fishery_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Fishery_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Fishery_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Fishery_2x2_v001 | PASS | poseDelta=-0.08203125 |
| MOTION:Building_Kamaboko_2x2_v001 | FAIL | parts=1; phase=4; poseDelta=0 |
| STOP:Building_Kamaboko_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Kamaboko_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Kamaboko_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Kamaboko_2x2_v001 | FAIL | poseDelta=0 |
| MOTION:Building_KelpFarm_2x2_v001 | PASS | parts=1; phase=4; poseDelta=-0.2109375 |
| STOP:Building_KelpFarm_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_KelpFarm_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_KelpFarm_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_KelpFarm_2x2_v001 | PASS | poseDelta=-0.0859375 |
| MOTION:Building_Oden_2x2_v001 | PASS | parts=1; phase=4; poseDelta=-0.2070313 |
| STOP:Building_Oden_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Oden_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Oden_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Oden_2x2_v001 | PASS | poseDelta=-0.08203125 |
| MOTION:Building_Power_2x2_v001 | FAIL | parts=1; phase=4; poseDelta=0 |
| STOP:Building_Power_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Power_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Power_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Power_2x2_v001 | PASS | poseDelta=-11 |
| MOTION:Building_Preparation_2x2_v001 | PASS | parts=1; phase=4; poseDelta=0.001953125 |
| STOP:Building_Preparation_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Preparation_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Preparation_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Preparation_2x2_v001 | PASS | poseDelta=-0.001953125 |
| MOTION:Building_Research_2x2_v001 | PASS | parts=2; phase=4; poseDelta=-0.3847656 |
| STOP:Building_Research_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Research_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Research_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Research_2x2_v001 | PASS | poseDelta=-0.1542969 |
| MOTION:Building_Saltworks_2x2_v001 | PASS | parts=1; phase=4; poseDelta=-0.2050781 |
| STOP:Building_Saltworks_2x2_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Saltworks_2x2_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Saltworks_2x2_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Saltworks_2x2_v001 | PASS | poseDelta=-0.08203125 |
| MOTION:Building_Sorter_1x1_v001 | PASS | parts=1; phase=4; poseDelta=5.363281 |
| STOP:Building_Sorter_1x1_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Sorter_1x1_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Sorter_1x1_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Sorter_1x1_v001 | PASS | poseDelta=-7.173828 |
| MOTION:Building_Warehouse_1x1_v001 | PASS | parts=1; phase=4; poseDelta=-0.3925781 |
| STOP:Building_Warehouse_1x1_v001 | PASS | poseDelta=0; particles emission stopped |
| STOP_MATERIAL:Building_Warehouse_1x1_v001 | PASS | Every MeshRenderer slot compared against configured stopped material. |
| RESTORE_MATERIAL:Building_Warehouse_1x1_v001 | PASS | Original material arrays restored. |
| RESUME:Building_Warehouse_1x1_v001 | PASS | poseDelta=-0.1582031 |
| LINK_FLOW | FAIL | xDelta@1=1; xDelta@3=-0.9999989; count=6; tint=RGBA(0.000, 1.000, 1.000, 1.000) |
| LINK_DIRECTION | PASS | end=(4.00, 0.00, 0.00); directionDot=1 |
| LINK_STATE:Normal | PASS | material=Link_Normal; width=0.08 |
| LINK_STATE:Flowing | PASS | material=Link_Flowing; width=0.08 |
| LINK_STATE:Blocked | PASS | material=Link_Blocked; width=0.08 |
| LINK_STATE:Selected | PASS | material=Link_Selected; width=0.12 |
| LINK_STATE:Drawing | PASS | material=Link_Drawing; width=0.08 |
| LINK_ZERO | PASS | Zero flow hides all beads and preserves position. |
| ANIMATOR:CarryWalk | PASS | 13 engine samples over .65s; poseRange=65.67773; carry=True; normalized=0.3 |
| ANIMATOR:WorkLoop | PASS | 13 engine samples over .65s; poseRange=69.3418; carry=False; normalized=0.3 |
| ANIMATOR:Idle | PASS | 13 engine samples over .65s; poseRange=31.08008; carry=False; normalized=0.2 |
| ANIMATOR:Cheer | PASS | 13 engine samples over .65s; poseRange=58.99805; carry=False; normalized=0.3 |
| BURST:ProductionPlusOne | PASS | start=(0.00, 0.00, 0.00); mid=(0.00, 0.40, 0.00); alphaMid=0; elapsed=39.99999; hidden=True |
| BURST_REENABLE:ProductionPlusOne | PASS | Reset position=(0.00, 0.00, 0.00); alphaOnEnable=0 |
| BURST_ALPHA_RESET:ProductionPlusOne | FAIL | Expected immediately visible text after re-enable, alpha=0 |
| BURST:IceMelt | PASS | start=(0.00, 0.00, 0.00); mid=(0.00, -0.35, 0.00); alphaMid=1; elapsed=39.99999; hidden=True |
| BURST_REENABLE:IceMelt | PASS | Reset position=(0.00, 0.00, 0.00); alphaOnEnable=-1 |
| PORT_PULSE | BLOCKED | Editor Time.time did not advance; brightnessRange=0 |
| PLAYMODE_ACCEPTANCE | BLOCKED | Current user scene and Play Mode left untouched. This preview harness does not verify automatic lifecycle scheduling, rendering or device performance. |
| ISOLATION | PASS | Before=1467:2304:Assets/Scenes/HomeWorld.unity:False active=1467:2304; after=1467:2304:Assets/Scenes/HomeWorld.unity:False active=1467:2304 |
