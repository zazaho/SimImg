# Similar Image Finder (Simimg)
![Simimg in action](doc/demo.gif)

# Description
This is a python GUI for displaying pictures grouped according to
similarity. The main aim of the program is to help identify groups of
holiday snaps that resemble each-other and efficiently inspect those
groups. It allows you to easily keep only the best photos.

The program is **not** designed to identify the same but modified pictures
(recompressed jpgs, cropped images or adapted colours, etc.). Although
it can be used for this there are many and better solutions available.

Upon starting Simimg from the command line, by default it will load
the pictures it finds in the startup directory and sub-directories
into the GUI. These are settings that can be changed within the GUI by
clicking on settings (![](simimg/icons/settings.png)). *In particular
in the case you want to use the program by clicking on its icon, you
may want to set an empty startup directory.*

You can play with different filters that take into account how similar
two pictures are. These are the panels in the left section of the
finder window below the **Filters** title. You can activate a
filter by clicking on its name. The following options exist:

* I have implemented measurements of how similar the colours are
between two images, as well as between 5 regions (the four corners and
the central part). The measurement in HSV (hue-saturation-value)
supposedly reflects best how humans perceive image information.

* Some gradient metrics adapted from ImageHash (dhash). Basically
these measure whether two images have similar patterns of brighter and
darker regions.

* You can further select the maximum allowed time-span between the
moments the pictures were taken in order to be considered a match.

* You can match on camera model. This means that two pictures are
considered to be a match if they were taken with the same camera.
  
* Finally you can match on image shape. You can choose:

	* portrait/landscape: width smaller/larger or equal to height

	* exact: width/height are identical

	* some percentage difference allowed

Some of the selection criteria have additional parameters that you can
play with.

Each filter has a **Must Match** checkbox. If this is switched on,
only those pairs that satisfy this filter are considered matches.
Note that:

1) **Must Match** has no effect if only one filter is active.

2) If some filter(s) have **Must Match** set, other filters without
**Must Match** have no effect.

3) When multiple filters are active and no **Must Match** is set,
two images are considered a matching pair if any of the conditions is
satisfied.

The actual use is to be able to better drill down the list. For
example it allows to show only those groups that have similar colours
**and** are taken with the same camera by switching on **Must Match** for
both filters.

# What matching groups are shown?
When the program starts, there are no active filters and thumbnails
of all files are shown in a grid sorted by filename.

Once some filters are activated or changed the display will be
updated.

For each picture that has some matches in the collection, the group
of matching thumbnails will be shown in a row. The only exception is a
group that is already displayed in its entirety as a
subgroup on another line.

Simimg does its best to maintain the sorting order of the displayed
files according to filename. This is chosen for two reasons. 

1) It limits the visual changes when modifying parameters or filters.
This helps to understand the impact of the modification.

2) Many times the filename of holiday pictures represents a natural
sorting order; for example the serial photo-number or a prefix chosen
to indicate where a picture was taken. Maintaining this order, means
related pictures have more chance of being presented close together.

Note that completely identical files (exact copies of some image file)
will not be shown twice. Instead one thumbnail will be shown with a
green border around it.

# Available functions
## Thumbnail buttons
You can click on the **Hide**, **Move** or **Delete** button below
each image.

* **Hide** will remove the thumbnail from the display but it will not delete
the file from your hard-disk.

* **Delete** will remove the file from the display and from your
hard-disk.

* **Move** will Move the file to the folder selected in the move list
on the bottom left. See below.

## (De)selecting thumbnails
You can select a thumbnail by clicking on it; its background will turn
blue to indicate that it is selected.

Pressing the Control (Ctrl) key while clicking will select or deselect
the entire line of thumbnails.

Pressing the Shift key while clicking will select all thumbnails between
the current image and the last selected image.

Clicking in an empty part of the thumbnail display area deselects all
images.

The little red check-mark button  (![](simimg/icons/uncheck.png)) in the toolbar area
(top-left) also switches between select-all and unselect-all thumbnails.

Pressing Ctrl+a toggles between selecting and unselecting all thumbnails.

## Actions for selected thumbnails
The *Play* button (![](simimg/icons/play.png))  in the toolbar will show a window that allows
to view the selected images in larger versions (Ctrl+v).

The *Minus* button (![](simimg/icons/hide.png)) will hide all selected thumbnails (Ctrl+h)

The *Red-X* button (![](simimg/icons/delete.png)) will delete all selected thumbnails (Ctrl+d)

The *Two folder* button (![](simimg/icons/move.png)) will move the selected thumbnails (Ctrl+m)

## Photo organisation functions
Because the Finder window is also a great way to get an overview, even
without using the filtering functions, I have implemented a very basic
organisation option into it. These are represented by the *Move*
folders.

Imagine you have 2 folders defined: "WebAlbum", "EditWithGimp". You
peruse you photos, select and delete those that are poor, you select
those that are nice but either need better framing or need playing a
bit with the brightness. Activate the "EditWithGimp" folder and press
*Move* button (![](simimg/icons/move.png)). Next, you have found a
number of great pictures that you want to publish. Select those,
activate the "WebAlbum" target and press *Move*.

## Actions in the viewer window
One design goal is a clean interface with a lot of room for the
pictures themselves. Therefore there are no action buttons in the
viewer.

The follow actions are available in the viewer window:

* F1 or i: show a short help window

* left mouse button, arrow-right or n: show the next picture

* right mouse button, arrow left or p: show the previous picture

* scrollwheel: zoom-in on part of the picture

* delete or d: delete the picture from disk

* m: move the file to the move-target directory selected in the finder
  window

* 1: move the file to the **first** move-target directory

* 2: move the file to the **second** move-target directory

* 3: move the file to the **third** move-target directory

* escape or q: quit the viewer

## Tips
There are a few features that are not immediately obvious. *Camera
Model* and *Picture Shape* can be set to "different". By themselves
these options are not useful because they will show unrelated pictures
together. They can become interesting in the following scenario:

Several people have taken pictures of the same scene, you select
pictures taken close in time or with similar colours. If you impose
different *Camera Model* you can concentrate on similar pictures but
taken by different people.

The Folder select dialog for **move** does not allow to create folders
on some platforms. Selecting the parent directoy and adding (by
typing) the target folder you would like to create before pressing OK
will create the directory.

## Technical remarks
I have seen quite a variety of 'success', meaning that some algorithm
detects matches that I myself would also call a match. It depends a
lot on the set of images that one uses as input. I find it useful to
play around a bit with selecting different algorithms and playing with
the numerical limits. To help with this, the tooltip of the limit
selectors will tell you at which value the first match happens and at
which value more than 10 matches are found. 

In my experience, for the purpose of detecting the most interesting
similar holiday pictures the "Gradient (horizontal)" algorithm can be
useful but the "HSV (5 regions)" in the Colours Distance gives the
best results.

The other filters should be considered optional to further limit the
shown matches.

Some of the calculations can be time-consuming and Simimg tries to be
clever about not recalculating. It will store the calculated values in
a database for future use. It recognises the pictures files by their
MD5-hash which means that even if you move files or rename them, their
image properties will not be recalculated.

It attempts to do the most expensive calculations in parallel making
optimal use of your computers capabilities.

Note that, for reasons of speed, the maximum number of thumbnails that
will be shown will not exceed about 300.

Note that, for reasons of speed and memory, the maximum number of
files that will be loaded when adding a folder is 900.

# Credit
This project uses the following open source packages:

* [Python](https://www.python.org/): version 3

* [tkinter](https://docs.python.org/3/library/tkinter.html) that
should normally come with your python

* [pillow](https://python-pillow.org/) for image reading and processing.

* The tooltip code is adapted from an example found on
  [Daniweb](https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter).
  
Some of the algorithms used have been inspired by code found at
[imagedupes](https://github.com/ghemsley/imagedupes), 
[pyimagesearch](https://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/)
and [imageHash](https://github.com/JohannesBuchner/imagehash).

