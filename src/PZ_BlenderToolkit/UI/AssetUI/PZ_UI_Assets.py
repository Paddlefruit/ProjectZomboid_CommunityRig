# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel, UIList
from .PZ_UI_ClothingItemsSubpanel import draw_clothing_items_subpanel
from .PZ_UI_OutfitsSubpanel import draw_outfits_subpanel
from .PZ_UI_HairStylesSubpanel import draw_hair_styles_subpanel

# The UI List of mod directories used
class PZ_UL_ModDirectoryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.prop(item, 'active', text='')

class PZ_HumanRig_AssetsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_assets_panel"
    bl_label = "Assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    def draw(self, context):

        # Get all data
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        # Create the initial layout
        layout = self.layout

        # The subpanel containing the main directories
        subpanel, subpanel_area = layout.panel("directories_subpanel", default_closed=False)
        subpanel.label(text='Directories')

        if subpanel_area:

            # The main Project Zomboid directory settings
            subpanel_area.label(text='Project Zomboid Directory')
            subpanel_area.separator(factor=0.5)

            exp_column = subpanel_area.column()
            exp_column.scale_y = 0.7
            exp_column.label(text='In Steam, select \'Manage\' on Project Zomboid in your library.', icon='QUESTION_LARGE')
            exp_column.label(text='        Then, go to the \'Installed Files\' tab. Click on \'Browse\'.')
            exp_column.label(text='        The directory it opens up to is the directory you should put here.')

            subpanel_area.prop(addon_data, 'pz_directory', text='')

            subpanel_area.separator()

            # The list of Project Zomboid mod directories
            subpanel_area.label(text='Mod Directories')

            subrow = subpanel_area.row()
            subrow.operator('zomboid.get_mod_directories', text='Get Mods')
            subrow.operator('zomboid.remove_mod_directories', text='Clear Mods')

            subpanel_area.template_list("PZ_UL_ModDirectoryList", "pz_mod_directory_list", addon_data, "pz_mod_directories", addon_data, "mod_directory_active_index")

        # The main operators that get or remove all references
        subrow = layout.row()
        subrow.scale_y = 1.5
        subrow.operator('zomboid.get_all_assets', text='Get References')

        layout.operator('zomboid.clear_all_assets', text='Clear References')

        if addon_data.debug:
            layout.label(text='References Obtained: ' + str(addon_data.references_obtained))

        # The subpanel that will store all of the reference lists
        subpanel, subpanel_area = layout.panel("references_subpanel", default_closed=True)
        subpanel.label(text='References')

        if subpanel_area:
            draw_clothing_items_subpanel(context, subpanel_area)
            draw_outfits_subpanel(context, subpanel_area)
            draw_hair_styles_subpanel(context, subpanel_area)




        
        

