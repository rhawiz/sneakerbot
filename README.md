
# SneakerBot #

**Automatically purchase trainers from online stores**

## Prerequisites
 * Python 2.7
 * ```pip install -r requirements.txt```
 * phantom.js can be found [here](http://phantomjs.org/)


## Usage
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
 * adidas bot configuration file
 * Add phantom.js binary to project
