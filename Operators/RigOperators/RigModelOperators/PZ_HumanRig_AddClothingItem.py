# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

from random import randint

class PZ_HumanRig_AddClothingItem(Operator):
    bl_idname = "zomboid.add_clothing_item"
    bl_label = "Add Clothing Item"
    bl_description = "Adds a clothing item onto the model"

    guid: StringProperty()
    generate_mask: BoolProperty(
        default=True
    )

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_human_prop_mesh_slots

        item = None
        for clothing_item in addon_prefs.pz_human_clothing_item_slots:
            if clothing_item.guid == self.guid:
                item = clothing_item

        if item is not None:

            # Body Texture
            if item.is_body_texture:
                t = t_list.add()

                rnd = randint(0, len(item.texture_choices) - 1)
                t.name = item.name
                t.decal_group = item.decal_group
                t.texture_path = item.texture_choices[rnd].texture_path

                bpy.ops.zomboid.create_body_texture()

            # Clothing Mesh
            elif item.static == False and item.attach_bone == 'None' or item.static == True and item.attach_bone == 'None':
                p.clothing_mesh_slot_active_index += 1
                m = m_list.add()

                m.male_model_path = item.male_model_path
                m.female_model_path = item.female_model_path
                m.model_type = item.model_type

                rnd = randint(0, len(item.texture_choices) - 1)
                m.texture_path = item.texture_choices[rnd].texture_path
                m.name = item.name

                for i in range(len(item.mask_array)):
                    if item.mask_array[i] == True:
                        m.mask_array[i] = True

                m.hat_category = item.hat_category

                bpy.ops.zomboid.import_clothing_model()

            # Prop Mesh
            else:
                p.prop_mesh_slot_active_index += 1
                a = a_list.add()

                a.male_model_path = item.male_model_path
                a.female_model_path = item.female_model_path
                a.model_type = item.model_type

                rnd = randint(0, len(item.texture_choices) - 1)
                a.texture_path = item.texture_choices[rnd].texture_path
                a.name = item.name

                a.attach_bone = item.attach_bone

                a.hat_category = item.hat_category

                bpy.ops.zomboid.import_accessory_model()

            if self.generate_mask:
                bpy.ops.zomboid.create_visibility_mask()

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})