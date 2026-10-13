import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'ArtSource/Penguin_Production_v001/Penguin_Production_v001.blend'))
scene=bpy.context.scene
socket=bpy.data.objects['CarrySocket']
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/3Dmodel/Item_Fish_v001/Item_Fish_v001.fbx'),use_anim=False)
prop=[o for o in set(bpy.data.objects)-before if o.parent is None][0]
prop.parent=socket
prop.location=(0,0,0)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012))
mat=bpy.data.materials.new('Snow'); mat.diffuse_color=(.93,.97,1,1)
bpy.context.object.data.materials.append(mat)
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.75,.85,1,1); bg.inputs['Strength'].default_value=.65
bpy.ops.object.light_add(type='AREA',location=(2,3,5))
bpy.context.object.data.energy=350; bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(1.5,3,1.8))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.72))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=1.85; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.samples=12; scene.cycles.use_denoising=True
scene.render.resolution_x=400; scene.render.resolution_y=480; scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard'
for name,frame in [('CarryWalk',13),('WorkLoop',73),('Idle',157),('Cheer',229)]:
    scene.frame_set(frame)
    prop.hide_render=name!='CarryWalk'
    for child in prop.children_recursive: child.hide_render=prop.hide_render
    scene.render.filepath=str(ROOT/f'ArtSource/ProductionIsland_v001/Penguin_{name}.png')
    bpy.ops.render.render(write_still=True)
