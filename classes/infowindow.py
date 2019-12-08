from tkinter import messagebox

def showInfoDialog():
    ''' show basic info about this program '''
    msg = '''
SiMilar ImaGe finder:

This program is designed to display groups of pictures that are similar.
In particular, it aims to group together pictures that show the same scene.
The use case is to be able to quickly inspect these pictures and keep only the best ones.

The program in not designed to find copies of the same image that have been slightly altered or identical copies, although it can be use for this. 
There are already many good (better) solutions available to do this.

The workflow is as follows:
* Activate some selection criterion of the left by clicking on its label
* Adapt the parameters
* The matching groups are updated

* Select images by clicking on the thumbnail (background turns blue)
* Click the play button to inspect the selected images
* Click the delete button to delete selected images
    '''
    messagebox.showinfo("Information",msg)
