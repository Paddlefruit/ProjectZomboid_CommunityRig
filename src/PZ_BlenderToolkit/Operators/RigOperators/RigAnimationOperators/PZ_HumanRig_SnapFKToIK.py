# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from bpy.types import Operator
from bpy.props import StringProperty

class PZ_HumanRig_SnapFKToIK(Operator):
    bl_idname = "zomboid.snap_fk_to_ik"
    bl_label = "Snap FK to IK"
    bl_options = {'REGISTER', 'UNDO'}

    first_fk_bone: StringProperty()
    second_fk_bone: StringProperty()
    first_ik_bone: StringProperty()
    second_ik_bone: StringProperty()
    extremity_bone: StringProperty()
    ik_control_bone: StringProperty()

    ik_fk_prop: StringProperty()

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        animation_properties = context.active_object.pz_animation_properties

        bones = context.active_object.pose.bones

        first_fk_bone = bones.get(self.first_fk_bone)
        second_fk_bone = bones.get(self.second_fk_bone)
        first_ik_bone = bones.get(self.first_ik_bone)
        second_ik_bone = bones.get(self.second_ik_bone)
        ik_control_bone = bones.get(self.ik_control_bone)
        extremity_bone = bones.get(self.extremity_bone)

        if first_fk_bone and second_fk_bone and first_ik_bone and second_ik_bone and ik_control_bone and extremity_bone:

            first_fk_bone.matrix = first_ik_bone.matrix.copy()
            context.view_layer.update()

            second_fk_bone.matrix = second_ik_bone.matrix.copy()
            context.view_layer.update()

            extremity_bone.matrix = ik_control_bone.matrix.copy()
            context.view_layer.update()

            if addon_data.auto_switch_kinematics:
                setattr(animation_properties, self.ik_fk_prop, 0.0)
                context.active_object.update_tag()
                context.view_layer.update()
            
            if addon_data.auto_key_snaps:
                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current - 1)

                setattr(animation_properties, self.ik_fk_prop, 1.0)
                context.active_object.update_tag()
                context.view_layer.update()

                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current + 1)

            return ({'FINISHED'})

        print('Could not find all bones')
        return ({'CANCELLED'})