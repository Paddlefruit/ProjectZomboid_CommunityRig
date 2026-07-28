# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from random import random, randint
from bpy.types import Operator

class PZ_HumanRig_ApplyOutfit(Operator):
    bl_idname = "zomboid.apply_outfit"
    bl_label = "Apply Outfit"
    bl_description = "Applies the outfit from the selected XML with the same paramaters and probabilities as in game"
    bl_options = {'REGISTER', 'UNDO'}

    selected_guids = []
    random_top = False
    random_pants = False

    @classmethod
    def poll(cls, context):
        return context.active_object.pz_human_props.selected_outfit != ''

    def select_guids(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        outfit_name = p.selected_outfit.split()[0]
        outfit_sex = ''
        if '(Male)' in p.selected_outfit:
            outfit_sex = 'MALE'
        elif '(Female)' in p.selected_outfit:
            outfit_sex = 'FEMALE'

        for outfit in addon_prefs.pz_human_outfit_slots:
            if outfit.name == outfit_name and outfit.sex == outfit_sex:
                # Outfit is found, begin getting GUIDs
                for outfit_item in outfit.outfit_items:
                    if random() > outfit_item.probability:
                        continue
                    rnd = randint(0, len(outfit_item.choices) - 1)
                    self.selected_guids.append(outfit_item.choices[rnd].guid)
                self.random_top = outfit.random_top
                self.random_pants = outfit.random_pants
                return ({'FINISHED'})

        return ({'CANCELLED'})

    def add_clothing_items(self, context):
        p = context.active_object.pz_human_props

        # Select the model sex
        if '(Male)' in p.selected_outfit:
            p.model_sex = 'MALE'

            if p.random_hair_style:
                bpy.ops.zomboid.randomize_hair_model(hair_type='M')
            if randint(1, 100) <= p.random_beard_chance:
                bpy.ops.zomboid.randomize_hair_model(hair_type='B')
            else:
                p.beard_style = 'None'
        elif '(Female)' in p.selected_outfit:
            p.model_sex = 'FEMALE'

            if p.random_hair_style:
                bpy.ops.zomboid.randomize_hair_model(hair_type='F')

        # Select random body textures, if enabled
        if p.random_skin_color:
            p.skin_color = randint(0, 4)
        if p.random_zombie:
            p.zombification = randint(1, 3)
        else:
            p.zombification = 0

        # Select random hair color, if enabled
        if p.random_hair_color:
            bpy.ops.zomboid.randomize_hair_color()

        # Randomize injuries, if enabled
        if p.randomize_injuries:
            bpy.ops.zomboid.randomize_body_injuries()
            bpy.ops.zomboid.randomize_zombie_injuries()
            bpy.ops.zomboid.randomize_bloodiness()
            bpy.ops.zomboid.randomize_dirtiness()

        if self.random_top:
            match randint(1, 6):
                case 1:
                    # Standard Default T-Shirt
                    bpy.ops.zomboid.add_clothing_item(
                        guid='e4ec9087-006d-41dc-81f4-585b6d2e958c', generate_mask=False)
                case 2:
                    # Tintable Default T-Shirt
                    bpy.ops.zomboid.add_clothing_item(
                        guid='19af00e4-ed4d-49bc-a893-a4a3376fe6da', generate_mask=False)
                case 3:
                    # Standard Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(
                        guid='d0616b36-b727-4c08-9274-020cb2e72bf8', generate_mask=False)
                case 4:
                    # Tintable Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(
                        guid='53b95680-245b-4439-8ba7-5aa6d938e465', generate_mask=False)
                case 5:
                    # Standard Default Vest
                    bpy.ops.zomboid.add_clothing_item(
                        guid='903c06ea-78e7-4f42-a3da-768be61f216f', generate_mask=False)
                case 6:
                    # Tintable Default Vest
                    bpy.ops.zomboid.add_clothing_item(
                        guid='a700a956-32c2-49a6-bd5f-5a2895073f19', generate_mask=False)

        if self.random_pants:
            match randint(1, 3):
                case 1:
                    # Standard Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='e4b71599-604d-4cc7-9ce4-7723a7e37d8a', generate_mask=False)
                case 2:
                    # Hue-able Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='5b07d45e-84c9-4ddf-ad6e-4bc2f27cace7', generate_mask=False)
                case 3:
                    # Tintable Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='1e2ed52f-9ee7-464b-9581-a450f2fbb403', generate_mask=False)

        # Call the clothing item adder for each GUID
        for guid in self.selected_guids:
            bpy.ops.zomboid.add_clothing_item(guid=guid, generate_mask=False)

        bpy.ops.zomboid.create_visibility_mask()

        return ({'FINISHED'})

    def execute(self, context):
        self.selected_guids.clear()
        self.select_guids(context)

        bpy.ops.zomboid.remove_all_clothing_items()

        self.add_clothing_items(context)

        return ({'FINISHED'})