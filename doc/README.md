# SIMilar IMaGe finder (SIMIMG)

# Description:
This is a python GUI for displaying pictures grouped according to
similarity. The main aim of the program is to help identify groups of
holiday snaps that resemble eachother and quickly inspect them. It
allows to easily keep only the best photos.

The progam is not designed to identify the same but modified pictures
(recompressed jpgs, cropped images or adapted colours, etc.). Although
it can be used for this there are many and better solutions available.

Upon starting SIMIMG from the command line, it will load the pictures
it finds in the start directory and subdirectories into the GUI.

You can play with different options that calculate how similar two
pictures are. It uses some similarity metrics from ImageHash.

I have also implemented a measurement of how similar the colours are
between two images, as well as between 5 regions (the four corners and
the central part).

You can further select the maximum allowed time-span between the
moments the pictures were taken in order to be considered a match.

Finally you can match on camera model.

Some of the calculations can be costly and SIMING tried to be clever
about not recalculating. It will store the calculated values in a
database for future use. It recognised the pictures files by their
MD5-hash which means that even if you move files or rename them, their
image properties will not be recalculated.

It attempts to do the most expensive calculations in parellel making
optimal use of the CPU capabilities.

One design goal is a clean interface with a lot of room for the
pictures themselves. In particular in the image-viewer interface there
are no buttons 
The longest calc
