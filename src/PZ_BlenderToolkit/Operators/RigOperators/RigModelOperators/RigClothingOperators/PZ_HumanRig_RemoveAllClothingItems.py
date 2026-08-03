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
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_accessory_models

        # Remove all existing clothing meshes
        for i in range(len(m_list)):
            bpy.ops.zomboid.remove_clothing_model()

        # Remove all existing accessory meshes
        for i in range(len(a_list)):
            bpy.ops.zomboid.remove_accessory_model()

        # Remove all existing body textures
        if self.halt_texture_updates:
            p.halt_texture_updates = True
        t_list.clear()
        p.body_texture_slot_active_index = -1

        if self.halt_texture_updates:
            p.halt_texture_updates = False
            bpy.ops.zomboid.create_body_texture()

        #TEMP
        context.active_object.pz_used_body_locations.clear()

        return ({'FINISHED'})