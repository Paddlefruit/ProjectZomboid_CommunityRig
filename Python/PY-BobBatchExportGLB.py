# Only for use for V3 of the rig, on Blender 5 and up

import os
import bpy

from bpy_extras import anim_utils
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

class ExportZomboidGLBs(Operator, ExportHelper):
    bl_idname = "zomboid.export_glb"
    bl_label = "Select Folder"
    
    filter_glob: StringProperty(
        default='.glb',
        options={'HIDDEN'}
    )
    
    all_actions: BoolProperty(
        name='Export All Actions',
        description="Batch export all actions in the Blend file to their own unique .glb file. Otherwise, only export Bip01's active action.",
        default=True
    )
    
    action_filter: StringProperty(
        name='Action Filter',
        description="Only actions that have this substring will be exported. Only useful with 'Export All Actions'.",
        default='Bob_'
    )
    
    filename_ext = ""
    
    def export_anim(self, action):        
        context = bpy.context
        
        dummy01 = bpy.data.objects.get('Dummy01')
        bip01 = bpy.data.objects.get('Bip01')
        mesh = bpy.data.objects.get('GEO-MaleBody')
        translation_data = bpy.data.objects.get('Translation_Data')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
        dummy01.select_set(True)
        bip01.select_set(True)
        mesh.select_set(True)
        translation_data.select_set(True)

        translation_data.animation_data_create()
        
        bip01_track = bip01.animation_data.nla_tracks.new()
        bip01_track.name = action.name
        translation_data_track = translation_data.animation_data.nla_tracks.new()
        translation_data_track.name = action.name
                
        bip01.animation_data.action = action
        anim_length = int(action.frame_range[0])
        bip01_strip = bip01_track.strips.new(action.name, anim_length, action)
                
        translation_data.animation_data.action = action
        translation_data_strip = translation_data_track.strips.new(action.name, anim_length, action)
        translation_data_strip.frame_end = bip01_strip.frame_end
                
        bpy.ops.export_scene.gltf( 
            filepath= self.filepath + '/' + action.name +'.glb',
            use_selection=True,
            export_hierarchy_flatten_objs=True,
            export_bake_animation=True,
            export_materials='NONE',
            export_morph=False,
            export_def_bones=True,
            export_animation_mode="NLA_TRACKS"
        )
                
        for strip in bip01_track.strips:
            bip01_track.strips.remove(strip)
        for strip in translation_data_track.strips:
            translation_data_track.strips.remove(strip)

        bip01.animation_data.nla_tracks.remove(bip01_track)
        translation_data.animation_data.nla_tracks.remove(translation_data_track)
        return {'FINISHED'}
    
    def execute(self, context): 
        
        index = self.filepath.rfind('/')
        
        if index != -1:
            self.filepath = self.filepath[:index]
           
        if self.all_actions:
            for action in bpy.data.actions:
                if self.action_filter in action.name:
                    self.export_anim(action)
        else:
            if bpy.data.objects.get('Bip01').animation_data.action is not None:
                self.export_anim(bpy.data.objects.get('Bip01').animation_data.action)
            else:
                print("Bip01 has no active action selected.")
                
        return {'FINISHED'}

        
def register():
    bpy.utils.register_class(ExportZomboidGLBs)
    
def unregister():
    bpy.utils.unregister_class(ExportZomboidGLBs)

if __name__ == "__main__":
    register()
        
    bpy.ops.zomboid.export_glb('INVOKE_DEFAULT')    
