# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty

from ..PropertyGroups.General.PZ_Attachment import PZ_Attachment, PZ_AttachmentPoint
from ..PropertyGroups.General.PZ_BodyLocation import PZ_BodyLocation
from ..PropertyGroups.General.PZ_ClothingItem import PZ_ClothingItemReference
from ..PropertyGroups.General.PZ_GameAnimation import PZ_GameAnimation
from ..PropertyGroups.General.PZ_HairStyle import PZ_HairStyle
from ..PropertyGroups.General.PZ_Injuries import PZ_BodyInjury, PZ_ZombieInjury
from ..PropertyGroups.General.PZ_Item import PZ_Item
from ..PropertyGroups.General.PZ_Masks import PZ_HoleMask, PZ_OverlayMask, PZ_VisibilityMask
from ..PropertyGroups.General.PZ_ModDirectory import PZ_ModDirectory
from ..PropertyGroups.General.PZ_Outfit import PZ_Outfit
from ..PropertyGroups.General.PZ_SkinTexture import PZ_SkinTexture
from ..PropertyGroups.General.PZ_StubbleTexture import PZ_StubbleTexture


class PZ_AddonPreferences(AddonPreferences):
    bl_idname = 'PZ_BlenderToolkit'

# ============================================================================================
# ASSET DIRECTORIES
# ============================================================================================

    pz_directory: StringProperty(
        name="Project Zomboid Directory",
        default="",
        description="The location of your Project Zomboid install, most commonly found in the 'common' folder in the Steam directory",
        subtype='DIR_PATH'
    )

# ============================================================================================
# SETTINGS
# ============================================================================================

    debug : BoolProperty(
        default=False,
        name='Debug',
        description='Show underlying information and options on the rig'
    )
    auto_switch_kinematics: BoolProperty(
        name='Auto Switch Kinematics on Snap',
        description='When a snap from FK to IK or vice versa is performed, automatically switch the limb to the target context',
        default=True
    )
    auto_key_snaps: BoolProperty(
        name='Auto Key Snaps',
        description='When a snap from FK to IK or vice versa is performed, automatically key the toggle state and the positions of the affected controls',
        default=False
    )
    allow_overwriting: BoolProperty(
        name='Allow Overwriting',
        description='If an asset entry has the same name as an already registered asset, remove that asset and replace it with the new one. Useful for mods that modify vanilla assets, such as Fluffy Hair',
        default=True
    )

# ============================================================================================
# MISC
# ============================================================================================

    assets_parsed: BoolProperty(
        default=False
    )

# ============================================================================================
# LIST INDICIES
# ============================================================================================

    mod_directory_slot_active_index: IntProperty(
        default=-1
    )
    clothing_item_slot_active_index: IntProperty(
        default=-1
    )
    outfit_slot_active_index: IntProperty(
        default=-1
    )
    skin_texture_active_index: IntProperty(
        default=-1
    )
    stubble_texture_active_index: IntProperty(
        default=-1
    )
    visibility_mask_active_index: IntProperty(
        default=-1
    )
    overlay_mask_active_index: IntProperty(
        default=-1
    )
    hair_style_slot_active_index: IntProperty(
        default=-1
    )
    beard_style_slot_active_index: IntProperty(
        default=-1
    )
    decal_slot_active_index: IntProperty(
        default=-1
    )
    body_location_active_index: IntProperty(
        default=-1
    )
    attachment_point_active_index: IntProperty(
        default=-1
    )
    attachment_active_index: IntProperty(
        default=-1
    )

# ============================================================================================
# ASSET COLLECTIONS
# ============================================================================================

    pz_human_mod_directory_slots : CollectionProperty(type=PZ_ModDirectory)
    pz_human_clothing_item_references : CollectionProperty(type=PZ_ClothingItemReference)
    pz_human_outfit_slots : CollectionProperty(type=PZ_Outfit)
    pz_human_hair_style_slots : CollectionProperty(type=PZ_HairStyle)
    pz_human_male_hair_styles : CollectionProperty(type=PZ_HairStyle)
    pz_human_female_hair_styles : CollectionProperty(type=PZ_HairStyle)
    pz_human_beard_styles : CollectionProperty(type=PZ_HairStyle)
    pz_human_body_injuries : CollectionProperty(type=PZ_BodyInjury)
    pz_human_zombie_injuries : CollectionProperty(type=PZ_ZombieInjury)
    pz_human_skin_textures : CollectionProperty(type=PZ_SkinTexture)
    pz_human_stubble_textures : CollectionProperty(type=PZ_StubbleTexture)
    pz_human_visibility_masks : CollectionProperty(type=PZ_VisibilityMask)
    pz_human_overlay_masks : CollectionProperty(type=PZ_OverlayMask)
    pz_human_imported_animations : CollectionProperty(type=PZ_GameAnimation)
    pz_human_body_locations : CollectionProperty(type=PZ_BodyLocation)
    pz_human_attachment_points : CollectionProperty(type=PZ_AttachmentPoint)
    pz_human_attachments : CollectionProperty(type=PZ_Attachment)

# ============================================================================================
# PREFERENCES LAYOUT
# ============================================================================================

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'debug')
        layout.prop(self, 'pz_directory')