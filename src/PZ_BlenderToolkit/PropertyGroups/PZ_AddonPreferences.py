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

    references_obtained: BoolProperty(
        default=False
    )

# ============================================================================================
# LIST INDICIES
# ============================================================================================

    mod_directory_active_index: IntProperty(
        default=-1
    )
    clothing_item_reference_active_index: IntProperty(
        default=-1
    )
    outfit_reference_active_index: IntProperty(
        default=-1
    )
    skin_texture_reference_active_index: IntProperty(
        default=-1
    )
    stubble_texture_reference_active_index: IntProperty(
        default=-1
    )
    visibility_mask_reference_active_index: IntProperty(
        default=-1
    )
    overlay_mask_reference_active_index: IntProperty(
        default=-1
    )
    hair_style_reference_active_index: IntProperty(
        default=-1
    )
    beard_style_reference_active_index: IntProperty(
        default=-1
    )
    decal_reference_active_index: IntProperty(
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

    pz_mod_directories : CollectionProperty(type=PZ_ModDirectory)
    pz_clothing_item_references : CollectionProperty(type=PZ_ClothingItemReference)
    pz_outfit_references : CollectionProperty(type=PZ_Outfit)
    pz_hair_style_references : CollectionProperty(type=PZ_HairStyle)
    pz_male_hair_style_references : CollectionProperty(type=PZ_HairStyle)
    pz_female_hair_style_references : CollectionProperty(type=PZ_HairStyle)
    pz_beard_style_references : CollectionProperty(type=PZ_HairStyle)
    pz_body_injury_references : CollectionProperty(type=PZ_BodyInjury)
    pz_zombie_injury_references : CollectionProperty(type=PZ_ZombieInjury)
    pz_skin_texture_references : CollectionProperty(type=PZ_SkinTexture)
    pz_stubble_texture_references : CollectionProperty(type=PZ_StubbleTexture)
    pz_visibility_mask_references : CollectionProperty(type=PZ_VisibilityMask)
    pz_overlay_mask_references : CollectionProperty(type=PZ_OverlayMask)
    pz_game_animation_references : CollectionProperty(type=PZ_GameAnimation)
    pz_body_locations : CollectionProperty(type=PZ_BodyLocation)
    pz_attachment_points : CollectionProperty(type=PZ_AttachmentPoint)
    pz_attachments : CollectionProperty(type=PZ_Attachment)

# ============================================================================================
# PREFERENCES LAYOUT
# ============================================================================================

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'debug')
        layout.prop(self, 'pz_directory')