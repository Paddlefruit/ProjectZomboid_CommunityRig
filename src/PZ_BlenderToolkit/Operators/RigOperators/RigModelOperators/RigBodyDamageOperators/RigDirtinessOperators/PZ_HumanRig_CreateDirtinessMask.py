# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import numpy as np
from bpy.types import Operator

class PZ_HumanRig_CreateDirtinessMask(Operator):

    '''
    This operator will draw the full dirtiness mask texture that combines all of 
    the body part health location masks at a specified intensity from 0.0 to 2.0 for each.
    It draws it to each rig's specific MaskData texture on the green channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_dirtiness_mask"
    bl_label = "Create Dirtiness Mask"
    bl_description = "Create a combined dirt mask from the blood mask textures"

    dirt_textures = []

    def get_dirt_textures(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        injury_properties = context.active_object.pz_injury_properties
        overlay_masks = addon_data.pz_overlay_mask_references

        self.dirt_textures.clear()

        dirt_props = [injury_properties.upper_torso_dirtiness, injury_properties.lower_torso_dirtiness, injury_properties.left_hand_dirtiness,
                      injury_properties.right_hand_dirtiness, injury_properties.left_forearm_dirtiness, injury_properties.right_forearm_dirtiness,
                      injury_properties.left_upperarm_dirtiness, injury_properties.right_upperarm_dirtiness, injury_properties.head_dirtiness,
                      injury_properties.neck_dirtiness, injury_properties.groin_dirtiness, injury_properties.left_thigh_dirtiness,
                      injury_properties.right_thigh_dirtiness, injury_properties.left_shin_dirtiness, injury_properties.right_shin_dirtiness,
                      injury_properties.left_foot_dirtiness, injury_properties.right_foot_dirtiness, injury_properties.back_dirtiness]

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
        for dirt in dirt_props:
            if dirt != 0:
                self.dirt_textures.append((overlay_masks.get(body_part_dict[index]).texture_path, dirt))
            index = index + 1

        return ({'FINISHED'})

    def generate_dirtiness_texture(self, context):

        main_properties = context.active_object.pz_main_properties
        object_pointers = context.active_object.pz_object_pointers

        instance_str = main_properties.get_instance_str(context)

        generated_image = object_pointers.mask_data_image
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData' + instance_str, 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )
            object_pointers.mask_data_image = generated_image

        # Assign the image to the body material node tree
        if object_pointers.body_material:
            object_pointers.body_material.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the green channel
        generated_pixels[1::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        dirt_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.dirt_textures:
            dirt_texture = bpy.data.images.load(tex_path[0])
            dirt_texture.scale(256, 256)

            dirt_texture.pixels.foreach_get(dirt_pixels)
            dirt_rgba = dirt_pixels.reshape(-1, 4)

            dirt_alpha = dirt_rgba[:, 3:4] * tex_path[1]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + dirt_alpha * (1.0 - generated_alpha)
            green = (dirt_rgba[:, 1:2] * dirt_alpha + generated_rgba[:,1:2])

            generated_rgba[:, 1:2] = green

            dirt_texture.user_clear()
            bpy.data.images.remove(dirt_texture)

        generated_image.pixels.foreach_set(generated_rgba.flatten())
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if addon_data.pz_directory != '':
            self.get_dirt_textures(context)
            self.generate_dirtiness_texture(context)
            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})