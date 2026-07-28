# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_CheckHatCategory(Operator):
    bl_idname = "zomboid.check_hat_category"
    bl_label = "Check Hat Category"

    count_self: BoolProperty(
        default=True
    )

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        a_list = context.active_object.pz_accessory_models
        clothing_prop_list = context.active_object.pz_clothing_models

        # If there are no props or clothing meshes, set the hair style to the selected one
        if p.accessory_model_active_index == -1 and p.clothing_model_active_index == -1:
            if p.current_male_hair_style != p.selected_male_hair_style:
                p.current_male_hair_style = p.selected_male_hair_style
                bpy.ops.zomboid.import_hair_model(hair_type='M')
            if p.current_female_hair_style != p.selected_female_hair_style:
                p.current_female_hair_style = p.selected_female_hair_style
                bpy.ops.zomboid.import_hair_model(hair_type='F')
            if p.current_beard_style != p.selected_beard_style:
                p.current_beard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_model(hair_type='B')
            p.current_hat_category = -1

            return ({'FINISHED'})

        test = False
        if p.accessory_model_active_index != -1:
            prop_prop = a_list[p.accessory_model_active_index]

            for i in range(len(a_list)):
                if a_list[i].hat_category != -1:  # Found a p mesh that has a hat category
                    if (a_list[i].name == prop_prop.name and not self.count_self):
                        continue
                    test = True
                    if a_list[i].hat_category > p.current_hat_category:
                        p.current_hat_category = a_list[i].hat_category

        if p.clothing_model_active_index != -1:
            clothing_prop = clothing_prop_list[p.clothing_model_active_index]

            for i in range(len(clothing_prop_list)):
                # Found a clothing mesh that has a hat category
                if clothing_prop_list[i].hat_category != -1:
                    if (clothing_prop_list[i].name == clothing_prop.name and not self.count_self):
                        continue
                    test = True
                    if clothing_prop_list[i].hat_category > p.current_hat_category:
                        p.current_hat_category = clothing_prop_list[i].hat_category

        if test:
            if p.current_hat_category >= 8:
                p.current_male_hair_style = 'Bald'
                p.current_female_hair_style = 'Bald'
                bpy.ops.zomboid.import_hair_model(hair_type='M')
                bpy.ops.zomboid.import_hair_model(hair_type='F')
                if p.current_hat_category == 9:
                    p.current_beard_style = 'None'
                    bpy.ops.zomboid.import_hair_model(hair_type='B')
                else:
                    p.current_breard_style = p.selected_beard_style
                    bpy.ops.zomboid.import_hair_model(hair_type='B')
            else:
                p.current_breard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_model(hair_type='B')

                for hair in addon_prefs.pz_human_hair_style_slots:
                    if hair.name == p.selected_male_hair_style and hair.sex == 'MALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == p.current_hat_category:
                                if p.current_male_hair_style != hat_style.style_name:
                                    p.current_male_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_model(
                                        hair_type='M')
                                break

                    if hair.name == p.selected_female_hair_style and hair.sex == 'FEMALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == p.current_hat_category:
                                if p.current_female_hair_style != hat_style.style_name:
                                    p.current_female_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_model(
                                        hair_type='F')
                                break
        else:
            if p.current_male_hair_style != p.selected_male_hair_style:
                p.current_male_hair_style = p.selected_male_hair_style
                bpy.ops.zomboid.import_hair_model(hair_type='M')
            if p.current_female_hair_style != p.selected_female_hair_style:
                p.current_female_hair_style = p.selected_female_hair_style
                bpy.ops.zomboid.import_hair_model(hair_type='F')
            if p.current_beard_style != p.selected_beard_style:
                p.current_beard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_model(hair_type='B')
            p.current_hat_category = -1

        return ({'FINISHED'})