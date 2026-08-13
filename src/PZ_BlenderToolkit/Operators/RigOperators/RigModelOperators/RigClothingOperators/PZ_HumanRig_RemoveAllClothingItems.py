# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.props import BoolProperty

from bpy.types import Operator

class PZ_HumanRig_RemoveAllClothingItems(Operator):
    bl_idname = "zomboid.remove_all_clothing_items"
    bl_label = "Remove All Clothing Items"
    bl_description = "Removes all clothing items from the model"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        # Get all data
        model_properties = context.active_object.pz_model_properties
        equipped_clothing = context.active_object.pz_equipped_clothing_items

        # Set the pointer to the top of the clothing items, then call the remove operator for each one
        model_properties.equipped_clothing_item_active_index = len(equipped_clothing) - 1
        for i in range(len(equipped_clothing)):
            bpy.ops.zomboid.remove_clothing_item(stop_texture_updates=self.stop_texture_updates)

        bpy.ops.zomboid.create_body_texture()

        #TEMP
        context.active_object.pz_used_body_locations.clear()

        return ({'FINISHED'})