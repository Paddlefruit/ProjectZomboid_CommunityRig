# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_ZombieInjuryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)

def draw_injury_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    injury_properties = context.active_object.pz_injury_properties
    model_properties = context.active_object.pz_model_properties

    pz_icons = context.window_manager.pz_icons

    # Draw the panel
    panel, panel_area = layout.panel("injury_subpanel", default_closed=True)
    panel.label(text='Injuries')

    if panel_area:

        panel_area.operator('zomboid.remove_all_body_damage', text='Remove All')
        
        split = panel_area.split()
        left_column = split.column()
        right_column = split.column()

        def create_injury_spot(label, property_name, column, skip_injury=False):
            column.label(text=label)
            box = column.box()
            box.prop(injury_properties, property_name + '_bloodiness', text='Bloodiness')
            box.prop(injury_properties, property_name + '_dirtiness', text='Dirtiness')
            if not skip_injury:
                subrow = box.split(factor=0.25)
                subrow.label(text='Injury:')
                subrow.prop(injury_properties, property_name + '_injury', text='')

        create_injury_spot('Head', 'head', left_column)
        create_injury_spot('Neck', 'neck', right_column)

        create_injury_spot('Lower Torso', 'lower_torso', left_column)
        create_injury_spot('Upper Torso', 'upper_torso', right_column)

        create_injury_spot('Left Hand', 'left_hand', left_column)
        create_injury_spot('Right Hand', 'right_hand', right_column)

        create_injury_spot('Left Upper Arm', 'left_upperarm', left_column)
        create_injury_spot('Right Upper Arm', 'right_upperarm', right_column)

        create_injury_spot('Left Forearm', 'left_forearm', left_column)
        create_injury_spot('Right Forearm', 'right_forearm', right_column)

        create_injury_spot('Left Thigh', 'left_thigh', left_column)
        create_injury_spot('Right Thigh', 'right_thigh', right_column)

        create_injury_spot('Left Shin', 'left_shin', left_column)
        create_injury_spot('Right Shin', 'right_shin', right_column)

        create_injury_spot('Left Foot', 'left_foot', left_column)
        create_injury_spot('Right Foot', 'right_foot', right_column)

        create_injury_spot('Groin', 'groin', left_column)
        create_injury_spot('Back', 'back', right_column, skip_injury=True)

        subpanel, subpanel_area = layout.panel("zombie_injuries_subpanel", default_closed=True)
        subpanel.label(text='Zombie Injuries')

        if subpanel_area:

            subpanel_area.prop(injury_properties, 'selected_zombie_injury')
            subpanel_area.template_list("PZ_UL_ZombieInjuryList", "pz_zombie_injury_list", context.object, "pz_zombie_injuries", injury_properties, "zombie_injury_active_index")

            if injury_properties.zombie_injury_active_index != -1:
                subpanel_area.operator('zomboid.remove_zombie_injury')

        layout.separator(factor=0.5)

        # The randomization popover
        subrow = layout.row()
        subrow.scale_y = 2.0
        subrow.popover(panel='VIEW3D_PT_pz_human_rig_random_injury_popover', text='Randomization', icon_value=pz_icons["pz_random_icon"].icon_id)

