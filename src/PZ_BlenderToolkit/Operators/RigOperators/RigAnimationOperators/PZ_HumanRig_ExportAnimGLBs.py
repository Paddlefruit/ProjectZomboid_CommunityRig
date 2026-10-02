# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy  

from bpy.types import Operator
from ....Utility.PZ_AssetMethods import ADDON_ROOT

class PZ_HumanRig_ExportAnimGLBs(Operator):
    bl_idname = "zomboid.export_anim_glbs"
    bl_label = "Export GLBs for Project Zomboid"
    bl_description = "Export your animations as GLB files that are adjusted for Project Zomboid"


    @classmethod
    def poll(cls, context):
        if context.active_object:
            export_properties = context.active_object.pz_export_properties

            if export_properties.file_output_path != '':
                if export_properties.batch_export:
                    return True
                else:
                    return context.active_object.animation_data.action is not None
            else:
                return False
        else:
            return False

# ------------------------------------------------------------------------#
#  Main Function

    def export_anim(self, context, action):

        models_blend_path = ADDON_ROOT / 'Assets' / 'Blend' / 'CH-PZ_HumanRig_BaseModels.blend'

        # Get reference to the rig's properties
        object_pointers = context.active_object.pz_object_pointers
        export_properties = context.active_object.pz_export_properties

        # Force set the animation to export at 30 FPS, which is what Project Zomboid evaluates animations at
        context.scene.render.fps = 30

        with bpy.context.temp_override():

            # Get references to the objects that will be exported
            dummy01 = object_pointers.dummy01_object
            bip01 = object_pointers.rig_object
            translation_data = object_pointers.translation_data_object

            # Temporarially bring in the male model as a copy to be used as the mesh exported with the anim
            with bpy.data.libraries.load(str(models_blend_path)) as (data_from, data_to):
                if 'MaleBody_BASE' in data_from.objects:
                    data_to.objects.append('MaleBody_BASE')
            mesh = bpy.data.objects.get('MaleBody_BASE')
            mesh.name = 'AnimBody'

            object_pointers.model_collection.objects.link(mesh)

            # Parent the imported object to the rig
            mesh.parent = object_pointers.rig_object
            mesh.matrix_parent_inverse = object_pointers.rig_object.matrix_world.inverted()
        
            # Offset the object based on the difference between the rig position and world origin
            mesh.location += object_pointers.rig_object.location / 100
        
            # Rotate the body to the rig object
            mesh.rotation_euler = object_pointers.rig_object.rotation_euler
        
            # Scale the body to the rig object
            mesh.scale = object_pointers.rig_object.scale
        
            # Add the armature modifier to the object, set it to the rig
            arm_modifier = mesh.modifiers.new(name='Armature', type='ARMATURE')
            arm_modifier.object = object_pointers.rig_object

            # Rename the objects to their PZ names and store their Blender names to restore later
            prev_dummy01_name = dummy01.name
            dummy01.name = 'Dummy01'

            prev_bip01_name = bip01.name
            bip01.name = 'Bip01'

            prev_translation_data_name = translation_data.name
            translation_data.name = 'Translation_Data'

            # Set the mode to Object Mode and deselect all objects
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            # Temporarily enable selectability and visibility on the relevant objects
            dummy01.hide_select = False
            dummy01.hide_viewport = False

            bip01.hide_select = False
            bip01.hide_viewport = False

            mesh.hide_select = False
            mesh.hide_viewport = False

            translation_data.hide_select = False
            translation_data.hide_viewport = False

            # Select the objects that will be exported
            dummy01.select_set(True)
            bip01.select_set(True)
            mesh.select_set(True)
            translation_data.select_set(True)

            # Create animation data for TranslationData if it does not have any
            translation_data.animation_data_create()

            # Create a new temporary NLA track that will be used to export to PZ for both Bip01 and TranslationData
            bip01_track = bip01.animation_data.nla_tracks.new()
            # NLA track will have the same name as the action
            bip01_track.name = action.name
            translation_data_track = translation_data.animation_data.nla_tracks.new()
            translation_data_track.name = action.name
            
            start_frame = int(action.frame_range[0])
            end_frame = int(action.frame_range[1])

            bip01.animation_data.action = action
            bip01_strip = bip01_track.strips.new(action.name, start_frame, action)
            bip01_strip.frame_end = end_frame

            translation_data.animation_data.action = action
            translation_data_strip = translation_data_track.strips.new(action.name, start_frame, action)
            translation_data_strip.frame_end = end_frame

            # Call the Blender gltf exporter with specific settings tailored for our setup and Project Zomboid
            bpy.ops.export_scene.gltf(
                filepath=export_properties.file_output_path + '/' + action.name + '.glb',
                use_selection=True,
                export_hierarchy_flatten_objs=True,
                export_bake_animation=True,
                export_materials='NONE',
                export_morph=False,
                export_def_bones=True,
                export_animation_mode="NLA_TRACKS"
            )

            # Remove all of the NLA tracks and strips that we created
            for strip in bip01_track.strips:
                bip01_track.strips.remove(strip)
            for strip in translation_data_track.strips:
                translation_data_track.strips.remove(strip)

            bip01.animation_data.nla_tracks.remove(bip01_track)
            translation_data.animation_data.nla_tracks.remove(
                translation_data_track)

            # Restore the previous selection and visibility properties
            dummy01.hide_select = True

            mesh.hide_select = True
            mesh.hide_viewport = True

            translation_data.hide_select = True
            translation_data.hide_viewport = True

            # Restore Object Names
            dummy01.name = prev_dummy01_name
            bip01.name = prev_bip01_name
            translation_data.name = prev_translation_data_name

            # Delete the temporary model
            data = mesh.data
            bpy.data.objects.remove(mesh, do_unlink=True)
            if data:
                bpy.data.meshes.remove(data, do_unlink=True)

        context.scene.render.fps = 30

        return {'FINISHED'}

# ------------------------------------------------------------------------#
#  Execute

    def execute(self, context):

        # Get reference to the rig's properties
        export_properties = context.active_object.pz_export_properties

        if len(export_properties.file_output_path) > 0:
            if export_properties.batch_export:
                for action in bpy.data.actions:
                    if export_properties.action_filter in action.name:
                        self.export_anim(context, action)
            else:
                if context.active_object.animation_data.action is not None:
                    self.export_anim(
                        context, context.active_object.animation_data.action)
                else:
                    print("Selected rig has no active action selected.")
        else:
            self.report({"WARNING"}, "Declare a filepath to export to")

        return {'FINISHED'}