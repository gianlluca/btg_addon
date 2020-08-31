# BTG Addon

## Addon to export meshs from blender to godot import as polygons.

### How install?
Put folder **addons/** inside your godot project root and activate the addon.
Put **io_scene_btg/** inside Blender addons folder and activate the addon.

### How manage the blender project.

First off all to keep the consinstency of colors between blender and godot you should change a property from color management. In the Render Properties > Color Management > View Transform change from Filmic to Standard.


**The project hierarchy from blender to godot:**

- *Collections* will be *Folders* on Godot Project.
- *Objects* that are immediate child from a *Collection* will be *Scenes* (excluding *Curves* and *Collisions*), *Objects* that are child of another *Objects* will be inside their respective scenes.
- *Emptys* and *Meshs* will be the node type selected.
- *Curves* will be a *Path2D*.
- *Curves* and *Collisions* can be imported only if has a *Object* as a parent.
- Node Type can be changed in Object Data Properties > Godot Engine > Node Type.

### Example:

**Blender on export:**

- Assets (Collection)
	- Props (Collection)
		- Lamp (Empty) (Node2D)
			- LampMesh1 (Mesh) (Sprite)
			- LampPol (Mesh) (Polygon2D)
			- CollisionsImport (Node2D)
				- MeshCollision (Mesh) (CollisionPolygon2D)
				- MeshCollision2 (Mesh) (CollisionPolygon2D)
			- CurvesImport (Node2D)
				- MeshCurve (Curve)
		- Table (Empty) (Node2D)
			- TableMesh1 (Mesh) (Polygon2D)
			- TableMesh2 (Mesh) (Polygon2D)
		- Chair (Mesh) (Sprite)

**will be on Godot Import:**

- Assets (Folder)
	- Props (Folder)
		- Lamp.tscn (Scene) (Node2D)
			- LampMesh (Sprite)
			- LampPol (Polygon2D)
			- CollisionsImport (Node2D)
				- MeshCollision (CollisionPolygon2D)
				- MeshCollision2 (CollisionPolygon2D)
			- CurvesImport (Node2D)
				- MeshCurve (Path2D)
		- Table.tscn (Scene) (Node2D)
			- TableMesh1 (Polygon2D)
			- TableMesh2 (Polygon2D)
		- Chair.tscn (Scene) (Sprite)
