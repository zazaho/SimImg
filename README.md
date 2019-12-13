# SIMilar IMaGe finder (SIMIMG)

## One minute demo video
<video src="doc/demo.ogv" controls preload></video>

# Description:
This is a python GUI for displaying pictures grouped according to
similarity. The main aim of the program is to help identify groups of
holiday snaps that resemble each-other and efficiently inspect those
groups. It allows to easily keep only the best photos.

The program is **not** designed to identify the same but modified pictures
(recompressed jpgs, cropped images or adapted colours, etc.). Although
it can be used for this there are many and better solutions available.

Upon starting SIMIMG from the command line, by default it will load
the pictures it finds in the startup directory and sub-directories
into the GUI. These are settings that can be changed within the GUI by
clicking on settings. *In particular in the case you want to use the
program by clicking on it's icon, you may want to set an empty startup
directory.*

You can play with different options that take into account how similar
two pictures are. These are the panels in the left section of the
finder window. You can activate a condition by clicking on it name.
For now the following options exist:

* Some similarity metrics from ImageHash.

* I have also implemented a measurement of how similar the colours are
between two images, as well as between 5 regions (the four corners and
the central part).

* You can further select the maximum allowed time-span between the
moments the pictures were taken in order to be considered a match.

* Finally you can match on camera model. This means that to pictures
  are considered to be a match if they were taken with the same
  camera.
  
Some of the selection criteria have additional parameters that you can
play with.

Each condition has a **Must Match** checkbox. If this is switched on,
only those pairs that satisfy this condition are considered matches.
Note that:

1) **Must Match** has no effect if only one condition is active.

2) If some condition(s) have **Must Match** set, other conditions without
**Must Match** have no effect.

3) When multiple conditions are active and no **Must Match** is set two
images are considered a pair if any of the conditions is satisfied.

The actual use is to be able to better drill down the list. For
example it allows to show only those groups that have similar colours
**and** are taken with the same camera by switch on **Must Match** for
both conditions

# What matching groups are shown?
When the program starts, there are no active conditions and thumbnails
of all files are shown in a grid sorted by filename.

Once some conditions are activated or changed the display will be
updated.

For each picture that has some matches in the collection, the groups
of matching thumbnails will be shown in a line. The only exception is a
group that is already displayed in its entirety as a
subgroup on another line.

Note that completely identical files (exact copies of some image file)
will not be shown twice. Instead one thumbnail will be shown with a
green border around it.

Note that for reasons of speed, the maximum number of thumbnails that
will be show will not exceed about 300.

# Available functions
## Thumbnail buttons
You can click on the **Hide** or **Delete** button below each image.

* **Hide** will remove the thumbnail from the display but it will not delete
the file from your hard-disk.

* **Delete** will remove the file from the display and from your
hard-disk.

## (De)selecting thumbnails
You can select thumbnails by clicking on them; its background will turn
blue to indicate that it is selected.

Pressing the Control (Ctrl) key while clicking will select or deselect
the entire line of thumbnails.

Pressing the Shift key while clicking will select all thumbnails between
the current image and the last selected image.

Clicking in an empty area of the thumbnail display area deselects all
images. Pressing the little red check-mark button in the toolbar area
(top-left) also deselects all thumbnails.

Pressing Ctrl+a selects all thumbnails.

## Actions for selected thumbnails
The *Play* button  in the toolbar will show a window that allows
to view the selected images in larger versions (Ctrl+v).

The *Minus* button will hide all selected thumbnails (Ctrl+h)

The *Red-X* button will delete all selected thumbnails (Ctrl+d)

## Actions in the viewer window
One design goal is a clean interface with a lot of room for the
pictures themselves. Therefore there are no action buttons in the
viewer.

The follow actions are available in the viewer window:

* F1 or i: show a short help window

* arrow right, scroll-wheel up or n: show the next picture

* arrow left, scroll-wheel down or p: show the previous picture

* delete or d: delete the picture from disk

* escape of q: quit the viewer

## Technical remarks
Some of the calculations can be time consuming and SIMIMG tries to be
clever about not recalculating. It will store the calculated values in
a database for future use. It recognises the pictures files by their
MD5-hash which means that even if you move files or rename them, their
image properties will not be recalculated.

It attempts to do the most expensive calculations in parallel making
optimal use of the CPU capabilities.

# Credit:
This project uses the following open source packages:

* [Python](https://www.python.org/): version 3

* [tkinter](https://docs.python.org/3/library/tkinter.html) that
should normally come with your python

* [pillow](https://python-pillow.org/) for image reading and processing.

* [imageHash](https://github.com/JohannesBuchner/imagehash) for
calculating image hashes as a means to compare images.

* [pysqlite3](https://github.com/coleifer/pysqlite3) for storing and
  reading values from an sqlite database.

* The tooltip code is adapted from an example found on
  [Daniweb](https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter).
  
Some of the algorithms used have been inspired by code found at
[imagedupes](https://github.com/ghemsley/imagedupes) and [pyimagesearch](https://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/)