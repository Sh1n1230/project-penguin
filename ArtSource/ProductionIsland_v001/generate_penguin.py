"""Preserve the existing v001 transform/shape-key rig and add four baked clips."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
bpy.context.preferences.filepaths.save_version=0
OUT = ROOT/'Assets/3Dmodel/Penguin_Production_v001'
SOURCE = ROOT/'ArtSource/Penguin_Production_v001'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/3Dmodel/Penguin_v001/Penguin_Waddle_1p3m.fbx'))
scene=bpy.context.scene
scene.frame_set(2)
mesh=bpy.data.objects['Penguin']
ground=bpy.data.objects['Penguin_Unity_GroundRoot']
rock=bpy.data.objects['Penguin_Waddle_Root']
squash=bpy.data.objects['Penguin_Waddle_Squash']
for obj in scene.objects:
    obj.animation_data_clear()
if mesh.data.shape_keys:
    mesh.data.shape_keys.animation_data_clear()
    for key in mesh.data.shape_keys.key_blocks:
        key.value=0
for action in list(bpy.data.actions):
    if action.users == 0: bpy.data.actions.remove(action)
ground.rotation_euler=(0,0,0)
ground.rotation_euler.z=math.pi
rock.rotation_euler=(0,0,0)
squash.scale=(1,1,1)
base_location=rock.location.copy()
ground_location=ground.location.copy()
basis=mesh.data.shape_keys.key_blocks['Basis']

def smooth(a,b,t):
    t=max(0,min(1,(t-a)/(b-a)))
    return t*t*(3-2*t)

carry=mesh.shape_key_add(name='Carry_Flippers')
work=mesh.shape_key_add(name='Work_Flippers')
tilt=mesh.shape_key_add(name='Idle_HeadTilt')
cheer=mesh.shape_key_add(name='Cheer_Flippers')
for index,vertex in enumerate(basis.data):
    x,y,z=vertex.co
    wing=smooth(1.9,2.9,abs(x))*smooth(-.2,1.2,z)*(1-smooth(5.0,6.2,z))
    carry.data[index].co=vertex.co+Vector((-x*.55*wing,-3.4*wing,2.5*wing))
    work.data[index].co=vertex.co+Vector((-x*.18*wing,-2.0*wing,2.0*wing))
    cheer.data[index].co=vertex.co+Vector((x*.15*wing,-.2*wing,5.0*wing))
    head=smooth(5.8,7.5,z)
    angle=.16*head
    tilt.data[index].co=(x*math.cos(angle)+(z-6.2)*math.sin(angle),y,
                         -x*math.sin(angle)+(z-6.2)*math.cos(angle)+6.2)

clips=[('CarryWalk',1,49),('WorkLoop',61,109),('Idle',121,193),('Cheer',205,253)]
scene.render.fps=24
scene.frame_start=1
scene.frame_end=253
for name,start,end in clips:
    for frame in range(start,end+1):
        t=(frame-start)/(end-start)
        phase=t*math.tau
        for key in mesh.data.shape_keys.key_blocks:
            if key.name!='Basis': key.value=0
        rock.location=base_location.copy()
        rock.rotation_euler=(0,0,0)
        squash.scale=(1,1,1)
        if name=='CarryWalk':
            carry.value=.85
            mesh.data.shape_keys.key_blocks['Left_Foot_Lift'].value=max(0,math.sin(phase*2))*.65
            mesh.data.shape_keys.key_blocks['Right_Foot_Lift'].value=max(0,-math.sin(phase*2))*.65
            rock.rotation_euler[1]=math.sin(phase*2)*.035
            rock.location.z += abs(math.sin(phase*2))*.07
        elif name=='WorkLoop':
            carry.value=.32
            work.value=(1-math.cos(phase*3))*.35
            rock.rotation_euler[0]=.04*(1-math.cos(phase*3))
        elif name=='Idle':
            tilt.value=(1-math.cos(phase))*.5
            squash.scale=(1+.004*math.sin(phase),1+.004*math.sin(phase),1-.006*math.sin(phase))
        else:
            cheer.value=math.sin(math.pi*t)**2
            rock.location.z += math.sin(math.pi*t)**2*.75
            rock.rotation_euler[1]=math.sin(phase*2)*.05
        for key in mesh.data.shape_keys.key_blocks:
            if key.name!='Basis': key.keyframe_insert('value',frame=frame)
        rock.keyframe_insert('location',frame=frame)
        rock.keyframe_insert('rotation_euler',frame=frame)
        squash.keyframe_insert('scale',frame=frame)
for obj in (rock,squash):
    for curve in obj.animation_data.action.fcurves:
        for point in curve.keyframe_points: point.interpolation='LINEAR'
for curve in mesh.data.shape_keys.animation_data.action.fcurves:
    for point in curve.keyframe_points: point.interpolation='LINEAR'
for name,start,end in clips:
    scene.timeline_markers.new(name,frame=start)
# CarrySocket is a documented attachment transform, retaining the original rig.
socket=bpy.data.objects.new('CarrySocket',None)
bpy.context.collection.objects.link(socket)
socket.parent=ground
socket.location=(0,-4.4,3.65)
socket.scale=(1/ground.scale.x,)*3
bpy.ops.object.select_all(action='SELECT')
scene.frame_set(1)
bpy.ops.export_scene.fbx(filepath=str(OUT/'Penguin_Production_v001.fbx'),use_selection=True,
    axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=True,
    bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,
    path_mode='COPY',embed_textures=False)
for image in bpy.data.images:
    if image.source=='FILE':
        try: image.pack()
        except RuntimeError: pass
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'Penguin_Production_v001.blend'))
(OUT/'IMPORT_README.md').write_text('''# Penguin Production v001

P-01 CarryWalk / P-02 WorkLoop / P-03 Idle / P-04 Cheer。

元データは Penguin_v001/Penguin_Waddle_1p3m.fbx。元の親子階層、メッシュ、足のブレンドシェイプを維持し、ヒレと頭のブレンドシェイプを追加しています。元モデルにはボーンがありません。v002 の静止モデルへクリップだけを直接割り当てる構成ではありません。

24fps の一本のベイク済みタイムラインを Unity Editor の Build Asset Pack が4つに切り分けます。

| clip | start | end | loop |
|---|---:|---:|---|
| CarryWalk | 0 | 48 | yes |
| WorkLoop | 60 | 108 | yes |
| Idle | 120 | 192 | yes |
| Cheer | 204 | 252 | no |

CarrySocket に Item_* の Prefab を子として付けてください。アニメーションはその場で動き、経路移動はゲーム側で制御します。正面 -Z、足元 Y=0、元モデルと同じ約1.3m。PNG は元モデルのテクスチャをコピーしています。URP Lit の Base Map / Normal Map に元と同じ画像を指定してください。

編集元: ArtSource/Penguin_Production_v001/Penguin_Production_v001.blend。
''',encoding='utf-8')
print('Four baked clips created with the existing transform and blendshape rig.')
