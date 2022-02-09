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
    "author": "Bill Currie, Aleksander Marhall",
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
from bpy.props import FloatVectorProperty, PointerProperty
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

class QFMDLSettings(bpy.types.PropertyGroup):
    palette : EnumProperty(
        items=PALETTE,
        name="Palette",
        description="Palette")
    eyeposition : FloatVectorProperty(
        name="Eye Position",
        description="View possion relative to object origin")
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

    mdl_scale_mins : FloatVectorProperty(
        name="MDL Mins",
        default=(-400.0,-100.0,-100.0),
        description="Minimum allowed vertex coordinates")
    mdl_scale_maxs : FloatVectorProperty(
        name="MDL Maxs",
        default=(100.0,100.0,100.0),
        description="Maximum allowed vertex coordinates")
    


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
    mdl_scale_mins : FloatVectorProperty(
        name="MDL Mins",
        default=(-100.0,-100.0,-100.0),
        # default = bpy.context.active_object.qfmdl.mdl_scale_mins,
        description="Minimum allowed vertex coordinates")
    mdl_scale_maxs : FloatVectorProperty(
        name="MDL Maxs",
        default=(100.0,100.0,100.0),
        # default = bpy.context.active_object.qfmdl.mdl_scale_maxs,
        description="Maximum allowed vertex coordinates")

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
        layout.prop(obj.qfmdl, "mdl_scale_mins")
        layout.prop(obj.qfmdl, "mdl_scale_maxs")

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
