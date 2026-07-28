# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_MainPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_label = "Rig Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        try:
            return context.active_object.get("rig_id") == "ZOMBOID_Human"
        except:
            return False

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        layout.prop(p, 'rig_name')
        
        # layout.prop(p, 'debug_toggle')

     #   layout.operator('zomboid.duplicate_rig')
        layout.operator('zomboid.remove_rig')

        if addon_prefs.debug:
            layout.prop(p, 'rig_instance')

            layout.prop(p, 'rig_collection')
            layout.prop(p, 'male_body_object')
            layout.prop(p, 'translation_data_empty')
            layout.prop(p, 'dummy01_empty')

            layout.separator()

            layout.prop(p, 'body_mat')
            layout.prop(p, 'mask_tex')
            layout.prop(p, 'body_tex')

            layout.separator()

            layout.prop(p, 'current_male_hair_style')
            layout.prop(p, 'current_beard_style')
            layout.prop(p, 'current_female_hair_style')
            layout.prop(p, 'current_hat_category')

            layout.separator()

            layout.prop(p, 'body_texture_slot_active_index')
            layout.prop(p, 'clothing_model_active_index')
            layout.prop(p, 'accessory_model_active_index')
