# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import numpy as np
from bpy.types import Operator

class PZ_HumanRig_CreateBloodinessMask(Operator):

    '''
    This operator will draw the full bloodiness mask texture that combines all of 
    the body part health location masks at a specified intensity from 0.0 to 5.0 for each.
    It draws it to each rig's specific MaskData texture on the red channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_bloodiness_mask"
    bl_label = "Create Bloodiness Mask"
    bl_description = "Create a combined blood image from the blood textures"

    blood_textures = []

    def get_blood_textures(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        overlay_masks = addon_prefs.pz_human_overlay_masks

        self.blood_textures.clear()

        blood_props = [p.upper_torso_bloodiness, p.lower_torso_bloodiness, p.left_hand_bloodiness,
                       p.right_hand_bloodiness, p.left_forearm_bloodiness, p.right_forearm_bloodiness,
                       p.left_upperarm_bloodiness, p.right_upperarm_bloodiness, p.head_bloodiness,
                       p.neck_bloodiness, p.groin_bloodiness, p.left_thigh_bloodiness,
                       p.right_thigh_bloodiness, p.left_shin_bloodiness, p.right_shin_bloodiness,
                       p.left_foot_bloodiness, p.right_foot_bloodiness, p.back_bloodiness]

        body_part_dict = {
            0: 'Chest',
            1: 'Stomach',
            2: 'HandL',
            3: 'HandR',
            4: 'LArmL',
            5: 'LArmR',
            6: 'UArmL',
            7: 'UArmR',
            8: 'Head',
            9: 'Neck',
            10: 'Groin',
            11: 'ULegL',
            12: 'ULegR',
            13: 'LLegL',
            14: 'LLegR',
            15: 'FootL',
            16: 'FootR',
            17: 'Back'
        }

        index = 0
        for blood in blood_props:
            if blood != 0:
                self.blood_textures.append((overlay_masks.get(body_part_dict[index]).texture_path, blood))
            index = index + 1

        return ({'FINISHED'})

    def generate_bloodiness_texture(self, context):

        p = context.active_object.pz_human_props

        generated_image = bpy.data.images.get(
            'MASK-MaskData (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData (' + str(p.rig_instance) + ')', 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )

        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the red channel
        generated_pixels[0::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        blood_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.blood_textures:
            blood_texture = bpy.data.images.load(tex_path[0])
            blood_texture.scale(256, 256)
            
            blood_texture.pixels.foreach_get(blood_pixels)
            blood_rgba = blood_pixels.reshape(-1, 4)

            blood_alpha = blood_rgba[:, 3:4] * tex_path[1]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + blood_alpha * (1.0 - generated_alpha)
            red = (blood_rgba[:, 0:1] * blood_alpha + generated_rgba[:,0:1])

            generated_rgba[:, 0:1] = red

            blood_texture.user_clear()
            bpy.data.images.remove(blood_texture)

        generated_image.pixels.foreach_set(generated_pixels)
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        if addon_prefs.pz_directory != '':
            self.get_blood_textures(context)
            self.generate_bloodiness_texture(context)

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})