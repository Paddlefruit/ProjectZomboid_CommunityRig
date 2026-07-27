# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_DirectoriesPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_directories_panel"
    bl_label = "Directories"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_global_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        sub_column = layout.column(align=True)
        sub_column.scale_y = 0.7
        
        sub_column.label(text='In Steam, select \'Manage\' on Project Zomboid in your library.', icon='QUESTION_LARGE')
        sub_column.label(text='        Then, go to the \'Installed Files\' tab. Click on \'Browse\'.')
        sub_column.label(text='        The directory it opens up to is the directory you should put here.')

        layout.separator(factor=0.5)

        column = layout.column()

        column.prop(addon_prefs, "pz_directory")

        column.separator(factor=5, type='LINE')

        column.label(text="Mod Directories (EXPERIMENTAL)")

        column.separator(factor=0.5)

        row = column.row()

        row.operator('zomboid.get_mod_directories')
        row.operator('zomboid.remove_mod_directories')

        row = column.row(align=True)

        row.template_list("PZ_UL_ModDirectoryList", "pz_mod_directory_list", addon_prefs,
                          "pz_human_mod_directory_slots", addon_prefs, "mod_directory_slot_active_index")

        if addon_prefs.mod_directory_slot_active_index != -1:
        
            dir_prop = addon_prefs.pz_human_mod_directory_slots[addon_prefs.mod_directory_slot_active_index]

            box = column.box()

            box.label(
                text='Mod Author:                                            ' + dir_prop.author)
            box.label(text='Latest PZ Version:                                   ' +
                      str(round(dir_prop.latest_pz_version, 2)))
            box.prop(dir_prop, 'mod_dir')

        column.separator()