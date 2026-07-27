# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy  

from bpy.types import Operator

class PZ_HumanRig_ExportAnimGLBs(Operator):
    bl_idname = "zomboid.export_anim_glbs"
    bl_label = "Export GLBs for Project Zomboid"
    bl_description = "Export your animations as GLB files that are adjusted for Project Zomboid"


    @classmethod
    def poll(cls, context):
        p = context.active_object.pz_human_props

        if p.file_output_path != '':
            if p.batch_export:
                return True
            else:
                return context.active_object.animation_data.action is not None
        else:
            return False

# ------------------------------------------------------------------------#
#  Main Function

    def export_anim(self, context, action):
        # Get reference to the rig's properties
        p = context.active_object.pz_human_props

        # Force set the animation to export at 30 FPS, which is what Project Zomboid evaluates animations at
        context.scene.render.fps = 30

        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        # Get references to the objects that will be exported
        dummy01 = p.dummy01_empty
        bip01 = prev_active_object
        mesh = p.male_body_object
        translation_data = p.translation_data_empty

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
            filepath=p.file_output_path + '/' + action.name + '.glb',
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

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Restore Object Names
        dummy01.name = prev_dummy01_name
        bip01.name = prev_bip01_name
        translation_data.name = prev_translation_data_name

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        context.scene.render.fps = 30

        for obj in prev_selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = prev_active_object

        return {'FINISHED'}

# ------------------------------------------------------------------------#
#  Execute

    def execute(self, context):

        # Get reference to the rig's properties
        p = context.active_object.pz_human_props

        if len(p.file_output_path) > 0:
            if p.batch_export:
                for action in bpy.data.actions:
                    if p.action_filter in action.name:
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