# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty
from random import randint, choice

from ...Utility.PZ_UpdateMethods import *

class PZ_ClothingItemTextureChoices(PropertyGroup):

    # The path that leads to the image texture for this texture choice
    texture_path: StringProperty(
        subtype='FILE_PATH'
    )

class PZ_ClothingItemReference(PropertyGroup):

    # The specific GUID that was assigned to this clothing item
    guid: StringProperty()

    # The type of clothing that this clothing item is
    clothing_type: EnumProperty(
        items=[
            ('BODYTEXTURE', 'Body Texture', ''),
            ('CLOTHINGMODEL', 'Clothing Model', ''),
            ('ACCESSORY', 'Accessory', '')
        ]
    )

    # The paths that lead to the respective model assets for the respective sexes
    male_model_path: StringProperty(
        subtype='FILE_PATH'
    )
    male_alt_model_path: StringProperty(
        subtype='FILE_PATH'
    )
    female_model_path: StringProperty(
        subtype='FILE_PATH'
    )
    female_alt_model_path: StringProperty(
        subtype='FILE_PATH'
    )

    # The model format that this clothing item uses
    model_type: StringProperty()

    # A collection of texture choice objects that will be pulled from when the clothing item is added
    texture_choices: CollectionProperty(type=PZ_ClothingItemTextureChoices)

    # Is this clothing item able to have a random color tint?
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )

    # If this clothing item is an accessory, what bone is it supposed to be attached to?
    attach_bone: StringProperty()

    # The array of boolean toggles for each mask.
    # Clothing model objects use these to obscur body geometry that would otherwise clip through the clothing
    visibility_mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )

    # The hat category is used to indicate if the rig should use a subsitute hair model when this item is equipped
    hat_category: IntProperty(
        default=-1
    )

    # What shirt decal group does this clothing item use, if any?
    decal_group: StringProperty(
        default='None'
    )

    # What body location does this clothing item use? 
    # This is used for things like body clothing texture sorting and making sure you can't put an apron on over a hazmat suit
    body_location: StringProperty()

    # Whether this clothing item should be able to have hole texture overlays on it
    can_have_holes: BoolProperty(default=True)

    # Where does this clothing item come from? Project Zomboid, or a mod?
    origin: StringProperty()

class PZ_EquippedClothingItem(PropertyGroup):

    # The reference data that this property group should reference
    data: PointerProperty(
        type=PZ_ClothingItemReference
    )

    # Method that will grab a random texture path from one of the texture choices
    def get_texture_path(self):
        return choice(self.data.texture_choices).texture_path

    # The color that this clothing item texture will multiply itself with.
    # The default value of white means that the color will be unchanged.
    def update_tint_color(self, context):
        model_properties = context.active_object.pz_model_properties
        if not model_properties.stop_texture_updates:
            bpy.ops.zomboid.create_body_texture()

    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0,
        update=update_tint_color
    )

    # The toggle of whether this clothing item should use an alternate mode
    use_alt_model: BoolProperty(
        default=False
    )

    # The model objects that this clothing item uses, if they exist
    male_model_object: PointerProperty(
        type=Object
    )
    female_model_object: PointerProperty(
        type=Object
    )

    # The material that this clothing item uses, if it exists
    material: PointerProperty(
        type=Material
    )

    # The image texture that this clothing item uses, if it exists
    image: PointerProperty(
        type=Image
    )