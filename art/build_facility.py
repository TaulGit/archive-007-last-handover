"""Build the Archive 007 playable-scale environment using Blender 4.5."""
from pathlib import Path
import math
import bpy
from mathutils import Vector

out = Path(__file__).resolve().parent / "facility-007"
out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
palette = {}
for name, color in dict(concrete=(.32,.37,.36), enamel=(.65,.70,.63),
                        graphite=(.055,.083,.09), brass=(.82,.51,.19),
                        red=(.58,.13,.08), green=(.16,.39,.35), paper=(.9,.82,.64),
                        blue=(.17,.30,.39), glow=(.55,.96,.78)).items():
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color,1)
    if name == "glow":
        shader.inputs["Emission Color"].default_value = (*color,1)
        shader.inputs["Emission Strength"].default_value = 1.8
    palette[name] = mat

def zone(name):
    global group
    group = bpy.data.collections.new(name)
    scene.collection.children.link(group)

def assign(obj, name, mat):
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    group.objects.link(obj)
    obj.data.materials.append(palette[mat])
    return obj

def box(name,x,y,z,w,d,h,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z))
    obj = assign(bpy.context.object,name,mat)
    obj.dimensions = (w,d,h)
    return obj

def label(name,x,y,z,size,vertical=False):
    bpy.ops.object.text_add(location=(x,y,z))
    obj=assign(bpy.context.object,name,"paper")
    obj.data.body=name
    obj.data.align_x="CENTER"
    obj.data.size=size
    if vertical:
        obj.rotation_euler.x=math.pi/2
    bpy.ops.object.convert(target="MESH")

def desk(x,y):
    box("Worktop",x,y,.84,3.2,.95,.13,"enamel")
    for offset in [-1.25,1.25]:
        box("Drawer pedestal",x+offset,y,.39,.52,.76,.78,"graphite")
    box("CRT housing",x+.5,y,1.25,.74,.56,.72,"graphite")
    box("Phosphor screen",x+.5,y-.285,1.26,.59,.02,.48,"glow")
    box("Keyboard",x+.45,y-.36,.93,.62,.19,.055,"blue")
    box("Dossier",x-.75,y-.1,.93,.43,.32,.04,"paper")

def cabinet(x,y):
    box("Steel cabinet",x,y,1.05,1,.68,2.1,"graphite")
    for i in range(5):
        z=.24+i*.4
        box("File drawer",x,y-.35,z,.92,.045,.35,"green")
        box("Index tab",x,y-.38,z+.06,.25,.02,.06,"paper")

zone("00 | Central spine")
box("Central corridor",0,0,-.13,36,3.4,.26,"concrete")
for side in [-1,1]:
    box("Guidance stripe",0,side*1.28,.012,36,.09,.024,"brass")
for x in [-15,-9,-3,3,9,15]:
    box("Inset floor lamp",x,0,.013,.65,.12,.025,"glow")
for side in [-1,1]:
    box("End bulkhead",side*18,0,1.5,.18,3.4,3,"enamel")

rooms=[(-12,1,"01 | Records","RECORDS","green"),(0,1,"02 | Personnel","PERSONNEL","blue"),
       (12,1,"04 | Handover","HANDOVER","red"),(-12,-1,"03 | Quarters","QUARTERS","blue"),
       (0,-1,"03 | Maintenance","WORKSHOP","brass"),(12,-1,"05 | Control","DISPATCH","green")]
for x,s,name,sign,accent in rooms:
    zone(name)
    y=s*5.75
    box("Floor",x,y,-.13,12,8.1,.26,"concrete")
    for dx in [-3.53,3.53]:
        box("Corridor partition",x+dx,s*1.7,1.5,4.94,.16,3,"enamel")
        box("Wall band",x+dx,s*1.7,1.05,4.94,.19,.14,accent)
    box("Door lintel",x,s*1.7,2.76,2.12,.23,.48,"graphite")
    for dx in [-1.07,1.07]:
        box("Door jamb",x+dx,s*1.7,1.28,.11,.25,2.56,accent)
    box("Threshold ID",x,s*2.65,.018,4.6,.84,.035,"graphite")
    label(sign,x,s*2.65-.14,.04,.45)
    box("West wall",x-5.94,y,1.5,.12,8.1,3,"enamel")
    if x==12:
        box("East wall",17.94,y,1.5,.12,8.1,3,"enamel")
    if x!=12:
        box("Rear wall",x,s*9.8,1.5,12,.14,3,"enamel")
    else:
        for offset,width in [(-2,8),(5.1,1.8)]:
            box("Exit partition",x+offset,s*9.8,1.5,width,.16,3,"enamel")
        box("Exit sill",x+3.1,s*10.6,-.13,2.2,1.6,.26,"green")
        label("EXIT",x+3.1,s*10.6,.02,.4)
    if sign in ("PERSONNEL","RECORDS"):
        desk(x,y)
        for i in range(7):
            cabinet(x-4.5+i*1.4,s*8.8)
        if sign=="RECORDS":
            box("Jammed shredder",x-2.7,y, .62,.85,.8,1.24,"blue")
            box("Feed slot",x-2.7,y,1.245,.64,.09,.018,"graphite")
            box("Trapped disposal slip",x-2.7,y,1.38,.34,.025,.27,"paper")
    elif sign=="QUARTERS":
        for dx in [-3,3]:
            box("Bunk base",x+dx,y,.3,1.35,2.3,.6,"graphite")
            box("Mattress",x+dx,y,.66,1.3,2.25,.17,"blue")
            box("Pillow",x+dx,y+.76,.8,.88,.45,.14,"paper")
        desk(x,s*8.6)
    elif sign=="WORKSHOP":
        desk(x-2,s*8.4)
        for i in range(3):
            box("Pump enclosure",x+3,y+i*.95,.63,1.5,.76,1.26,"brass")
            box("Pressure strip",x+3,y+i*.95,1.28,.96,.13,.05,"graphite")
    elif sign=="HANDOVER":
        box("Interview counter",x-1,y,.56,6,.52,1.12,"green")
        for dx in [-3.9,1.9]:
            box("Window mullion",x+dx,y,1.8,.12,.15,1.4,"graphite")
        box("Window header",x-1,y,2.48,6,.15,.15,"graphite")
        label("008",x-1,y-.27,.55,.5,True)
        box("Signature pad",x,y-.04,1.15,.5,.35,.05,"brass")
    else:
        desk(x-2,y)
        for dx in [-3,-1.4,.2]:
            cabinet(x+dx,s*8.8)
        box("Manual dispatch station",x+2,y,.57,.78,.7,1.14,"red")
        box("Dispatch key",x+2,y,1.17,.27,.23,.07,"brass")

zone("06 | Shift details")
for x in [-12,0,12]:
    for s in [-1,1]:
        for station in [-1,1]:
            box("Threshold light",x+station*1.13,s*1.7,2.15,.13,.28,.45,"glow")
        for dx in [-4.8,-3.6,-2.4,2.4,3.6,4.8]:
            box("Ribbed acoustic panel",x+dx,s*1.7,2.03,.88,.205,.62,"concrete")
        box("Overhead task light",x-3.7,s*9.55,2.64,2.9,.22,.12,"glow")
for x in [-12,0,10]:
    y = 5.75 if x!=10 else -5.75
    box("Operator stool",x,y-1.12,.46,.5,.48,.1,"blue")
    box("Seat post",x,y-1.12,.22,.13,.13,.44,"graphite")
    box("Chair foot",x,y-1.12,.055,.47,.42,.1,"graphite")
box("Recovered tape deck",-12,-8.2,1.04,.72,.38,.22,"green")
zone("08 | Close inspection props")
def disc(name, xyz, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=xyz)
    return assign(bpy.context.object,name,mat)

for dx in [-.16,.16]:
    disc("Tape reel rim",(-12+dx,-8.2,1.164),.115,.022,"graphite")
    disc("Wound magnetic tape",(-12+dx,-8.2,1.18),.092,.014,"brass")
    disc("Capstan",(-12+dx,-8.2,1.193),.028,.016,"paper")
    for i in range(3):
        angle=i*math.tau/3
        disc("Spool opening",(-12+dx+.063*math.cos(angle),-8.2+.063*math.sin(angle),1.191),.019,.01,"graphite")
for i in range(5):
    box("Transport key",-12.19+.08*i,-8.05,1.166,.057,.06,.035,"red" if i==0 else "paper")
box("Shredder inspection hatch",-14.7,5.342,.76,.70,.025,.67,"graphite")
box("Removable bin",-14.7,5.319,.73,.61,.025,.54,"blue")
box("Recessed pull",-14.7,5.302,.91,.32,.02,.042,"graphite")
for i in range(9):
    box("Motor vent",-14.95+i*.064,5.337,.25,.032,.025,.12,"graphite")
for i in range(7):
    box("Feed guide tooth",-14.95+i*.083,5.72,1.259,.031,.067,.018,"brass")
label("007",-14.7,5.303,.70,.12,True)
box("Evidence inset",11,5.473,.84,.93,.035,.27,"graphite")
box("Document tray",11,5.34,.735,.88,.30,.035,"brass")
for dx in [-.44,.44]:
    box("Tray return",11+dx,5.34,.78,.025,.30,.09,"brass")
box("Intercom grille",11.85,5.47,.88,.38,.04,.29,"graphite")
for i in range(6):
    box("Grille slat",11.85,5.442,.78+.038*i,.31,.016,.012,"enamel")
for obj in list(bpy.data.objects):
    if obj.name.startswith(("CRT housing","Jammed shredder","Recovered tape deck","Removable bin","Interview counter","Manual dispatch station","Steel cabinet")):
        bpy.context.view_layer.objects.active=obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bevel=obj.modifiers.new("Rolled edges","BEVEL")
        bevel.width=.018
        bevel.segments=3
        bpy.ops.object.modifier_apply(modifier=bevel.name)
        obj.select_set(False)
zone("09 | Signs of occupancy")
for name in ["canvas","zinc","manila","terrazzo"]:
    palette[name]=palette["concrete"].copy()
    palette[name].name=name
for obj in list(scene.objects):
    if obj.name.startswith(("Floor","Central corridor")):
        obj.data.materials[0]=palette["terrazzo"]
for x in [-15,-9]:
    box("Folded field blanket",x,-5.23,.782,1.29,1.05,.095,"canvas")
    for i in range(5):
        box("Quilted seam",x,-5.65+i*.19,.833,1.28,.015,.014,"green")
for x in [-12.95,-.95]:
    for i in range(5):
        folder=box("Unprocessed file",x+(i%2)*.045,5.64,.943+i*.031,.52,.35,.03,"manila")
        folder.rotation_euler.z=(i%3-1)*.075
        box("File tab",x+.16,5.45,.947+i*.031,.14,.06,.018,"manila")
for x in [-4.8,4.7]:
    pipe=disc("Service riser",(x,-9.50,1.48),.086,2.85,"zinc")
    for z in [.32,1.5,2.5]:
        disc("Compression fitting",(x,-9.5,z),.109,.105,"brass")
    bpy.ops.mesh.primitive_torus_add(location=(x,-9.30,1.15),rotation=(math.pi/2,0,0),major_radius=.17,minor_radius=.024)
    assign(bpy.context.object,"Isolation valve wheel","red")
    box("Valve spoke",x,-9.30,1.15,.34,.03,.025,"red")
    box("Valve stem",x,-9.4,1.15,.055,.21,.055,"zinc")
for x in [-16,-4,8]:
    box("Hall service duct",x+4,.94,2.80,8,.31,.28,"zinc")
    for dx in [1,4,7]:
        box("Duct suspension band",x+dx,.94,2.80,.06,.34,.31,"graphite")
for x in [-15,-3,9]:
    box("Noticeboard backing",x,1.585,1.76,1.55,.08,.83,"green")
    for i in range(3):
        box("Pinned duty roster",x-.46+i*.47,1.534,1.76,.34,.014,.53,"manila")
        box("Roster clip",x-.46+i*.47,1.515,2.01,.10,.018,.045,"zinc")
zone("07 | Ceiling - toggle for interior view")
roof=group
for x,s,name,sign,accent in rooms:
    box("Ceiling slab",x,s*5.75,3.12,12,8.1,.2,"concrete")
    for dx in [-3,3]:
        box("Fluorescent housing",x+dx,s*5.75,2.97,.36,2.45,.13,"graphite")
        box("Diffuser",x+dx,s*5.75,2.89,.28,2.32,.05,"glow")
box("Spine ceiling",0,0,3.12,36,3.4,.2,"concrete")
for x in [-15,-9,-3,3,9,15]:
    box("Spine ceiling strip",x,0,2.99,1.8,.24,.07,"glow")
roof.hide_viewport=True
roof.hide_render=True
zone("Camera and lighting")
def point(obj,at):
    obj.rotation_euler=(Vector(at)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(17,-40,57))
cam=bpy.context.object
point(cam,(0,0,0))
cam.data.type="ORTHO"
cam.data.ortho_scale=46
scene.camera=cam
bpy.ops.object.camera_add(location=(-12,3.4,1.67))
eye=bpy.context.object
eye.name="Player start - Records"
eye.data.lens=21
point(eye,(-13.4,6.7,1.12))
scene.camera=cam
bpy.ops.object.light_add(type="SUN",location=(-14,-20,30))
sun=bpy.context.object
point(sun,(0,0,0))
sun.data.energy=3
sun.data.angle=.25
scene.world=bpy.data.worlds.new("Overcast")
scene.world.color=(.4,.4,.4)
scene.render.engine="CYCLES"
scene.cycles.samples=6
scene.render.resolution_x=1200
scene.render.resolution_y=820
scene.render.resolution_percentage=100
for area in bpy.context.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
        area.spaces.active.region_3d.view_distance=46
        area.spaces.active.shading.color_type="MATERIAL"
bpy.ops.object.select_all(action="DESELECT")
atlas=bpy.data.images.load(str(out/"material-atlas.png"))
atlas.pack()
quadrants={"green":(0,1),"enamel":(1,1),"graphite":(0,0),"blue":(1,0)}
extra=bpy.data.images.load(str(out/"nightshift-atlas.jpg"))
extra.pack()
new_surfaces={"canvas":(0,1),"zinc":(1,1),"manila":(0,0),"terrazzo":(1,0)}
quadrants.update(new_surfaces)
for material_name in quadrants:
    material=palette[material_name]
    tex=material.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image=extra if material_name in new_surfaces else atlas
    shader=material.node_tree.nodes.get("Principled BSDF")
    material.node_tree.links.new(tex.outputs["Color"],shader.inputs["Base Color"])
    shader.inputs["Roughness"].default_value=.68
for obj in scene.objects:
    if obj.type!="MESH" or not obj.active_material or obj.active_material.name not in quadrants:
        continue
    uv=obj.data.uv_layers.active
    if uv is None:
        continue
    col,row=quadrants[obj.active_material.name]
    for face in obj.data.polygons:
        axis=max(range(3),key=lambda a:abs(face.normal[a]))
        axes=[a for a in range(3) if a!=axis]
        corners=[obj.data.vertices[obj.data.loops[i].vertex_index].co for i in face.loop_indices]
        for idx,coord in zip(face.loop_indices,corners):
            coords=[]
            for a,offset in zip(axes,(col,row)):
                lo=min(v[a] for v in corners)
                span=max(v[a] for v in corners)-lo
                coords.append(offset*.5+.006+.488*(coord[a]-lo)/max(span,.00001))
            uv.data[idx].uv=coords
scene.render.filepath=str(out/"facility-overview.png")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/"Archive-007.blend"))
roof.hide_viewport=False
bpy.ops.export_scene.gltf(filepath=str(out/"Archive-007.glb"),export_format="GLB")
roof.hide_viewport=True
bpy.ops.render.render(write_still=True)
