import os
import bpy
import math
from mathutils import Vector
from . import util
import json



def get_tree_collection_rec(operator, collection, col_folder, scene_ep):

	if(collection.children.__len__() < 1 and collection.objects.__len__() < 1):
		return None

	data = []

	for col in collection.children:
		col.name = (col.name).replace('.', '_')

		folder = os.path.join(os.path.dirname(col_folder), col.name + "/")

		if not os.path.isdir(folder):
			os.makedirs(folder)

		data_col = {
				'name'      : col.name,
				'type'      : 'collection',
				'node_type' : 'folder',
				'children'  : get_tree_collection_rec(operator, col, folder, scene_ep),
			}

		data.append(data_col)

	for obj in collection.objects:
		obj.name = (obj.name).replace('.', '_')

		if(obj.parent == None): # To get only objects that are immediate child from collection

			data_obj = get_tree_object_rec(operator, obj, col_folder, scene_ep)

			data.append(data_obj)

	return data


def get_tree_object_rec(operator, object, col_folder, scene_ep):

	object.name = (object.name).replace('.', '_')

	node_type = util.get_node_type(object)

	data = {
			'name'      : object.name,
			'type'      : object.type,
			'node_type' : node_type,
			'position'  : util.get_object_position(object, scene_ep),
		}

	if(object.type == 'MESH'):

		if node_type == "Sprite":
			data['obj_data'] = util.get_sprite_data(object, col_folder, scene_ep)

		else: # node_type == "POLYGON"
			data['obj_data'] = util.get_mesh_data(object, col_folder, scene_ep)

	elif(object.type == 'CURVE'):
		data['obj_data'] = util.get_curve_data(object, scene_ep)


	if(object.children.__len__() < 1):
		data['children'] = None
	else:
		data['children'] = []

		for obj in object.children:
			data['children'].append(get_tree_object_rec(operator, obj, col_folder, scene_ep))

	return data



def save(operator, context, filepath, **kwargs):

	scene = context.scene
	master_collection = bpy.context.scene.collection

	util.hide_unhide_all(master_collection, True)

	fp = open(os.fsencode(filepath), 'w')

	data = {
			'name'      : 'master_collection',
			'type'      : 'collection',
			'node_type' : 'root_project_folder',
			'children'  : get_tree_collection_rec(operator, master_collection, filepath, scene.btg_export_properties),
		}

	json.dump(data, fp)

	fp.close()

	util.hide_unhide_all(master_collection, False)

	return {'FINISHED'}
