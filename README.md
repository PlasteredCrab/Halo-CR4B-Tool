# Halo Completely Ready 4 Blender (Halo CR4B Tool)

This tool is called Completely Ready 4 Blender and aims to do most of the work needed to port levels and objects from Halo 3, ODST, and Reach to Blender.
It accesses the raw tag files in binary and pulls the correct values, colors, scaling info, as well as various texture information needed by said object and tries it's best to setup the Shader nodes for you as well.

[Batch Importing / Exporting Assets from Halo games]
This tool just got a major update that allows for batch importing and exporting of:
- Halo CE         Models / Levels / Textures
- Halo 2          Models / Levels / Textures
- Halo 3          Models / Levels / Textures
- Halo 3 ODST     Models / Levels / Textures
- Halo Reach      Models / Levels / Textures
- Halo 5          Models / Textures
- Halo Infinite   Models / Textures

Tool is currently in Open Beta and is ready for public testing on Halo 3 and ODST objects and levels. Reach support coming later as Shader Nodes need to be made.



Support this tool and other tools I work on by donating a coffee: https://ko-fi.com/plasteredcrab

# Video for what it does and how it is used
(Ignore the outdated install part of this video. New install process is in the video below)
https://youtu.be/749xwvg-GK4

# Install Instructions for recent build
Install Video: https://youtu.be/xhRq8ChDz3s
- Run Blender as Administrator and be sure to set the path correctly to the py360convert folder included in this repo. If you do not do these two things, the required Python modules will not be installed.
- Be sure to set the paths to the CR4BTool-Shaders.blend file and H3EK tags folder (i.e. steamapps/common/H3EK/tags/ ) correctly as these are the most important. The Export Assets here folder is also important at the moment due to it needing the default textures, so be sure to set that correctly too while it is still needed.
- To get access to .ass/.jms export/import functionality make sure to install the Halo Asset Blender Development Toolset

# Special Thanks
- Chiefster and Soulburnin for the help making the Shader Nodes used by this tool to make the objects and levels to be as accurate as they can be! Without their help, this tool would not have gotten as far as it did.
- Lord Zedd for giving me some ideas on how to fix Mirror Wrapped textures being incorrect in terms of texture resolution ratios being the key. 
- Gravemind2401 for his amazing work with Reclaimer, which all of this work was started using models and textures ripped using Reclaimer. And for help making changes to the custom build of Reclaimer that CR4B Tool uses for importing
- General_101 for his great work with the Halo Asset Blender Development Toolkit
- Gamergotten for his Halo5Bitmap Exporter for Xbox files since he changed it to accept commandline arguments which allows for CR4B Tool to batch import / export Halo 5 models and textures from Xbox
- Urium86 for his tool HIRT which he changed to allow for Command Line functions to be sent to it by CR4B Tool which allows for Halo Infinite Importing / Exporting
