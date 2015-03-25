# ![](http://i.imgur.com/2B9xJqy.png) Tsuitekoi

Tsuitekoi is a small, easy tool to see who's unfollowed you on Twitter. It also lets you see and log who followed you and who changed names, but those aren't as interesting!

## Usage

Simply run `tsuitekoi.py` from the command line (or `python tsuitekoi.py`, if it's not in your PATH), and authorize Tsuitekoi to read from your account following the instructions it gives. This first time, Tsuitekoi sets up everything it needs to check your Twitter account.

Whenever you're wondering who unfollowed you, just run Tsuitekoi again and it'll compare your current followers to the the ones you had when you last ran it. It'll save a log of things that have happened, so you can easily remember, and naturally also print all the changes.

## Requirements

You will need [Python 2](https://www.python.org/downloads/) and Tweepy to run Tsuitekoi. To install Python, just download the installer and run it. To install Tweepy, run `pip install tweepy` from the command line.

If you don't have pip yet, install that first: on Linux, run `sudo apt-get install python-pip` and on Windows and OS X download `get-pip.py` from [pip's installation page](https://pip.readthedocs.org/en/latest/installing.html#install-pip) and run it with Python. Then follow the instructions on installing Tweepy above, and you should be all set.

## Note

Tsuitekoi stores your user key and user secret for authentication in plain text on your computer - this shouldn't be an issue, since they can only be used with Tsuitekoi, but don't go 'round giving the file named "auth" to people or they'll be able to check your account's unfollowers.

## Contact

If you've got any questions or just want to talk a bit, you can find me at [@obskyr](http://twitter.com/obskyr) on Twitter, or [e-mail me](mailto:powpowd@gmail.com). If you want a fast answer, Twitter is the place to go!

If there's a problem with Tsuitekoi, or a feature you think should be added, feel free to open an issue or pull request here on GitHub.
