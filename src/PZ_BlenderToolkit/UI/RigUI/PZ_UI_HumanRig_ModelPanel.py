# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel
from ...Utility.PZ_AssetMethods import directx_import_available

class PZ_HumanRig_ModelPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_model_panel"
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    # def draw(self, context):
    #     addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    #     p = context.active_object.pz_human_props

    #     layout = self.layout

    def draw(self, context):
        layout = self.layout
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        main_column = layout.column()

        column = main_column.column()

        sub_column = column.column(align=True)
        sub_column.scale_y = 0.7
        if not directx_import_available():
            sub_column.label(text='The .x importer extension is not installed or enabled.', icon='WARNING_LARGE')
            sub_column.label(text='         The link to it is on the rig GitHub.')
            sub_column.separator(factor=2.0)

        if not addon_prefs.assets_parsed:
            sub_column.label(text='Zomboid\'s assets have not been parsed yet.', icon='WARNING_LARGE')
            sub_column.label(text='         In the Properties Editor, open the \'Scene\' tab,')
            sub_column.label(text='         then find the \'Zomboid Assets\' panel.')
            sub_column.label(text='         Assign the path to your Project Zomboid install')
            sub_column.label(text='         in \'Directories\', then click \'Parse All Assets\'')
            sub_column.label(text='         in \'Assets\'.')
            sub_column.separator(factor=2.0)

        row = column.row()
        row.operator('zomboid.reset_model')

        column.separator(factor=2.0)

        row = column.row()
        
        row.scale_y = 1.5
        row.prop(p, "model_sex", expand=True)

        row = column.row()
        row.enabled = addon_prefs.assets_parsed and directx_import_available()
        row.prop(p, 'skin_set')

        column.separator(factor=2)

        row = column.row()
        row.enabled = addon_prefs.assets_parsed and directx_import_available()
        row.prop_search(p, 'selected_clothing_item',
                        addon_prefs, 'pz_human_clothing_item_slots')

        row = column.row()
        row.operator('zomboid.remove_all_clothing_items')

        column.separator(factor=2)

        subpanel, panel_area = column.panel(
            "body_model_subpanel", default_closed=False)
        subpanel.label(text='Body')

        icon = "HIDE_OFF" if p.show_body else "HIDE_ON"
        subpanel.prop(p, "show_body", text='', icon=icon)

        if p.show_body and panel_area:
            box = panel_area.box()
            column = box.column()
            column.enabled = addon_prefs.assets_parsed and directx_import_available()

            if p.skin_set != 'SKELETON':

                if p.debug_toggle:
                    column.label(text="Body Masks")
                    column.separator(factor=0.5)

                    subcolumn = column.column(align=True)

                    row = subcolumn.row(align=True)
                    for index in range(6):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    row = subcolumn.row(align=True)
                    for index in range(6, 12):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    row = subcolumn.row(align=True)
                    for index in range(12, 17):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    subcolumn.separator()
                    column.separator(factor=3, type='LINE')
            
            column.label(text="Skin Texture")
            column.separator(factor=0.5)

            box = column.box()
            sub_col = box.column()
            row = sub_col.row()

            match p.skin_set:
                case 'HUMAN':
                    row.prop(p, "skin_color")
                    row.prop(p, "zombification")
                    if p.model_sex == 'MALE':
                        row = sub_col.row()
                        row.prop(p, 'chest_hair')
                    column.separator(factor=3, type='LINE')
                case 'SKELETON':
                    row.prop(p, "skeleton_type")
                    column.separator(factor=3, type='LINE')
                case 'MANNEQUIN':
                    row.prop(p, "mannequin_type")
                    column.separator(factor=3, type='LINE')

            if p.skin_set == 'HUMAN':

                column.label(text="Body Damage")
                column.separator(factor=0.5)

                box = column.box()

                body_injury_subpanel, body_injury_panel_area = box.panel(
                    "body_injury_subpanel", default_closed=False)
                body_injury_subpanel.label(text='Body Injuries')

                if body_injury_panel_area:
                    sub_col = body_injury_panel_area.column()
                    sub_col.prop(p, 'upper_torso_injury')
                    sub_col.prop(p, 'lower_torso_injury')
                    sub_col.prop(p, 'left_hand_injury')
                    sub_col.prop(p, 'right_hand_injury')
                    sub_col.prop(p, 'left_forearm_injury')
                    sub_col.prop(p, 'right_forearm_injury')
                    sub_col.prop(p, 'left_upperarm_injury')
                    sub_col.prop(p, 'right_upperarm_injury')
                    sub_col.prop(p, 'head_injury')
                    sub_col.prop(p, 'neck_injury')
                    sub_col.prop(p, 'groin_injury')
                    sub_col.prop(p, 'left_thigh_injury')
                    sub_col.prop(p, 'right_thigh_injury')
                    sub_col.prop(p, 'left_shin_injury')
                    sub_col.prop(p, 'right_shin_injury')
                    sub_col.prop(p, 'left_foot_injury')
                    sub_col.prop(p, 'right_foot_injury')

                    sub_box = sub_col.box()

                    sub_box.prop(p, 'random_scratch_chance')
                    sub_box.prop(p, 'random_laceration_chance')
                    sub_box.prop(p, 'random_bite_chance')
                    sub_box.prop(p, 'random_bandage_chance')
                    sub_box.prop(p, 'random_bloody_bandage_chance')

                    row = sub_box.row()
                    row.prop(p, 'random_injury_intensity')
                    row.operator('zomboid.randomize_body_injuries')

                    sub_col.operator('zomboid.remove_all_body_injuries')

                zombie_injury_subpanel, zombie_injury_panel_area = box.panel(
                    "zombie_injury_subpanel", default_closed=False)
                zombie_injury_subpanel.label(text='Zombie Injuries')

                if zombie_injury_panel_area:
                    sub_col = zombie_injury_panel_area.column()
                    sub_col.prop(p, 'selected_zombie_injury')
                    sub_col.template_list("PZ_UL_ZombieInjuryList", "pz_zombie_injury_list", context.object,
                                          "pz_human_zombie_injuries", context.object.pz_human_props, "zombie_injury_active_index")
                    if p.zombie_injury_active_index != -1:
                        sub_col.operator('zomboid.remove_zombie_injury')

                    row = sub_col.row()
                    row.prop(p, 'random_zombie_injury_intensity')
                    row.operator('zomboid.randomize_zombie_injuries')
                    sub_col.operator('zomboid.remove_all_zombie_injuries')

            if p.skin_set != 'SKELETON':

                bloodiness_subpanel, bloodiness_panel_area = box.panel(
                    "bloodiness_subpanel", default_closed=False)
                bloodiness_subpanel.label(text='Bloodiness')

                if bloodiness_panel_area:
                    sub_col = bloodiness_panel_area.column()
                    sub_col.prop(p, 'upper_torso_bloodiness')
                    sub_col.prop(p, 'lower_torso_bloodiness')
                    sub_col.prop(p, 'left_hand_bloodiness')
                    sub_col.prop(p, 'right_hand_bloodiness')
                    sub_col.prop(p, 'left_forearm_bloodiness')
                    sub_col.prop(p, 'right_forearm_bloodiness')
                    sub_col.prop(p, 'left_upperarm_bloodiness')
                    sub_col.prop(p, 'right_upperarm_bloodiness')
                    sub_col.prop(p, 'head_bloodiness')
                    sub_col.prop(p, 'neck_bloodiness')
                    sub_col.prop(p, 'groin_bloodiness')
                    sub_col.prop(p, 'left_thigh_bloodiness')
                    sub_col.prop(p, 'right_thigh_bloodiness')
                    sub_col.prop(p, 'left_shin_bloodiness')
                    sub_col.prop(p, 'right_shin_bloodiness')
                    sub_col.prop(p, 'left_foot_bloodiness')
                    sub_col.prop(p, 'right_foot_bloodiness')
                    sub_col.prop(p, 'back_bloodiness')

                    row = sub_col.row()
                    row.prop(p, 'random_bloodiness_intensity')
                    row.operator('zomboid.randomize_bloodiness')
                    sub_col.operator('zomboid.remove_body_bloodiness')

                dirtiness_subpanel, dirtiness_panel_area = box.panel(
                    "dirtiness_subpanel", default_closed=False)
                dirtiness_subpanel.label(text='Dirtiness')

                if dirtiness_panel_area:
                    sub_col = dirtiness_panel_area.column()
                    sub_col.prop(p, 'upper_torso_dirtiness')
                    sub_col.prop(p, 'lower_torso_dirtiness')
                    sub_col.prop(p, 'left_hand_dirtiness')
                    sub_col.prop(p, 'right_hand_dirtiness')
                    sub_col.prop(p, 'left_forearm_dirtiness')
                    sub_col.prop(p, 'right_forearm_dirtiness')
                    sub_col.prop(p, 'left_upperarm_dirtiness')
                    sub_col.prop(p, 'right_upperarm_dirtiness')
                    sub_col.prop(p, 'head_dirtiness')
                    sub_col.prop(p, 'neck_dirtiness')
                    sub_col.prop(p, 'groin_dirtiness')
                    sub_col.prop(p, 'left_thigh_dirtiness')
                    sub_col.prop(p, 'right_thigh_dirtiness')
                    sub_col.prop(p, 'left_shin_dirtiness')
                    sub_col.prop(p, 'right_shin_dirtiness')
                    sub_col.prop(p, 'left_foot_dirtiness')
                    sub_col.prop(p, 'right_foot_dirtiness')
                    sub_col.prop(p, 'back_dirtiness')

                    row = sub_col.row()
                    row.prop(p, 'random_dirtiness_intensity')
                    row.operator('zomboid.randomize_dirtiness')
                    sub_col.operator('zomboid.remove_body_dirtiness')

                box.operator('zomboid.remove_all_body_damage')

                column.separator(factor=3, type='LINE')

            row = column.row()

            row.label(text="Body Clothing Textures")

            row = column.row(align=True)

            row.template_list("PZ_UL_BodyTextureList", "pz_body_texture_list", context.object,
                                "pz_human_body_texture_slots", context.object.pz_human_props, "body_texture_slot_active_index")

            side_column = row.column(align=True)

            if p.body_texture_slot_active_index != -1:
                side_column.operator(
                    "zomboid.remove_body_texture", text="", icon="REMOVE")

                column.separator()

                side_column.operator(
                    "zomboid.move_body_texture_up", icon="TRIA_UP", text="")
                side_column.operator(
                    "zomboid.move_body_texture_down", icon="TRIA_DOWN", text="")

            column.separator(factor=1.5)
            row = column.row()

            if p.body_texture_slot_active_index != -1:
                row.label(text="Current Slot Properties")
                t = context.active_object.pz_human_body_texture_slots[
                    p.body_texture_slot_active_index]

                box = column.box()
                column = box.column()

                row = column.row()
                row.prop(t, "tintable")
                if t.tintable:
                    row.prop(t, "tint_color")


        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "clothing_model_subpanel", default_closed=True)
        subpanel.label(text='Clothes')

        icon = "HIDE_OFF" if p.show_clothing else "HIDE_ON"
        subpanel.prop(p, "show_clothing", text ='', icon=icon)

        if panel_area and p.show_clothing:
            box = panel_area.box()
            column = box.column()
            column.enabled = addon_prefs.assets_parsed and directx_import_available()

            row = column.row()
            row.label(text="Clothing Models")
            column.separator(factor=0.5)

            row = column.row(align=True)
            side_column = row.column(align=True)

            side_column.template_list("PZ_UL_ClothingMeshList", "pz_clothing_mesh_list", context.object,
                                      "pz_clothing_models", context.object.pz_human_props, "clothing_model_active_index")

            side_column = row.column(align=True)

            if p.clothing_model_active_index != -1:
                side_column.operator(
                    "zomboid.remove_clothing_model", text="", icon="REMOVE")

            column.separator(factor=1.5)
            row = column.row()

            if p.clothing_model_active_index != -1:
                row.label(text="Current Slot Properties")
                m = context.active_object.pz_clothing_models[
                    p.clothing_model_active_index]

                box = column.box()
                column = box.column()

                row = column.row()
                row.prop(m, "tintable")
                if m.tintable:
                    row.prop(m, "tint_color")

        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "prop_model_subpanel", default_closed=True)
        subpanel.label(text='Props')

        icon = "HIDE_OFF" if p.show_props else "HIDE_ON"
        subpanel.prop(p, "show_props", text='', icon=icon)

        if panel_area and p.show_hair:
            box = panel_area.box()
            column = box.column()
            column.enabled = addon_prefs.assets_parsed and directx_import_available()

            row = column.row()
            row.label(text="Prop Models")
            column.separator(factor=0.5)

            row = column.row(align=True)
            side_column = row.column(align=True)

            side_column.template_list("PZ_UL_PropMeshList", "pz_prop_mesh_list", context.object,
                                      "pz_accessory_models", context.object.pz_human_props, "accessory_model_active_index")

            side_column = row.column(align=True)

            if p.accessory_model_active_index != -1:
                side_column.operator(
                    "zomboid.remove_accessory_model", text="", icon="REMOVE")

            column.separator(factor=1.5)
            row = column.row()

            if p.accessory_model_active_index != -1:
                row.label(text="Current Slot Properties")
                m = context.active_object.pz_accessory_models[p.accessory_model_active_index]

                box = column.box()
                column = box.column()

                row = column.row()
                row.prop(m, "tintable")
                if m.tintable:
                    row.prop(m, "tint_color")

        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "hair_model_subpanel", default_closed=True)
        subpanel.label(text='Hair')

        icon = "HIDE_OFF" if p.show_hair else "HIDE_ON"
        subpanel.prop(p, "show_hair", text='', icon=icon)

        if panel_area and p.show_hair:
            box = panel_area.box()
            column = box.column()
            column.enabled = addon_prefs.assets_parsed and directx_import_available()

            row = column.row()

            row.prop(p, 'hair_color')
            row.operator('zomboid.randomize_hair_color',
                         text='', icon='FILE_REFRESH')

            row = column.row()
            row.prop(p, 'darken_zombie_hair')

            column.separator(factor=1.5, type='LINE')

            row = column.row(align=True)

            if p.model_sex_index == 0:
                row.prop_search(p, 'selected_male_hair_style',
                                addon_prefs, 'pz_human_male_hair_styles')
                row.operator('zomboid.randomize_hair_model', text='',
                             icon='FILE_REFRESH').hair_type = 'M'

                column.separator()

                row = column.row(align=True)
                row.prop_search(p, 'selected_beard_style',
                                addon_prefs, 'pz_human_beard_styles')
                row.operator('zomboid.randomize_hair_model', text='',
                             icon='FILE_REFRESH').hair_type = 'B'
            else:
                row.prop_search(p, 'selected_female_hair_style',
                                addon_prefs, 'pz_human_female_hair_styles')
                row.operator('zomboid.randomize_hair_model', text='',
                             icon='FILE_REFRESH').hair_type = 'F'
            
            column.separator(factor=1.5, type='LINE')

            row = column.row()

            row.prop(p, 'hair_stubble')

            if p.model_sex == 'MALE':
                row.prop(p, 'beard_stubble')

        main_column.separator(factor=1.5)

        main_column.separator(factor=3.0)

        subpanel, panel_area = main_column.panel(
            "presets_subpanel", default_closed=False)
        subpanel.label(text='Outfits')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            column.enabled = addon_prefs.assets_parsed and directx_import_available()

            row = column.row()

            row.prop_search(p, 'selected_outfit', addon_prefs,
                            'pz_human_outfit_slots', item_search_property='search_name')

            row = column.row()

            row.prop(p, 'random_zombie')
            row.prop(p, 'random_skin_color')

            row = column.row()

            row.prop(p, 'random_tint_color')
            if not p.random_tint_color:
                row.prop(p, 'static_tint_color')

            row = column.row()

            row.prop(p, 'random_hair_style')
            row.prop(p, 'random_hair_color')

            row = column.row()

            row.prop(p, 'natural_hair_color')

            row = column.row()

            row.prop(p, 'random_beard_chance', slider=True)

            row = column.row()
            row.prop(p, 'randomize_injuries')

            if p.randomize_injuries:
                box = column.box()

                box.prop(p, 'random_bloodiness_intensity')
                box.prop(p, 'random_dirtiness_intensity')

                box.separator()

                box.prop(p, 'random_injury_intensity')
                box.prop(p, 'random_zombie_injury_intensity')

                box.separator()

                box.prop(p, 'random_scratch_chance')
                box.prop(p, 'random_laceration_chance')
                box.prop(p, 'random_bite_chance')

                box.separator()

                box.prop(p, 'random_bandage_chance')
                box.prop(p, 'random_bloody_bandage_chance')

            row = column.row()
            row.scale_y = 2.0

            row.operator('zomboid.apply_outfit')

            row = column.row()
            row.scale_y = 1.5

            row.operator('zomboid.apply_random_outfit')