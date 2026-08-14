# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel
from .PZ_UI_HumanRig_BodySubpanel import draw_body_subpanel
from .PZ_UI_HumanRig_InjurySubpanel import draw_injury_subpanel
from .PZ_UI_HumanRig_ClothingSubpanel import draw_clothing_subpanel
from .PZ_UI_HumanRig_HairSubpanel import draw_hair_subpanel
from .PZ_UI_HumanRig_OutfitsSubpanel import draw_outfits_subpanel
from .PZ_UI_HumanRig_ShadingSubpanel import draw_shading_subpanel
from .PZ_UI_HumanRig_DebugSubpanel import draw_debug_subpanel

from ...Utility.PZ_AssetMethods import directx_import_available

class PZ_UI_HumanRig_RigPropertiesPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_model_panel"
    bl_label = "Rig Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    @classmethod
    def poll(cls, context):

        # Only show this panel if the rig is selected, and a relevant bone is selected
        if context.active_object:
            if context.active_object.get("rig_id") == "ZOMBOID_Human":
                return True
        return False

    def draw(self, context):

        # Get all data
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties

        # Get the initial layout
        layout = self.layout

        # The operator for resetting the model
        layout.operator('zomboid.reset_model')

        # Warning if the DirectX importer is not enabled/installed
        sub_column = layout.column(align=True)
        sub_column.scale_y = 0.7
        if not directx_import_available():
            sub_column.label(text='The .x importer extension is not installed or enabled.', icon='WARNING_LARGE')
            sub_column.label(text='         The link to it is on the rig GitHub.')
            sub_column.separator(factor=2.0)

        # Warning if the asset references have not been obtained
        if not addon_data.references_obtained:
            sub_column.label(text='Zomboid\'s asset references have not been', icon='WARNING_LARGE')
            sub_column.label(text='         obtained yet. In the \'Assets\' panel in the')
            sub_column.label(text='         \'Zomboid\' tab, assign your PZ directory and')
            sub_column.label(text='         press \'Get References\'.')
            sub_column.separator(factor=2.0)

        # Draw the various sub panels
        draw_body_subpanel(context, layout)
        draw_hair_subpanel(context, layout)
        draw_clothing_subpanel(context, layout)
        if model_properties.human_subtype != 'SKELETON':
            draw_injury_subpanel(context, layout)
        draw_outfits_subpanel(context, layout)
        layout.separator(type='LINE')
        draw_shading_subpanel(context, layout)

        # Show the properties for the visibility masks if debug is enabled
        if addon_data.debug:
            layout.separator(type='LINE')
            draw_debug_subpanel(context, layout)
            
