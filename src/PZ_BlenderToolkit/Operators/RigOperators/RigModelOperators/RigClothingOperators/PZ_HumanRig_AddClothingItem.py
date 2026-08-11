# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

from random import randint, uniform

class PZ_HumanRig_AddClothingItem(Operator):
    bl_idname = "zomboid.add_clothing_item"
    bl_label = "Add Clothing Item"
    bl_description = "Adds a clothing item onto the model"

    guid: StringProperty()

    generate_mask: BoolProperty(
        default=True
    )

    create_body_texture: BoolProperty(
        default=True
    )

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties
        random_properties = context.active_object.pz_random_properties

        # The collection of body location references
        body_locations = addon_data.pz_body_locations

        # The collection of equipped clothing items
        equipped_items = context.active_object.pz_equipped_clothing_items

        # Collection of the list of used body locations
        used_locs = context.active_object.pz_used_body_locations

        item = None
        for clothing_item in addon_data.pz_clothing_item_references:
            if clothing_item.guid == self.guid:
                item = clothing_item

        if item is not None:

            # Skip adding this item if its body location is forbidden by another item, and the toggle is on
            # Also check if alternate models need to be used, or if this model needs to be hidden
            use_alt_model = False
            start_hidden = False
            for used_loc in used_locs:
                if body_locations.get(item.body_location):
                    if model_properties.use_body_location_exclusivity:
                        for ban_loc in body_locations.get(item.body_location).properties.exclusive_locations:
                            if used_loc.name == ban_loc.name:
                                return({'CANCELLED'})
                    if model_properties.use_body_location_alt_models:
                        for alt_loc in body_locations.get(item.body_location).properties.alt_locations:
                            if used_loc.name == alt_loc.name:
                                use_alt_model = True
                                break
                    if model_properties.use_body_location_hiding:
                        for hide_loc in body_locations.get(item.body_location).properties.hide_locations:
                            if used_loc.name == hide_loc.name:
                                start_hidden = True
                                break

            # Create a new eqipped item entry and increment the index
            new_item = equipped_items.add()
            model_properties.equipped_clothing_item_active_index += 1

            # Copy the general data
            new_item.name = item.name
            new_item.data.name = item.name
            new_item.data.guid = item.guid
            new_item.data.clothing_type = item.clothing_type
            new_item.data.hat_category = item.hat_category
            new_item.data.can_have_holes = item.can_have_holes
            new_item.data.origin = item.origin
            new_item.data.attach_bone = item.attach_bone
            new_item.data.decal_group = item.decal_group

            # Equipped clothing item specific parameters
            new_item.use_alt_model = use_alt_model
            
            # Copy the body location (in name)
            new_item.data.body_location = item.body_location

            # Copy the tint settings, and get a random or set tint if applicable
            new_item.data.tintable = item.tintable
            if new_item.data.tintable:
                if random_properties.random_tint_color:
                    new_item.tint_color = ((uniform(0.15, 1.0), uniform(0.15, 1.0), uniform(0.15, 1.0)))
                else:
                    new_item.tint_color = random_properties.static_tint_color

            # Copy the model data
            new_item.data.male_model_path = item.male_model_path
            new_item.data.male_alt_model_path = item.male_alt_model_path
            new_item.data.female_model_path = item.female_model_path
            new_item.data.female_alt_model_path = item.female_alt_model_path

            new_item.data.model_type = item.model_type

            # Copy the texture choices
            for choice in item.texture_choices:
                new_choice = new_item.data.texture_choices.add()
                new_choice.texture_path = choice.texture_path

            # Copy the mask settings
            for i in range(len(item.visibility_mask_array)):
                if item.visibility_mask_array[i] == True:
                    new_item.data.visibility_mask_array[i] = True

            # Call the specific operators for the appropriate clothing type
            if new_item.data.clothing_type == 'BODYTEXTURE' and self.create_body_texture:
                bpy.ops.zomboid.create_body_texture()

            if new_item.data.clothing_type == 'CLOTHINGMODEL':
                bpy.ops.zomboid.import_clothing_model()
                if self.generate_mask:
                    bpy.ops.zomboid.create_visibility_mask()

            if new_item.data.clothing_type == 'ACCESSORY':
                bpy.ops.zomboid.import_accessory_model()

            # Check Hat Category Validity
            bpy.ops.zomboid.check_hat_category()

            # Check Body Location Validity
            bpy.ops.zomboid.check_body_locations(clothing_item_added = item.name, count_self = True)

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})