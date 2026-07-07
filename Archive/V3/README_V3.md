# Project Zomboid Community Human Rig V3.1.0
By Paddlefruit

<img width="829" height="862" alt="IMG-RigV3_Preview" src="https://github.com/user-attachments/assets/f0a869da-9b89-4150-b6ac-d6bf1c87c8b4" />

## CHANGED

- Rig is updated to now primarially support GLB exports instead of FBX exports. GLB files are dramatically smaller in size than FBX files, so it is best practice to use them instead.
- To do so, use the new script included, 'PY-BobBatchExportGLB', to easily export either all actions in the scene or the active action on Bip01.

- Automatic skirt bone positioning is now much better.
- Added the male and female skeleton models from the game as attatched meshes to Bip01 that you can toggle on (just for fun!)

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
3. Change the value of the desired limb to switch it. A value of 0 is FK, and a value of 1 is IK. Be sure to keyframe this value for animations. This value will also automatically hide and reveal whatever control bones are needed for a certain context.

If you don't know what the difference between IK and FK is, here's a good video as a refresher:
https://youtu.be/JnkAlwMjalc?feature=shared
   
### Toggling the 'Look Point' for the head
If you would rather have the head rotate towards an object rather than rotating the head yourself, do the following instructions.
1. Follow steps 1 and 2 from the IK/FK Switching section.
2. Change the value of the property 'Head_UseLookPoint' from 0 to 1. Be sure to keyframe this value. It will reveal and hide the necessary controls you need.

<img width="454" height="639" alt="IMG-Properties" src="https://github.com/user-attachments/assets/f04e49f1-df48-4bbf-9359-6883ff3b563d" />

### Moving the Character Location
If you want the animation to actually move the character in-game (not just the model), you need to animate the location of the 'CTRL_TranslationData' bone, NOT the 'CTRL_Root' bone. It may look unintuitive to not see the character moving with the TranslationData control in Blender, but that is how the game reads movement.

### Moving Character's Held Items
The prop bones (responsible for where the player holds weapons, etc.) automatically move along with the hands. If you need to adjust their rotation or location, you can do that on top of it. 

### Hiding Bones
If you want to simplify your viewport and hide bones you don't need, you can do so by hiding the visibility of Bone Collections, located in the armature tab of the Properties window. I highly reccomend only revealing collections from the 'CTRL' category, as those are the only ones you should need.

Do NOT use Alt-H! This will reveal ALL the bones, and will make your viewport messy. If this happens, turn off the visibility of the 'DEF' and 'IK' collections.

Note that some of the collections' visibility settings are driven by the custom properties, meaning they cannot be directly hidden. You CAN hide their parent collection though.

### Switching from the Male Model to the Female Model
Simply enable/disable the meshes you want or don't want. They are all located within the 'Bip01' armature.

### Revealing the Dress Model
As with above, enable and disable the meshes you do or don't want to see.

### Textures
There are some textures packed into the file. If you want more, go to your Project Zomboid install in the 'common' folder. They are found in: 'projectzomboid/media/textures/Body'.
Once you have found there (or any custom textures you want), go to the Shading tab. In the Shader Node editor, select the 'Image Texture' node and select your texture from your files.

## Exporting

### Animations
#### GLB (Reccomended)
- Make sure that the objects 'Dummy01', 'Bip01', 'GEO-MaleBody', and 'Translation_Data' are visible in the scene.
- Open 'PY-BobBatchExportGLB' in the Blender text editor in your Blender project containing your animation. (Script is in the GitHub repository if you lose it)
- Run the script. It will prompt you to select a file path, and this is where your animations will be exported to.
- By default it will export every action in the Blend file that contains the substring 'Bob_'. If you want to only export the active action on Bip01, uncheck 'Export All Animations' in the file path popup.
 
<img width="785" height="476" alt="IMG-ExportScript" src="https://github.com/user-attachments/assets/4095b2c8-5890-4805-af88-b8677c6600e6" />

#### FBX (Currently Not Working)
- Currently this version of the rig does not support FBX exports. Use the GLB exports instead. (There is no difference to PZ which type you use, and you can mix and match FBXs and GLBs)

### AnimationMeshes
This is for when you want to export a custom model to the game, potentially to replace the main human mesh.
#### GLB
- Select the following objects (with your custom model selected instead of 'GEO-MaleBody'):

<img width="446" height="323" alt="IMG-Selection" src="https://github.com/user-attachments/assets/373ec824-5469-4e4f-870e-1e380bbf46cb" />

- Open the standard GLTF/GLB Blender exporter (not the script!).
- Select the following options:

<img width="243" height="917" alt="IMG-Settings1" src="https://github.com/user-attachments/assets/e12c335f-8da5-41d3-b0c2-df76c85a938d" />
<img width="243" height="810" alt="IMG-Settings2" src="https://github.com/user-attachments/assets/481f723a-3ae5-44f1-bbe7-793a5e23ad02" />

- Export


## Things to note

### Dress Bones
The dress bones should automatically move according to the legs, but may require some adjustment from the animator.

### Asset Library
The 'CH-PZ_Human' collection is marked as an asset for you to use in asset libraries.

## Credits
Rig and scripts made by Paddlefruit

Special thanks to CrystalChris and others from the Discord helping test the rig out!

Original rig, model, and textures are from The Indie Stone.
