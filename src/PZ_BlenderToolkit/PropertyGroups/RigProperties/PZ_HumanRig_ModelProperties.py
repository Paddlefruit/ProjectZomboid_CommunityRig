# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to a rig's model
and appearance inside Blender
'''

class PZ_HumanRigModelProperties(PropertyGroup):

    ### STOP TEXTURE UPDATES ###

    stop_texture_updates: BoolProperty(
        default=False
    )

    ### SELECTED CLOTHING ITEM ###

    def update_selected_clothing_item(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if self.selected_clothing_item != '':
            item = self.selected_clothing_item
            self.selected_clothing_item = ''

            if item != '':
                for clothing_item in addon_data.pz_clothing_item_references:
                    if clothing_item.name == item:
                        bpy.ops.zomboid.add_clothing_item(guid=clothing_item.guid)
                        break
            

    selected_clothing_item: StringProperty(
        name='Add Clothing Item',
        update=update_selected_clothing_item,
        override={"LIBRARY_OVERRIDABLE"}
    )


    ### SELECTED ATTACHMENT ###

    def update_selected_attachment(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if self.selected_attachment != '':
            item = self.selected_attachment
            self.selected_attachment = ''
            
            if item != '':
                bpy.ops.zomboid.add_attachment(attachment_name=item)

    selected_attachment: StringProperty(
        name='Add Attachment',
        update=update_selected_attachment
    )


    ### SELECTED OUTFIT ###
    
    selected_outfit: StringProperty(
        name='Selected Outfit',
        override={"LIBRARY_OVERRIDABLE"}
    )

    ### MODEL SEX ###

    '''
    Almost every clothing model has a different verson for both sexes.
    So, whenever the sex is changed, call functions that properly
    hide and show the correct sex's clothing in both the viewport and renders
    '''

    def update_body_texture(self, context):
        bpy.ops.zomboid.create_body_texture()

    def update_clothing_sex_visibility_settings(self, context):
        update_clothing_sex_viewport(self, context)
        update_clothing_sex_render(self, context)

    def update_hair_sex_visibility_settings(self, context):
        update_hair_sex_viewport(self, context)
        update_hair_sex_render(self, context)

    def update_sex_index(self, context):
        self.model_sex_index = 0 if self.model_sex == 'MALE' else 1
        self.update_clothing_sex_visibility_settings(context)
        self.update_hair_sex_visibility_settings(context)
        self.update_body_texture(context)

    model_sex: EnumProperty(
        name="Model Sex",
        description="Which human model to use",
        items=[
            ('MALE', "Male", "The male model and clothing", 0),
            ('FEMALE', "Female", "The female model and clothing", 1),
        ],
        default='MALE',
        update=update_sex_index
    )

    model_sex_index: IntProperty()

    ### BODY VISIBILITY ###

    def update_body_visibility(self, context):
        main_properties = context.active_object.pz_main_properties
        instance_str = main_properties.get_instance_str(context)

        col = bpy.data.collections.get('COL-PZ_Human_Bodies' + instance_str)
        if col:
            col.hide_viewport = not self.show_body
            col.hide_render = not self.show_body

    show_body: BoolProperty(
        name="Body Enabled",
        default=True,
        description="Show the body of the character",
        update=update_body_visibility
    )

    ### USE SKELETON ###

    use_skeleton: BoolProperty(
        default=False
    )

    ### SKIN SET ###

    def update_human_subtype(self, context):
        self.use_skeleton = self.human_subtype == 'SKELETON'
        self.update_body_texture(context)

    human_subtype: EnumProperty(
        name='Skin Set',
        items=[
            ('HUMAN', "Human", "Human and zombie textures", 0),
            ('SKELETON', "Skeleton", "Skeleton model and textures", 1),
            ('MANNEQUIN', "Mannequin", "Mannequin textures", 2),
            ('SCARECROW', "Scarecrow", "Long curly hair texture", 3),
        ],
        default='HUMAN',
        update=update_human_subtype
    )

    ### SKIN PARAMETERS ###

    skin_tone: EnumProperty(
        name="Skin Tone",
        items=[
            ('PORCELAIN', 'Porcelain', '', 0),
            ('PEACH', 'Peach', '', 1),
            ('ALMOND', 'Almond', '', 2),
            ('AMBER', 'Amber', '', 3),
            ('COCOA', 'Cocoa', '', 4)
        ],
        default='PORCELAIN',
        description="Which skin tone texture set to use",
        update=update_body_texture
    )

    chest_hair: BoolProperty(
        name='Chest Hair',
        default=False,
        update=update_body_texture
    )

    def update_zombification(self, context):
        self.zombification_index = context.active_object.pz_model_properties['zombification']
        self.update_body_texture(context)
    zombification: EnumProperty(
        name="Zombification",
        items=[
            ('NONE', 'None', '', 0),
            ('EARLY', 'Early Stage', '', 1),
            ('MID', 'Mid Stage', '', 2),
            ('LATE', 'Late Stage', '', 3)
        ],
        default='NONE',
        description="Level of zombification to use",
        update=update_zombification
    )
    zombification_index: IntProperty()

    skeleton_type: EnumProperty(
        name="Skeleton Type",
        items=[
            ('NORMAL', 'Normal', '', 0),
            ('BURNED', 'Burned', '', 1),
            ('MUSCLE', 'Muscle', '', 2),
        ],
        default='NORMAL',
        description="Which skeleton texture to use",
        update=update_body_texture
    )

    mannequin_type: EnumProperty(
        name="Mannequin Type",
        items=[
            ('WHITE', 'White', '', 0),
            ('BLACK', 'Black', '', 1)
        ],
        default='WHITE',
        description="Which mannequin texture to use",
        update=update_body_texture
    )

    ### CURRENT HAT CATEGORY ###
    current_hat_category: IntProperty(
        default=-1
    )

    ### MALE HAIR STYLE ###

    def update_male_hair_style(self, context):
        if self.selected_male_hair_style == '':
            self.selected_male_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_male_hair_style: StringProperty(
        name="Male Hair",
        update=update_male_hair_style
    )

    current_male_hair_style: StringProperty()

    ### FEMALE HAIR STYLE ###

    def update_female_hair_style(self, context):
        if self.selected_female_hair_style == '':
            self.selected_female_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_female_hair_style: StringProperty(
        name="Female Hair",
        update=update_female_hair_style
    )

    current_female_hair_style: StringProperty()

    ### BEARD STYLE ###

    def update_beard_style(self, context):
        if self.selected_beard_style == '':
            self.selected_beard_style = 'None'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_beard_style: StringProperty(
        name="Beard",
        update=update_beard_style
    )

    current_beard_style: StringProperty()

    ### STUBBLE ###

    hair_stubble: BoolProperty(
        name='Hair Stubble',
        default=False,
        update=update_body_texture
    )

    beard_stubble: BoolProperty(
        name='Beard Stubble',
        default=False,
        update=update_body_texture
    )

    ### HAIR VISIBILITY ###

    hair_color: FloatVectorProperty(
        name="Hair Color",
        subtype='COLOR',
        default=(0.25, 0.15, 0.05),
        min=0,
        max=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

    darken_zombie_hair: BoolProperty(
        name='Darken Zombie Hair',
        description='If character is a zombie, darken the hair color which is similar to how it looks in the game',
        default=True
    )

    ### VISIBILITY MASK ARRAY ###

    def update_visibility_mask_array(self, context):
        model_properties = context.active_object.pz_model_properties
        if not model_properties.stop_texture_updates:
            bpy.ops.zomboid.create_visibility_mask()

    visibility_mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                    False, False, False, False, False, False,
                    False, False, False, False, False),
        update=update_visibility_mask_array
    )

    ### BODY LOCATION SYSTEM TOGGLES ###
    use_body_location_exclusivity: BoolProperty(
        name='Use Body Location Exclusivity',
        description='Use the body location exclusivity system from the game, meaning that some clothing items will block other clothing items from being added',
        default=True
    )
    use_body_location_hiding: BoolProperty(
        name='Use Body Location Hiding',
        description='Use the body location hiding system from the game, meaning that some clothing items still be on the rig, but will be hidden if another body location blocks it',
        default=True
    )
    use_body_location_alt_models: BoolProperty(
        name='Use Body Location Alt Models',
        description='Use the body location alt model system from the game, where some equipped clothing items will force some other body locations to use an alternate model',
        default=True
    )
    use_body_location_sorting: BoolProperty(
        name='Use Body Location Sorting',
        description='Use the body location sorting system from the game, which will automatically sort body textures to make sure that the render order is correct. For instance, always putting shoes over socks',
        default=True
    )

    ### MODEL ACTIVE INDICIES ###

    equipped_clothing_item_active_index: IntProperty(
        default=-1
    )
    used_body_location_active_index: IntProperty(
        default=-1
    )
