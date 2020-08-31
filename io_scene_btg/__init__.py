import bpy
from bpy_extras.io_utils import ExportHelper, orientation_helper
from . import export_btg, util
import os



from bpy.props import(
		StringProperty,
		BoolProperty,
		IntProperty,
		FloatProperty,
		FloatVectorProperty,
		EnumProperty,
		PointerProperty,
	)

from bpy.types import(
		Panel,
		Menu,
		Operator,
		PropertyGroup,
	)


bl_info = {
		'name': 'Blender to Godot 2D',
		'author': 'Gianlluca Harenza',
		'blender': (2, 83, 3),
		'location': 'File > Import-Export and ObjectData > Godot Engine',
		'description': ('Export from Blender to Godot'),
		'category': 'Import-Export'
	}


class ExportBTG(bpy.types.Operator, ExportHelper):

	bl_idname = 'export_scene.btg'
	bl_label = 'Export BTG'
	bl_options = {'PRESET'}

	filter_glob : StringProperty(default='*.btg', options={'HIDDEN'})
	check_extension = True
	filename_ext = '.btg'

	def execute(self, context):
		'''Begin the export'''

		try:
			if not self.filepath:
				raise Exception('filepath not set')

			keywords = self.as_keywords(ignore=('axis_forward', 'axis_up', 'global_scale', 'check_existing', 'filter_glob'))

			return export_btg.save(self, context, **keywords)

		except RuntimeError as error:
			self.report({'ERROR'}, str(error))

	def draw(self, context):
		pass # It's needed to get panels available and make export properties groups


def menu_func_export(self, context):
	self.layout.operator(ExportBTG.bl_idname, text='Blender to Godot 2D (.btg)')


class BTG_PT_export_include(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = 'Include'
	bl_parent_id = 'FILE_PT_operator'


	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator

		return operator.bl_idname == 'EXPORT_SCENE_OT_btg'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.

		layout.prop(context.scene.btg_export_properties, 'use_selection')


class BTG_PT_export_transform(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = 'Transform'
	bl_parent_id = 'FILE_PT_operator'


	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator

		return operator.bl_idname == 'EXPORT_SCENE_OT_btg'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.

		layout.prop(context.scene.btg_export_properties, 'meter_pixel_scale')


class BTG_PT_export_geometry(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = 'Geometry'
	bl_parent_id = 'FILE_PT_operator'


	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator

		return operator.bl_idname == 'EXPORT_SCENE_OT_btg'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.


		layout.prop(context.scene.btg_export_properties, 'use_mesh_modifiers')


class BTG_PT_export_settings(bpy.types.Panel):
	bl_space_type = 'FILE_BROWSER'
	bl_region_type = 'TOOL_PROPS'
	bl_label = 'Sprite Settings'
	bl_parent_id = 'FILE_PT_operator'


	@classmethod
	def poll(cls, context):
		sfile = context.space_data
		operator = sfile.active_operator

		return operator.bl_idname == 'EXPORT_SCENE_OT_btg'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.

		sfile = context.space_data
		operator = sfile.active_operator

		layout.prop(context.scene.btg_export_properties, 'max_render_size')
		layout.prop(context.scene.btg_export_properties, 'margin_render')
		layout.prop(context.scene.btg_export_properties, 'scale_type')
		layout.prop(context.scene.btg_export_properties, 'super_sampling')


class GodotProperties(PropertyGroup):

	empty_type: EnumProperty(
			name = 'Node Type',
			description = 'Type to be exported.',
			items = [
					('Node',   'Node',       ''),
					('Node2D', 'Node2D',     ''),
					('Position2D',  'Position2D', ''),
				],
			default = 'Node2D',
			)

	mesh_type: EnumProperty(
			name = 'Node Type',
			description = 'Type to be exported.',
			items =	[
					('Sprite',             'Sprite',             ''),
					('Polygon2D',          'Polygon2D',          ''),
					('CollisionPolygon2D', 'CollisionPolygon2D', ''),
				],
			default = 'Sprite'
			)

	curve_type: EnumProperty(
			name = 'Node Type',
			description = 'Type to be exported.',
			items =	[
					('Path2D', 'Path2D', ''),
				],
			default = 'Path2D'
			)

class ExportProperties(PropertyGroup):

	# List of operator properties, the attributes will be assigned to the class instance from the operator settings before calling

	use_selection: BoolProperty(
			name='Selection Only',
			description='Export selected objects only',
			default=False,
		)

	# object group
	use_mesh_modifiers: BoolProperty(
			name='Apply Modifiers',
			description='Apply modifiers',
			default=True,
		)

	meter_pixel_scale: IntProperty(
			name='Meter to Pixel',
			description='Convert metric scale to pixels',
			min=0, max=512,
			default=32
		)

	max_render_size: IntProperty(
			name='Max Render Size',
			description='Max Render Sprite Size.',
			min=0, max=4096,
			default=512,
		)

	scale_type: EnumProperty(
			name='Scale Type',
			description='',
			items=[('0','Scale-Up',''),('1','Scale-Down','')],
			default='1',
		)

	super_sampling: EnumProperty(
			name='Super Sampling',
			description='',
			items=[('1','1x',''),('2','2x',''),('4','4x',''),('8','8x',''),('16','16x','')],
			default='1',
		)

	margin_render: IntProperty(
			name='Margin Render',
			description='Margin Render Sprite Size.',
			min=0, max=16,
			default=2,
		)



class GodotPropPanel(bpy.types.Panel):
	bl_idname = 'OBJECT_PT_godot_properties'
	bl_label = 'Godot Engine'
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = 'data'

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		object = context.object

		col = layout.column()
		row = col.row(align=True)

		util.add_object_panel(object, row)



classes = (
	ExportBTG,
	BTG_PT_export_include,
	BTG_PT_export_transform,
	BTG_PT_export_geometry,
	BTG_PT_export_settings,
	ExportProperties,
	GodotProperties,
	GodotPropPanel,
	)

def register(): #Add addon to blender

	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
	bpy.types.ID.godot_properties = PointerProperty(type=GodotProperties)
	bpy.types.Scene.btg_export_properties = PointerProperty(type=ExportProperties)


def unregister(): #Remove addon from blender

	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
	del bpy.types.ID.godot_properties
	del bpy.types.Scene.btg_export_properties

	for cls in classes:
		bpy.utils.unregister_class(cls)



if __name__ == '__main__':
	register()
