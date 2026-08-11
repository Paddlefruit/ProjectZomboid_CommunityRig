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
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties

        equipped_clothing = context.active_object.pz_equipped_clothing_items
        clothing_models = [item for item in equipped_clothing if item.data.clothing_type == 'CLOTHINGMODEL']
        accessories = [item for item in equipped_clothing if item.data.clothing_type == 'ACCESSORY']
        evaluated_clothing = clothing_models + accessories

        def restore_default_hair():
            if model_properties.current_male_hair_style != model_properties.selected_male_hair_style:
                model_properties.current_male_hair_style = model_properties.selected_male_hair_style
                bpy.ops.zomboid.remove_hair_model(hair_type='M')
                bpy.ops.zomboid.import_hair_model(hair_type='M')
            if model_properties.current_female_hair_style != model_properties.selected_female_hair_style:
                model_properties.current_female_hair_style = model_properties.selected_female_hair_style
                bpy.ops.zomboid.remove_hair_model(hair_type='F')
                bpy.ops.zomboid.import_hair_model(hair_type='F')
            if model_properties.current_beard_style != model_properties.selected_beard_style:
                model_properties.current_beard_style = model_properties.selected_beard_style
                bpy.ops.zomboid.remove_hair_model(hair_type='B')
                bpy.ops.zomboid.import_hair_model(hair_type='B')
            model_properties.current_hat_category = -1


        # If there are no props or clothing meshes, set the hair style to the selected one
        if len(evaluated_clothing) == 0:
            restore_default_hair()
            return ({'FINISHED'})

        test = False
        if len(evaluated_clothing) > 0:
            for clothing in evaluated_clothing:
                if clothing.data.hat_category != -1:
                    # if (clothing.name == prop_prop.name and not self.count_self):
                    #     continue
                    test = True
                    if clothing.data.hat_category > model_properties.current_hat_category:
                        model_properties.current_hat_category = clothing.data.hat_category

        if test:
            if model_properties.current_hat_category >= 8:
                model_properties.current_male_hair_style = 'Bald'
                model_properties.current_female_hair_style = 'Bald'
                bpy.ops.zomboid.remove_hair_model(hair_type='M')
                bpy.ops.zomboid.import_hair_model(hair_type='M')
                bpy.ops.zomboid.remove_hair_model(hair_type='F')
                bpy.ops.zomboid.import_hair_model(hair_type='F')
                if model_properties.current_hat_category == 9:
                    model_properties.current_beard_style = 'None'
                    bpy.ops.zomboid.remove_hair_model(hair_type='B')
                    bpy.ops.zomboid.import_hair_model(hair_type='B')
                else:
                    model_properties.current_breard_style = model_properties.selected_beard_style
                    bpy.ops.zomboid.remove_hair_model(hair_type='B')
                    bpy.ops.zomboid.import_hair_model(hair_type='B')
            else:
                model_properties.current_breard_style = model_properties.selected_beard_style
                bpy.ops.zomboid.remove_hair_model(hair_type='B')
                bpy.ops.zomboid.import_hair_model(hair_type='B')

                for hair in addon_data.pz_hair_style_references:
                    if hair.name == model_properties.selected_male_hair_style and hair.sex == 'MALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == model_properties.current_hat_category:
                                if model_properties.current_male_hair_style != hat_style.style_name:
                                    model_properties.current_male_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.remove_hair_model(hair_type='M')
                                    bpy.ops.zomboid.import_hair_model(hair_type='M')
                                break

                    if hair.name == model_properties.selected_female_hair_style and hair.sex == 'FEMALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == model_properties.current_hat_category:
                                if model_properties.current_female_hair_style != hat_style.style_name:
                                    model_properties.current_female_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.remove_hair_model(hair_type='F')
                                    bpy.ops.zomboid.import_hair_model(hair_type='F')
                                break
        else:
            restore_default_hair()

        return ({'FINISHED'})