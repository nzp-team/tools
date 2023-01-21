# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# copied from io_scene_obj

# <pep8 compliant>

bl_info = {
    "name": "Quake MDL format",
    "author": "Bill Currie, Aleksander Marhall, Luis Gutierrez",
    "version": (0, 7, 0),
    "blender": (2, 80, 0),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export Quake MDL (version 6) files. (.mdl)",
    "warning": "still work in progress",
    "wiki_url": "",
    "tracker_url": "",
#   "support": 'OFFICIAL',
    "category": "Import-Export"}

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    import imp
    if "import_mdl" in locals():
        imp.reload(import_mdl)
    if "export_mdl" in locals():
        imp.reload(export_mdl)


import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy.props import FloatVectorProperty, PointerProperty, IntProperty, BoolProperty, PointerProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper, path_reference_mode, axis_conversion

PALETTE=(
    ('PAL_QUAKE', "Quake", "Quake palette"),
    ('PAL_HEXEN2', "Hexen 2", "Hexen 2 palette"),
    #('PAL_CUSTOM', "Custom", "Custom palette from file"),
)

SYNCTYPE=(
    ('ST_SYNC', "Syncronized", "Automatic animations are all together"),
    ('ST_RAND', "Random", "Automatic animations have random offsets"),
)

EFFECTS=(
    ('EF_NONE', "None", "No effects"),
    ('EF_ROCKET', "Rocket", "Leave a rocket trail"),
    ('EF_GRENADE', "Grenade", "Leave a grenade trail"),
    ('EF_GIB', "Gib", "Leave a trail of blood"),
    ('EF_TRACER', "Tracer", "Green split trail"),
    ('EF_ZOMGIB', "Zombie Gib", "Leave a smaller blood trail"),
    ('EF_TRACER2', "Tracer 2", "Orange split trail + rotate"),
    ('EF_TRACER3', "Tracer 3", "Purple split trail"),
)


import bgl
import gpu
import mathutils
from gpu_extras.batch import batch_for_shader


def mdl_draw_bbox_callback(self, context):
    def draw_line(start, end, color):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': [start,end]})
        shader.bind()
        shader.uniform_float('color', color)
        batch.draw(shader)


    bbox_mins = context.view_layer.objects.active.qfmdl.mdl_scale_mins
    bbox_maxs = context.view_layer.objects.active.qfmdl.mdl_scale_maxs
    if not context.view_layer.objects.active.qfmdl.mdl_draw_bbox:
        return



    bbox_corners = {
        'left_front_lower':     mathutils.Vector((bbox_mins[0], bbox_mins[1], bbox_mins[2])),
        'right_front_lower':    mathutils.Vector((bbox_maxs[0], bbox_mins[1], bbox_mins[2])),
        'right_back_lower':     mathutils.Vector((bbox_maxs[0], bbox_maxs[1], bbox_mins[2])),
        'left_back_lower':      mathutils.Vector((bbox_mins[0], bbox_maxs[1], bbox_mins[2])),
        'left_front_upper':     mathutils.Vector((bbox_mins[0], bbox_mins[1], bbox_maxs[2])),
        'right_front_upper':    mathutils.Vector((bbox_maxs[0], bbox_mins[1], bbox_maxs[2])),
        'right_back_upper':     mathutils.Vector((bbox_maxs[0], bbox_maxs[1], bbox_maxs[2])),
        'left_back_upper':      mathutils.Vector((bbox_mins[0], bbox_maxs[1], bbox_maxs[2])),
    }
    color_red = (1.0, 0.0, 0.0, 0.7)
    color_green = (0.0, 1.0, 0.0, 0.7)
    color_blue = (0.0, 0.0, 1.0, 0.7)

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glDisable(bgl.GL_DEPTH_TEST)

    draw_line(bbox_corners['left_front_lower'], bbox_corners['right_front_lower'], color_red)
    draw_line(bbox_corners['left_back_lower'], bbox_corners['right_back_lower'], color_red)
    draw_line(bbox_corners['left_front_upper'], bbox_corners['right_front_upper'], color_red)
    draw_line(bbox_corners['left_back_upper'], bbox_corners['right_back_upper'], color_red)

    draw_line(bbox_corners['left_front_lower'], bbox_corners['left_back_lower'], color_green)
    draw_line(bbox_corners['right_front_lower'], bbox_corners['right_back_lower'], color_green)
    draw_line(bbox_corners['left_front_upper'], bbox_corners['left_back_upper'], color_green)
    draw_line(bbox_corners['right_front_upper'], bbox_corners['right_back_upper'], color_green)

    draw_line(bbox_corners['left_front_lower'], bbox_corners['left_front_upper'], color_blue)
    draw_line(bbox_corners['right_front_lower'], bbox_corners['right_front_upper'], color_blue)
    draw_line(bbox_corners['left_back_lower'], bbox_corners['left_back_upper'], color_blue)
    draw_line(bbox_corners['right_back_lower'], bbox_corners['right_back_upper'], color_blue)

    # bgl.glEnd()
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glEnable(bgl.GL_DEPTH_TEST)


# This dictionary is used to store bbox preview handlers
# Keys: object names
# Values: registered handlers
draw_bbox_handlers = {
}


def mdl_draw_bbox_updated(self, context):
    global draw_bbox_handlers

    # Disable all existing handlers:
    while len(draw_bbox_handlers) > 0:
        k = list(draw_bbox_handlers.keys())[0]
        v = draw_bbox_handlers.pop(k)
        bpy.types.SpaceView3D.draw_handler_remove(v, 'WINDOW')

    # Add a new handler for this object name:
    if self.mdl_draw_bbox:
        obj_name = context.view_layer.objects.active.name
        handler = bpy.types.SpaceView3D.draw_handler_add(mdl_draw_bbox_callback, (self,context), 'WINDOW', 'POST_VIEW')
        # Store the handler to later remove it
        draw_bbox_handlers[obj_name] = handler



class QFMDLSettings(bpy.types.PropertyGroup):
    palette : EnumProperty(
        items=PALETTE,
        name="Palette",
        description="Palette")
    eyeposition : FloatVectorProperty(
        name="Eye Position",
        description="View position relative to object origin")
    synctype : EnumProperty(
        items=SYNCTYPE,
        name="Sync Type",
        description="Add random time offset for automatic animations")
    rotate : BoolProperty(
        name="Rotate",
        description="Rotate automatically (for pickup items)")
    effects : EnumProperty(
        items=EFFECTS,
        name="Effects",
        description="Particle trail effects")

    #doesn't work :(
    #script = PointerProperty(
    #    type=bpy.types.Object,
    #    name="Script",
    #    description="Script for animating frames and skins")

    xform : BoolProperty(
        name="Auto transform",
        description="Auto-apply location/rotation/scale when exporting",
        default=True)
    md16 : BoolProperty(
        name="16-bit",
        description="16 bit vertex coordinates: QuakeForge only")
    xform : BoolProperty(
        name="Auto transform",
        description="Auto-apply location/rotation/scale when exporting",
        default=True)
    # md16 : BoolProperty(
    #     name="16-bit",
    #     description="16 bit vertex coordinates: QuakeForge only")
    #script = StringProperty(
    #    name="Script",
    #    description="Script for animating frames and skins")

    mdl_first_frame : IntProperty(
        name="First Frame",
        default=0,
        description="First animation frame to export."
    )
    mdl_last_frame : IntProperty(
        name="Last Frame",
        default=0,
        description="Final animation frame to export. (Inclusive)"
    )

    mdl_scale_mins : FloatVectorProperty(
        name="MDL Mins",
        default=(-100.0,-100.0,-100.0),
        description="Minimum allowed vertex coordinates")
    mdl_scale_maxs : FloatVectorProperty(
        name="MDL Maxs",
        default=(100.0,100.0,100.0),
        description="Maximum allowed vertex coordinates")
    mdl_draw_bbox : BoolProperty(
        name="Show MDL bounding box",
        default=False,
        description="Draw the specified MDL bounding box in the blender 3D viewport.",
        update=mdl_draw_bbox_updated,
    )


class ImportMDL6(bpy.types.Operator, ImportHelper):
    '''Load a Quake MDL (v6) File'''
    bl_idname = "import_mesh.quake_mdl_v6"
    bl_label = "Import MDL"
    bl_options = {'PRESET'}

    filename_ext = ".mdl"
    filter_glob : StringProperty(default="*.mdl", options={'HIDDEN'})

    palette : EnumProperty(
        items=PALETTE,
        name="Palette",
        description="Palette")

    def execute(self, context):
        from . import import_mdl
        keywords = self.as_keywords (ignore=("filter_glob",))
        return import_mdl.import_mdl(self, context, **keywords)




class ExportMDL6(bpy.types.Operator, ExportHelper):
    '''Save a Quake MDL (v6) File'''

    bl_idname = "export_mesh.quake_mdl_v6"
    bl_label = "Export MDL"
    bl_options = {'PRESET'}

    filename_ext = ".mdl"
    filter_glob : StringProperty(default="*.mdl", options={'HIDDEN'})

    palette : EnumProperty(
        items=PALETTE,
        name="Palette",
        description="Palette")
    eyeposition : FloatVectorProperty(
        name="Eye Position",
        description="View possion relative to object origin")
        #default = bpy.context.active_object.qfmdl.eyeposition)
    synctype : EnumProperty(
        items=SYNCTYPE,
        name="Sync Type",
        description="Add random time offset for automatic animations")
    rotate : BoolProperty(
        name="Rotate",
        description="Rotate automatically (for pickup items)",
        default=False)
    effects : EnumProperty(
        items=EFFECTS,
        name="Effects",
        description="Particle trail effects")
    xform : BoolProperty(
        name="Auto transform",
        description="Auto-apply location/rotation/scale when exporting",
        default=True)
    md16 : BoolProperty(
        name="16-bit",
        description="16 bit vertex coordinates: QuakeForge only")

    mdl_first_frame : IntProperty(
        name="Start Frame",
        default=0,
        description="First animation frame to export."
    )
    mdl_last_frame : IntProperty(
        name="End Frame",
        default=0,
        description="Final animation frame to export. (Inclusive)"
    )

    mdl_scale_mins : FloatVectorProperty(
        name="MDL Mins",
        default=(-100.0,-100.0,-100.0),
        description="Minimum allowed vertex coordinates")
    mdl_scale_maxs : FloatVectorProperty(
        name="MDL Maxs",
        default=(100.0,100.0,100.0),
        description="Maximum allowed vertex coordinates")
    mdl_draw_bbox : BoolProperty(
        name="Show MDL bounding box",
        default=False,
        description="Draw the specified MDL bounding box in the blender 3D viewport.",
        update=mdl_draw_bbox_updated,
    )

    @classmethod
    def poll(cls, context):
        return (context.active_object != None
                and type(context.active_object.data) == bpy.types.Mesh)

    def execute(self, context):
        from . import export_mdl
        keywords = self.as_keywords (ignore=("check_existing", "filter_glob"))
        return export_mdl.export_mdl(self, context, **keywords)

    def invoke(self, context, event):
        # self.eyeposition = bpy.context.active_object.qfmdl.eyeposition
        self.mdl_scale_mins = bpy.context.active_object.qfmdl.mdl_scale_mins
        self.mdl_scale_maxs = bpy.context.active_object.qfmdl.mdl_scale_maxs
        self.mdl_first_frame = bpy.context.active_object.qfmdl.mdl_first_frame
        self.mdl_last_frame = bpy.context.active_object.qfmdl.mdl_last_frame
        return ExportHelper.invoke(self,context,event)
        # return {"RUNNING_MODAL"}
        # return {'FINISHED'}

class OBJECT_PT_MDLPanel(bpy.types.Panel):
    bl_label = "MDL Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        # layout.prop(obj, "select", text="")

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        layout.prop(obj.qfmdl, "palette")
        layout.prop(obj.qfmdl, "eyeposition")
        layout.prop(obj.qfmdl, "synctype")
        layout.prop(obj.qfmdl, "rotate")
        layout.prop(obj.qfmdl, "effects")
        # layout.prop(obj.qfmdl, "script")
        layout.prop(obj.qfmdl, "xform")
        layout.prop(obj.qfmdl, "md16")
        layout.prop(obj.qfmdl, "mdl_first_frame")
        layout.prop(obj.qfmdl, "mdl_last_frame")
        layout.prop(obj.qfmdl, "mdl_scale_mins")
        layout.prop(obj.qfmdl, "mdl_scale_maxs")
        layout.prop(obj.qfmdl, "mdl_draw_bbox")

        

def menu_func_import(self, context):
    self.layout.operator(ImportMDL6.bl_idname, text="Quake MDL (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(ExportMDL6.bl_idname, text="Quake MDL (.mdl)")

classes = (
    QFMDLSettings,
    OBJECT_PT_MDLPanel,
    ImportMDL6,
    ExportMDL6
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.qfmdl = PointerProperty(type=QFMDLSettings)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
