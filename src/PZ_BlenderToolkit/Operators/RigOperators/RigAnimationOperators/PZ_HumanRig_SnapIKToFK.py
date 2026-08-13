# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy
import math

from bpy.types import Operator
from bpy.props import StringProperty

from mathutils import Vector, Quaternion

class PZ_HumanRig_SnapIKToFK(Operator):
    bl_idname = "zomboid.snap_ik_to_fk"
    bl_label = "Snap IK to FK"
    bl_options = {'REGISTER', 'UNDO'}

    fk_bone: StringProperty()
    ik_control_bone: StringProperty()
    ik_pole_bone: StringProperty()
    extremity_bone: StringProperty()

    limb_type: StringProperty()

    ik_fk_prop: StringProperty()

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        animation_properties = context.active_object.pz_animation_properties

        bones = context.active_object.pose.bones

        fk_bone = bones.get(self.fk_bone)
        ik_control_bone = bones.get(self.ik_control_bone)
        ik_pole_bone = bones.get(self.ik_pole_bone)
        extremity_bone = bones.get(self.extremity_bone)

        if fk_bone and extremity_bone and ik_control_bone and ik_pole_bone:

            orig_fk_matrix = fk_bone.matrix.copy()

            ik_control_bone.matrix = extremity_bone.matrix.copy()
            context.view_layer.update()

            bone_dir = Vector(fk_bone.tail - fk_bone.head).normalized()

            ik_pole_bone.matrix = orig_fk_matrix
            context.view_layer.update()

            if self.limb_type == 'ARM':
                ik_pole_bone.location -= bone_dir * 15
            elif self.limb_type == 'LEG':
                ik_pole_bone.location += bone_dir * 15
            context.view_layer.update()

            if self.limb_type == 'ARM':
                shift_location = Vector((0.023 * 200, 0, 0))
            elif self.limb_type == 'LEG':
                shift_location = Vector((0.023 * -1000, 0, 0))
            ik_pole_bone.location = ik_pole_bone.location + shift_location
            context.view_layer.update()

            flip_rads = math.radians(180)
            flip_quaternion = Quaternion((math.cos(flip_rads / 2), math.sin(flip_rads / 2), 0, 0))
            ik_pole_bone.rotation_quaternion = ik_pole_bone.rotation_quaternion @ flip_quaternion
            context.view_layer.update()

            if addon_data.auto_switch_kinematics:
                setattr(animation_properties, self.ik_fk_prop, 1.0)
                context.active_object.update_tag()
                context.view_layer.update()

            if addon_data.auto_key_snaps:
                context.active_object.keyframe_insert(data_path='pz_animation_properties.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current - 1)

                setattr(animation_properties, self.ik_fk_prop, 0.0)
                context.active_object.update_tag()
                context.view_layer.update()

                context.active_object.keyframe_insert(data_path='pz_animation_properties.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current + 1)

        return ({'FINISHED'})