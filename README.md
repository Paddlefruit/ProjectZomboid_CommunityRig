# Project Zomboid Community Human Rig V1.0.5
By Paddlefruit

![PZ_Rigs](https://github.com/user-attachments/assets/8a50a094-093e-4813-9ba9-5730ac3fb688)


## Bone Collection Descriptions

### DEF
The deformation bones that Project Zomboid uses to move the character. The control bones will move these for you, so there is no need to modify them.

### CTRL
The control bones that move the deformation bones in a more intuitive way. These are the only bones that you should modify for your animations.

### IK
Extra bones for the IK solver. There is no need to mess with these.

## How to use

### IK/FK Switching
To switch a certain limb from forward kinematics (FK) to inverse kinematics (IK) or vice versa, do the following instructions.
1. In pose mode, select the 'CTRL_Root' bone (the white lines around the feet of the model).
2. In the Context Tabs at the right of the 3D viewport (press N if it is not already open), open the 'Item' tab then scroll down to 'Properties'
3. Change the value of the desired limb to switch it. A value of 0 is FK, and a value of 1 is IK. Be sure to keyframe this value for animations!
4. To reveal or hide relevant controls, go to the 'Armature' tab in the Properties editor. Expand the 'CTRL' bone collection and hide or reveal the relevant collections you need.

If you don't know what the difference between IK and FK is, here's a good video as a refresher:
https://youtu.be/JnkAlwMjalc?feature=shared
   
### Toggling the 'Look Point' for the head
If you would rather have the head rotate towards an object rather than rotating the head yourself, do the following instructions.
1. Follow steps 1 and 2 from the IK/FK Switching section.
2. Change the value of the property 'Head_LookPointInfluence' from 0 to 1. Be sure to keyframe this value!
3. To reveal the Look Point control object, reveal the collection 'CTRL_LookPoint', located under 'CTRL_Head'.

### Moving the Character Location
If you want the animation to actually move the character in-game (not just the model), you need to animate the location of the 'CTRL_TranslationData' bone, NOT the 'CTRL_Root' bone. It may look unintuitive to not see the character moving with the TranslationData control in Blender, but that is how the game reads movement.

### Moving Character's Held Items
The prop bones (responsible for where the player holds weapons, etc.) automatically move along with the hands. If you need to adjust their rotation or location, you can do that on top of it. 

### Switching from the Male Model to the Female Model
Simply enable/disable the meshes you want or don't want. They are all located within the 'Bip01' armature.

## How to export

### Selecting Objects
Only select the following objects when exporting the rig:

![Screenshot from 2025-01-24 17-32-19](https://github.com/user-attachments/assets/ef128884-a938-47d3-8375-4fe67382e8b6)


### Export Options
Make sure to select the following options when exporting as FBX:

![PZ_Rig_Export](https://github.com/user-attachments/assets/0ab9ff5b-404e-4263-8a02-cea3bdf2ae94)


## Things to note

### Dress Bones
The bones that control how dresses move on the player should automatically adjust themselves based on the legs' locations, So you shouldn't need to worry about them.

### Asset Library
The 'Bip01' armature is marked as an asset for you to use in asset libraries.

## Credits
Rig made by Paddlefruit

Special thanks to CrystalChris and others from the Discord helping test the rig out!

Original rig, model, and textures are from The Indie Stone.
