"""Blender 4.3: purpose-readable v002 facilities, independent of approved Kamaboko.

Moving assemblies retain pivots; fixed meshes and each item are merged with atlas UVs.
Existing Penguin_v002 is composed in Unity, never regenerated here.
"""
from pathlib import Path
import bpy
import math
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
helpers = (ROOT / 'ArtSource/ProductionIsland_v001/generate_models.py').read_text(encoding='utf-8').split('def terrain():')[0]
exec(compile(helpers.replace('_v001', '_v002'), '<v002 helpers>', 'exec'))
REVIEW = ROOT / 'ArtSource/ProductionIsland_v002/Facilities'
REVIEW.mkdir(parents=True, exist_ok=True)
records = []


def empty(name, pos):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    return obj


def assembly(name, pos, make, parent=None):
    before = set(bpy.context.scene.objects)
    pivot = empty(name, pos)
    make()
    for obj in set(bpy.context.scene.objects) - before - {pivot}:
        if obj.parent is None:
            obj.parent = pivot
    if parent:
        # pos is relative to the parent; generated parts are relative to this pivot.
        pivot.parent = parent
    return pivot


def profile(name, points, y, depth, color):
    """Closed front-facing icon extruded through Y, points counterclockwise in X/Z."""
    n = len(points)
    verts = [(x, y + d, z) for d in (-depth/2, depth/2) for x, z in points]
    faces = [tuple(range(n)), tuple(reversed(range(n, n*2)))]
    faces += [(i, n+i, n+(i+1)%n, (i+1)%n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, color)


def fish_icon(name, x, y, z, size, dried=False):
    outline = [(-.5, -.2), (-.30, -.11), (-.17, -.23), (.13, -.23),
               (.45, 0), (.13, .23), (-.17, .23), (-.30, .11), (-.5, .2)]
    profile(name, [(x+a*size, z+b*size) for a,b in outline], y, .09, 8 if dried else 2)
    ball(name+'Eye', (x+.23*size, y-.055, z+.04*size), (.024, .016, .024), 4)
    if dried:
        rod(name+'Spine', (x-.2*size, y-.057, z), (x+.25*size, y-.057, z), .012, 13)
        for dx in (-.1, .03, .16):
            rod(name+'Bone', (x+dx*size, y-.057, z-.12*size), (x+dx*size, y-.057, z+.12*size), .008, 13)


def tube(name, loc, radius, length, cooked=True):
    # Real through-hole, cream ends and a browned middle. Axis along Y.
    x,y,z = loc
    steps = 12
    inner = radius*.43
    verts = [(x+r*math.cos(i*math.tau/steps), y+dy, z+r*math.sin(i*math.tau/steps))
             for dy in (-length/2, -length*.29, length*.29, length/2)
             for r in (radius, inner) for i in range(steps)]
    faces, colors = [], []
    for layer in range(3):
        a, b = layer*24, (layer+1)*24
        for i in range(steps):
            j=(i+1)%steps
            faces += [(a+i,b+i,b+j,a+j), (a+12+j,b+12+j,b+12+i,a+12+i)]
            colors += [12 if cooked and layer==1 else 13 if cooked else 6, 6]
    for start, reverse in ((0,False),(72,True)):
        for i in range(steps):
            j=(i+1)%steps
            face=(start+i,start+j,start+12+j,start+12+i)
            faces.append(tuple(reversed(face)) if reverse else face)
            colors.append(6)
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    finish(obj,name,6)
    uv=obj.data.uv_layers.active
    for poly,color in zip(mesh.polygons,colors):
        for loop in poly.loop_indices:
            uv.data[loop].uv=((color%4+.5)/4,(color//4+.5)/4)
    return obj


def leaf(name, loc, size=.3):
    x,y,z=loc
    points=[(x,z),(x+size*.38,z+size*.18),(x+size*.18,z+size*.36),
            (x+size*.40,z+size*.6),(x+size*.13,z+size*.81),(x,z+size),
            (x-size*.17,z+size*.78),(x-size*.35,z+size*.58),
            (x-size*.13,z+size*.35),(x-size*.30,z+size*.15)]
    profile(name,points,y,.035,10)
    rod(name+'Vein',(x,y-.023,z+.06),(x,y-.023,z+size*.85),.01,11)


def crystal(name, loc, size=.12):
    obj=box(name,loc,(size,size,size),6,.012)
    obj.rotation_euler=(.15,.25,.3)


def loaf(name, loc=(0,0,0), size=.16):
    x,y,z=loc
    n=10
    points=[(x+size*math.cos(i*math.pi/n), z+size*math.sin(i*math.pi/n)) for i in range(n+1)]
    profile(name+'Pink',points,y,size*1.6,14)
    points=[(x+size*.80*math.cos(i*math.pi/n),z+size*.80*math.sin(i*math.pi/n)) for i in range(n+1)]
    profile(name+'White',points,y-size*.81,.008,6)
    box(name+'Board',(x,y,z-.015),(size*2+.04,size*1.6+.04,.025),12,.006)


def oden(name, loc=(0,0,0), size=1):
    x,y,z=loc
    rod(name+'Stick',(x,y,z-.02),(x,y,z+.4*size),.012*size,12)
    ball(name+'Round',(x,y,z+.09*size),(.085*size,.07*size,.07*size),13)
    cyl(name+'Daikon',(x,y,z+.22*size),.08*size,.08*size,7,10)
    profile(name+'Triangle',[(x-.1*size,z+.30*size),(x+.1*size,z+.30*size),(x,z+.43*size)],y,.1*size,13)


def bowl(name, loc=(0,0,0), size=1, content=6):
    x,y,z=loc
    cyl(name+'Bowl',(x,y,z),.13*size,.08*size,5,10)
    for dx,dy in ((0,0),(-.05,.025),(.045,.025)):
        ball(name+'Paste',(x+dx*size,y+dy*size,z+.05*size),(.08*size,.065*size,.045*size),content)


def cargo(name, loc=(0,0,0), size=.27):
    crate(loc,size)
    x,y,z=loc
    box(name+'Label',(x,y-size*.52,z),(.12,.012,.10),1,.004)


def paper(name, loc=(0,0,0), stamped=False):
    x,y,z=loc
    box(name,(x,y,z),(.30,.23,.025),1 if stamped else 6,.008)
    for dy in (-.04,.03): box(name+'Line',(x,y+dy,z+.015),(.19,.013,.006),3,0)
    if stamped: ball(name+'Seal',(x+.09,y-.06,z+.02),(.035,.035,.009),10)


def base(small=False, color=2):
    width=.88 if small else 1.86
    box('Foundation',(0,0,.045),(width,width,.09),0,.02)
    box('AccentRim',(0,0,.1),(width-.05,width-.05,.035),color,.008)
    box('WorkshopFloor',(0,0,.13),(width-.13,width-.13,.025),6,.005)


def frontage(color, small=False):
    if small: return
    for x in (-.58,.58): box('BackPillar',(x,.60,.64),(.075,.075,1.0),12,.008)
    box('BackPanel',(0,.72,.57),(1.26,.045,.82),11,.008)
    box('EmblemShelf',(0,.44,1.02),(1.50,.60,.065),color,.012)


def tables(color, small=False):
    span=.29 if small else .64
    y=-.26 if small else -.4
    height=.30 if small else .50
    size=.25 if small else .43
    for x,name,tint in ((-span,'Input',2),(span,'Output',color)):
        box(name+'Table',(x,y,height-.045),(size,.36 if small else .46,.07),tint,.01)
        box(name+'Tray',(x,y,height),(size-.04,.32 if small else .4,.02),6,.004)
        box(name+'Leg',(x,y,height*.5),(.07,.07,height-.1),12,.008)
    return span,y,height


def recipe(input_make, raw_make, done_make, output_make, small=False, tool=None, center_z=.60, y=-.4):
    span=.29 if small else .64
    z=.36 if small else .60
    assembly('InputItem',(-span,y,z),input_make)
    assembly('OutputItem',(span,y,z),output_make)
    assembly('ProcessRaw',(0,0,0) if tool else (0,y,center_z),raw_make,parent=tool)
    assembly('ProcessFinished',(0,0,0) if tool else (0,y,center_z),done_make,parent=tool)
    empty('ProcessCenter',(0,y,center_z))
    empty('WorkerStand',(0,0,.14))


def fixed_merge():
    # UVs already encode each palette color; all groups can use one atlas material.
    buckets={}
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH':
            # Blender joins UV layers by name. Keep icons and primitive UVs in the same channel.
            obj.data.uv_layers.active.name='AtlasUV'
            buckets.setdefault(obj.parent,[]).append(obj)
    for parent, objects in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1: bpy.ops.object.join()
        obj=bpy.context.object
        obj.name='FixedShell' if parent is None else parent.name+'Mesh'
        obj.data.materials.clear();obj.data.materials.append(MATS[0])
        for poly in obj.data.polygons: poly.material_index=0


def deliver(kind, request, small=False, stage=-1):
    fixed_merge()
    name='Harbor_Stage'+str(stage) if stage>=0 else 'Building_'+kind+('_1x1' if small else '_2x2')
    save(name,request,1 if small else 2,'building')
    record=manifest[-1]
    record.update(kind=kind,stage=stage,small=small)
    records.append(record)
    folder=OUT/(name+'_v002')
    (folder/'IMPORT_README.md').write_text(
        f'# {name} v002\n\n{record["triangles"]}三角形。既存かまぼこ工場に合わせた用途の目印と、工程が見える施設。\n\n'
        'FBXは固定部品と工程ごとの可動グループを結合済み。1枚のカラーアトラスを共用する。'
        'Unityの Production Island > Build Facility Design Revisions で材質・Prefab・レビューシーンを生成する。'
        'ペンギンは既存Penguin_v002を使用する。元のモデルは変更しない。\n\n'
        f'制作元：ArtSource/{name}_v002/{name}_v002.blend。生成コード：ArtSource/ProductionIsland_v002/generate_facilities.py。\n'
        '生産・増幅・在庫のゲーム計算は含まない。表示専用の工程ループ。停止/再開に対応。\n',encoding='utf-8')


def build(kind):
    small=kind in ('Warehouse','Dormitory','Sorter')
    accents={'Fishery':2,'Preparation':11,'Chikuwa':8,'Saltworks':1,'Drying':8,'KelpFarm':10,
             'Oden':9,'Research':3,'Warehouse':12,'Dormitory':14,'Sorter':7,
             'ElectricAmplifier':7,'WaterAmplifier':2,'GasAmplifier':8}
    color=accents[kind]
    base(small,color)
    if not small: frontage(color)
    if kind not in ('Dormitory',): tables(color,small)
    if kind=='Fishery':
        fish_icon('FishRoof',0,.34,1.31,1.27)
        box('SeaPool',(0,-.34,.22),(1.08,.50,.08),2,.015)
        for x in (-.42,.42): box('NetPost',(x,-.1,.68),(.055,.055,1.0),12,.006)
        tool=empty('WorkingPart',(0,-.4,.39))
        assembly('NetBasket',(0,0,0),lambda:net_basket(),parent=tool)
        recipe(lambda:fish((0,0,0),1.2),lambda:fish((0,0,.01),1.2),
               lambda:fish((0,0,.08),1.2),lambda:(cargo('FishCrate',(0,0,-.06),.22),fish((0,0,.08),1.1)),tool=tool,center_z=.45)
        bpy.data.objects['InputItem'].location=(-.24,-.34,.30)
    elif kind=='Preparation':
        bowl('GiantPaste',(0,.40,1.17),2.05)
        profile('KnifeRoof',[(-.6,1.08),(-.50,1.08),(-.50,1.44),(-.6,1.44)],.29,.06,5)
        box('KnifeGrip',(-.55,.29,1.48),(.13,.09,.19),12,.005)
        box('CuttingCounter',(0,-.4,.46),(.58,.50,.14),12,.012)
        box('CuttingBoard',(0,-.4,.55),(.52,.43,.025),13,.006)
        assembly('WorkingPart',(.14,-.4,.71),lambda:(box('Blade',(0,0,0),(.035,.26,.16),5,.003),box('Grip',(0,0,.12),(.055,.12,.10),12,.008)))
        assembly('SecondaryTool',(0,-.4,.69),lambda:(rod('MixingStick',(0,0,-.05),(0,0,.18),.018,12),ball('MixerTip',(0,0,-.06),(.045,.04,.03),5)))
        recipe(lambda:fish((0,0,0),1.3),lambda:fish((0,0,0),1.3),lambda:bowl('Paste'),lambda:bowl('Paste'))
    elif kind=='Chikuwa':
        tube('ChikuwaRoof',(0,.42,1.24),.32,.75)
        box('GrillBody',(0,-.4,.43),(.64,.52,.23),5,.015)
        for x in (-.27,.27): box('SpitBracket',(x,-.4,.61),(.04,.30,.25),12,.006)
        tool=assembly('WorkingPart',(0,-.4,.67),lambda:rod('Spit',(-.34,0,0),(.34,0,0),.024,5))
        def on_spit(cooked):
            t=tube('GrillingTube',(0,0,0),.11,.35,cooked);t.rotation_euler.z=math.pi/2
        recipe(lambda:bowl('Paste'),lambda:on_spit(False),lambda:on_spit(True),lambda:tube('Finished',(0,0,0),.11,.35),tool=tool,center_z=.67)
        assembly('EffectPart',(0,-.67,.45),lambda:(ball('Fire',(0,0,0),(.16,.026,.10),8),ball('Core',(0,-.008,-.03),(.09,.02,.045),7)))
    elif kind=='Saltworks':
        for x,s in ((-.38,.25),(0,.40),(.38,.25)): crystal('SaltRoof',(x,.4,1.20),s)
        box('SaltPan',(0,-.4,.45),(.56,.46,.10),1,.01)
        assembly('WorkingPart',(.15,-.4,.63),lambda:(rod('RakeHandle',(0,0,0),(0,0,.25),.025,12),box('Rake',(0,-.03,-.04),(.3,.035,.035),5,.002)))
        recipe(lambda:cyl('SeaWater',(0,0,0),.13,.025,2),lambda:cyl('Water',(0,0,-.07),.20,.025,2),
               lambda:[crystal('Salt',(x,0,0),.09) for x in (-.10,0,.1)],
               lambda:(ball('SaltBag',(0,0,0),(.13,.10,.13),6),box('BlueLabel',(0,-.10,0),(.09,.01,.07),2,.005)))
    elif kind=='Drying':
        fish_icon('DriedFishRoof',0,.34,1.27,1.22,True)
        for x in (-.35,.35): box('RackSupport',(x,-.16,.58),(.05,.05,.9),12,.006)
        tool=empty('WorkingPart',(0,-.35,.83))
        assembly('DryingMesh',(0,0,0),lambda:drying_mesh(),parent=tool)
        def rack_fish(dried):
            for x in (-.23,0,.23): fish_icon('RackFish',x,-.025,0,.25,dried)
        recipe(lambda:(fish((0,0,0),1.15),crystal('Salt',(0,.09,.06),.06)),lambda:rack_fish(False),lambda:rack_fish(True),
               lambda:fish((0,0,0),1.35,True),tool=tool,center_z=.83)
    elif kind=='KelpFarm':
        for x,z,s in ((-.35,1.04,.46),(0,1.0,.57),(.35,1.06,.43)): leaf('KelpRoof',(x,.35,z),s)
        box('SeaBed',(0,-.4,.36),(.62,.48,.08),2,.01)
        assembly('WorkingPart',(.15,-.38,.72),lambda:(rod('HarvestPole',(0,0,-.22),(0,0,.25),.022,12),rod('HookLeft',(0,0,-.22),(-.08,0,-.12),.015,5),rod('HookRight',(0,0,-.22),(.08,0,-.12),.015,5)))
        recipe(lambda:leaf('Harvest',(0,0,-.05),.27),lambda:[leaf('Growing',(x,0,-.17),.34) for x in (-.14,0,.14)],
               lambda:[leaf('Cut',(x,0,-.07),.22) for x in (-.10,0,.10)],
               lambda:(leaf('Bundle',(-.06,0,-.07),.25),leaf('Bundle',(.05,.03,-.07),.25),box('Tie',(0,-.03,.03),(.21,.02,.045),13,.004)))
    elif kind=='Oden':
        oden('OdenRoof',(0,.42,1.06),1.08)
        for x in (-.58,.58):
            cyl('RedLantern',(x,.10,.88),.095,.19,9,10)
            for z in (.78,.98): cyl('LanternBand',(x,.10,z),.098,.02,4,10)
            rod('LanternString',(x,.10,.98),(x,.10,1.04),.009,12)
        box('Pot',(0,-.4,.50),(.58,.50,.18),5,.02)
        box('GoldenBroth',(0,-.4,.60),(.49,.40,.018),7,.006)
        assembly('WorkingPart',(.20,-.37,.76),lambda:(rod('LadleStem',(0,0,0),(0,0,.22),.018,12),ball('Ladle',(0,0,-.06),(.07,.06,.035),5)))
        def ingredients():
            loaf('Pink',(-.11,0,0),.08);tube('Chikuwa',(.1,0,.05),.055,.17);leaf('Kelp',(0,.05,0),.15)
        recipe(ingredients,ingredients,lambda:oden('Simmered',(0,0,-.07),.67),lambda:oden('Ready',(0,0,-.06),.72),center_z=.64)
        assembly('EffectPart',(0,-.4,.90),lambda:[ball('Steam',(x,0,z),(.05,.05,.075),6) for x,z in ((-.1,0),(0,.12),(.1,.05))])
    elif kind=='Research':
        ring_icon('Magnifier',0,.38,1.34,.25,3)
        rod('MagnifierGrip',(.16,.38,1.12),(.40,.38,1.00),.052,12)
        box('Desk',(0,-.4,.48),(.58,.48,.13),3,.012)
        paper('OpenNotes',(0,-.4,.56))
        assembly('WorkingPart',(0,-.4,.84),lambda:(ring_icon('Lens',0,0,0,.13,3),rod('LensHandle',(.08,0,-.09),(.18,0,-.18),.024,12)))
        recipe(lambda:paper('Blank'),lambda:paper('Study'),lambda:paper('Recipe',stamped=True),lambda:paper('Blueprint',stamped=True))
        assembly('EffectPart',(.26,-.12,.88),lambda:ball('IdeaLamp',(0,0,0),(.06,.06,.08),7))
        assembly('SecondaryTool',(.12,-.4,.76),lambda:(cyl('StampBase',(0,0,-.04),.055,.025,9,10),rod('StampStem',(0,0,-.025),(0,0,.06),.018,12),ball('StampHandle',(0,0,.09),(.06,.045,.04),12)))
        rod('LampStand',(.26,-.12,.58),(.26,-.12,.82),.015,5)
    elif kind=='Warehouse':
        box('WarehouseBack',(0,.31,.42),(.72,.08,.56),13,.01)
        for x in (-.35,.35): box('SideWall',(x,.13,.42),(.05,.35,.56),12,.008)
        cargo('CrateRoof',(0,.08,.78),.42)
        for z in (.23,.46): box('StorageShelf',(0,.16,z),(.62,.32,.035),12,.005)
        assembly('WorkingPart',(-.31,-.08,.43),lambda:box('Door',(.15,0,0),(.31,.035,.47),12,.008))
        assembly('SecondaryTool',(0,-.10,.27),lambda:box('LiftTray',(0,0,0),(.24,.20,.035),5,.004))
        recipe(lambda:cargo('Arrival',size=.16),lambda:cargo('Stored',size=.16),lambda:cargo('Stock',size=.16),lambda:cargo('Dispatch',size=.16),small=True,center_z=.37,y=-.13)
    elif kind=='Sorter':
        box('BinShelf',(0,.17,.53),(.75,.28,.045),12,.006)
        for x in (-.34,.34): box('ShelfSupport',(x,.20,.33),(.045,.045,.40),12,.006)
        box('TurntableStand',(0,-.1,.26),(.12,.12,.22),12,.008)
        for x,tint in ((-.25,2),(0,10),(.25,8)): box('SortRoofBin',(x,.17,.63),(.18,.21,.18),tint,.008)
        rod('RouteMark',(0,.1,.73),(0,.1,.9),.022,5)
        for x in (-.23,.23): rod('ForkArrow',(0,.1,.85),(x,.1,.91),.015,5)
        cyl('Turntable',(0,-.1,.38),.20,.045,13,10)
        assembly('WorkingPart',(0,-.1,.42),lambda:box('Diverter',(0,0,0),(.33,.025,.065),5,.003))
        for i,x in enumerate((-.25,0,.25)): empty('Route'+str(i),(x,.10 if i!=1 else .21,.44))
        recipe(lambda:fish((0,0,0),.7),lambda:fish((0,0,0),.7),lambda:fish((0,0,0),.7),lambda:fish((0,0,0),.7),small=True,center_z=.47,y=-.13)
    elif kind=='Dormitory':
        box('CabinBack',(0,.29,.38),(.73,.07,.48),13,.01)
        for x in (-.34,.34): box('CabinSide',(x,.1,.38),(.055,.4,.48),14,.008)
        roof(.86,.7,.86,14)
        box('PillowEmblem',(0,-.05,.91),(.43,.25,.16),6,.025)
        box('BedFrame',(0,-.10,.27),(.38,.49,.08),12,.01)
        box('Pillow',(0,.08,.33),(.29,.13,.05),6,.01)
        assembly('WorkingPart',(0,-.13,.33),lambda:box('Blanket',(0,0,0),(.31,.28,.035),14,.008))
        assembly('EffectPart',(.22,.24,.52),lambda:box('WarmWindow',(0,0,0),(.15,.012,.17),7,.008))
        recipe(lambda:None,lambda:None,lambda:None,lambda:None,small=True,center_z=.4,y=-.12)
    else:
        # Amplify externally earned resources; no generator / pump / fuel production.
        if kind=='ElectricAmplifier':
            profile('BoltRoof',[(-.1,1.01),(.27,1.32),(.08,1.32),(.2,1.55),(-.25,1.23),(-.04,1.23)],.38,.14,7)
            box('Battery',(0,-.4,.51),(.49,.41,.53),4,.02)
            for i,z in enumerate((.37,.48,.59)):
                box('ChargeSlot',(0,-.62,z),(.27,.018,.055),5,.004)
                assembly('Charge'+str(i),(0,-.636,z),lambda:box('ChargeLight',(0,0,0),(.23,.012,.035),7,.003))
            assembly('SecondaryTool',(.25,-.4,.52),lambda:box('ChargeSwitch',(0,0,0),(.07,.09,.14),9,.008))
        elif kind=='WaterAmplifier':
            droplet('DropRoof',(0,.38,1.28),.29)
            cyl('Reservoir',(0,-.4,.45),.25,.40,1,12)
            cyl('Water',(0,-.4,.655),.21,.018,2,12)
            box('LevelWindow',(0,-.655,.45),(.28,.028,.31),5,.008)
            assembly('FluidLevel',(0,-.675,.45),lambda:box('Level',(0,0,0),(.23,.012,.27),2,.004))
            assembly('SecondaryTool',(.22,-.4,.68),lambda:(ball('Float',(0,0,0),(.05,.05,.045),7),rod('FloatRod',(0,0,0),(0,0,.1),.012,5)))
        else:
            flame('GasRoof',(0,.38,1.04),.48)
            for x in (-.14,.14): cyl('GasTank',(x,-.4,.47),.12,.49,13,10)
            rod('Pipe',(-.14,-.4,.76),(.14,-.4,.76),.025,5)
            assembly('SecondaryTool',(0,-.4,.81),lambda:(cyl('ValveWheel',(0,0,0),.12,.025,9,10),rod('ValveSpoke',(-.13,0,.02),(.13,0,.02),.012,6)))
        cyl('Meter',(0,-.64,.70),.115,.035,6,12,(math.pi/2,0,0))
        assembly('WorkingPart',(0,-.64,.70),lambda:rod('Needle',(0,-.024,0),(.07,-.024,.04),.008,9))
        def token(many=False):
            for x in ((-.09,0,.09) if many else (0,)):
                if kind=='WaterAmplifier': droplet('EarnedDrop',(x,0,0),.055)
                elif kind=='ElectricAmplifier': box('EarnedCharge',(x,0,0),(.045,.045,.12),7,.006)
                else: flame('EarnedGas',(x,0,-.05),.12)
        recipe(lambda:token(),lambda:token(),lambda:token(True),lambda:token(True))
    req={'Fishery':'B-01','Warehouse':'B-02','Preparation':'B-04','Chikuwa':'B-05','Saltworks':'B-07',
         'Drying':'B-08','KelpFarm':'B-09','Oden':'B-10','Research':'B-12','Dormitory':'B-14','Sorter':'B-15',
         'ElectricAmplifier':'A-01','WaterAmplifier':'A-02','GasAmplifier':'A-03'}[kind]
    deliver(kind,req,small)


def net_basket():
    for x in (-.28,0,.28): rod('NetThread',(x,-.19,0),(x,.19,0),.008,6)
    for y in (-.19,0,.19): rod('NetThread',(-.28,y,0),(.28,y,0),.008,6)
    for x in (-.28,.28): rod('NetRope',(x,0,0),(x,0,.4),.012,13)
    rod('NetBeam',(-.30,0,.4),(.30,0,.4),.021,12)


def drying_mesh():
    for x in (-.37,.37): rod('Frame',(x,0,-.20),(x,0,.20),.015,12)
    for z in (-.20,.20): rod('Frame',(-.37,0,z),(.37,0,z),.015,12)
    for x in (-.24,-.12,0,.12,.24): rod('MeshThread',(x,0,-.2),(x,0,.2),.004,5)
    for z in (-.1,0,.1): rod('MeshThread',(-.37,0,z),(.37,0,z),.004,5)


def ring_icon(name,x,y,z,radius,color):
    tube_obj=tube(name,(x,y,z),radius,.045)
    # Preserve the hole, recolor all faces as the icon frame.
    uv=tube_obj.data.uv_layers.active
    for loop in uv.data: loop.uv=((color%4+.5)/4,(color//4+.5)/4)


def droplet(name,loc,size):
    x,y,z=loc
    profile(name,[(x-size*.55,z-size*.35),(x,z-size*.58),(x+size*.55,z-size*.35),
                  (x+size*.62,z+size*.07),(x,z+size),(x-size*.62,z+size*.07)],y,.09,2)


def flame(name,loc,size):
    x,y,z=loc
    profile(name,[(x-size*.32,z),(x+size*.32,z),(x+size*.43,z+size*.32),(x+size*.05,z+size),
                  (x-size*.05,z+size*.45),(x-size*.30,z+size*.72),(x-size*.43,z+size*.32)],y,.08,8)


def harbor(stage):
    base(False,3)
    box('HarborWater',(0,.47,.15),(1.7,.75,.035),2,.005)
    box('Dock',(0,-.28,.22),(1.70,.62,.14),12,.01)
    if stage==0:
        for x in (-.7,.7): rod('Stake',(x,-.35,.14),(x,-.35,.55),.025,12)
        rod('Boundary',(-.7,-.35,.49),(.7,-.35,.49),.008,13)
    if stage>=1: box('StoneBase',(0,.10,.30 if stage==1 else .23),(1.30,.55,.16 if stage==1 else .10),5,.015)
    if stage>=2:
        for x in (-.59,.59): box('Post',(x,.3,.72),(.075,.075,.93),12,.008)
        rod('Beam',(-.64,.3,1.18),(.64,.3,1.18),.035,12)
    if stage>=3:
        roof(1.6,.64,1.35,3)
        # Giant anchor under the roof makes this clearly a port.
        ring_icon('AnchorRing',0,-.37,1.40,.065,6)
        rod('AnchorStem',(0,-.37,1.37),(0,-.37,1.10),.025,6)
        rod('AnchorCross',(-.11,-.37,1.29),(.11,-.37,1.29),.018,6)
        for sign in (-1,1):
            rod('AnchorHook',(0,-.37,1.10),(sign*.17,-.37,1.18),.022,6)
    if stage>=4:
        assembly('EffectPart',(0,.13,1.06),lambda:[cyl('Lamp',(x,0,0),.06,.14,7,8) for x in (-.4,.4)])
    if stage==5:
        for x in (-.72,.72):
            box('FestivalFlag',(x,.09,1.17),(.18,.025,.34),9,.005)
            rod('FlagPole',(x,.12,.23),(x,.12,1.40),.016,12)
        assembly('WorkingPart',(-.48,.62,.26),lambda:(ball('Hull',(0,0,0),(.14,.20,.075),12),box('BoatCabin',(0,0,.10),(.15,.15,.16),6,.01),rod('BoatMast',(0,0,.18),(0,0,.46),.015,5)))
        rod('HoistPost',(-.37,-.10,.28),(-.37,-.10,1.08),.025,5)
        rod('HoistArm',(-.37,-.10,1.08),(0,-.4,1.08),.025,5)
        assembly('SecondaryTool',(0,-.4,.85),lambda:(rod('HoistRope',(0,0,0),(0,0,.21),.009,13),rod('Hook',(0,0,0),(.035,0,-.055),.015,5)))
        tables(3)
        recipe(lambda:cargo('Delivery',size=.22),lambda:cargo('Loading',size=.22),lambda:cargo('Loaded',size=.22),lambda:cargo('Delivered',size=.22),center_z=.60)
    deliver('Harbor','B-03 / H-0'+str(stage),stage=stage)


for kind in ('Fishery','Preparation','Chikuwa','Saltworks','Drying','KelpFarm','Oden',
             'Warehouse','Sorter','Research','Dormitory','ElectricAmplifier','WaterAmplifier','GasAmplifier'):
    build(kind)
for stage in range(6): harbor(stage)
(REVIEW/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('FACILITIES_GENERATED',len(records))
