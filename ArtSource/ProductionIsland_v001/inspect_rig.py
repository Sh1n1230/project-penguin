import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(root/'Assets/3Dmodel/Penguin_v001/Penguin_Waddle_1p3m.fbx'))
for obj in bpy.context.scene.objects:
    print('OBJECT',obj.name,obj.type,tuple(obj.dimensions))
    print('TRANSFORM',tuple(obj.location),tuple(obj.rotation_euler),tuple(obj.scale),'parent',obj.parent.name if obj.parent else '-')
    if obj.type == 'MESH':
        print('BOUNDS',tuple(min(v.co[i] for v in obj.data.vertices) for i in range(3)),tuple(max(v.co[i] for v in obj.data.vertices) for i in range(3)))
        if obj.data.shape_keys:
            print('SHAPEKEYS',[key.name for key in obj.data.shape_keys.key_blocks])
    if obj.type=='ARMATURE':
        for bone in obj.data.bones:
            print('BONE',bone.name,'parent',bone.parent.name if bone.parent else '-', 'head',tuple(bone.head_local))
        if obj.animation_data:
            print('ACTION',obj.animation_data.action.name if obj.animation_data.action else None)
for action in bpy.data.actions:
    print('CLIP',action.name,tuple(action.frame_range),len(action.fcurves))
