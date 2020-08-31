import os
import bpy
import math
from mathutils import Vector
import json



# COLOR
# ----------------------------------------------------------------------------------------------------------
def format_hex(c):
    h = c.split('x')

    return '0' + h[1] if (h[1].__len__() < 2) else h[1]


def to_hex(c):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.9
    else:
        srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055

    return format_hex(hex(max(min(int(srgb * 255 + 0.5), 255), 0)))


def get_mesh_color(obj):
    if(obj.material_slots.__len__() < 1):
        return '#ffffffff'

    for mat in obj.material_slots:
        nodes = mat.material.node_tree.nodes
        principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

        col2 = principled.inputs[0].default_value

        col = (to_hex(col2[3]) + to_hex(col2[0]) + to_hex(col2[1]) + to_hex(col2[2]))

        return col.upper()
# ----------------------------------------------------------------------------------------------------------
# COLOR



# DATA
# ----------------------------------------------------------------------------------------------------------

def get_sprite_data(object, col_folder, scene_ep):

    center_location = get_geometry_center(object)

    sprite_path = os.path.join(os.path.dirname(col_folder), object.name + ".png")

    render_data = configure_render(object, center_location, sprite_path, scene_ep)

    obj_data = {
        # 'sprite_path'  : sprite_path,
        'pivot_offset' : render_data['pivot_offset'],
        'sprite_scale' : render_data['sprite_scale'],
    }

    return obj_data


def get_mesh_data(object, col_folder, scene_ep):

    depsgraph = bpy.context.view_layer.depsgraph
    obj_eval = object.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    data = {
            'color'   : get_mesh_color(object),
            'polygon' : [],
        }

    vertices = mesh.vertices
    ordered_vertices = []

    for loop in mesh.loops:
        for ver in vertices:
            if(ver.index == loop.vertex_index):
                ordered_vertices.append(ver)

    for ver in ordered_vertices:
        data['polygon'].append(
                [
                    round( ver.co.x * scene_ep.meter_pixel_scale, 3),
                    round(-ver.co.y * scene_ep.meter_pixel_scale, 3), # blender and godot have opposites Y axis
                    #round(ver.co.z * scene_ep.meter_pixel_scale, 3),
                ]
            )

    return data


def get_curve_data(obj, scene_ep):
    curve = obj.data

    data = { 'bezier_points' : [] }

    if(curve.splines.__len__() > 0):
        spline = curve.splines[0]

        for b_point in spline.bezier_points:

            data['bezier_points'].append(
                [
                    [
                        round( b_point.co.x * scene_ep.meter_pixel_scale, 3),
                        round(-b_point.co.y * scene_ep.meter_pixel_scale, 3), # blender and godot have opposites Y axis
                        #round(b_point.co.z * scene_ep.meter_pixel_scale, 3),
                    ],
                    [
                        round( (b_point.handle_left.x - b_point.co.x) * scene_ep.meter_pixel_scale, 3),
                        round(-(b_point.handle_left.y - b_point.co.y) * scene_ep.meter_pixel_scale, 3), # blender and godot have opposites Y axis
                        #round((b_point.handle_left.z - b_point.co.z) * scene_ep.meter_pixel_scale, 3),
                    ],
                    [
                        round( (b_point.handle_right.x - b_point.co.x) * scene_ep.meter_pixel_scale, 3),
                        round(-(b_point.handle_right.y - b_point.co.y) * scene_ep.meter_pixel_scale, 3), # blender and godot have opposites Y axis
                        #round((b_point.handle_right.z - b_point.co.z) * scene_ep.meter_pixel_scale, 3),
                    ],
                ]
            )

    return data

# ----------------------------------------------------------------------------------------------------------
# DATA



# RENDER
# ----------------------------------------------------------------------------------------------------------
def configure_camera(orthoscale, center_location):
    scene = bpy.context.scene
    cam_obj = scene.camera

    if(cam_obj == None):
        master_collection = scene.collection

        camera = bpy.data.cameras.new("Camera")
        cam_obj = bpy.data.objects.new("Camera", camera)
        master_collection.objects.link(cam_obj)
        scene.camera = cam_obj
    else:
        cam_obj.rotation_euler = (0, 0, 0)

    cam_obj.data.type = 'ORTHO'
    cam_obj.data.ortho_scale = orthoscale
    cam_obj.location.x = center_location[0]
    cam_obj.location.y = center_location[1]
    cam_obj.location.z = center_location[2] + 15.0

    return cam_obj


def get_sprite_res(orthoscale, scene_ep):
    render_sizes = []

    aux = 2
    while aux < scene_ep.max_render_size:
        render_sizes.append(aux)
        aux *= 2

    sprite_res = orthoscale * scene_ep.meter_pixel_scale

    if( int(scene_ep.scale_type) ):
        for size in render_sizes:
            if(size > sprite_res):
                sprite_res = size
                break
    else:
        render_sizes.reverse()

        for size in render_sizes:
            if(size < sprite_res):
                sprite_res = size
                break

    if(sprite_res > render_sizes[render_sizes.__len__() - 1]):
    	sprite_res = render_sizes[render_sizes.__len__() - 1]
    elif(sprite_res < render_sizes[0]):
    	sprite_res = render_sizes[0]

    return sprite_res


def configure_render(object, center_location, sprite_path, scene_ep):

    scene = bpy.context.scene
    orthoscale = get_orthoscale_object(object, scene_ep)

    configure_camera(orthoscale, center_location)

    object.hide_render = False

    sprite_res = get_sprite_res(orthoscale, scene_ep)

    scene.render.resolution_x = sprite_res * int(scene_ep.super_sampling)
    scene.render.resolution_y = sprite_res * int(scene_ep.super_sampling)

    bpy.context.scene.render.filepath = sprite_path

    bpy.ops.render.render(write_still=True)

    object.hide_render = True

    sprite_scale = ((orthoscale * scene_ep.meter_pixel_scale) / sprite_res) / int(scene_ep.super_sampling)

    render_data = {
        'sprite_scale' : round(sprite_scale, 3),
        'pivot_offset' : [
                round( (center_location.x - object.location.x) * scene_ep.meter_pixel_scale / sprite_scale, 3),
                round(-(center_location.y - object.location.y) * scene_ep.meter_pixel_scale / sprite_scale, 3),
                round( (center_location.z - object.location.z) * scene_ep.meter_pixel_scale / sprite_scale, 3),
            ]
        }

    return render_data


def hide_unhide_all(master_collection, hide):

    for col in master_collection.children:
        hide_unhide_all(col, hide)

    for obj in master_collection.objects:
        if(obj.type == "MESH"):
            obj.hide_render = hide
# ----------------------------------------------------------------------------------------------------------
# RENDER



# OBJECT
# ----------------------------------------------------------------------------------------------------------
def get_geometry_center(obj):
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    centerCoord = obj.matrix_world @ local_bbox_center

    return centerCoord


def get_orthoscale_object(object, scene_ep):
    vertices = []

    centerCoord = get_geometry_center(object)

    for ver in object.data.vertices:
        vertices.append(centerCoord - (object.location + ver.co))

    if(vertices.__len__() < 1):
        return 0 # "Object has no vertices!

    bigger = 0
    for ver in vertices: # Get most distant vertice
        bigger_ver = max( [ abs(ver.x), abs(ver.y) ] )

        if(bigger_ver > bigger):
            bigger = bigger_ver

    return (bigger * 2.0) + (scene_ep.margin_render / scene_ep.meter_pixel_scale / int(scene_ep.super_sampling))


def get_node_type(object):
    node_type = None

    if(object.type == "EMPTY"):
        node_type = object.godot_properties.empty_type

    elif(object.type == "MESH"):
        node_type = object.data.godot_properties.mesh_type

    else: #elif(object.type == "CURVE"):
        node_type = object.data.godot_properties.curve_type

    return node_type

def add_object_panel(object, row):

    if(object.type == "EMPTY"):
        row.prop(object.godot_properties, 'empty_type', text='Node Type:', expand=False)

    elif(object.type == "MESH"):
    	row.prop(object.data.godot_properties, 'mesh_type', text='Node Type:', expand=False)

    elif(object.type == "CURVE"):
    	if(object.data.splines != None):
    		aux = 0

    		for i in object.data.splines[0].bezier_points:
    			aux+=1
    			break

    		if(aux):
    			row.prop(object.data.godot_properties, 'curve_type', text='Node Type:', expand=False)


def get_object_position(object, scene_ep):
    return [
            round(  object.location.x * scene_ep.meter_pixel_scale, 3),
            round( -object.location.y * scene_ep.meter_pixel_scale, 3), # blender and godot have opposites Y axis
            round(  object.location.z * scene_ep.meter_pixel_scale, 3),
        ]

# ----------------------------------------------------------------------------------------------------------
# OBJECT
