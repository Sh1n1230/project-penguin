"""Blender 4.3: --background --python ArtSource/ProductionIsland_v001/generate_models.py.

All coordinates are metres, Blender Z up, front -Y. Unity export is Y up.
No existing asset is overwritten. Each deliverable has its own editable source.
"""
import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
bpy.context.preferences.filepaths.save_version = 0
OUT = ROOT / 'Assets/3Dmodel'
SOURCE = ROOT / 'ArtSource'
COLORS = ['EEF7FF', 'B5DBF7', '1F8BEA', '1565C0', '17385F', '6B8199',
          'FFFFFF', 'FFC928', 'F5A623', 'E5534B', '2EB872', 'DDF5E8',
          'A96740', 'EAC79F', 'FFB3C7', '596A75']
NAMES = ['ice', 'ice-edge', 'sea', 'canal', 'navy', 'steel', 'white',
         'yellow', 'orange', 'red', 'green', 'mint', 'wood', 'sand', 'pink', 'grey']
manifest = []
preview = []


def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)


def palette():
    image = bpy.data.images.new('ProductionIsland_ColorAtlas_v001', width=1024, height=1024)
    pixels = []
    rgb = [tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) for h in COLORS]
    for y in range(1024):
        for x in range(1024):
            pixels.extend((*rgb[(y // 256) * 4 + x // 256], 1))
    image.pixels = pixels
    materials = []
    for i, (name, color) in enumerate(zip(NAMES, rgb)):
        mat = bpy.data.materials.new('PI_' + name)
        mat.diffuse_color = (*color, 1)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = image
        mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
        shader.inputs['Roughness'].default_value = .78
        materials.append(mat)
    return image, materials


reset()
atlas, MATS = palette()
for material in MATS: material.use_fake_user=True
stopped_atlas = bpy.data.images.new('ProductionIsland_StoppedAtlas_v001', width=1024, height=1024)
stopped_pixels = list(atlas.pixels)
for index in range(0, len(stopped_pixels), 4):
    r,g,b = stopped_pixels[index:index+3]
    grey = r*.2126 + g*.7152 + b*.0722
    stopped_pixels[index:index+3] = [grey*.72 + value*.12 for value in (r,g,b)]
stopped_atlas.pixels = stopped_pixels


def finish(obj, name, color, bevel=0):
    obj.name = name
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft corners', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.clear()
    obj.data.materials.append(MATS[color])
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='AtlasUV')
    center = ((color % 4 + .5) / 4, (color // 4 + .5) / 4)
    for loop in uv.data:
        loop.uv = center
    return obj


def box(name, loc, size, color, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, color, min(bevel, min(size) * .2))


def cyl(name, loc, radius, depth, color, vertices=10, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    if rotation:
        obj.rotation_euler = rotation
    return finish(obj, name, color)


def ball(name, loc, scale, color):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=1, location=loc)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, color)


def rod(name, start, end, radius, color):
    a, b = Vector(start), Vector(end)
    obj = cyl(name, (a+b)/2, radius, (b-a).length, color, 8)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj


def roof(width=1.65, depth=1.2, height=1.3, color=3):
    verts = [(-width/2, -depth/2, height-.2), (width/2, -depth/2, height-.2),
             (0, -depth/2, height), (-width/2, depth/2, height-.2),
             (width/2, depth/2, height-.2), (0, depth/2, height)]
    mesh = bpy.data.meshes.new('GableRoof')
    mesh.from_pydata(verts, [], [(0,1,2), (5,4,3), (0,2,5,3), (2,1,4,5), (0,3,4,1)])
    obj = bpy.data.objects.new('Roof', mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, 'Roof', color)


def crate(loc=(0,0,.18), size=.3):
    box('Crate', loc, (size,size,size), 12)
    x,y,z = loc
    for dx in (-.33,.33):
        box('CrateBand', (x+dx*size,y-size*.51,z), (size*.07,.018,size*.85), 13, 0)


def fish(loc=(0,0,.11), size=1, dried=False):
    x,y,z = loc
    ball('FishBody', loc, (.12*size,.045*size,.04*size), 8 if dried else 2)
    ball('FishTail', (x-.12*size,y,z), (.055*size,.075*size,.018*size), 12 if dried else 3)
    ball('FishEye', (x+.075*size,y-.035*size,z+.01*size), (.008*size,)*3, 4)


def kelp(loc=(0,0,0), size=1, animated=False):
    x,y,z = loc
    for i in range(3):
        obj = box('Kelp_Anim' if animated else 'Kelp', (x+(i-1)*.045*size,y,z+.13*size),
                  (.045*size,.025*size,.25*size), 10)
        obj.rotation_euler[1] = (i-1)*.22


def save(name, request, footprint, category='model'):
    folder = OUT / (name + '_v001')
    source = SOURCE / (name + '_v001')
    folder.mkdir(parents=True, exist_ok=True)
    source.mkdir(parents=True, exist_ok=True)
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    bounds = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
    dims = [max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
    limit = 200 if name.startswith('Tile_') else 1500 if footprint == 1 else 3000
    if tris > limit:
        raise RuntimeError(f'{name}: {tris} triangles exceeds {limit}')
    if category == 'building' and (dims[0] > footprint-.1+.001 or dims[1] > footprint-.1+.001):
        raise RuntimeError(f'{name}: footprint {dims} exceeds specification')
    # Root is at ground centre; moving parts retain independent transforms.
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for obj in list(bpy.context.scene.objects):
        if obj != root and obj.parent is None:
            obj.parent = root
    # Unity's FBX importer converts Blender -Y to Unity +Z. Turn the design
    # around its ground pivot so the delivered buildings face Unity -Z.
    if category != 'link':
        root.rotation_euler.z = math.pi
    shared_folder = OUT / 'ProductionIsland_v001'
    shared_folder.mkdir(parents=True, exist_ok=True)
    atlas.filepath_raw = str(shared_folder / 'ProductionIsland_ColorAtlas_v001.png')
    atlas.file_format = 'PNG'
    atlas.save()
    stopped_atlas.filepath_raw = str(shared_folder / 'ProductionIsland_StoppedAtlas_v001.png')
    stopped_atlas.file_format = 'PNG'
    stopped_atlas.save()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(folder/(name+'_v001.fbx')), use_selection=True,
        object_types={'EMPTY','MESH'}, axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
        bake_anim=False, add_leaf_bones=False, path_mode='AUTO')
    atlas.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(source/(name+'_v001.blend')))
    parts = [o.name for o in bpy.context.scene.objects if '_Anim' in o.name]
    record = dict(name=name, request=request, triangles=tris, footprint=footprint,
                  dimensions_blender=dims, moving_parts=parts, category=category)
    manifest.append(record)
    (folder/'IMPORT_README.md').write_text(
        f'# {name} v001\n\n依頼 ID: {request}。{tris} 三角形。1 単位 = 1m。足元中心が原点、Unity Y=0 が地面、正面 -Z。\n\n'
        '## 中身\n\n- FBX: 別メッシュの動く部品を含むモデル。\n- 共有アトラス: Assets/3Dmodel/ProductionIsland_v001/。1024×1024 の Base Map。Normal は不要。\n'
        f'- 編集用 .blend: ArtSource/{name}_v001/。\n\n'
        '## Unity\n\nProduction Island > Build Asset Pack を実行すると、URP Lit、稼働中・停止マテリアル、Prefab を作成します。'
        '色は各メッシュの UV でアトラスを参照します。停止は彩度の低い別マテリアルに切り替えます。\n\n'
        f'動く部品: {", ".join(parts) or "なし"}。ゲーム規則や自動配置は含みません。\n', encoding='utf-8')
    preview.append((name, folder/(name+'_v001.fbx')))
    # Keep shared material datablocks alive across scenes.
    for mat in MATS:
        mat.use_fake_user = True
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def terrain():
    for name,request,thick,color in [
        ('Tile_Ice_Core','T-01',.22,0), ('Tile_Ice_Expanded','T-01',.1,1),
        ('Tile_Ice_CrackSmall','T-02',.1,1), ('Tile_Ice_CrackLarge','T-02',.1,1),
        ('Tile_Ice_Sinking','T-02',.06,1), ('Tile_Sea','T-03',.035,2),
        ('Tile_Sea_Expandable','T-03',.035,2), ('Tile_Canal_OneBank','T-04',.035,3),
        ('Tile_Canal_TwoBanks','T-04',.035,3)]:
        box('Tile', (0,0,-thick/2), (1,1,thick), color, .018)
        if 'Core' in name:
            box('PermanentIceMark', (.36,-.35,.003), (.1,.1,.01),6,.006)
        if 'Crack' in name or 'Sinking' in name:
            for i in range(2 if 'Small' in name else 4):
                obj = box('Crack', ((i-1)*.15,(i%2)*.12,.002), (.26,.018,.008),3,0)
                obj.rotation_euler[2] = (i-1)*.6
        if 'Expandable' in name:
            for x in (-.47,.47):
                box('ExpansionRim', (x,0,.004), (.025,.92,.012),11,0)
        if 'Bank' in name:
            box('Bank', (0,.46,.03), (1,.08,.08),1,.01)
            if 'Two' in name:
                box('Bank', (0,-.46,.03), (1,.08,.08),1,.01)
        save(name,request,1,'terrain')
    for name in ('Straight','OuterCorner','InnerCorner'):
        box('ShoreLip',(0,.44,-.045),(1,.12,.09),0,.01)
        if name != 'Straight':
            box('ShoreLip',(.44,0,-.045),(.12,.76,.09),0,.01)
        if name == 'InnerCorner':
            box('InnerFill',(.35,.35,-.045),(.16,.16,.09),1,.01)
        save('Shore_'+name,'T-05',1,'terrain')
    for name in ('Fishing','Salt','Kelp'):
        cyl('Marker',(0,0,.012),.15,.024,4,12)
        if name == 'Fishing': fish((0,0,.06),.7)
        elif name == 'Salt': ball('SaltCrystal',(0,0,.08),(.06,.06,.06),6)
        else: kelp((0,0,.02),.5)
        save('Marker_'+name,'T-06',1,'terrain')


def building(kind, request, small=False):
    width = .88 if small else 1.86
    box('Foundation',(0,0,.045),(width,width,.09),0,.025)
    if kind in ('Fishery','Saltworks','KelpFarm'):
        box('WaterBasin',(0,.35,.11),(1.6,.8,.05),3)
        box('Pier',(0,-.3,.16),(1.6,.4,.12),12)
        for x in (-.65,.65):
            rod('PierPost',(x,-.45,.1),(x,-.45,.8),.04,12)
        if kind == 'Fishery':
            rod('NetBeam',(-.65,-.45,.76),(.65,-.45,.76),.035,12)
            box('Net_Anim',(0,-.4,.46),(1.1,.035,.36),5)
            for x in (-.4,-.2,0,.2,.4):
                rod('NetThread',(x,-.43,.28),(x,-.43,.64),.008,1)
            ball('Boat_Anim',(0,.4,.26),(.42,.18,.12),12)
            fish((0,.4,.35),1.6)
        elif kind == 'Saltworks':
            for x in (-.48,0,.48):
                box('SaltPan_Anim',(x,.28,.17),(.42,.62,.045),6)
                ball('SaltPile',(x,-.3,.3),(.16,.15,.12),6)
        else:
            for x in (-.5,0,.5): kelp((x,.4,.18),1.7,True)
            crate((.5,-.35,.32),.3)
        # Lighthouse-like store at rear keeps silhouette recognizable.
        box('Store',(-.55,-.55,.48),(.45,.5,.56),13)
        box('StoreRoof',(-.55,-.55,.8),(.55,.6,.08),3)
        rod('SignalMast',(.7,-.48,.1),(.7,-.48,1.1),.024,5)
        ball('SignalLamp',(.7,-.48,1.12),(.07,.07,.07),7)
    elif kind in ('Warehouse','Dormitory','Collection','Sorter'):
        if kind == 'Sorter':
            box('SortingTable',(0,0,.38),(.72,.68,.15),12)
            cyl('SortingPlate_Anim',(0,0,.49),.28,.05,7)
            rod('IconStand',(0,.25,.4),(0,.25,.82),.025,5)
            cyl('IconPlate',(0,.25,.83),.11,.02,2,rotation=(math.pi/2,0,0))
        elif kind == 'Collection':
            box('Tank',(-.14,0,.38),(.4,.6,.58),2)
            group=bpy.data.objects.new('Waterwheel_Anim',None)
            bpy.context.collection.objects.link(group); group.location=(.22,-.08,.4)
            wheel=cyl('Waterwheel',(.22,-.08,.4),.28,.1,12,12,(0,math.pi/2,0))
            wheel.parent=group; wheel.matrix_parent_inverse=group.matrix_world.inverted()
            for a in range(8):
                t=a*math.pi/4
                obj=box('WheelPaddle',(.22,math.sin(t)*.25-.08,math.cos(t)*.25+.4),(.14,.08,.1),13,0)
                obj.rotation_euler[0]=-t
                obj.parent=group; obj.matrix_parent_inverse=group.matrix_world.inverted()
        else:
            box('Walls',(0,.03,.4),(.67,.62,.62),13)
            roof(.86,.86,.94,3)
            box('Door_Anim',(0,-.29,.31),(.28,.045,.44),12)
            for x in (-.22,.22): box('Window',(x,-.295,.56),(.12,.025,.13),1)
            if kind == 'Dormitory':
                box('Chimney',(.2,.14,.95),(.1,.1,.1),5)
    elif kind == 'Drying':
        for x in (-.67,.67): rod('RackPost',(x,0,.1),(x,0,1.2),.045,12)
        rod('DryingBeam',(-.75,0,1.2),(.75,0,1.2),.045,12)
        box('DryingNet_Anim',(0,0,.77),(1.3,.025,.62),13,0)
        for i in range(5):
            fish(((i-2)*.25,-.07,.75),.85,True)
        crate((.48,-.5,.3),.34)
    elif kind == 'Power':
        box('Generator',(0,.15,.4),(.85,.78,.6),5)
        rod('WindTower',(0,.2,.6),(0,.2,1.17),.075,6)
        group=bpy.data.objects.new('WindRotor_Anim',None)
        bpy.context.collection.objects.link(group); group.location=(0,.08,1.15)
        hub=cyl('RotorHub',(0,.08,1.15),.1,.1,7,rotation=(math.pi/2,0,0))
        hub.parent=group; hub.matrix_parent_inverse=group.matrix_world.inverted()
        for i in range(4):
            t=i*math.pi/2
            obj=box('WindBlade',(math.sin(t)*.21,.05,1.15+math.cos(t)*.21),(.09,.045,.4),6,.018)
            obj.rotation_euler[1]=t
            obj.parent=group; obj.matrix_parent_inverse=group.matrix_world.inverted()
        box('Switchboard',(0,-.28,.5),(.45,.06,.2),3)
        for x in (-.13,0,.13): ball('StatusLight',(x,-.33,.5),(.04,.02,.04),10)
    else:
        # Open front workshops expose the production-specific station.
        box('BackWall',(0,.59,.64),(1.5,.1,1.04),13)
        for x in (-.72,.72): rod('Post',(x,-.52,.1),(x,-.52,1.13),.05,12)
        roof(1.8,1.5,1.4,3 if kind != 'Oden' else 9)
        box('Worktop',(0,-.3,.55),(1.38,.66,.13),12)
        if kind == 'Preparation':
            box('CuttingBoard',(0,-.3,.64),(.6,.4,.035),13)
            fish((-.12,-.3,.72),1.6)
            box('Knife_Anim',(.25,-.3,.81),(.035,.26,.2),5)
            box('KnifeHandle',(.25,-.3,.96),(.035,.13,.06),12)
        elif kind == 'Chikuwa':
            box('Oven',(0,-.28,.72),(.95,.5,.23),5)
            cyl('Grill_Anim',(0,-.3,.89),.065,.95,13,12,(0,math.pi/2,0))
            for x in (-.28,0,.28):
                cyl('Chikuwa',(x,-.3,.91),.095,.17,8,12,(0,math.pi/2,0))
            ball('FlameLow_Anim',(0,-.58,.76),(.2,.04,.09),8)
            ball('FlameHigh_Anim',(0,-.57,.83),(.25,.04,.17),9)
        elif kind == 'Kamaboko':
            cyl('Steamer',(0,-.25,.75),.3,.23,5,12)
            cyl('SteamerLid_Anim',(0,-.25,.88),.32,.04,6,12)
            cyl('LidHandle',(0,-.25,.93),.07,.065,12)
            for x in (-.45,.45): ball('Kamaboko',(x,-.35,.66),(.14,.08,.09),14)
        elif kind == 'Oden':
            box('Pot',(0,-.3,.72),(.85,.48,.2),5)
            box('Broth',(0,-.3,.83),(.72,.36,.015),7)
            for x in (-.22,0,.22): ball('OdenFood',(x,-.3,.86),(.08,.08,.045),13)
            box('Curtain_Anim',(0,-.7,1.04),(1.5,.03,.18),9)
            for x in (-.7,.7): cyl('Lantern',(x,-.64,.91),.085,.17,7)
        elif kind == 'Research':
            box('Desk',(0,-.2,.67),(.85,.44,.08),6)
            scope=cyl('Telescope_Anim',(0,-.2,.96),.12,.6,2,12,(0,.6,0))
            rod('Tripod',(0,-.2,.6),(0,-.2,.95),.035,5)
            ball('Lamp_Anim',(.48,-.2,.77),(.09,.09,.09),7)
        crate((-.5,.28,.3),.34)
    save('Building_'+kind+('_1x1' if small else '_2x2'),request,1 if small else 2,'building')


def harbors():
    for stage in range(6):
        if stage > 0: box('StoneFoundation',(0,0,.15),(1.86,1.86,.3),5)
        if stage != 1:
            for x in (-.72,.72):
                for y in (-.65,.65):
                    rod('Post',(x,y,0 if stage==0 else .3),(x,y,.4 if stage==0 else 1.16),.045,12)
        if stage==0:
            for y in (-.65,.65): rod('Rope',(-.72,y,.35),(.72,y,.35),.012,13)
        if stage>=2:
            for y in (-.65,.65): rod('Beam',(-.78,y,1.13),(.78,y,1.13),.055,12)
        if stage>=3: roof(1.85,1.8,1.43)
        if stage>=4:
            for x in (-.57,0,.57): cyl('Lantern_Anim',(x,-.71,1.02),.09,.19,7)
        if stage>=5:
            box('FestivalCounter',(0,-.46,.58),(1.4,.48,.14),12)
            box('OdenPot',(0,-.46,.73),(.68,.36,.16),5)
            box('OdenBroth',(0,-.46,.82),(.57,.26,.01),7,0)
            rod('BannerPost',(.79,.12,.3),(.79,.12,1.5),.018,5)
            box('FestivalBanner',(.68,.12,1.32),(.22,.025,.3),9)
        if stage >= 2: crate((.4,.33,.47),.28)
        save('Harbor_Stage'+str(stage),'B-03 / H-0'+str(stage),2,'building')


def items():
    for name,req in [('Pearl','I-05'),('Fish','I-06'),('Surimi','I-07'),('Salt','I-08'),
                     ('Kelp','I-09'),('Kamaboko','I-10'),('Chikuwa','I-11'),('DriedFish','I-12'),('Oden','I-13')]:
        if name in ('Fish','DriedFish'): fish((0,0,.045),.75,name=='DriedFish')
        elif name=='Pearl':
            ball('Shell',(0,0,.028),(.095,.08,.028),14)
            ball('Pearl',(0,0,.068),(.045,)*3,6)
        elif name=='Surimi':
            cyl('Bowl',(0,0,.035),.085,.055,5)
            ball('Surimi',(0,0,.072),(.075,.07,.025),6)
        elif name=='Salt':
            ball('SaltBag',(0,0,.08),(.075,.06,.08),6)
            cyl('BagTie',(0,0,.145),.025,.018,12)
        elif name=='Kelp': kelp((0,0,0),.7)
        elif name=='Kamaboko':
            box('Board',(0,0,.012),(.19,.12,.024),13,.005)
            ball('Kamaboko',(0,0,.04),(.085,.045,.055),14)
            ball('CutFace',(.05,-.002,.042),(.035,.046,.046),6)
        elif name=='Chikuwa':
            verts=[]; faces=[]
            for x,radius in ((-.09,.04),(.09,.04),(-.09,.018),(.09,.018)):
                for i in range(12):
                    angle=i*math.tau/12
                    verts.append((x,math.sin(angle)*radius,.04+math.cos(angle)*radius))
            for i in range(12):
                j=(i+1)%12
                faces.extend([(i,j,j+12,i+12),(i+24,i+36,j+36,j+24),
                              (i,i+24,j+24,j),(i+12,j+12,j+36,i+36)])
            mesh=bpy.data.meshes.new('HollowChikuwa'); mesh.from_pydata(verts,[],faces)
            obj=bpy.data.objects.new('Chikuwa',mesh); bpy.context.collection.objects.link(obj)
            finish(obj,'Chikuwa',8)
        elif name=='Oden':
            rod('Skewer',(0,0,0),(0,0,.2),.005,12)
            for z,c in ((.04,13),(.1,7),(.16,12)): ball('OdenFood',(0,0,z),(.045,.035,.027),c)
        save('Item_'+name,req,1,'item')
    for name,color in [('Normal',2),('Blocked',9)]:
        mesh=bpy.data.meshes.new('Arrow')
        mesh.from_pydata([(-.08,-.08,0),(.08,-.08,0),(0,.1,0),(-.08,-.08,.025),(.08,-.08,.025),(0,.1,.025)],[],
                        [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
        obj=bpy.data.objects.new('Arrowhead',mesh); bpy.context.collection.objects.link(obj); finish(obj,'Arrowhead',color)
        save('Link_Arrow_'+name,'L-02',1,'link')
    for direction in ('Input','Output'):
        for state,color in [('Free',5),('Connected',10),('Selectable',7)]:
            cyl('PortDisc',(0,0,.015),.07,.03,color,12)
            box('PortDirection',(0,-.01,.034),(.018,.065,.008),6,0)
            box('PortDirection',(-.014 if direction=='Input' else .014,.015,.034),(.042,.018,.008),6,0)
            save('Link_Port_'+direction+'_'+state,'L-03',1,'link')


def render_contact_sheet():
    reset()
    for index,(name,path) in enumerate(preview):
        before=set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
        imported=set(bpy.data.objects)-before
        bpy.context.view_layer.update()
        meshes=[o for o in imported if o.type=='MESH']
        bounds=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
        record=next(record for record in manifest if record['name']==name)
        record['dimensions_blender']=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
        roots=[o for o in imported if o.parent is None]
        col=8-index%9; row=index//9
        for root in roots: root.location += Vector((col*2.5,row*4.0,0))
        bpy.ops.object.text_add(location=(col*2.5+1.0,row*4.0+1.3,.02),rotation=(0,0,math.pi))
        text=bpy.context.object; text.data.body=name.replace('Building_','').replace('Tile_','').replace('Link_','')
        text.data.size=.16; text.data.extrude=0
        mat=bpy.data.materials.get('Label')
        if not mat: mat=bpy.data.materials.new('Label'); mat.diffuse_color=(.04,.1,.17,1)
        text.data.materials.append(mat)
    box('Backdrop',(10,9,-.35),(50,50,.15),0,.01)
    scene=bpy.context.scene
    scene.render.engine='CYCLES'; scene.cycles.samples=6; scene.cycles.use_denoising=True
    scene.world.use_nodes=True
    background=scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value=(.75,.85,1,1)
    background.inputs['Strength'].default_value=.65
    bpy.ops.object.light_add(type='AREA',location=(7,14,20))
    bpy.context.object.data.energy=2600; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=18
    bpy.ops.object.camera_add(location=(10,35,32))
    camera=bpy.context.object; target=Vector((10,10,0)); camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale=27; scene.camera=camera
    scene.render.resolution_x=2100; scene.render.resolution_y=1800; scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard'
    scene.render.filepath=str(SOURCE/'ProductionIsland_v001/Model_ContactSheet.png')
    bpy.ops.render.render(write_still=True)
    (SOURCE/'ProductionIsland_v001/model-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


if '--render-only' in sys.argv:
    manifest=json.loads((SOURCE/'ProductionIsland_v001/model-manifest.json').read_text(encoding='utf-8'))
    preview=[(record['name'],OUT/(record['name']+'_v001')/(record['name']+'_v001.fbx')) for record in manifest]
else:
    terrain()
    for args in [('Fishery','B-01'),('Warehouse','B-02',True),('Preparation','B-04'),
                 ('Chikuwa','B-05'),('Kamaboko','B-06'),('Saltworks','B-07'),
                 ('Drying','B-08'),('KelpFarm','B-09'),('Oden','B-10'),('Power','B-11'),
                 ('Research','B-12'),('Collection','B-13',True),('Dormitory','B-14',True),('Sorter','B-15',True)]:
        building(*args)
    harbors()
    items()
    (SOURCE/'ProductionIsland_v001/model-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if '--skip-render' not in sys.argv: render_contact_sheet()
