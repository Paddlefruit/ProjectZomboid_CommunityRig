# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import numpy as np
from bpy.types import Operator
from mathutils import Vector

class PZ_CreateBodyTexture(Operator):
    bl_idname = "zomboid.create_body_texture"
    bl_label = "Create Body Texture"

    # -------------------------------------------------------------#
    # Get All Body Textures

    body_textures = []

    def get_all_body_textures(self, context, p):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        skin_textures = addon_prefs.pz_human_skin_textures
        stubble_textures = addon_prefs.pz_human_stubble_textures
        body_injury_textures = addon_prefs.pz_human_body_injuries
        zombie_injuries = context.active_object.pz_human_zombie_injuries
        clothing_textures = context.active_object.pz_human_body_texture_slots

        # Get the base skin texture
        match p.skin_set:
            case 'HUMAN':
                if p.zombification == 0:
                    sex = 'MaleBody' if p.model_sex == 'MALE' else 'FemaleBody'
                    chest_hair = 'a' if p.chest_hair and p.model_sex == 'MALE' else ''
                    skin_color = '0' + str(p.skin_color + 1)

                    self.body_textures.append((skin_textures.get(sex + skin_color + chest_hair).texture_path, (1.0, 1.0, 1.0)))
                else:
                    skin_5_fix = p.skin_color == 4 and p.zombification != 0
                    zombie_3_fix = p.skin_color == 2 and p.zombification > 1 and p.model_sex == 'MALE'

                    sex = 'M_ZedBody' if p.model_sex == 'MALE' else 'F_ZedBody'
                    skin_color = '0' + str(p.skin_color + 1) if not skin_5_fix else '0' + str(p.skin_color)
                    intensity = '_level' + str(p.zombification) if not zombie_3_fix else '_level1'

                    self.body_textures.append((skin_textures.get(sex + skin_color + intensity).texture_path, (1.0, 1.0, 1.0)))
            case 'SKELETON':
                match p.skeleton_type:
                    case 0:
                        self.body_textures.append((skin_textures.get('Skeleton').texture_path, (1.0, 1.0, 1.0)))
                    case 1:
                        self.body_textures.append((skin_textures.get('SkeletonBurned').texture_path, (1.0, 1.0, 1.0)))
                    case 2:
                        self.body_textures.append((skin_textures.get('SkeletonMuscle').texture_path, (1.0, 1.0, 1.0)))
            case 'MANNEQUIN':
                if p.mannequin_type == 0:
                    self.body_textures.append((skin_textures.get('M_Mannequin_White').texture_path, (1.0, 1.0, 1.0)))
                else:
                    self.body_textures.append((skin_textures.get('M_Mannequin_Black').texture_path, (1.0, 1.0, 1.0)))
            case 'SCARECROW':
                self.body_textures.append((skin_textures.get('Male_Scarecrow').texture_path, (1.0, 1.0, 1.0)))

        # Get the stubble textures
        if p.skin_set == 'HUMAN':
            if p.hair_stubble:
                if p.model_sex == 'MALE':
                    self.body_textures.append((stubble_textures.get('M_Hair_Stubble').texture_path, (1.0, 1.0, 1.0)))
                else:
                    self.body_textures.append((stubble_textures.get('F_Hair_Stubble').texture_path, (1.0, 1.0, 1.0)))
            
            if p.beard_stubble and p.model_sex == 'MALE':
                self.body_textures.append((stubble_textures.get('M_Beard_Stubble').texture_path, (1.0, 1.0, 1.0)))

            # Get the body injury textures
            injury_props = [p.upper_torso_injury, p.lower_torso_injury, p.left_hand_injury,
                            p.right_hand_injury, p.left_forearm_injury, p.right_forearm_injury,
                            p.left_upperarm_injury, p.right_upperarm_injury, p.head_injury,
                            p.neck_injury, p.groin_injury, p.left_thigh_injury,
                            p.right_thigh_injury, p.left_shin_injury, p.right_shin_injury,
                            p.left_foot_injury, p.right_foot_injury]

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

            sex = p.model_sex

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

        if p.skin_set != 'SKELETON':
            # Get the clothing textures
            for clothing in clothing_textures:
                self.body_textures.append((clothing.texture_path, clothing.tint_color))

    # -------------------------------------------------------------#
    # Create Body Texture

    # TODO Optimize

    def generate_body_texture(self, context, p):
        generated_image = bpy.data.images.get(
            'TEX-BodyTexture (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='TEX-BodyTexture (' + str(p.rig_instance) + ')', width=256, height=256, alpha=True)
        
        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-TexSlot').image = generated_image

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
    def initialize_default_textures(self, context, p):
        # Assign the default image to the body material node tree
        if p.body_mat:
            img = bpy.data.images.get('TEX-DefaultMale') if p.model_sex == 'MALE' else bpy.data.images.get('TEX-DefaultFemale')
            p.body_mat.node_tree.nodes.get('NDE-TexSlot').image = img

    # -------------------------------------------------------------#
    # Execute

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        
        if addon_prefs.assets_parsed:
            self.body_textures.clear()

            self.get_all_body_textures(context, p)
            self.generate_body_texture(context, p)
        else:
            self.initialize_default_textures(context, p)

        return ({'FINISHED'})