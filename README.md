# Social Listening on Reddit

This is a social listening script built on top of [PRAW](https://praw.readthedocs.org/en/stable/) (Python Reddit API Wrapper). It was initially designed for sentiment analysis and competitive analysis for a project at Kaplan Test Prep, but it's general enough to search for and locally store any terms, within any or all subreddits. 

Note: This README is paced at a beginner level; if you already have PRAW up and running with OAuth, feel free to clone the repo and skip the reading, with the exception of the Configuration step below. 

###1. Setup

Start by grabbing all the dependencies, listed in order below. 

(a) [pip](https://pip.pypa.io/en/stable/installing/) (for easy installation of python packages)

You likely already have this if you have a standard Python installation; you can quickly check with 

```bash
$ pip --version
```

at the command line (where `$` here and below stands for whatever your terminal prompt is), or follow the installation instructions at the link.

(b) [PRAW](https://github.com/praw-dev/praw#installation) (for accessing Reddit's API via Python)

**Be sure** to install the development version by typing 

```bash
$ pip install --upgrade https://github.com/praw-dev/praw/archive/master.zip
``` 

at the command line. This gives access to the complete volume of relevant posts, not just the first 1000.

(c) [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) (for heavier HTML parsing)

Install the most recent version by typing 

```bash
$ pip install beautifulsoup4
```

 at the command line.


###2. Clone this repo

From the command line type:

```bash
$ cd <absolute path to desired parent folder for project>
$ git clone 'https://github.com/suddensleep/reddit_scraper.git'
```

###3. Configuration

This is certainly the most involved step, but is in fact the last step before your scraper is up and running. We will use the [OAuth 2.0](http://oauth.net/) protocol to connect our scraper to the Reddit API. OAuth makes it possible for an application (this is the scraper) to be granted a specific set of permissions (for our purposes, this will be a reading-only app) by a registered user (this is you). 

You'll notice in your new local copy of this repo a file called `praw.ini`; use a standard text editor to open it. You should see five lines of text in the following format.

```
[my_app]
oauth_client_id: 
oauth_client_secret:
oauth_redirect_uri:
oauth_refresh_token:
```

The name inside the square brackets is called the "site name"; you can change it at your discretion, as long as you change the relevant line in the code. Leave it as `my_app` for now. Our goal is to fill in all four fields below the site name. 

The [PRAW and OAuth tutorial](http://praw.readthedocs.org/en/stable/pages/oauth.html) on the PRAW website is an extremely lucid presentation of how to do this, with only minor explanations needed:

- The first thing to note is that `>>> import praw` is a command in Python; you can get to such a prompt by simply typing `python` at the command line.

- The other thing to note is that at the end of Step 3, the line 

```python
>>> url = r.get_authorize_url('uniqueKey', 'identity', True)
```

should actually read 

```python 
>>> url = r.get_authorize_url('uniqueKey', 'read', True)
```

This is because we are giving our app permission to read posts.

The first three fields in `praw.ini` should be filled out by the end of Step 1; the refresh token will be returned as part of the access_information dictionary during Step 4. Copy and paste these into your config file and you should be good to go!

###4. Using the script

The script runs from the command line, with the following syntax:

```bash
$ python reddit_scrape.py "<your> <search> <terms>" [<subreddit>]
```

#####A quick explanation:
The `$` is your terminal prompt (i.e. don't type it).

You must type `python reddit_scrape.py` followed by your search terms, separated by spaces *and* surrounded by quotes.

You can also optionally search within a specific subreddit by supplying the name of that subreddit after your quoted search terms. Without this optional argument, the scraper will search within all subreddits (which, depending on what your search terms are, may take a long time).

For example,

```bash
$ python reddit_scrape.py "cute cat videos" aww
```

will search for cute cat videos within the subreddit [/r/aww](http://www.reddit.com/r/aww) (good luck with that), and 

```bash
$ python reddit_scrape.py "kim jong-il looking at things"
```

will search in *all* subreddits for mentions of Kim Jong-il doing his thing (RIP).

###5. Reading the output

The search results will be output in [`.json`](http://www.json.org/) format to the `./output` directory, with the file name 

```
<your>_<search>_<terms>__<subreddit>.json
```
So, for example, the two files produced from the commands in step 4 would be:

```bash
cute_cat_videos__aww.json
kim_jong-il_looking_at_things__all.json
```

Included in each file is an array of json objects representing posts matching your search terms and the comments on these posts that match at least one of your search terms. For posts, the name/value pairs are:

- `author` - author of the post
- `created_utc` - [epoch timestamp](https://en.wikipedia.org/wiki/Unix_time) of the post
- `gilded` - 0 or 1 depending on whether or not another user awarded this post ["reddit gold"](https://www.reddit.com/gold/about/)
- `name` - unique identifier of this object in the Reddit database
- `num_comments` - number of comments on this post
- `score` - a [rough](https://www.reddit.com/r/announcements/comments/28hjga/reddit_changes_individual_updown_vote_counts_no/) estimate of how helpful others found this post
- `selftext` - the text of the post itself
- `title` - the title line of the post (visible from subreddit feed)
- `url` - where to go to find this post

For comments, the same fields are used, but `num_comments` and `title` are null, and `url` refers to the url of the parent post.