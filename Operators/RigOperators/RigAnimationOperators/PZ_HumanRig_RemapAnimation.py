# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math
import re

from bpy.types import Operator
from bpy.props import BoolProperty
from bpy_extras import anim_utils
from pathlib import Path

from ....Utility.PZ_AssetMethods import directx_import_available

class PZ_HumanRig_RemapAnimation(Operator):
    bl_idname = "zomboid.remap_animation"
    bl_label = "Add Animation to Rig"
    bl_description = "Remaps a vanilla or modded animation from the game back onto the control rig, to the best of its ability"

    use_ik: BoolProperty(
        default=False
    )

    control_dict = {
        'Bip01': 'CTRL-Pelvis',
        'Bip01_Spine': 'CTRL-Spine1',
        'Bip01_Spine1': 'CTRL-Spine2',
        'Bip01_Neck': 'CTRL-Chest',
        'Bip01_Head': 'CTRL-Head',
        'Bip01_L_Clavicle': 'CTRL-Shoulder.L',
        'Bip01_R_Clavicle': 'CTRL-Shoulder.R',
        'Bip01_L_UpperArm': 'CTRL-UpperArmFK.L',
        'Bip01_R_UpperArm': 'CTRL-UpperArmFK.R',
        'Bip01_L_Forearm': 'CTRL-ForearmFK.L',
        'Bip01_R_Forearm': 'CTRL-ForearmFK.R',
        'Bip01_L_Hand': 'CTRL-Hand.L',
        'Bip01_R_Hand': 'CTRL-Hand.R',
        'Bip01_L_Finger0': 'CTRL-Thumb.L',
        'Bip01_R_Finger0': 'CTRL-Thumb.R',
        'Bip01_L_Finger1': 'CTRL-Fingers.L',
        'Bip01_R_Finger1': 'CTRL-Fingers.R',
        'Bip01_Prop2': 'CTRL-Prop.L',
        'Bip01_Prop1': 'CTRL-Prop.R',
        'Bip01_L_Thigh': 'CTRL-ThighFK.L',
        'Bip01_R_Thigh': 'CTRL-ThighFK.R',
        'Bip01_L_Calf': 'CTRL-CalfFK.L',
        'Bip01_R_Calf': 'CTRL-CalfFK.R',
        'Bip01_L_Foot': 'CTRL-Foot.L',
        'Bip01_R_Foot': 'CTRL-Foot.R',
        'Bip01_BackPack': 'CTRL-Backpack',
        'Bip01_DressFront': 'CTRL-DressFront1',
        'Bip01_DressFront02': 'CTRL-DressFront2',
        'Bip01_DressBack': 'CTRL-DressBack1',
        'Bip01_DressBack02': 'CTRL-DressBack2',
        'Translation_Data': 'CTRL-TranslationData'
    }

    rest_deltas = {}

    reference_rig = None
    target_rig = None

    reference_action = None
    target_action = None

    reference_slot = None
    target_slot = None

    def import_reference_rig(self, context, p, g):
        selected_anim = context.scene.pz_human_imported_animations[
            g.imported_animation_active_index]

        if Path(selected_anim.anim_path).is_file():

            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            objs_before = set(context.scene.objects)

            match selected_anim.file_type:
                case '.x':
                    if not directx_import_available():
                        print("The .x importer is not enabled or installed")
                        return ({'CANCELLED'})

                    bpy.ops.import_scene.directx_x(
                        filepath=selected_anim.anim_path,
                        use_import_collection=False
                    )

            objs_after = set(bpy.context.scene.objects)

            imported_objects = list(objs_after - objs_before)

            for obj in imported_objects:
                if obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'ARMATURE':
                    self.reference_rig = obj
                    self.reference_action = obj.animation_data.action
                    self.reference_slot = obj.animation_data.action_slot
                    obj.rotation_euler[2] += math.pi
                    obj.scale[0] = -1

            # Calculate and store the differences in rest position, using the edit bones

            reference_bones = self.reference_rig.data.bones
            target_bones = self.target_rig.data.bones

            for reference_bone in reference_bones:
                if reference_bone.name in target_bones:
                    target_bone = target_bones[reference_bone.name]

                    reference_matrix = reference_bone.matrix_local
                    target_matrix = target_bone.matrix_local

                    self.rest_deltas.update(
                        {reference_bone.name: target_matrix @ reference_matrix.inverted()})

                    loc, rot, scale = (
                        target_matrix @ reference_matrix.inverted()).decompose()

                    print(f"Bone: {reference_bone.name}")
                    print(f"  Location Offset: {loc}")
                    print(f"  Rotation Diff (Quaternion): {rot}")
                    print("-" * 40)

            # Reorient Bones
            # bones = self.reference_rig.data.edit_bones
            # for bone in bones:
            #     axis_z = bone.matrix.to_3x3().col[2]

            #     rot_matrix = (Matrix.Translation(bone.head) @
            #                   Matrix.Rotation(math.radians(-90), 4, axis_z) @
            #                   Matrix.Translation(-bone.head))

            #     bone.matrix = rot_matrix @ bone.matrix

        return ({'FINISHED'})

    def cleanup_animation(self, context, p, g):
        action = self.reference_action
        channelbag = anim_utils.action_get_channelbag_for_slot(
            action, action.slots[0])

        # TODO: Make the curves match how it was before cleanup

        for fcurve in channelbag.fcurves:
            final_keys = []
            increasing = False
            decreasing = False
            prev_value = 0

            for index, key in enumerate(fcurve.keyframe_points):
                if not decreasing and not increasing and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    if key.co[1] > prev_value:
                        increasing = True
                    elif key.co[1] < prev_value:
                        decreasing = True

                    final_keys.append(key)

                elif increasing and key.co[1] < prev_value and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    decreasing = True
                    increasing = False

                    final_keys.append(fcurve.keyframe_points[index - 1])

                elif decreasing and key.co[1] > prev_value and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    decreasing = False
                    increasing = True

                    final_keys.append(fcurve.keyframe_points[index - 1])

                prev_value = key.co[1]

            for key in reversed(fcurve.keyframe_points[:]):
                if key not in final_keys:
                    fcurve.keyframe_points.remove(key)

        return ({'FINISHED'})

    def remap_animation(self, context, p, g):

        channelbag = anim_utils.action_get_channelbag_for_slot(
            self.reference_action, self.reference_slot)

        self.target_action = bpy.data.actions.new(
            self.reference_action.name + ' (IMPORT)')
        self.target_slot = self.target_action.slots.new(
            id_type='OBJECT', name='PZ_HumanRigSlot')
        self.target_rig.animation_data.action = self.target_action
        self.target_rig.animation_data.action_slot = self.target_slot

        bone_name_pattern = r'"(.*?)"'
        bone_name_regex = re.compile(bone_name_pattern)

        transform_type_pattern = r'\]\.(.*)'
        transform_type_regex = re.compile(transform_type_pattern)

        reference_bones = self.reference_rig.pose.bones
        target_bones = self.target_rig.pose.bones

        # # Capture the base pose for each bone
        # context.scene.frame_set(0)
        # for reference_bone_name, target_bone_name in self.control_dict.items():

        #     reference_bone = reference_bones.get(reference_bone_name)
        #     target_bone = target_bones.get(target_bone_name)

        #     self.base_poses.update({target_bone_name : reference_bone.matrix.copy()})

        #     data_path = 'pose.bones["' + target_bone_name + '"]'
        #     self.target_rig.keyframe_insert(data_path=data_path + '.location', frame=0)
        #     self.target_rig.keyframe_insert(data_path=data_path + '.rotation_quaternion', frame=0)

        # Capture the animation curves
        # TODO Optimize

        # Set the base pose

        for fcurve in channelbag.fcurves:
            bone_name = bone_name_regex.search(
                fcurve.data_path).group().replace('"', '')
            transform_type = transform_type_regex.search(
                fcurve.data_path).group().replace('].', '')

            if bone_name in self.control_dict:
                ctrl_bone_name = self.control_dict[bone_name]
                ctrl_bone = target_bones.get(ctrl_bone_name)
                target_data_path = fcurve.data_path.replace(
                    bone_name, self.control_dict[bone_name])

                for key in fcurve.keyframe_points:
                    context.scene.frame_set(int(key.co[0]))

                    axis_switch = 0

                    match transform_type:
                        case 'location':
                            match fcurve.array_index:
                                case 0:
                                    axis_switch = 1
                                case 1:
                                    axis_switch = 2
                                case 2:
                                    axis_switch = 0

                            ctrl_bone.location[axis_switch] = key.co[1] * 100
                            if bone_name in self.rest_deltas:
                                ctrl_bone.location[axis_switch] += self.rest_deltas[bone_name].to_translation()[
                                    axis_switch] / 100
                        case 'rotation_quaternion':
                            match fcurve.array_index:
                                case 0:
                                    # Let Blender calculate the quaternion w
                                    continue
                                case 1:
                                    axis_switch = 3
                                case 2:
                                    axis_switch = 1
                                case 3:
                                    axis_switch = 2

                            ctrl_bone.rotation_quaternion[axis_switch] = key.co[1]
                            if bone_name in self.rest_deltas:
                                ctrl_bone.rotation_quaternion[axis_switch] += self.rest_deltas[bone_name].to_quaternion()[
                                    axis_switch]

                    self.target_rig.keyframe_insert(
                        data_path=target_data_path, frame=int(key.co[0]))

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        # Store context to restore later
        prev_mode = context.mode
        prev_active_object = context.active_object
        if prev_active_object is not None:
            prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        self.target_rig = context.active_object

        self.import_reference_rig(context, p, g)
        # self.cleanup_animation(context, p, g)
        self.remap_animation(context, p, g)

        bpy.data.objects.remove(self.reference_rig, do_unlink=True)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in prev_selected_objects:
            obj.select_set(True)
        if prev_active_object is not None:
            context.view_layer.objects.active = prev_active_object

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        return ({'FINISHED'})