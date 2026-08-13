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
        main_properties = context.active_object.pz_main_properties
        model_properties = context.active_object.pz_model_properties

        equipped_clothing = context.active_object.pz_equipped_clothing_items
        clothing_to_remove = equipped_clothing[model_properties.equipped_clothing_item_active_index]

        instance_str = main_properties.get_instance_str(context)

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

        # Remove this clothing item data from the rig
        equipped_clothing.remove(model_properties.equipped_clothing_item_active_index)

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
        
        # If this clothing item wasn't the last in the list, adjust the indicies of all higher clothing items
        successive_clothing = [item for index, item in enumerate(equipped_clothing) if index > model_properties.equipped_clothing_item_active_index - 1]
        for index, clothing in enumerate(successive_clothing):

            # Change the names of the data objects if applicable
            if clothing.data.clothing_type != 'BODYTEXTURE':
                if clothing.male_model_object:
                    clothing.male_model_object.name = 'OBJ-MaleClothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                    if clothing.male_model_object.data:
                        clothing.male_model_object.data.name = 'GEO-MaleClothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                if clothing.female_model_object:
                    clothing.female_model_object.name = 'OBJ-FemaleClothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                    if clothing.female_model_object.data:
                        clothing.female_model_object.data.name = 'GEO-FemaleClothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str

                if clothing.image:
                    if clothing.data.clothing_type == 'CLOTHINGMODEL':
                        clothing.image.name = 'TEX-Clothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                    else: 
                        clothing.image.name = 'TEX-Accessory' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str

                if clothing.material:
                    if clothing.data.clothing_type == 'CLOTHINGMODEL':
                        clothing.material.name = 'MAT-Clothing' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                    else: 
                        clothing.material.name = 'MAT-Accessory' + str(model_properties.equipped_clothing_item_active_index + index) + instance_str
                
                    # Update the material color drivers
                    for fcurve in clothing.material.node_tree.animation_data.drivers:
                        driver = fcurve.driver
                        target = driver.variables[0].targets[0]

                        old_path = 'pz_equipped_clothing_items[' + str(model_properties.equipped_clothing_item_active_index + index + 1) + ']'
                        new_path = 'pz_equipped_clothing_items[' + str(model_properties.equipped_clothing_item_active_index + index) + ']'

                        target.data_path = target.data_path.replace(old_path, new_path)

                        clothing.material.node_tree.update_tag()

                        # Redraw the viewport
                        for area in context.window.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()

                        context.active_object.update_tag()


        model_properties.equipped_clothing_item_active_index -= 1

        return({'FINISHED'})