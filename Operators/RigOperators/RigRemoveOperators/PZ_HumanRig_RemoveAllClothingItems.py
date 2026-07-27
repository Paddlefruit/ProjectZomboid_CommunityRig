# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.props import BoolProperty

from bpy.types import Operator, Collection

class PZ_HumanRig_RemoveAllClothingItems(Operator):
    bl_idname = "zomboid.remove_all_clothing_items"
    bl_label = "Remove All Clothing Items"
    bl_description = "Removes all clothing items from the model"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_human_prop_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        # Remove all existing clothing meshes
        # self.remove_all_objs_from_col(bpy.data.collections.get("GEO-PZ_Human_Male_Clothes" + instance_str))
        # self.remove_all_objs_from_col(bpy.data.collections.get("GEO-PZ_Human_Female_Clothes" + instance_str))
         
        for i in range(len(m_list)):
            bpy.ops.zomboid.remove_clothing_model()

        # Remove all existing prop meshes
        # self.remove_all_objs_from_col(bpy.data.collections.get("GEO-PZ_Human_Male_Props" + instance_str))
        # self.remove_all_objs_from_col(bpy.data.collections.get("GEO-PZ_Human_Female_Props" + instance_str))
         
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

        

        return ({'FINISHED'})