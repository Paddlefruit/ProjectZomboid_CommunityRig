# Project Zomboid Community Human Rig V2.2.0
By Paddlefruit

<img width="1080" height="1080" alt="rigpreview" src="https://github.com/user-attachments/assets/af2ed701-3643-4239-b7e2-4286f8c47d25" />

## CHANGED

The root of the custom animations should now properly point to the pelvis rather than the ground, to be on par with vanilla animations. This should remove the excess jitter when transitioning to and from vanilla animations.
- This won't require any migration steps from you, but you will need to re-export your animation if you want the fix

Prop bones are now properly oriented by default

Replaced the deformation rig with a fixed one to finally circumvent that rotation snapping issue on animation transitions. This was due to an incorrect rig scale and a lack of the Dummy01 object as a parent, which has now been fixed.

Changed the static boolean toggle of the 'IK/FK' options to a float value which should allow you to properly interpolate between the two now. 

### TO MIGRATE PREVIOUS ANIMATIONS:

#### Automatic

1. Download the 'PY_RigMigrator_Blender5' script from the repository. 
2. Open the script in the text editor in the Blender file. Note that this script requires Blender 5.
3. Assign the action you want to convert onto the updated armature. Make sure that the updated rig has the proper names in the scene! (Bip01, Dummy01, Translation_Data and NOT Bip01.01 or Bip02 or anything like that)
4. Run the script.

#### Manual

1. Back up your animation just in case!
2. Bring the new rig into whatever Blender file had your original animation (you can scale the Dummy01 object down to fit your scene if need be, usually by a magnitude of 100. Just don't apply the scale.)
3. Assign the new rig the Action that the previous rig had in the Action Editor.
4. Go to the Graph Editor and select all the control bones. (Make sure that the new rig has the same IK/FK settings as the previous one!)
5. Set the 2D cursor at y-level 0 and set the 'Pivot Point' (the option next to the snapping toggle) to '2D Cursor'. This is to ensure that the animation data is scaled properly. 
6. Filter the animation channels to only include 'Location' channels. Grab every curve that is visible. 
7. Initiate a scale operation ('S' by default), restrict the scaling to the Y-axis (press 'Y' during the scalling operation), type '100', then enter.
8. Now your animation should look identical on the new rig. If it doesn't, make sure you did all the steps correctly! Feel free to dm me (@Paddlefruit) if you need some help.


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
3. Change the value of the desired limb to switch it. A value of False is FK, and a value of True is IK. Be sure to keyframe this value for animations. This value will also automatically hide and reveal whatever control bones are needed for a certain context.

If you don't know what the difference between IK and FK is, here's a good video as a refresher:
https://youtu.be/JnkAlwMjalc?feature=shared
   
### Toggling the 'Look Point' for the head
If you would rather have the head rotate towards an object rather than rotating the head yourself, do the following instructions.
1. Follow steps 1 and 2 from the IK/FK Switching section.
2. Change the value of the property 'Head_UseLookPoint' from False to True. Be sure to keyframe this value. It will reveal and hide the necessary controls you need.

<img width="365" height="596" alt="rootselect" src="https://github.com/user-attachments/assets/7b8b398f-4955-44d4-b08d-3b1f7ac7273f" />

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

## How to export

### Selecting Objects
Only select the following objects when exporting the rig:

<img width="391" height="277" alt="newselection" src="https://github.com/user-attachments/assets/def567e9-514b-4991-bf08-0146047c392f" />

### Export Options
Make sure to select the following options when exporting as FBX:

<img width="244" height="894" alt="settings" src="https://github.com/user-attachments/assets/f0e860e9-3645-4078-8705-2c29824c9358" />

## Things to note

### Dress Bones
The dress bones should automatically move according to the legs, but may require some adjustment from the animator. I plan to make them move more intelligently in the future.

### Asset Library
The 'CH-PZ_Human' collection is marked as an asset for you to use in asset libraries.

## Credits
Rig made by Paddlefruit

Special thanks to CrystalChris and others from the Discord helping test the rig out!

Original rig, model, and textures are from The Indie Stone.
