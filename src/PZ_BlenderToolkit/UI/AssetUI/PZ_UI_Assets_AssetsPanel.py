# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_AssetsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_assets_panel"
    bl_label = "Assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_global_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        main_column = layout.column()

        main_column.operator('zomboid.get_all_assets')
        main_column.operator('zomboid.clear_all_assets')

        # ------------------------------------------------------------------------#
        #  Clothing Items
        
        subpanel, panel_area = main_column.panel(
            "clothing_items_subpanel", default_closed=True)
        subpanel.label(text='Clothing Items')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row(align=True)

            row.template_list("PZ_UL_ClothingItemList", "pz_clothing_item_list", addon_prefs,
                              "pz_human_clothing_item_slots", addon_prefs, "clothing_item_slot_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.clothing_item_slot_active_index != -1:
                row.label(text="Clothing Item Properties")
                item_prop = addon_prefs.pz_human_clothing_item_slots[
                    addon_prefs.clothing_item_slot_active_index]

                box = column.box()
                split = box.split()
                sub_column = split.column()

                sub_column.label(
                    text="GUID:                             " + item_prop.guid
                )
                sub_column.label(
                    text="Male Model Path:         " + item_prop.male_model_path
                )
                sub_column.label(
                    text="Female Model Path:     " + item_prop.female_model_path
                )
                sub_column.label(
                    text="Male Alt Model Path:         " + item_prop.male_alt_model_path
                )
                sub_column.label(
                    text="Female Alt Model Path:     " + item_prop.female_alt_model_path
                )
                sub_column.label(
                    text="Model Type:                  " + item_prop.model_type)
                sub_column.label(
                    text="Tintable:                        " + str(item_prop.tintable))
                sub_column.label(
                    text="Body Location:             " + item_prop.body_location.name)

                sub_column = split.column()

                sub_column.label(
                    text="Static:                                         " + str(item_prop.static))
                sub_column.label(
                    text="Attach Bone:                             " + item_prop.attach_bone)
                sub_column.label(
                    text="Is Body Texture:                       " + str(item_prop.is_body_texture))
                sub_column.label(
                    text="Hat Category:                           " + str(item_prop.hat_category))
                sub_column.label(
                    text="Decal Group:                             " + str(item_prop.decal_group))
                sub_column.label(
                    text="Can Have Holes:                             " + str(item_prop.can_have_holes))
                sub_column.label(
                    text="Origin:                                        " + item_prop.origin)

                row = column.row()
                row.label(text="Texture Choices")

                texture_choices = item_prop.texture_choices

                box = column.box()
                split = box.split()
                sub_column = split.column()

                for texture in texture_choices:
                    sub_column.label(text=texture.texture_path)

                row = column.row()
                row.label(text="Masks")

                box = column.box()
                split = box.split()
                sub_column = split.column()

                masks = item_prop.mask_array
                for i in range(len(masks)):
                    if masks[i] == True:
                        sub_column.label(text=str(i))

        # ------------------------------------------------------------------------#
        #  Outfits

        subpanel, panel_area = main_column.panel(
            "outfits_subpanel", default_closed=True)
        subpanel.label(text='Outfits')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            # row = column.row()

            # row.operator("zomboid.parse_outfit_xmls")

            row = column.row(align=True)

            row.template_list("PZ_UL_OutfitList", "pz_outfit_list", addon_prefs,
                              "pz_human_outfit_slots", addon_prefs, "outfit_slot_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.outfit_slot_active_index != -1:
                row.label(text="Outfit Properties")
                item_prop = addon_prefs.pz_human_outfit_slots[addon_prefs.outfit_slot_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text="GUID:                             " + item_prop.guid)
                column.label(text="Random Top:                " +
                             str(item_prop.random_top))
                column.label(text="Random Pants:             " +
                             str(item_prop.random_pants))
                column.label(
                    text="Origin:                            " + str(item_prop.origin))

                for outfit_item in item_prop.outfit_items:
                    column.separator(factor=2.0)
                    column.label(text=str(
                        round(outfit_item.probability * 100, 2)) + '% chance for one of the following:')
                    for choice in outfit_item.choices:
                        column.label(text='- ' + choice.name)

        # ------------------------------------------------------------------------#
        #  Hair Styles

        subpanel, panel_area = main_column.panel(
            "hair_styles_subpanel", default_closed=True)
        subpanel.label(text='Hair Styles')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            # row = column.row()

            # row.operator("zomboid.parse_hair_style_xmls")

            row = column.row(align=True)

            row.template_list("PZ_UL_HairStyleList", "pz_hair_style_list", addon_prefs,
                              "pz_human_hair_style_slots", addon_prefs, "hair_style_slot_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.hair_style_slot_active_index != -1:
                row.label(text="Hair Properties")
                item_prop = addon_prefs.pz_human_hair_style_slots[addon_prefs.hair_style_slot_active_index]

                box = column.box()
                split = box.split()
                sub_column = split.column()

                sub_column.label(text='Model Path:        ' +
                                 item_prop.model_path)
                sub_column.label(text='Texture Path:      ' +
                                 item_prop.texture_path)
                sub_column.label(
                    text='Hair Level:           ' + str(item_prop.level))
                sub_column.label(
                    text="Origin:                  " + str(item_prop.origin))

                column.separator()
                column.label(text="Alternate Hat Styles")
                box = column.box()
                split = box.split()
                left_column = split.column()
                right_column = split.column()

                hat_styles = item_prop.hat_styles
                for i in range(len(hat_styles)):
                    left_column.label(text=str(hat_styles[i].hat_group))
                    right_column.label(text=hat_styles[i].style_name)

        # ------------------------------------------------------------------------#
        #  Beard Styles

        subpanel, panel_area = main_column.panel(
            "beard_styles_subpanel", default_closed=True)
        subpanel.label(text='Beard Styles')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row(align=True)

            row.template_list("PZ_UL_BeardStyleList", "pz_beard_style_list", addon_prefs,
                              "pz_human_beard_styles", addon_prefs, "beard_style_slot_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.beard_style_slot_active_index != -1:
                row.label(text="Beard Properties")
                item_prop = addon_prefs.pz_human_beard_styles[addon_prefs.beard_style_slot_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(text='Model Path:        ' + item_prop.model_path)
                column.label(text='Texture Path:        ' + item_prop.texture_path)
                column.label(text='Beard Level:           ' + str(item_prop.level))

        # ------------------------------------------------------------------------#
        #  Decals

        # subpanel, panel_area = main_column.panel(
        #     "decals_subpanel", default_closed=True)
        # subpanel.label(text='Decals')

        # if panel_area:
        #     box = panel_area.box()
        #     column = box.column()

        #     # row = column.row()

        #     # row.operator("zomboid.parse_decal_xmls")

        #     row = column.row(align=True)

        #     row.template_list("PZ_UL_DecalsList", "pz_decals_list", addon_prefs,
        #                       "pz_human_decals", addon_prefs, "decal_slot_active_index")

        #     column.separator()

        #     row = column.row()

        #     if addon_prefs.decal_slot_active_index != -1:
        #         row.label(text="Decal Properties")
        #         item_prop = addon_prefs.pz_human_decals[addon_prefs.decal_slot_active_index]

        #         box = column.box()
        #         split = box.split()
        #         column = split.column()

        #         column.label(text='Texture Path:         ' +
        #                      item_prop.texture_path)
        #         column.label(text='X Position:             ' +
        #                      str(item_prop.x_pos))
        #         column.label(text='Y Position:             ' +
        #                      str(item_prop.y_pos))
        #         column.label(text='Width:                    ' +
        #                      str(item_prop.width))
        #         column.label(text='Height:                   ' +
        #                      str(item_prop.height))

        # ------------------------------------------------------------------------#
        #  Body Locations

        subpanel, panel_area = main_column.panel(
            "body_locations_subpanel", default_closed=True)
        subpanel.label(text='Body Locations')

        if panel_area:  
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_BodyLocationList", "pz_body_location_list", addon_prefs,
                              "pz_human_body_locations", addon_prefs, "body_location_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.body_location_active_index != -1:
                row.label(text="Body Location Properties")
                item_prop = addon_prefs.pz_human_body_locations[addon_prefs.body_location_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(text='Render Order: ' + str(item_prop.order))

                if len(item_prop.properties.hide_locations) > 0:
                    column.label(
                        text='Body Location will be hidden if any of these locations are used:')
                    column.separator(factor=0.5)

                    for loc in item_prop.properties.hide_locations:
                        column.label(text=loc.name)

                    column.separator()

                if len(item_prop.properties.alt_locations) > 0:
                    column.label(
                        text='Body Location will use an alternate model if any of these locations are used:')
                    column.separator(factor=0.5)

                    for loc in item_prop.properties.alt_locations:
                        column.label(text=loc.name)

                    column.separator()

                if len(item_prop.properties.exclusive_locations) > 0:
                    column.label(
                        text='Body Location cannot be equpped if any of these locations are used:')
                    column.separator(factor=0.5)

                    for loc in item_prop.properties.exclusive_locations:
                        column.label(text=loc.name)

                    column.separator()

        # ------------------------------------------------------------------------#
        #  Skin Textures

        subpanel, panel_area = main_column.panel(
            "skin_textures_subpanel", default_closed=True)
        subpanel.label(text='Skin Textures')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_SkinTextureList", "pz_skin_texture_list", addon_prefs,
                              "pz_human_skin_textures", addon_prefs, "skin_texture_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.skin_texture_active_index != -1:

                row.label(text="Skin Properties")
                item_prop = addon_prefs.pz_human_skin_textures[
                    addon_prefs.skin_texture_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)
                column.label(
                    text='Sex:                              ' + item_prop.sex)
                column.label(
                    text='Chest Hair:                              ' + str(item_prop.chest_hair))
                column.label(
                    text='Origin:                              ' + item_prop.origin)
        
        # ------------------------------------------------------------------------#
        #  Stubble Textures

        subpanel, panel_area = main_column.panel(
            "stubble_textures_subpanel", default_closed=True)
        subpanel.label(text='Stubble Textures')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_StubbleTextureList", "pz_stuble_texture_list", addon_prefs,
                              "pz_human_stubble_textures", addon_prefs, "stubble_texture_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.stubble_texture_active_index != -1:

                row.label(text="Stubble Properties")
                item_prop = addon_prefs.pz_human_stubble_textures[
                    addon_prefs.stubble_texture_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)
                column.label(
                    text='Sex:                              ' + item_prop.sex)
                column.label(
                    text='Type:                              ' + item_prop.stubble_type)
                column.label(
                    text='Origin:                              ' + item_prop.origin)

        # ------------------------------------------------------------------------#
        #  Visibility Masks

        subpanel, panel_area = main_column.panel(
            "visibility_masks_subpanel", default_closed=True)
        subpanel.label(text='Visibility Masks')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_VisibilityMaskList", "pz_visibility_mask_list", addon_prefs,
                              "pz_human_visibility_masks", addon_prefs, "visibility_mask_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.visibility_mask_active_index != -1:

                row.label(text="Mask Properties")
                item_prop = addon_prefs.pz_human_visibility_masks[
                    addon_prefs.visibility_mask_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)

        # ------------------------------------------------------------------------#
        #  Overlay Masks

        subpanel, panel_area = main_column.panel(
            "overlay_masks_subpanel", default_closed=True)
        subpanel.label(text='Overlay Masks')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_OverlayMaskList", "pz_overlay_mask_list", addon_prefs,
                              "pz_human_overlay_masks", addon_prefs, "overlay_mask_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.overlay_mask_active_index != -1:

                row.label(text="Mask Properties")
                item_prop = addon_prefs.pz_human_overlay_masks[
                    addon_prefs.overlay_mask_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)

        # ------------------------------------------------------------------------#
        #  Attachment Points

        subpanel, panel_area = main_column.panel(
            "attachment_points_subpanel", default_closed=True)
        subpanel.label(text='Attachment Points')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_AttachmentPointList", "pz_attachment_point_list", addon_prefs,
                                "pz_human_attachment_points", addon_prefs, "attachment_point_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.attachment_point_active_index != -1:

                row.label(text="Attachment Point Properties")
                item_prop = addon_prefs.pz_human_attachment_points[addon_prefs.attachment_point_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Bone Name:                  ' + item_prop.bone_name
                )
                column.label(
                    text='Offset:                  ' + str(item_prop.offset[:])
                )
                column.label(
                    text='Rotation:                  ' + str(item_prop.rotation[:])
                )

        # ------------------------------------------------------------------------#
        #  Attachments

        subpanel, panel_area = main_column.panel(
            "attachments_subpanel", default_closed=True)
        subpanel.label(text='Attachments')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_AttachmentsList", "pz_attachments_list", addon_prefs,
                                "pz_human_attachments", addon_prefs, "attachment_active_index")

            column.separator()

            row = column.row()

            if addon_prefs.attachment_active_index != -1:

                row.label(text="Attachment Properties")
                item_prop = addon_prefs.pz_human_attachments[addon_prefs.attachment_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Model Path:                  ' + item_prop.model_path
                )
                column.label(
                    text='Model Type:                  ' + item_prop.model_type
                )
                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path
                )

                sub_box = column.box()
                sub_column = sub_box.column()

                for attachment_group in item_prop.attachment_groups:
                    sub_column.label(text='Attachment Group:   ' + attachment_group.attachment_point)
                    sub_column.label(text='Offset:             ' + str(attachment_group.offset[:]))
                    sub_column.label(text='Rotation:           ' + str(attachment_group.rotation[:]))
                    sub_column.label(text='Scale:              ' + str(attachment_group.scale))
                    sub_column.separator(factor=1.5, type='LINE')

        # ------------------------------------------------------------------------#
        #  Imported Animations

        # subpanel, panel_area = main_column.panel(
        #     "imported_animations_subpanel", default_closed=True)
        # subpanel.label(text='Imported Animations')

        # if panel_area:
        #     box = panel_area.box()
        #     column = box.column()

        #     row = column.row()

        #     row.template_list("PZ_UL_ImportedAnimationList", "pz_imported_animation_list", addon_prefs,
        #                       "pz_human_imported_animations", addon_prefs, "imported_animation_active_index")

        #     column.separator()

        #     row = column.row()

        #     if addon_prefs.imported_animation_active_index != -1:
        #         column.operator('zomboid.remap_animation')

        #         row.label(text="Animation Properties")
        #         item_prop = addon_prefs.pz_human_imported_animations[
        #             addon_prefs.imported_animation_active_index]

        #         box = column.box()
        #         split = box.split()
        #         column = split.column()

        #         column.label(
        #             text='Animation Path:                  ' + item_prop.anim_path)
        #         column.label(
        #             text='File Type:                              ' + item_prop.file_type)
