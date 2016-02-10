############################################
#######     Reddit Scraper v. 1.0    #######
####### Code Written by John Gilling #######
############################################

import sys
import os
import praw
import json


from praw.helpers import submissions_between, flatten_tree
from praw.errors import OAuthAppRequired
from pprint import pprint
from bs4 import BeautifulSoup as bs


def clean_comment(result):
    """
    Transform Comment object into a dictionary of
    cleaned information.
    
    Arguments: 
    result is a Submission object

    Returns: 
    Dictionary of information listed above.
    """

    result_dict = {}

    if result.author is None:
        result_dict['author'] = None
    else:
        result_dict['author'] = result.author.name
    result_dict['created_utc'] = int(result.created_utc)
    result_dict['gilded'] = int(result.gilded)
    result_dict['name'] = result.name
    result_dict['num_comments'] = None
    result_dict['score'] = int(result.score)
    result_dict['body'] = ' '.join(
        bs(result.body).text.split()
    )
    result_dict['title'] = None
    result_dict['url'] = result._submission.url

    return result_dict


def clean_results(results, terms):
    """
    Subset and do string cleaning on each submission
    and comment result, put them in dictionary format.
    
    Arguments: 
    results is a list of Submission and Comment objects
    terms is a string of search terms

    Returns: 
    A list of dictionaries with the relevant information.
    """

    clean_list = []

    for result in results:
        if isinstance(result, praw.objects.Submission):
            clean_list.append(clean_submission(result))
        elif isinstance(result, praw.objects.Comment):
            clean_list.append(clean_comment(result))
        else:
            print ("Search result " +
                   str(type(result)) +
                   " is not a submission or a comment."
            )

    return clean_list


def clean_submission(result):
    """
    Transform Submission object into a dictionary of
    cleaned information.
    
    Arguments: 
    result is a Submission object

    Returns: 
    Dictionary of information listed above.
    """

    result_dict = {}

    if result.author is None:
        result_dict['author'] = None
    else:
        result_dict['author'] = result.author.name
    result_dict['created_utc'] = int(result.created_utc)
    result_dict['gilded'] = int(result.gilded)
    result_dict['name'] = result.name
    result_dict['num_comments'] = int(result.num_comments)
    result_dict['score'] = int(result.score)
    result_dict['body'] = ' '.join(
        bs(result.selftext).text.split()
    )
    result_dict['title'] = result.title
    result_dict['url'] = result.url

    return result_dict


def get_comments(results):
    """
    Add comment responses to the submissions that matched
    the search terms.
        
    Arguments: 
    results is a list of search results

    Returns:
    A list of search results and their 
    flattened comment trees.
    """

    comment_list = []

    num_subs = len(results)
    
    for i in range(num_subs):
        print ("Fetching comments from submission " +
               str(i + 1) +
               " of " +
               str(len(results)) +
               " ..."
        )
        results[i].replace_more_comments(limit = None, threshold = 0)
        comments = flatten_tree(results[i].comments)
        comment_list += comments

    num_comms = len(comment_list)
    
    print ("All " +
           str(num_comms) +
           " comments successfully fetched,"
           " for a total of " +
           str(num_subs + num_comms) +
           " search results."
    )
    
    return (results + comment_list)


def write_results(results, terms, output_file):
    """
    Write results to the directory ./output/ with the
    supplied filename.

    Arguments:
    results is a list of dictionaries representing
    Submission and Comment data
    output_file is a string representing a target filename

    Returns: 
    None (writes to file instead)
    """

    output_dir = os.getcwd() + '/output/'

    while output_file in os.listdir(output_dir):
        output_file = raw_input("File already exists. New file name: ")

    list_terms = map(lambda x: x.lower(), terms.split())

    results = filter(
        lambda x: any(
            map(lambda y: y in x['body'].lower(),
                list_terms)
        ),
        results)
    
    with open(output_dir + output_file, 'w') as f:
        json.dump(results, f, sort_keys = True)

    
def main(*args):
    """ 
    Main loop of scraping iteration.
        
    Arguments: 
    terms is a string of search terms
    subreddit is a string representing subreddit to search in

    Returns: 
    None (write to file instead)
    """

    if len(args) == 1:
        terms = args[0]
        subreddit = 'all'
    elif len(args) == 2:
        terms = args[0]
        subreddit = args[1]
    else:
        print ('Usage: python reddit_scrape.py "<search terms>" '
               '[<subreddit>]')
        return
    
    output_file = "__".join(['_'.join(terms.split()),
                             subreddit]) + '.json'
    
    # initialize Reddit session (see praw.ini for OAuth details)
    r = praw.Reddit(user_agent='Full Scraper by '
                    '/u/<your_username_here> version 1.0',
                    site_name='my_app')

    # gather refresh token from praw.ini
    try:
        r.refresh_access_information()
    except OAuthAppRequired:
        print "Check your OAuth login information (see ./praw.ini)."

    # get list of search results with the given terms
    search_results = list(submissions_between(
        r,
        subreddit,
        extra_cloudsearch_fields={'selftext': terms}
        )
    )

    # get comments for each submission above
    # and pull the ones that match the search
    search_results_with_comments = get_comments(search_results)

    # get list of cleaned search results
    cleaned_results = clean_results(search_results_with_comments,
                                    terms)
    
    # write results to file in directory ./output/
    write_results(cleaned_results, terms, output_file)


if __name__ == '__main__':
    main(*sys.argv[1:])
