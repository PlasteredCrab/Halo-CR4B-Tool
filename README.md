# Completely Ready 4 Blender (CR4B Tool)

This tool is called Completely Ready 4 Blender and aims to do most of the work needed to port levels and objects from Halo 3, ODST, and Reach to Blender.
It accesses the raw tag files in binary and pulls the correct values, colors, scaling info, as well as various texture information needed by said object and tries it's best to setup the Shader nodes for you as well.

Tool is currently in Open Beta and is ready for public testing on Halo 3 and ODST objects and levels. Reach support coming later as Shader Nodes need to be made.

# Video for what it does and how it is used (needs to be updated for current build)
https://youtu.be/749xwvg-GK4

# Instructions for this build
- Run Blender as Administrator and be sure to set the path correctly to the py360convert folder included in this repo. If you do not do these two things, the required Python modules will not be installed.
- Be sure to set the paths to the CR4BTool-Shaders.blend and H3EK correctly as these are the most important. The Export Assets here folder is also important at the moment due to it needing the default textures, so be sure to set that correctly too while it is still needed.

# Special Thanks
- Chiefster and Soulburnin for the help making the Shader Nodes used by this tool to make the objects and levels to be as accurate as they can be! Without their help, this tool would not have gotten as far as it did.
- Lord Zedd for giving me some ideas on how to fix Mirror Wrapped textures being incorrect in terms of texture resolution ratios being the key. 
- Gravemind2401 for his amazing work with Reclaimer, which all of this work was started using models and textures ripped using Reclaimer.
