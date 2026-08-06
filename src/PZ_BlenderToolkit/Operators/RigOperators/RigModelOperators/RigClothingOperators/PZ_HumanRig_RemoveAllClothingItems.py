# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.props import BoolProperty

from bpy.types import Operator

class PZ_HumanRig_RemoveAllClothingItems(Operator):
    bl_idname = "zomboid.remove_all_clothing_items"
    bl_label = "Remove All Clothing Items"
    bl_description = "Removes all clothing items from the model"
    bl_options = {'REGISTER', 'UNDO'}

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        # Get all data
        p = context.active_object.pz_human_props
        equipped_clothing = context.active_object.pz_equipped_clothing_items

        # Set the pointer to the top of the clothing items, then call the remove operator for each one
        p.equipped_clothing_item_active_index = len(equipped_clothing) - 1
        for i in range(len(equipped_clothing)):
            bpy.ops.zomboid.remove_clothing_item(halt_texture_updates=self.halt_texture_updates)

        #TEMP
        context.active_object.pz_used_body_locations.clear()

        return ({'FINISHED'})