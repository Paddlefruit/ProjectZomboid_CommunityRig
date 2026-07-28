# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty

from ..Utility.PZ_UpdateMethods import *

# ============================================================================================
# RIG OBJECT
# ============================================================================================

'''
This property group is used be the scene to keep track of all of the
current human rigs in the scene
'''

class PZ_HumanRigObject(PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(type=Object)


# ============================================================================================
# BODY LOCATION
# ============================================================================================

'''
These property groups relate to the BodyLocation system used
in Project Zomboid, keeping track of which other body locations
it is exclusive with, needs to use an alternate model with, etc.
'''

class PZ_BodyLocationRef(PropertyGroup):
    pass


class PZ_BodyLocationProperties(PropertyGroup):
    # This body location will be hidden any of the body locations in this collection are occupied
    hide_locations: CollectionProperty(type=PZ_BodyLocationRef)
    # This body location will use an alternate model if any of the body locations in this collection are occupied
    alt_locations: CollectionProperty(type=PZ_BodyLocationRef)
    # This body location cannot be equipped if any of the body locations in this collection are occupied (No effect in Blender)
    exclusive_locations: CollectionProperty(type=PZ_BodyLocationRef)


class PZ_BodyLocation(PropertyGroup):
    name: StringProperty(default='NONE')
    properties: PointerProperty(type=PZ_BodyLocationProperties)


# ============================================================================================
# SKIN TEXTURE
# ============================================================================================

'''
This property group tracks specific skin texture assets
'''

class PZ_SkinTexture(PropertyGroup):
    texture_path: StringProperty()
    skin_tone: IntProperty(default=0)
    sex: StringProperty(default='BOTH')
    chest_hair : BoolProperty(default=False)
    body_type: StringProperty()
    zombification: IntProperty(default=0)
    origin: StringProperty()


# ============================================================================================
# STUBBLE TEXTURE
# ============================================================================================

'''
This property group tracks specific stubble texture assets
'''

class PZ_StubbleTexture(PropertyGroup):
    texture_path: StringProperty()
    stubble_type: StringProperty()
    sex: StringProperty()
    origin: StringProperty()

# ============================================================================================
# SHIRT DECAL SLOT
# ============================================================================================

'''
These property groups relate to the shirt decal system
used in Project Zomboid
'''

class PZ_ShirtDecal(PropertyGroup):
    texture_path: StringProperty()
    x_pos: IntProperty()
    y_pos: IntProperty()
    width: IntProperty()
    height: IntProperty()


class PZ_ShirtDecalGroup(PropertyGroup):
    decals: CollectionProperty(type=PZ_ShirtDecal)

# ============================================================================================
# BODY TEXTURE SLOT
# ============================================================================================

class PZ_BodyTextureSlot(PropertyGroup):

    def update_tint_color(self, context):
        bpy.ops.zomboid.create_body_texture()

    name: StringProperty(
        default="New Body Texture"
    )
    texture_path: StringProperty(
        name="Texture Path"
    )
    tintable: BoolProperty(
        name="Tintable", 
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color", 
        subtype='COLOR', 
        default=(1.0, 1.0, 1.0), 
        max=1.0, 
        min=0.0, 
        update=update_tint_color
    )
    decal_group: StringProperty(
        default='None'
    )
    origin: StringProperty()
    # decal : PointerProperty(type=PZ_ShirtDecal)

# ============================================================================================
# ZOMBIE INJURY
# ============================================================================================


class PZ_ZombieInjury(PropertyGroup):
    texture_path: StringProperty()

# ============================================================================================
# BODY INJURY
# ============================================================================================


class PZ_BodyInjury(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()
    damage_type: StringProperty()
    sex: StringProperty()

# ============================================================================================
# VISIBILITY MASK
# ============================================================================================


class PZ_VisibilityMask(PropertyGroup):
    texture_path: StringProperty()
    mask_set: StringProperty(default='Vanilla')
    body_part: StringProperty()

# ============================================================================================
# OVERLAY MASK
# ============================================================================================


class PZ_OverlayMask(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()


# ============================================================================================
# HOLE MASK MASK
# ============================================================================================


class PZ_HoleMask(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()

# ============================================================================================
# CLOTHING MESH SLOT
# ============================================================================================


class PZ_ClothingMeshSlot(PropertyGroup):

    def update_model_visibility(self, context):
        update_clothing_sex_visibility(self, context)

    def update_model_render(self, context):
        update_clothing_sex_render(self, context)

    name: StringProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_path: StringProperty()
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    slot_hide_render: BoolProperty(
        name="Visible in Render",
        default=True,
        update=update_model_render
    )
    slot_hide_viewport: BoolProperty(
        name="Visible in Viewport",
        default=True,
        update=update_model_visibility
    )
    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )
    bloodiness: FloatProperty(default=0.0, min=0.0, max=1.0)
    hat_category: IntProperty()
    origin: StringProperty()

# ============================================================================================
# ACCESSORY MESH SLOT
# ============================================================================================


class PZ_PropMeshSlot(PropertyGroup):

    def update_model_visibility(self, context):
        update_prop_sex_visibility(self, context)

    def update_model_render(self, context):
        update_prop_sex_render(self, context)

    name: StringProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_path: StringProperty()
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    attach_bone: StringProperty()
    slot_hide_render: BoolProperty(
        name="Visible in Render",
        default=True,
        update=update_model_render
    )
    slot_hide_viewport: BoolProperty(
        name="Visible in Viewport",
        default=True,
        update=update_model_visibility
    )
    hat_category: IntProperty()
    origin: StringProperty()

# ============================================================================================
# CLOTHING ITEM SLOT
# ============================================================================================


class PZ_ClothingItemTextureChoices(PropertyGroup):
    texture_path: StringProperty()


class PZ_ClothingItemSlot(PropertyGroup):
    guid: StringProperty()
    is_body_texture: BoolProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_choices: CollectionProperty(type=PZ_ClothingItemTextureChoices)
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    attach_bone: StringProperty()
    static: BoolProperty()
    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )
    hat_category: IntProperty()
    decal_group: StringProperty(default='None')
  #  body_location: PointerProperty(type=PZ_BodyLocation)
    origin: StringProperty()

# ============================================================================================
# OUTFIT SLOT
# ============================================================================================


class PZ_OutfitItemChoices(PropertyGroup):
    guid: StringProperty()
    name: StringProperty()


class PZ_OutfitItem(PropertyGroup):
    probability: FloatProperty(default=1.0)
    choices: CollectionProperty(type=PZ_OutfitItemChoices)


class PZ_OutfitSlot(PropertyGroup):
    name: StringProperty()
    search_name: StringProperty()
    guid: StringProperty()
    sex: StringProperty()
    random_top: BoolProperty()
    random_pants: BoolProperty()
    allow_tint: BoolProperty()
    allow_shirt_decal: BoolProperty()
    origin: StringProperty()

    outfit_items: CollectionProperty(type=PZ_OutfitItem)

# ============================================================================================
# HAIR STYLE SLOT
# ============================================================================================


class PZ_HairStyleHatStyle(PropertyGroup):
    hat_group: IntProperty()
    style_name: StringProperty()


class PZ_HairStyleSlot(PropertyGroup):
    name: StringProperty()
    model_path: StringProperty()
    texture_path: StringProperty()
    sex: StringProperty()
    level: IntProperty()
    hat_styles: CollectionProperty(type=PZ_HairStyleHatStyle)
    origin: StringProperty()

# ============================================================================================
# IMPORTED ANIMATION
# ============================================================================================


class PZ_ImportedAnimation(PropertyGroup):
    file_type: StringProperty()
    anim_path: StringProperty()
    origin: StringProperty()
    character_type: StringProperty()

# ============================================================================================
# MOD DIRECTORY
# ============================================================================================

class PZ_ModDirectorySlot(PropertyGroup):
    name: StringProperty(
        default='Unknown Mod'
    )
    active: BoolProperty(
        default=False
    )
    author: StringProperty(
        default='Unknown Author'
    )
    mod_dir: StringProperty(
        subtype='DIR_PATH'
    )
    latest_pz_version: FloatProperty(
        default=42.0
    )