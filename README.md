
# SneakerBot#
alpha 0.2

## Changes

 * Directly send data into requests without interacting with page elements
 * Token generation for adidas.co.uk

**Automatically purchase trainers from online stores**

Currently supports footpatrol.co.uk and adidas.co.uk

## Prerequisites
 * Python 2.7
 * [pip](https://pip.pypa.io/en/stable/installing/)
 * ```pip install -r requirements.txt```
 * [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) placed in system path (or System/System32 in windows).


## Usage
### Sneakerbot
 * clone repo with ```git clone https://github.com/rhawiz/sneakerbot.git``` or download through github.
 * ```cd sneakerbot/sneakerbot```
 * ```python sneakerbot.py --config <param> --instances <param>```
    * **config**: Path to config files separated by a list (see below) (e.g. sample1.cfg, sample2.cfg, sample3.cfg)
    * **instances**: Number of instances to run per config file

#### Configuration Parameters
Check ```sample.cfg``` for an example of how a sample configuration may look like.

##### **products** - [required] Product information
###### ```store = solebox | adidas | footpatrol``` - [required] Website to run the bot on. 
###### ```url = https://*``` - [optional] URL for the product. Will override code option (below).
###### ```code = XXXXX``` - [optional/required (if url not defined)] Product code for the website (e.g. BY1714, BA8530)
###### ```size = #``` - [required] Product size (e.g. 5, 5.5, 6, 6.5, 7, etc...)
###### ```quantity = #``` [required] Quantity of product to cart.

##### **delivery** - [required] Delivery details
###### ```first_name = xxxxx``` - [required] First name for delivery
###### ```last_name  = xxxxx``` - [required] Last name for delivery
###### ```address  = # xxxxx``` - [required] First line of address including number for delivery
###### ```city  = xxxxx``` - [required] City for delivery
###### ```postcode  = xxx xxx``` - [required] Postcode for delivery
###### ```email = xxx@xxx.xx``` - [required] Email for delivery
###### ```phone  = #######``` - [required] Phone number for delivery

##### **payment** - [required] Payment details
###### ```card_no = #############``` - [required] Long card number
###### ```name = ****``` - [required] First name and last name card is registered to
###### ```expiry = MM/YY``` - [required] Expire date in the format MM/YY (Format is important!)
###### ```cvv = ***``` - [required] CVV (3 digits on back of card)

##### **login** - [optional] Account and Login section for certain stores is required (e.g. solebox)
###### ```username = xxxxxxx``` - [optional] Site account username
###### ```password = xxxxxxx``` - [optional] Site account password

##### **settings**
###### ```bypass_stock_check = True | False``` - [optional] Defaults to False. Set this to true if too much traffic on website. It will bypass the process of checking whether the product is in stock.
###### ```driver = chrome``` - [optional] Defaults to chrome. If set to chrome process of buying products will be displayed. If set to phantomjs process will be run in the background. Must set to chrome if the process has some sort of captcha system inorder to manually input.
###### ```debug = True | False``` - [required] - Log process information for debugging purposes.




### ProductFinder
 * clone repo with ```git clone https://github.com/rhawiz/sneakerbot.git``` or download through github.
 * ```cd sneakerbot/sneakerbot```
 * ```python productfinder.py --store <param> --name <param> --colours <param> --gender <param>```
    * **store**: store (adidas only so far)
    * **name**: product name (does not have to be exact although for best results, try to)
    * **colours**: product colour (e.g. red,green,blue,purple)
    * **gender**: gender (e.g. men, women, kids)

### StockChecker
 * clone repo with ```git clone https://github.com/rhawiz/sneakerbot.git``` or download through github.
 * ```cd sneakerbot/sneakerbot```
 * ```python stockchecker.py --store <param> --codes <param> --sizes <param>```
    * **store**: product brand (adidas only so far)
    * **codes**: product codes alone or separated by comma (e.g. BB4314,S80682,S76724)
    * **sizes**: product colour alone or separated by comma (e.g. 12,7.5,13,6)

##Todo
 * ~~adidas bot configuration file readme~~
 * ~~Last test on release didn't go so well - inject request payload to URLs directly without loading content~~
 * ~~Wait for content to load before injecting the next javascript~~
 * Add phantom.js / chromedriver binary to project and link in code
 * Simplify config input 
 * Implement paypal payment
 * Stores:
    * ~~adidas.co.uk~~
    * ~~footpatrol.co.uk~~
    * solebox.com
    * offspring.co.uk
    * slamjamsocialism.com
    * size.co.uk
    * sneakersnstuff.com
    * thegoodwillout.com
    * asphaltgold.de
    * inflammable.com
    * mate-store.com
 
