# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ..Utility.PZ_UpdateMethods import *


# ============================================================================================
# RIG OBJECT
# ============================================================================================




# ============================================================================================
# BODY LOCATION
# ============================================================================================




# ============================================================================================
# SKIN TEXTURE
# ============================================================================================




# ============================================================================================
# STUBBLE TEXTURE
# ============================================================================================



# ============================================================================================
# SHIRT DECAL SLOT
# ============================================================================================



# ============================================================================================
# BODY TEXTURE SLOT
# ============================================================================================

# class PZ_BodyTextureSlot(PropertyGroup):

#     def update_tint_color(self, context):
#         bpy.ops.zomboid.create_body_texture()

#     name: StringProperty(
#         default="New Body Texture"
#     )
#     texture_path: StringProperty(
#         name="Texture Path"
#     )
#     tintable: BoolProperty(
#         name="Tintable", 
#         default=False
#     )
#     tint_color: FloatVectorProperty(
#         name="Tint Color", 
#         subtype='COLOR', 
#         default=(1.0, 1.0, 1.0), 
#         max=1.0, 
#         min=0.0, 
#         update=update_tint_color
#     )
#     decal_group: StringProperty(
#         default='None'
#     )
#     render_order: IntProperty()
#     origin: StringProperty()
    # decal : PointerProperty(type=PZ_ShirtDecal)





# ============================================================================================
# CLOTHING MESH SLOT
# ============================================================================================


# class PZ_ClothingMeshSlot(PropertyGroup):

#     def update_model_visibility(self, context):
#         update_clothing_sex_visibility(self, context)

#     def update_model_render(self, context):
#         update_clothing_sex_render(self, context)

#     name: StringProperty()
#     male_model_path: StringProperty()
#     male_alt_model_path: StringProperty()
#     female_model_path: StringProperty()
#     female_alt_model_path: StringProperty()
#     model_type: StringProperty()
#     texture_path: StringProperty()
#     tintable: BoolProperty(
#         name="Tintable",
#         default=False
#     )
#     tint_color: FloatVectorProperty(
#         name="Tint Color",
#         subtype='COLOR',
#         default=(1.0, 1.0, 1.0),
#         max=1.0,
#         min=0.0
#     )
#     slot_hide_render: BoolProperty(
#         name="Visible in Render",
#         default=True,
#         update=update_model_render
#     )
#     slot_hide_viewport: BoolProperty(
#         name="Visible in Viewport",
#         default=True,
#         update=update_model_visibility
#     )
#     mask_array: BoolVectorProperty(
#         name='Mask Array',
#         description='Array of toggles for each mesh mask',
#         size=17,
#         default=(False, False, False, False, False, False,
#                  False, False, False, False, False, False,
#                  False, False, False, False, False)
#     )
#     bloodiness: FloatProperty(default=0.0, min=0.0, max=1.0)
#     hat_category: IntProperty()
#     origin: StringProperty()

# ============================================================================================
# ACCESSORY MESH SLOT
# ============================================================================================


# class PZ_PropMeshSlot(PropertyGroup):

#     def update_model_visibility(self, context):
#         update_prop_sex_visibility(self, context)

#     def update_model_render(self, context):
#         update_prop_sex_render(self, context)

#     name: StringProperty()
#     male_model_path: StringProperty()
#     male_alt_model_path: StringProperty()
#     female_model_path: StringProperty()
#     female_alt_model_path: StringProperty()
#     model_type: StringProperty()
#     texture_path: StringProperty()
#     tintable: BoolProperty(
#         name="Tintable",
#         default=False
#     )
#     tint_color: FloatVectorProperty(
#         name="Tint Color",
#         subtype='COLOR',
#         default=(1.0, 1.0, 1.0),
#         max=1.0,
#         min=0.0
#     )
#     attach_bone: StringProperty()
#     slot_hide_render: BoolProperty(
#         name="Visible in Render",
#         default=True,
#         update=update_model_render
#     )
#     slot_hide_viewport: BoolProperty(
#         name="Visible in Viewport",
#         default=True,
#         update=update_model_visibility
#     )
#     hat_category: IntProperty()
#     origin: StringProperty()

# ============================================================================================
# CLOTHING ITEM SLOT
# ============================================================================================




# ============================================================================================
# OUTFIT SLOT
# ============================================================================================




# ============================================================================================
# HAIR STYLE SLOT
# ============================================================================================


# ============================================================================================
# IMPORTED ANIMATION
# ============================================================================================




# ============================================================================================
# ITEM SCRIPT
# ============================================================================================


# class PZ_ItemScript(PropertyGroup):
#     display_name: StringProperty(default='None')
#     display_category: StringProperty(default='None')


# ============================================================================================
# MOD DIRECTORY
# ============================================================================================

