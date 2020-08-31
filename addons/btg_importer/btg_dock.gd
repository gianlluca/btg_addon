tool
extends Control

var ImporterClass = load("res://addons/btg_importer/btg_importer.gd")

var ES  = null
var EI  = null
var EIS = null
var EDS = null
var EFS = null

var polygon_selected = null

func _ready():
	ES  = EditorScript.new()
	EI  = ES.get_editor_interface()
	EIS = EI.get_inspector()
	EDS = EI.get_selection()
	EFS = EI.get_resource_filesystem()
	
#	EDS.connect("selection_changed", self, "_on_selection_changed")
#	EIS.connect("property_edited", self, "_on_property_edited")



func get_file_path():
	if($SC/VB_Main/HB_File_Imp/File_Imp_Path.text == ""):
		print("Choose a file to import")
		return null
	else:
		return $SC/VB_Main/HB_File_Imp/File_Imp_Path.text


func reload_EI():
	ES  = EditorScript.new()
	EI  = ES.get_editor_interface()
	EIS = EI.get_inspector()
	EDS = EI.get_selection()
	EFS = EI.get_resource_filesystem()


func update_file_folder():
	if(EFS == null):
		reload_EI()
	EFS.scan()


func _on_FileDialog_file_selected(path):
	$SC/VB_Main/HB_File_Imp/File_Imp_Path.text = path


func _on_Change_File_Imp_pressed():
	$FileDialog.popup_centered()



func _on_ImportAllPolygons_pressed():
	if(EI == null):
		reload_EI()
	
	var Importer = ImporterClass.new()
	
	if(get_file_path() != null):
		Importer.start_import(get_file_path(), EI.get_open_scenes())
	
	print("Import Complete")
	yield(get_tree(), "idle_frame")
	
	update_file_folder()


func _on_ImportSceneCollisions_pressed():
	if(EI == null):
		reload_EI()
	
	var Importer = ImporterClass.new()
	
	if(get_file_path() != null):
		Importer.get_collisions(EI.get_edited_scene_root(), get_file_path())
	
	print("Import Complete")


func _on_ImportSceneCurves_pressed():
	if(EI == null):
		reload_EI()
	
	var Importer = ImporterClass.new()
	
	if(get_file_path() != null):
		Importer.get_curves(EI.get_edited_scene_root(), get_file_path())
	
	print("Import Complete")
