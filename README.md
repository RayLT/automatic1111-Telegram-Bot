
# automatic1111 Telegram Bot

 A Telegram Bot for your self-hosted instance of automatic1111.

 Make sure to enable the api.

 Add --api to the COMMANDLINE_ARGS in your webui-user.bat

 There is the option to check the prompt for nsfw tags from [List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words]
(https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en)

 If enabled the images will be flagged in telegram with has_spoiler which hides them until tapped.

 


## Installation

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
> Get / set the batch size (how many images to generate at once). Takes an optional integer to set the size. Ex: */batch 4*

/last
> Generates an images from the last prompt.

/cfg
> Get / set the cfg scale for automatic1111. Takes an optional float to set the cfg scale. Ex: */cfg 7.5*

/steps
> Get / set the amount of steps automatic1111 will take to generate an image. Takes an optional integer. Ex: */steps 35*

/settings
> Replies with a text message of the current settings.

/size
> Set the size of the generated images. Currently handled with inline buttons and only setting the aspect ratio.

>SQUARE, PORTRAIT OR LANDSCAPE in 512x512, 512x786, 786x512

/model
> Generates buttons of all available models in automatic1111. Select and load a new model by clicking the corresponding button.

/style
> Adds a style from the automatic1111 styles menu. Currently only possible to set one at a time. Will add the option to add multiple styles.

/sampler
> Generates buttons for all available samplers in automatic1111

/faces
> Choose to restore faces in generated images or not.

/nsfw
> Choose to check for nsfw prompts or not.
