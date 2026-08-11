# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_UI_HumanRig_RandomInjuryPopover(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_random_injury_popover"
    bl_label = "Rig Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'INSTANCED'}

    bl_ui_units_x = 23

    def draw(self, context):

        # Get all data
        injury_properties = context.active_object.pz_injury_properties
        random_properties = context.active_object.pz_random_properties

        pz_icons = context.window_manager.pz_icons

        # Get the initial layout
        layout = self.layout

        # Randomization settings for body part injuries
        split = layout.split()

        # Body Injury and Zombie Injury Column
        column = split.column()

        subrow = column.row()
        subrow.label(text='Randomize Body Injuries')
        subrow.prop(random_properties, 'randomize_body_injuries', text='')

        subrow = column.row(align=True)
        subrow.enabled = random_properties.randomize_body_injuries
        subrow.prop(random_properties, 'min_random_body_injuries', text='Min')
        subrow.prop(random_properties, 'max_random_body_injuries', text='Max')

        box = column.box()
        box.enabled = random_properties.randomize_body_injuries
        box.label(text='Injury Type Chances')
        subcolumn = box.column(align=True)
        subcolumn.prop(random_properties, 'random_scratch_chance', text='Scratch')
        subcolumn.prop(random_properties, 'random_laceration_chance', text='Laceration')
        subcolumn.prop(random_properties, 'random_bite_chance', text='Bite')
        box.separator()
        subcolumn = box.column(align=True)
        subcolumn.prop(random_properties, 'random_bandage_chance', text='Bandage')
        subcolumn.prop(random_properties, 'random_bloody_bandage_chance', text='Bandage is Bloody')

        column.separator(type='LINE')

        subrow = column.row()
        subrow.label(text='Randomize Zombie Injuries')
        subrow.prop(random_properties, 'randomize_zombie_injuries', text='')

        subrow = column.row(align=True)
        subrow.enabled = random_properties.randomize_zombie_injuries
        subrow.prop(random_properties, 'min_random_zombie_injuries', text='Min')
        subrow.prop(random_properties, 'max_random_zombie_injuries', text='Max')

        # Bloodiness and Dirtiness Column
        column = split.column()

        subrow = column.row()
        subrow.label(text='Randomize Bloodiness')
        subrow.prop(random_properties, 'randomize_bloodiness', text='')

        subcolumn = column.row()
        subcolumn.enabled = random_properties.randomize_bloodiness
        subcolumn.prop(random_properties, 'part_bloodiness_chance')

        subrow = column.row(align=True)
        subrow.enabled = random_properties.randomize_bloodiness
        subrow.prop(random_properties, 'min_random_bloodiness', text='Min')
        subrow.prop(random_properties, 'max_random_bloodiness', text='Max')

        column.separator(type='LINE')

        subrow = column.row()
        subrow.label(text='Randomize Dirtiness')
        subrow.prop(random_properties, 'randomize_dirtiness', text='')

        subcolumn = column.row()
        subcolumn.enabled = random_properties.randomize_dirtiness
        subcolumn.prop(random_properties, 'part_dirtiness_chance')

        subrow = column.row(align=True)
        subrow.enabled = random_properties.randomize_dirtiness
        subrow.prop(random_properties, 'min_random_dirtiness', text='Min')
        subrow.prop(random_properties, 'max_random_dirtiness', text='Max')

        # The Injury Randomization Operator
        subrow = layout.row()
        subrow.scale_y = 1.5
        subrow.operator('zomboid.randomize_body_damage', icon_value=pz_icons["pz_random_icon"].icon_id)