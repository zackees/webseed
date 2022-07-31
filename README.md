# webtorrent-webseed
Blazing Webseed Implementation for Webtorrent

# Usage

  * Installation
    * Get a docker app instance on render.com
    * Set it to this repo slug zackees/webtorrent-webseed
    * Rent disk storage and attach it as `/var/data`, 50GB should be good
    * Submit and allow docker to build and come up at port 80
  * Updating files
    * ssh into the running instance
    * Upload the content that you want to the `var/data/content` directory
      * Note, most videos downloaded from youtube DONT WORK. The around is to re-encode using ffmpeg and the x264 codec.
      * Wormhole file transfer is built into this service.
        * On your local machine with the content use: `wormhole send myfile.mp4`
        * Copy and paste the magic command into the remote machine and the file
          will transfer.
