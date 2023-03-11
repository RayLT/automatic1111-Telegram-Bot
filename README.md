
# automatic1111 Telegram Bot

 A Telegram Bot for your self-hosted instance of automatic1111 since the webui is bad on smaller screens (i.e. my iphone mini) or you don't have a vpn set up to generate images from a remote location.
 
 __Keep in mind that all generated images and messages are stored on telegram servers!__

 


## Installation

 __Make sure to enable the api for automatic1111.__

 Add --api to the COMMANDLINE_ARGS in your webui-user.bat

Copy the repository to some place on your computer.

Run the automtatic1111.py for the first time to create the settings.cfg file.

Create a Telegram bot with BotFather.

Copy the bot token into your ***settings.cfg***.

Create a new chat in telegram with your bot.
The bot will reply that you are not allowed to use it.

Copy the ID it sends you into the ***allowed_users*** inside of your ***settings.cfg***.

Save the file. Restart the script and you are good to go.
    
## Usage/Examples

To generate a prompt simply write a message to the bot.


Additionally the following commands are available:
/start
> Standard start command. Has to be replaced.

/help
> Will output a help message. Currently not useful :(

/batch
> Get / set the batch size (how many images to generate at once). Takes an optional integer to set the size.
> 
> Ex: */batch 4*
>
> _Note:_
>
> _For batch sizes > 1 the bot will group the images to media groups._
>
> _For batch sizes > 10 the bot will split the media groups into multiple since you can only send 10 images at once._

/last
> Generates an images from the last prompt.

/cfg
> Get / set the cfg scale for automatic1111. Takes an optional float to set the cfg scale.
> 
> Ex: */cfg 7.5*

/steps
> Get / set the amount of steps automatic1111 will take to generate an image. Takes an optional integer.
> 
> Ex: */steps 35*

/settings
> Replies with a text message of the current settings.

/size
> Set the size of the generated images. Currently handled with inline buttons and only setting the aspect ratio.
>
>SQUARE, PORTRAIT OR LANDSCAPE in 512x512, 512x786, 786x512

/model
> Generates buttons of all available models in automatic1111. Select and load a new model by clicking the corresponding button.

/style
> Adds a style from the automatic1111 styles menu. Currently only possible to set one at a time.

/sampler
> Generates buttons for all available samplers in automatic1111

/faces
> Choose to restore faces in generated images or not.

/nsfw
> Choose to check for nsfw prompts or not. Does not check the actual image for (accidental) nudity (yet).
>
> If enabled will check prompt content against a list of "bad" words from https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en
> 
> Flags images in telegram with the has_spoiler tag to blurr them until tapped.
> You could also add the nsfw-checker in automatic1111 itself to replace to automatically replace affected images with black ones

## To-Do / Planned
- Add the option to add multiple styles.
- Add options to not generate nsfw prompts at all _(if enabled)_.
- Add logs for generated images to regenerate and upscale them.

## Contributing

Contributions are always welcome!

Let me know how much I suck at programming via the issues tab ❤️