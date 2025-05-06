# Creating a new cookie cutter template 
## github
* Come up with a name for the template.
* Sign into github and go to the list of my repositories.
* Give the repository a name and optionally a description.
* Leave the repo as public.
* Don't use the options to create a readme, .gitignore or liscense.
* Hit the create button.

## OmniFocus
* Create a new project in OmniFocus Computing/Projects/*project_name*.
* Start adding known task to the project.

## Initial Setup
* Review the Cookie Cutter Templates document to select the approrate template to clone for the project.
* Move to the $HOME/devl directory.

`cd $HOME/devl`

Clone the new empty project to start things off.

`git clone https://github.com/jasmit35/cc-pypod.git`

Clone the source cookie cutter project into the /tmp directory.

`cd /tmp`

`git clone https://github.com/jasmit35/cc-pycmdline.git`

Remove the .git directory.

`rm -rf cc-pycmdline/.git`

Rename the directory to the new name them tar it up.

`mv cc-pycmdline cc-pypod`

`tar -cvf cc-pypod.tar cc-pypod`

Untar the code into the new devl directory.

`cd ~/devl`

`tar -xvf /tmp/cc-pypod.tar`

* Get the initial code onto github.

`git add .`

`git commit -m 'Initial Commit'`

`git remote add origin https://github.com/jasmit35/`*project_name*`.git`

`git push -u origin master`

## Add WOZ
`git remote -v`

`git remote rename origin github`

`remote add woz git@woz.local:/opt/app/git/Synctify.git`






* Create the virtual environment

`cd $HOME/devl/`*project_name*

`pyenv virtualenv 3.8.2 `*project_name*

`pyenv local `*project_name*

 


## Enhancements
Make sure the branch is up to date with the master branch in the repository.

`git pull origin master`

Create the new feature branch.

`git branch vers_0_2_0`

Check commits, tags and where HEAD is pointing.

`git log --oneline --decorate`

Switch to the new branch.

`git checkout vers_0_2_0`


## Add WOZ
`git remote -v`

`git remote rename origin github`

`remote add woz git@woz.local:/opt/app/git/Synctify.git`
