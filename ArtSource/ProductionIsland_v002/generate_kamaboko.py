"""Blender 4.3: generate only the reviewed Kamaboko v002 (metres, front -Y).

Reuse v001's palette/primitive/export helpers; never run its batch generation.
"""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
helpers = (ROOT / 'ArtSource/ProductionIsland_v001/generate_models.py').read_text(encoding='utf-8').split('def terrain():')[0]
exec(compile(helpers.replace('_v001', '_v002'), '<v002 primitive helpers>', 'exec'))


def group(name, position, make):
    before = set(bpy.context.scene.objects)
    pivot = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = position
    make()
    for obj in set(bpy.context.scene.objects) - before - {pivot}:
        if obj.parent is None:
            obj.parent = pivot
    return pivot


def half_loaf(name, loc, radius, length, color):
    """Faceted half cylinder with a flat base; axis along Y."""
    steps = 10
    x,y,z = loc
    ring = [(x+radius*math.cos(i*math.pi/steps), z+radius*math.sin(i*math.pi/steps)) for i in range(steps+1)]
    vertices = [(rx,y+dy,rz) for dy in (-length/2,length/2) for rx,rz in ring]
    n = steps+1
    faces = [tuple(reversed(range(n))), tuple(range(n,n*2))]
    faces += [(i,i+1,n+i+1,n+i) for i in range(steps)]
    faces += [(0,n,n*2-1,n-1)]
    faces = [tuple(reversed(face)) for face in faces]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj,name,color)


def loaf(name, radius, length):
    box(name+'Board',(0,0,-.015),(radius*2+.045,length+.04,.03),12,.008)
    half_loaf(name+'Pink',(0,0,0),radius,length,14)
    half_loaf(name+'WhiteFront',(0,-length/2-.004,0),radius*.81,.008,6)
    half_loaf(name+'WhiteBack',(0,length/2+.004,0),radius*.81,.008,6)


box('Foundation',(0,0,.045),(1.86,1.86,.09),0,.025)
box('FoundationPinkRim',(0,0,.1),(1.8,1.8,.035),14,.01)
box('WorkshopFloor',(0,0,.13),(1.73,1.73,.035),6,.01)
# A giant board-mounted pink/white kamaboko IS the roof/identity sign.
for x in (-.57,.57):
    box('RoofPillar',(x,.62,.59),(.075,.075,.95),12,.01)
box('RoofBackWall',(0,.76,.57),(1.22,.045,.82),11,.01)
group('KamabokoRoof',(0,.50,1.04),lambda:loaf('RoofLoaf',.65,.57))
box('PinkRoofApron',(0,.2,1.015),(1.31,.035,.08),14,.01)
# Input -> exposed steamer -> output, clearly separated across the frontage.
for x,name,color in ((-.65,'Input',2),(.65,'Output',14)):
    box(name+'Table',(x,-.4,.46),(.48,.6,.09),color,.015)
    box(name+'Tray',(x,-.4,.515),(.42,.47,.025),6,.005)
    for y in (-.58,-.22):
        box(name+'TableLeg',(x,y,.3),(.07,.07,.3),12,.008)
    # Arrow plates face inward/outward along the processing line.
    verts=[(x-.09,-.73,.54),(x+.09,-.73,.54),(x+.09,-.68,.54),(x+.18,-.78,.54),(x+.09,-.88,.54),(x+.09,-.83,.54),(x-.09,-.83,.54)]
    mesh=bpy.data.meshes.new(name+'Arrow'); mesh.from_pydata(verts,[],[tuple(range(7))]); mesh.update()
    obj=bpy.data.objects.new(name+'FlowArrow',mesh); bpy.context.collection.objects.link(obj); finish(obj,obj.name,color)
box('SteamerStove',(0,-.4,.3),(.55,.53,.3),13,.025)
box('StovePinkTrim',(0,-.685,.34),(.42,.025,.11),14,.01)
cyl('SteamerBasket',(0,-.4,.56),.275,.24,13,12)
for z in (.46,.54,.65):
    cyl('BasketBand',(0,-.4,z),.286,.025,12,12)
for angle in range(0,360,45):
    a=math.radians(angle)
    box('BasketSlat',(math.cos(a)*.278,-.4+math.sin(a)*.278,.56),(.035,.035,.17),12,.004)
group('SteamerLid',(0,-.4,.7),lambda:(cyl('LidDisk',(0,0,0),.3,.055,13,12),cyl('LidKnob',(0,0,.064),.065,.07,12,8)))
center=bpy.data.objects.new('ChamberCenter',None); bpy.context.collection.objects.link(center); center.location=(0,-.4,.59)
group('InputFish',(-.65,-.4,.58),lambda:fish((0,0,0),1.35))
group('OutputKamaboko',(.65,-.4,.55),lambda:loaf('Product',.17,.28))
for i in range(3):
    ball('SteamPuff'+str(i),(-.07+i*.07,-.4,.9+i*.12),(.075,.075,.09),6)
# Fish emblem on the input side reinforces the recipe without written labels.
box('InputSignPost',(-.73,.1,.67),(.035,.035,.91),12,.006)
box('InputSignPlate',(-.73,.095,1.04),(.30,.045,.23),1,.015)
group('FishSign',(-.73,.063,1.04),lambda:fish((0,0,0),.85))

# Render before the exporter removes the model from the Blender scene.
bpy.context.view_layer.update()
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1000; scene.render.resolution_y=850; scene.render.resolution_percentage=100
scene.world.color=(.7,.8,.9)
scene.view_settings.view_transform='Standard'
camera_data=bpy.data.cameras.new('PreviewCamera'); camera=bpy.data.objects.new('PreviewCamera',camera_data); scene.collection.objects.link(camera)
camera.location=(3.4,-5,3.4); target=Vector((0,0,.65)); camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler(); camera_data.type='ORTHO'; camera_data.ortho_scale=2.9; scene.camera=camera
light_data=bpy.data.lights.new('PreviewLight','AREA'); light=bpy.data.objects.new('PreviewLight',light_data); scene.collection.objects.link(light); light.location=(1,-3,5); light_data.energy=450; light_data.size=4
preview_dir=ROOT/'ArtSource/ProductionIsland_v002'; preview_dir.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(preview_dir/'Kamaboko_Design.png'); scene.render.film_transparent=False
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera,do_unlink=True); bpy.data.objects.remove(light,do_unlink=True)
save('Building_Kamaboko_2x2','B-06 design revision',2,'building')
manifest[0]['moving_parts']=['InputFish','SteamerLid','OutputKamaboko','SteamPuff0','SteamPuff1','SteamPuff2']
(OUT/'Building_Kamaboko_2x2_v002/IMPORT_README.md').write_text(
    '# かまぼこ工場 v002\n\n大きなピンク・白のかまぼこ形の屋根と、魚→蒸し器→完成品の表示工程。\n\n'
    '再生成：BlenderでArtSource/ProductionIsland_v002/generate_kamaboko.pyを実行し、Unity Editorの'
    'Production Island > Build Kamaboko Design Revisionを実行。確認シーン：Assets/Scenes/KamabokoDesignReview.unity。\n\n'
    '専用KamabokoProductionCycleが工程を7.5秒で繰り返す。SetRunning(false)で工程停止、RestartCycle()で投入から再開。'
    '生産計算や在庫は含まない。汎用ProductionIslandMotionの_Anim処理とは併用しない。\n',encoding='utf-8')
(preview_dir/'kamaboko-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
