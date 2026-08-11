# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import numpy as np
from bpy.types import Operator

class PZ_HumanRig_CreateVisibilityMask(Operator):

    '''
    This operator will draw the full visibility mask texture from the 17 different mask options
    used in game. It draws it to each rig's specific MaskData texture on the blue channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_visibility_mask"
    bl_label = "Create Visibility Mask"
    bl_description = "Create a visibility mask image from the mask textures"

    mask_textures = []

    def get_mask_textures(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        visibility_masks = addon_data.pz_visibility_mask_references

        model_properties = context.active_object.pz_model_properties

        self.mask_textures.clear()

        mask_dict = {
            0: "Head",
            1: "Chest",
            2: "Crotch",
            3: "LeftArm",
            4: "LeftHand",
            5: "RightArm",
            6: "RightHand",
            7: "LeftLeg",
            8: "LeftFoot",
            9: "RightLeg",
            10: "RightFoot",
            11: "Dress",
            12: "Chest",
            13: "Waist",
            14: "Belt",
            15: "Crotch",
            16: "FullBody"
        }

        index = 0
        for hide in model_properties.visibility_mask_array:
            if hide:
                self.mask_textures.append(visibility_masks.get(mask_dict[index]).texture_path)
            index = index + 1

        return ({'FINISHED'})

    def generate_mask_texture(self, context):
        main_properties = context.active_object.pz_main_properties
        model_properties = context.active_object.pz_model_properties
        object_pointers = context.active_object.pz_object_pointers

        generated_image = bpy.data.images.get('MASK-MaskData' + main_properties.get_instance_str(context))
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData' + main_properties.get_instance_str(context), 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )

        # Assign the image to the body material node tree
        if object_pointers.body_material:
            object_pointers.body_material.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the blue channel
        generated_pixels[2::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        mask_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.mask_textures:
            mask_texture = bpy.data.images.load(tex_path)
            mask_texture.scale(256, 256)

            mask_texture.pixels.foreach_get(mask_pixels)
            mask_rgba = mask_pixels.reshape(-1, 4)

            mask_alpha = mask_rgba[:, 3:4]

            generated_rgba[:, 2:3] += mask_alpha
            #generated_rgba[:, 3:4] += mask_alpha

            mask_texture.user_clear()
            bpy.data.images.remove(mask_texture)

        generated_image.pixels.foreach_set(generated_pixels)
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if addon_data.pz_directory != '':
            self.get_mask_textures(context)
            self.generate_mask_texture(context)
            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})