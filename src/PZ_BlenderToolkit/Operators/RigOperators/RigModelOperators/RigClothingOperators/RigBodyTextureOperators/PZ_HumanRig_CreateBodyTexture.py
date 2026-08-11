# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import numpy as np
from bpy.types import Operator

class PZ_CreateBodyTexture(Operator):
    bl_idname = "zomboid.create_body_texture"
    bl_label = "Create Body Texture"

    # -------------------------------------------------------------#
    # Get All Body Textures

    body_textures = []

    def get_all_body_textures(self, context):
        
        # Get all data
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties

        skin_textures = addon_data.pz_skin_texture_references
        stubble_textures = addon_data.pz_stubble_texture_references
        body_injury_textures = addon_data.pz_body_injury_references
        zombie_injuries = context.active_object.pz_zombie_injuries
        equipped_clothing = context.active_object.pz_equipped_clothing_items

        # Get the base skin texture
        match model_properties.human_subtype:

            case 'HUMAN':

                skin_tone = model_properties.bl_rna.properties['skin_tone'].enum_items.keys().index(model_properties.skin_tone)
                zombification = model_properties.bl_rna.properties['zombification'].enum_items.keys().index(model_properties.zombification)

                if zombification == 0:
                    sex_str = 'MaleBody' if model_properties.model_sex == 'MALE' else 'FemaleBody'
                    chest_hair_str = 'a' if model_properties.chest_hair and model_properties.model_sex == 'MALE' else ''
                    skin_tone_str = '0' + str(skin_tone + 1)

                    self.body_textures.append((skin_textures.get(sex_str + skin_tone_str + chest_hair_str).texture_path, (1.0, 1.0, 1.0)))
                else:
                    skin_5_fix = skin_tone == 4 and zombification != 0
                    zombie_3_fix = skin_tone == 2 and zombification > 1 and model_properties.model_sex == 'MALE'

                    sex_str = 'M_ZedBody' if model_properties.model_sex == 'MALE' else 'F_ZedBody'
                    skin_tone_str = '0' + str(skin_tone + 1) if not skin_5_fix else '0' + str(skin_tone)
                    intensity_str = '_level' + str(zombification) if not zombie_3_fix else '_level1'

                    self.body_textures.append((skin_textures.get(sex_str + skin_tone_str + intensity_str).texture_path, (1.0, 1.0, 1.0)))

            case 'SKELETON':
                match model_properties.skeleton_type:
                    case 'NORMAL':
                        self.body_textures.append((skin_textures.get('Skeleton').texture_path, (1.0, 1.0, 1.0)))
                    case 'BURNED':
                        self.body_textures.append((skin_textures.get('SkeletonBurned').texture_path, (1.0, 1.0, 1.0)))
                    case 'MUSCLE':
                        self.body_textures.append((skin_textures.get('SkeletonMuscle').texture_path, (1.0, 1.0, 1.0)))

            case 'MANNEQUIN':
                if model_properties.mannequin_type == 'WHITE':
                    self.body_textures.append((skin_textures.get('M_Mannequin_White').texture_path, (1.0, 1.0, 1.0)))
                else:
                    self.body_textures.append((skin_textures.get('M_Mannequin_Black').texture_path, (1.0, 1.0, 1.0)))

            case 'SCARECROW':
                self.body_textures.append((skin_textures.get('Male_Scarecrow').texture_path, (1.0, 1.0, 1.0)))

        # Get the stubble textures
        if model_properties.human_subtype == 'HUMAN':
            if model_properties.hair_stubble:
                if model_properties.model_sex == 'MALE':
                    self.body_textures.append((stubble_textures.get('M_Hair_Stubble').texture_path, (1.0, 1.0, 1.0)))
                else:
                    self.body_textures.append((stubble_textures.get('F_Hair_Stubble').texture_path, (1.0, 1.0, 1.0)))
            
            if model_properties.beard_stubble and model_properties.model_sex == 'MALE':
                self.body_textures.append((stubble_textures.get('M_Beard_Stubble').texture_path, (1.0, 1.0, 1.0)))

            # Get the body injury textures
            injury_props = [injury_properties.upper_torso_injury, injury_properties.lower_torso_injury, injury_properties.left_hand_injury,
                            injury_properties.right_hand_injury, injury_properties.left_forearm_injury, injury_properties.right_forearm_injury,
                            injury_properties.left_upperarm_injury, injury_properties.right_upperarm_injury, injury_properties.head_injury,
                            injury_properties.neck_injury, injury_properties.groin_injury, injury_properties.left_thigh_injury,
                            injury_properties.right_thigh_injury, injury_properties.left_shin_injury, injury_properties.right_shin_injury,
                            injury_properties.left_foot_injury, injury_properties.right_foot_injury]

            body_injury_lookup = {
                (tex.sex, tex.damage_type, tex.body_part): tex.texture_path for tex in body_injury_textures
            }

            body_part_dict = {
                0: 'chest',
                1: 'abdomen',
                2: 'left_hand',
                3: 'right_hand',
                4: 'lower_left_arm',
                5: 'lower_right_arm',
                6: 'upper_left_arm',
                7: 'upper_right_arm',
                8: 'head',
                9: 'neck',
                10: 'groin',
                11: 'left_thigh',
                12: 'right_thigh',
                13: 'left_calf',
                14: 'right_calf',
                15: 'left_foot',
                16: 'right_foot'
            }

            sex = model_properties.model_sex

            for index, injury in enumerate(injury_props):
                if injury != 'NONE':
                    if injury == 'BANDAGE' or injury == 'BANDAGEBLOODY':
                        key = ('MALE', injury, body_part_dict[index])
                    else:
                        key = (sex, injury, body_part_dict[index])
                    if key in body_injury_lookup:
                        self.body_textures.append((body_injury_lookup[key], (1.0, 1.0, 1.0)))

            # Get the zombie injury textures
            for injury in zombie_injuries:
                self.body_textures.append((injury.texture_path, (1.0, 1.0, 1.0)))

        if model_properties.human_subtype != 'SKELETON':
            # Get the body clothing textures
            for clothing in [item for item in equipped_clothing if item.data.clothing_type == 'BODYTEXTURE']:
                self.body_textures.append((clothing.get_texture_path(), clothing.tint_color))

    # -------------------------------------------------------------#
    # Create Body Texture

    # TODO Optimize

    def generate_body_texture(self, context):

        main_properties = context.active_object.pz_main_properties
        object_pointers = context.active_object.pz_object_pointers

        generated_image = object_pointers.body_texture_image
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='TEX-BodyTexture' + main_properties.get_instance_str(context), 
                width=256, 
                height=256, 
                alpha=True
            )
            object_pointers.body_texture_image = generated_image
        
        # Assign the image to the body material node tree
        if object_pointers.body_material:
            object_pointers.body_material.node_tree.nodes.get('NDE-TexSlot').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the alpha channel
        generated_pixels[3::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        body_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.body_textures:
            body_texture = bpy.data.images.load(tex_path[0])
            body_texture.scale(256, 256)

            body_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            body_texture.pixels.foreach_get(body_pixels)

            generated_rgba = generated_pixels.reshape(-1, 4)
            body_rgba = body_pixels.reshape(-1, 4)

            body_alpha = body_rgba[:, 3:4]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + body_alpha * (1.0 - generated_alpha)
            rgb = ((body_rgba[:, :3] * tex_path[1])* body_alpha + generated_rgba[:, :3] * generated_alpha * (1.0 - body_alpha)) 

            generated_rgba[:, :3] = rgb
            generated_rgba[:, 3] = alpha.squeeze()

            body_texture.user_clear()
            bpy.data.images.remove(body_texture)

        generated_image.pixels.foreach_set(generated_rgba.flatten())
        generated_image.update()


    # -------------------------------------------------------------#
    # Default Textures
    def initialize_default_textures(self, context):
        model_properties = context.active_object.pz_model_properties
        object_pointers = context.active_object.pz_object_pointers

        # Assign the default image to the body material node tree
        if object_pointers.body_material:
            img = bpy.data.images.get('TEX-DefaultMale') if model_properties.model_sex == 'MALE' else bpy.data.images.get('TEX-DefaultFemale')
            object_pointers.body_material.node_tree.nodes.get('NDE-TexSlot').image = img

    # -------------------------------------------------------------#
    # Execute

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if addon_data.references_obtained:
            self.body_textures.clear()

            self.get_all_body_textures(context)
            self.generate_body_texture(context)
        else:
            self.initialize_default_textures(context)

        return ({'FINISHED'})