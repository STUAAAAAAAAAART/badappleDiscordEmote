# Bad Apple!! - Discord Animated Emote Edition

or at best an attempt to make the video play in its entire run length in a discord emote

## downloading the GIF emote

it's the GIF at the root of this repo

for web users: this image:

![BAD APPLE!!](badApple.gif)

## Full-er Explainer

[🔗 https://stuaaaaaaaaaart.github.io/posts/toys/badAppleEmote.html](https://stuaaaaaaaaaart.github.io/posts/toys/badAppleEmote.html)


## Brief Background

There was previous a naiive attempt to compress the bad apple video into an animated GIF that would meet Discord's file upload limits for emotes (which was 256KB at the time). The first attempt was a 24x24 pixel GIF with a colour palette of black, white, and grey, and had a filesize of 242KB and a constant frametime of 0.07s each frame.

Unfortunately, Discord limited playback of the GIF to around the 2000th frame, playing halfway through before looping back to the start. With that in mind, this project aims to include and address this limitation of animated GIF emotes on Discord.

## Strategy

GIFs can only specify frametimes of each frame in multiples of 0.01s (10ms), so FPS ranges (e.g. 25, 30, 60 etc) would be rounded to the nearest 0.01s. This project will work in frametimes rather than framerates

The pipeline for the very first image was:
- crop and transcode the video down to a size managable in photoshop's animated timeline workspace
  - there was a point in time where photoshop limits the timeline of an open project file to 500 frames when importing, but this is circumvented by copying all the frames from one project to another in the timeline window
- use the legacy Save For Web to preview the estimated filesize and reduce colour and size resolution to fit the 256KB limit

With the 2000 frame budget, and a target average frametime of 0.08s (about 12.5fps), sections of the video with a slower motion rate would have the frametimes increased (displayed frame lingers more, saving a few frames each), and faster motion gets more frames through shorter frametimes, effectively making a GIF with a variable framerate.

The new strategy, in abstract:
- convert the 30fps source to 25fps for editing purposes
- upscale the 30fps source to 100fps for image processing purposes (with optical flow)
- in the 25fps cut: remove all static frames (i.e. frames with almost no motion relative to nearby frames)
  - **implemented**: see next point
  - **future improvement**:
    - a frame difference comparison to see if the difference of luminance are somewhere near zero
- remove as many low-motion frames as possible without completely tanking motion rate (i.e. the sequence of images with an object/pixel moving across pixel length between frames)
  - **implemented**: a premiere pro sequence, cut to separate the video by percieved motion
  - **future improvement**:
    - a motion vector system to deduce possible motion in frame (edge cases include certain shots where the frames or sections invert in "colour"), and evaluating the the statistical difference to determine which frames to group together into a section (smaller sections would be possible compared to the manual cut, right down to the resultant per-frame info in the final GIF)
- export the cuts to a processable JSON file outside of premiere pro
  - **implemented**: a helper python script to transcribe the cuts
  - **future improvement**:
    - interfacing with premiere directly (or export the sequence into a final cut XML) to read the cuts programmetically and save them to file
	- in lieu of using premiere (from a possible improvement from the previous step), this would be unnecessary, but figuring out an interface to access information from a sequence in a premiere pro project would be nice for other purposes
- tagging each cut with a blending mode when merging multiple 100fps frames into a single GIF output frame
  - **implemented**: manual input with above helper python script
  - **limitations**: sections of the video where it switches from white being the objective to black being the objective (and vice versa, even half-half towards the end). these sections are averaged together (rather than adding or multiplying frames together)
  - **future improvement**:
    - possibly luminance counting? object detection? this would be much easier working forward rather than backwards 
- using the 100fps sequence: blend each section of frames together according to the cut file
  - **implementation**: carried out the operation using python pillow image library and hold as list of `PIL.image.image` objects, along with a separate list of frametimes
- export the list of images and frametimes into a GIF
  - **implementation**: `PIL.image.save()`
  - **considered**: saving individual frames and exporting to photoshop, but assigning frametimes per frame manually in the timeline editor would be a nightmare
- import GIF into photoshop and compress using legacy save for web
  - **future improvement**:
    - carry this operation out programmatically in python, with a function estimating resultant filesize with what's currently generated for the export
	  - this is currently possible with static images, but more experimentation with PIL is needed with animated sequences, especially with GIFs

additional helper tools:
- `cutListInput.py` -> `cutFile.json`
  - for manual transcription of cutes made in premiere pro
  - simple line input without a UI, with enough fallbacks for common errors (e.g. mistype, writing to file on sudden stopping)
- `imagePreviewer.py`
  - to preview playback without importing back to premiere or photoshop
  - counts the number of GIF frames that would be created in the end
  - also to test frametime adjustments to sections and playing back the changes in-situ without editng the cut list
  - uses the [openCV python library](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html) instead of PIL, because PIL writes files to disk when previewing and there are about 2000 frames to play back.<br/>as far as i could find while reading the docs, openCV pushes images to the GPU for playback
    - `pip install --upgrade opencv-python`

# Result

![BAD APPLE!!](badApple.gif)

- 248 KB
- variable framerates, nominally 12.5fps, fastest sections 16.66fps
- 1999 frames total
- 32px x 32px
- 4-colour web palette

issues:

- not great as a standalone large emote when used without text in chat. some fizzy edges but it's mostly from using the diffusion setting in the gradient solver in photoshop
- ~~due to lots of rounding, this emote plays a bit quicker~~
  - 99.99% fixed! total frametimes lost to rounding is added back every time the running subtotal can make 0.01s worth of frametime to the actively processed GIF frame (you can probably sing to this now!)
- a few hold and slow sections feel stuttery, although addressing it requires fighting the 2000 frame limit again

# Questons asked by peers

- Why not do everything straight ahead in Photoshop?

> Photoshop's importer would normally do up to the first 500 frames, although this can be circumvented by copying the frames from one open project to another. Importing the source video as-is would be very memory intensive and would slow the program down.
>
> Most importantly: combing through the entire timeline to do layer merges and adjusting frametimes while ensuring the right layer is visible during the frame is extremely prone to human error, and there is not an easy way to quickly preview and edit and undo frametime changes across the whole duration (Photoshop also struggles with playback at times)
>
> Executing this in python would allow me more general control of the process, while delegating discrete tasks to the script. Also this would allow for intraframe layer merging options like averaging multiple layers together (not an easy task within the means of Photoshop) or adding/multiplying layers together (easier than averaging, but still prone to human error) 

- Why not export the sections in Premiere directly and port that to Photoshop?

> There are 272 sections in the whole duration which can have their frametimes individually adjusted, and strategies to export them correctly would involve many sequences with different non-standard framerates (a luxury historically not afforded in versions of Premiere). Assembling them in Photoshop introduces another factor in human error, and adjusting the traget frametimes would involve finding the cut and exporting it in media encoder again (also deleting and inserting the frames in Photoshop's timeline, which is another factor for errors)
>
> Compiling the cuts into a JSON file and manipulating it in python would allow me to make planned adjustments first before actually exporting them, and the previewer script lets me play back an estimate of the final GIF to see if it looks right. (In fact, when the previewer script was complete, this was absolutely the shortest part in the process) Also this is the most easy way to keep count of produced GIF frames, and it's also possible to override all sections of a specific frametime down to a higher frametime value to quickly reduce GIF frame count

- Why not a constant frametime/framerate?

> The video has sections where the images didn't move, and I wanted to deal with that by having 1 frame represent each entire section where it's not moving
>
> Also I took inspiration from how traditional animation animated in multiples (e.g. "animating in twos / threes / fours"), and would like to see how I could potentially distribute frames in needed sections throughout the entire duration (i.e. faster motion has more frames, slower motion has fewer). A tiny GIF (in reactions or messages) would allow for some hiding of resolution artifacts (mostly visual, but potentially in time as well due to all motion in a space reduced to a tiny square)

- Why not use another format instead of a GIF? e.g. aPNG, silent mp4

> Discord only accepts animated emotes in animated GIF formats, although they do accept aPNG for larger stickers but that's a feature fewer users can partake in (i.e. everyone can react with an existing invoked emote, but no one can copy-use a sticker sent in a message)
>
> Also silent mp4 videos would be great for reaction images, but that's already covered by many others on GIF sites, and not what this project is about

- Why (mark) cut(s) in 25fps and have intermediaries in 100fps?

> The 100fps intermediary sequence is there to keep a 1:1 time resoltuion to the frametime resolution of the GIF format (i.e. one 100fps frame says on for 0.01s). Working out cuts in 25fps is just a convenience to cut the video in premiere and makes sequence traversal (and reading frame positions) a lot easier. Reconciling them is a factor of 4
>
> I had considered using 25fps as the intermediaries, but I thought to experiment with upscaling the number of frames with optical flow in Premiere and see if it would make adequate smear frames in motion

- Why use the openCV library for previewing a GIF test instead of using PIL throughout?

> PIL creates a temporary image file on disk every time `image.show()` is invoked, and that's an overhead (and write) i want to minimise. As far as I understand (i may be wrong, please DO open an issue to correct me here), OpenCV pushes the frames to the GPU instead, which would allow for a better playback (albeit not 100% time accurate due to my naiive use of the python time package to time frame playback)
>
> PIL is still used as the exporter from the python step, and has clear options for specifying data relating to GIFs

## other projects by others doing similar emotes:
- PotatoCider's Bad Apple 10x8 Animated Emote Wall <br/> https://github.com/PotatoCider/bad-apple-discord
- bad apple animated emote gif by /u/Karpa_RT <br/>https://www.reddit.com/r/touhou/comments/o3je2g/i_turned_bad_apple_into_a_gif/

