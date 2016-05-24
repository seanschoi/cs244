# CS 244 Abstractions for Network Update

## Reproduction steps

### Initializing EC2 instance

1. Launch an EC2 instance with Ubuntu 10.04 i386. You can search for it in the list of community AMIs.

2. SSH into the EC2 instance and run the following commands to install the git package (If it does not exist already).

  `sudo apt-get update`  
  `sudo apt-get -y install git-core`

3. Run the following to get the project repo.

  `cd ~`
  `git clone https://github.com/yo2seol/cs244`

4. Run the following code to install mininet and all other dependencies.

  `cd ~`
  `tar -xzvf ~/cs244/pa3/mininet/mininet-1.0.0.tar.gz`
  `mv mininet-1.0.0/ mininet`
  `cp ~/cs244/pa3/mininet/install.sh ./mininet/util/`
  `sudo ./mininet/util/install.sh`

5. Go into '~/noxcore/build/src/nox/coreapps/examples' by running

  `cd ~/noxcore/build/src/nox/coreapps/examples`
  
  and add the following lines to meta.json

  {
    "name":  "UpdateApp",
      "dependencies": [
         "python"
      ],
      "python": "nox.coreapps.examples.update_app"
  }

6. Add in a link for the the update app specified above in `~/noxcore/build/src/nox/coreapps/examples`.

  `sudo ln -s ~/cs244/pa3/updates/update_app.py .`

7. `cd` into `~/cs244/pa3/updates/`

8. Clean the Mininet state by running

  `sudo mn -c`

8. Run the following command

  `sudo ./run.sh fattree 4 1`

9. IMPORTANT. First run will fail and hang infinitely. If you see that the program hangs after "Application Started" message, simply Ctrl+C and end the program, and rerun the run.sh script.
