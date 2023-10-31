<<<<<<< refs/remotes/upstream/main
 
# Create a standard Yes/No message box dialog passing in the 
=======

# Create a standard Yes/No message box dialog passing in the
>>>>>>> Revert "enlever le chain de argu"
# dialog title and text.
proc CreateDialog {title text} {
   tk_messageBox \
      -type yesno \
      -title $title \
      -default yes \
      -message $text \
      -icon question
}
<<<<<<< refs/remotes/upstream/main
 
=======

>>>>>>> Revert "enlever le chain de argu"
# Do this when user clicks Yes
proc Yes {} {
   post_message -type info "*******************************************************************"
   post_message -type info "User request to update project revision"
   source "update_rev.tcl"
   post_message -type info "*******************************************************************"



}
<<<<<<< refs/remotes/upstream/main
 
=======

>>>>>>> Revert "enlever le chain de argu"
# Do this when user clicks No
proc No {} {
   post_message -type warning "*******************************************************************"
   post_message -type warning "Project revision was not updated."
   post_message -type warning "*******************************************************************"
}
<<<<<<< refs/remotes/upstream/main
 
=======

>>>>>>> Revert "enlever le chain de argu"
#################
# Program Start #
#################
init_tk
set dialogTitle "Project revision update"
set dialogText "Update project revision?"
<<<<<<< refs/remotes/upstream/main
 
=======

>>>>>>> Revert "enlever le chain de argu"
if {[CreateDialog $dialogTitle $dialogText] == yes} {
   Yes
} else {
   No
<<<<<<< refs/remotes/upstream/main
}
=======
}
>>>>>>> Revert "enlever le chain de argu"
