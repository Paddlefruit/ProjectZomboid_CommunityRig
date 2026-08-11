# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveClothingItem(Operator):
    bl_idname = "zomboid.remove_clothing_item"
    bl_label = "Remove Clothing Item"
    bl_description = "Removes a clothing item from the model"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=False
    )

    def execute(self, context):
        # Get all data
        model_properties = context.active_object.pz_model_properties

        equipped_clothing = context.active_object.pz_equipped_clothing_items
        clothing_to_remove = equipped_clothing[model_properties.equipped_clothing_item_active_index]

        # Store the clothing type for future use
        clothing_type = clothing_to_remove.data.clothing_type
            
        # Remove the model objects, if they exist
        if clothing_to_remove.male_model_object:
            data = clothing_to_remove.male_model_object.data
            bpy.data.objects.remove(clothing_to_remove.male_model_object, do_unlink=True)
            if data:
                bpy.data.meshes.remove(data, do_unlink=True)
        if clothing_to_remove.female_model_object:
            data = clothing_to_remove.female_model_object.data
            bpy.data.objects.remove(clothing_to_remove.female_model_object, do_unlink=True)
            if data:
                bpy.data.meshes.remove(data, do_unlink=True)

        # Remove the material, if it exists
        if clothing_to_remove.material:
            bpy.data.materials.remove(clothing_to_remove.material, do_unlink=True)

        # Remove the image, if it exists
        if clothing_to_remove.image:
            bpy.data.images.remove(clothing_to_remove.image, do_unlink=True)

        # Check the visibility masks on the rig
        if clothing_type == 'CLOTHINGMODEL':

            # Temporarily pause automatic updating of the visibility mask, if toggle is enabled
            if self.stop_texture_updates:
                model_properties.stop_texture_updates = True

            # Update masks on rig
            for i in range(len(model_properties.visibility_mask_array)):
                test = False
                for j in range(len(equipped_clothing) - 1):
                    if equipped_clothing[j].data.visibility_mask_array[i] == True:
                        test = True
                        break
                model_properties.visibility_mask_array[i] = test
                model_properties.visibility_mask_array[i] = model_properties.visibility_mask_array[i]
    
            if self.stop_texture_updates:
                model_properties.stop_texture_updates = False
                bpy.ops.zomboid.create_visibility_mask()

        # Recreate the body texture if the toggle is enabled, and the clothing removed was a body texture
        if clothing_type == 'BODYTEXTURE' and not self.stop_texture_updates:
            bpy.ops.zomboid.create_body_texture()

        # Remove this clothing item data from the rig
        equipped_clothing.remove(model_properties.equipped_clothing_item_active_index)
        model_properties.equipped_clothing_item_active_index -= 1

        # If this clothing item wasn't the last in the list, adjust the indicies of all higher clothing items

        return({'FINISHED'})