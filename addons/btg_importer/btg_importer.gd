extends Node

const SUPPORTED_NODE_TYPES = ["Node", "Node2D", "Position2D", "Sprite", "Polygon2D", "CollisionPolygon2D", "Path2D"]
const SUPPORTED_TYPES = ["MESH", "EMPTY", "CURVE"]

var file = null
var open_scenes = null


func _init():
	pass


func start_import(file_path : String, open_scenes : Array):
	self.open_scenes = open_scenes
	
	var json_parse = open_json_file(file_path)
	
	if json_parse == null:
		print("Error parsing json.")
		return
	
	read_json_file(json_parse, "res:/")

func open_json_file(file_path):
	file = File.new()
	var err = file.open(file_path, File.READ)
	
	if(err != OK):
		print("File opening error.")
		file.close()
		return
	
	var file_text = file.get_as_text()
	
	var json_parse = JSON.parse(file_text)
	
	if json_parse.error != OK:
		print("Error getting file as json.")
		file.close()
		return
	
	file.close()
	
	return json_parse.result["children"]

func read_json_file(json, current_path : String):
	
	if(typeof(json) == TYPE_DICTIONARY):
		
		if(json["type"] == "collection"):
			current_path += "/" + json["name"]
			
			if not dir_exists(current_path):
				print("Directory did not exist. Some error with blender addon ocurred.")
			
			if(json["children"] != null):
				read_json_file(json["children"], current_path)
		
		else:
			if json["type"] in SUPPORTED_TYPES:
				if(json["node_type"] in SUPPORTED_NODE_TYPES):
					manage_scene(json, current_path + "/")
	else:
		for json_dict in json:
			read_json_file(json_dict, current_path)


func manage_scene(json, current_path):
	var scene = null
	var scene_path = current_path + json["name"] + ".tscn"
	
	for open_scene in open_scenes:
		if scene_path == open_scene.filename:
			#Scene exist but is open
			scene = open_scene
			modify_existent_scene(scene, json, current_path)
	
	if(scene == null):
		if file_exists(scene_path):
			#Scene exist but is close
			scene = load(scene_path).instance()
			modify_existent_scene(scene, json, current_path)
		else:
			scene = create_scene_from_scratch(json, current_path)

func create_scene_from_scratch(json, current_path):
	var scene = null
	var scene_path = current_path + json["name"] + ".tscn"
	
	
	scene = create_node(json, current_path)
	
	if json["children"] != null:
		fill_scene_from_scratch(scene, scene, json, current_path)
	
	var packed_scene = PackedScene.new()
	packed_scene.pack(scene)
	
	ResourceSaver.save(scene_path, packed_scene)

func fill_scene_from_scratch(scene, current_node, json : Dictionary, current_path : String):
	
	for j in json["children"]:
		
		# IGNORE CURVES AND COLLISIONS
		if j["node_type"] == "CollisionPolygon2D" or j["node_type"] == "Path2D":
			continue
		
		var node = create_node(j, current_path)
		
		current_node.add_child(node)
		
		node.set_owner(scene)
		
		if j["children"] != null:
			fill_scene_from_scratch(scene, node, j, current_path)

func modify_existent_scene(scene, json, current_path):
	
	var scene_path = current_path + json["name"] + ".tscn"
	
	if scene.get_class() != json["node_type"]:
		print("In " + scene.filename + ", Node \'" + scene.name + 
		"\' dont match types. Current = " + scene.get_class() + 
		", File = " + json["node_type"] + ".\n" + "Maybe have issues because of that.\n")
		return null
	
	if json["children"] != null:
		fill_existent_scene(scene, scene, json, current_path)
	
	var packed_scene = PackedScene.new()
	packed_scene.pack(scene)
	
	ResourceSaver.save(scene_path, packed_scene)

func fill_existent_scene(scene, current_node, json, current_path):
	
	for j in json["children"]:
		
		# IGNORE CURVES AND COLLISIONS
		if j["node_type"] == "CollisionPolygon2D" or j["node_type"] == "Path2D":
			continue
		
		var node = null
		
		if(current_node.has_node(j["name"])):
			node = modify_node(current_node.get_node(j["name"]), j, current_path)
		else:
			node = create_node(j, current_path)
			current_node.add_child(node)
			node.set_owner(scene)
		
		if j["children"] != null:
			fill_existent_scene(scene, node, j, current_path)


func create_node(json : Dictionary, current_path : String = ""):
	var node = null
	
	match json["node_type"]:
		"Node":
			node = Node.new()
		"Node2D":
			node = Node2D.new()
		"Position2D":
			node = Position2D.new()
		"Sprite":
			node = Sprite.new()
			var sprite_path = current_path + json["name"] + ".png"
			
			if not file_exists(sprite_path):
				print("Sprite not found: ", sprite_path)
			else:
				var image = load(sprite_path)
				node.texture = image
				
		"Polygon2D":
			node = Polygon2D.new()
			
			var polygons = []
			
			for pol in json["obj_data"]["polygon"]:
				polygons.append( Vector2(pol[0], pol[1]) )
			
			node.polygon = polygons
			node.color = Color(json["obj_data"]["color"])
			node.antialiased = true
			
		"CollisionPolygon2D":
			node = CollisionPolygon2D.new()
			
			var polygons = []
			
			for pol in json["obj_data"]["polygon"]:
				polygons.append( Vector2(pol[0], pol[1]) )
			
			node.polygon = polygons
		"Path2D":
			node = Path2D.new()
			
			var curve = Curve2D.new()
			curve.bake_interval = 1.0
			
			for points in json["obj_data"]["bezier_points"]:
				curve.add_point(
					Vector2(points[0][0], points[0][1]),
					Vector2(points[1][0], points[1][1]),
					Vector2(points[2][0], points[2][1])
				)
			
			node.curve = curve
		_:
			print("Node unrecognizable: ", json["name"])
	
	node.set_name(json["name"])
	node.set_position( Vector2( json["position"][0], json["position"][1] ) )
	return node

func modify_node(node, json : Dictionary, current_path : String = ""):
	
	if node.get_class() != json["node_type"]:
		
		print(json["name"] + " type was changed to " + json["node_type"] + "!")
		var replace_node = create_node(json, current_path)
		node.replace_by(replace_node)
		
		node.queue_free()
	else:
		match json["node_type"]:
			"Sprite":
				var sprite_path = current_path + json["name"] + ".png"
				
				if not file_exists(sprite_path):
					print("Sprite not found: ", sprite_path)
				else:
					var image = load(sprite_path)
					node.texture = image
					node.scale = Vector2(json["obj_data"]["sprite_scale"], json["obj_data"]["sprite_scale"])
					
			"Polygon2D":
				var polygons = []
				
				for pol in json["obj_data"]["polygon"]:
					polygons.append( Vector2(pol[0], pol[1]) )
				
				node.polygon = polygons
				node.color = Color(json["obj_data"]["color"])
				node.antialiased = true
				
			"CollisionPolygon2D":
				var polygons = []
				
				for pol in json["obj_data"]["polygon"]:
					polygons.append( Vector2(pol[0], pol[1]) )
				
				node.polygon = polygons
			"Path2D":
				var curve = Curve2D.new()
				curve.bake_interval = 1.0
				
				for points in json["obj_data"]["bezier_points"]:
					curve.add_point(
						Vector2(points[0][0], points[0][1]),
						Vector2(points[1][0], points[1][1]),
						Vector2(points[2][0], points[2][1])
					)
				
				node.curve = curve
			_:
				print("Node unrecognizable: ", json["name"])
	
	node.set_name(json["name"])
	node.set_position( Vector2( json["position"][0], json["position"][1] ) )
	return node


func get_scene_json(json, scene_path : Array):
	if(typeof(json) == TYPE_DICTIONARY):
		if(scene_path[0] == json["name"]):
			if scene_path.size() == 1:
				return json
			else:
				scene_path.remove(0)
				return get_scene_json(json["children"], scene_path)
	else:
		for json_dict in json:
			return get_scene_json(json_dict, scene_path)


func get_nodes_json(json, scene_path : Array, node_type : String, nodes : Array):
	if typeof(json) == TYPE_DICTIONARY:
		if(json["node_type"] == node_type):
			nodes.append(json)
			if json["children"] != null:
				get_nodes_json(json["children"], scene_path, node_type, nodes)
		else:
			if json["children"] != null:
				get_nodes_json(json["children"], scene_path, node_type, nodes)
	else:
		for json_dict in json:
			get_nodes_json(json_dict, scene_path, node_type, nodes)
	
	return nodes


func get_collisions(scene, file_path : String):
	
	var json_parse = open_json_file(file_path)
	
	if json_parse == null:
		print("Error parsing json.")
		return
	
	var scene_path = scene.filename
	scene_path = scene_path.split("//")[1]
	scene_path = scene_path.split(".")[0]
	scene_path = scene_path.split("/")
	
	var json = get_scene_json(json_parse, scene_path)
	
	if json == null:
		return
	
	var collisions = null
	
	if scene.has_node("CollisionsImport"):
		collisions = scene.get_node("CollisionsImport")
	else:
		collisions = Node2D.new()
		collisions.name = "CollisionsImport"
		scene.add_child(collisions)
		collisions.set_owner(scene)
	
	var nodes_json = get_nodes_json(json, scene_path, "CollisionPolygon2D", [])
	
	for node_json in nodes_json:
		var node = null
		
		if collisions.has_node(node_json["name"]):
			node = collisions.get_node(node_json["name"])
			modify_node(node, node_json)
		else:
			node = create_node(node_json)
			collisions.add_child(node)
			node.set_owner( collisions.get_owner() )



func get_curves(scene, file_path : String):
	
	var json_parse = open_json_file(file_path)
	
	if json_parse == null:
		print("Error parsing json.")
		return
	
	var scene_path = scene.filename
	scene_path = scene_path.split("//")[1]
	scene_path = scene_path.split(".")[0]
	scene_path = scene_path.split("/")
	
	var json = get_scene_json(json_parse, scene_path)
	
	if json == null:
		return
	
	var curves = null
	
	if scene.has_node("CurvesImport"):
		curves = scene.get_node("CurvesImport")
	else:
		curves = Node2D.new()
		curves.name = "CurvesImport"
		scene.add_child(curves)
		curves.set_owner(scene)
	
	var nodes_json = get_nodes_json(json, scene_path, "Path2D", [])
	
	for node_json in nodes_json:
		var node = null
		
		if curves.has_node(node_json["name"]):
			node = curves.get_node(node_json["name"])
			modify_node(node, node_json)
		else:
			node = create_node(node_json)
			curves.add_child(node)
			node.set_owner( curves.get_owner() )



func dir_exists(dir_path : String):
	var dir = Directory.new()
	
	if !dir.dir_exists(dir_path):
		dir.make_dir_recursive(dir_path)
		return false
	
	return true

func file_exists(file_path : String):
	var file = File.new()
	
	if !file.file_exists(file_path):
		return false
	
	return true
