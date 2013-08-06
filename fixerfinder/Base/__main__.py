import time
import datetime
import praw

global done
global fixed
global keywords

def isFixed(title, keywords):
    return any(string in title for string in keywords)

def findFixed():
    i=0
    for submission in subreddit.get_new(limit=1000):
        #Early Kickout if already scanned
        if submission.id in done:
            print("Reached end of new posts")
            return 0
        #Percent Counter
        i+=1
        if i%100 == 0:
            print(str(i/10) + "%")
        title_lwr = submission.title.lower()
        if submission.id not in done and isFixed(title_lwr, keywords):
            fixed.append(submission.id)
            print("isFixed: (" + submission.id + ") " + title_lwr)
            findOriginal(title_lwr, submission)
        done.append(submission.id)
        
def findOriginal(title, original_submission):
    #Format Title to Find Original Post
    print("Before: " + str(title))
    for word in keywords:
        if word in title:
            title = title.replace(word, "")
            print("After: " + str(title))
            break
    x=0
    for search_result in r.search(title):
        #Make search_result title lowercase
        search_result_title = search_result.title.lower()
        #Find date created
        created = datetime.datetime.fromtimestamp(search_result.created).date()
        #Get current date
        time = datetime.datetime.now().date()
        #Identify if search_result isFixed
        fixed = isFixed(search_result_title, keywords)
        #DEBUG
        print("Search Result " + str(x+1) + ": " + str(search_result_title) + "\n"
              + "-- ID: " + str(search_result.id) + "\n"
              + "-- Created Date: " + str(created) + "\n"
              + "-- Current Date: " + str(time) + "\n"
              + "-- Contains Fixed: " + str(fixed))
        #Compare search_result with fixed
        if (created == time and fixed == False):
            #print("Same day match...")
            if search_result_title in title or title in search_result_title:
                print("MATCH FOUND: \n   " 
                    + search_result.title + "\n   "
                    + title)
                matched_url = search_result.short_link
                matched_title = search_result.title
                print("Posting Comment...")
                original_submission.add_comment("**Original Post**  " +
                                       "This FIXED post has a found Original Post  " +
                                       "  " + 
                                       "Title: " + matched_title + "  "
                                       "Link: [" + matched_url + "](" + matched_url + ")  " +
                                       "  " +
                                       "*Questions or concerns? Message /u/fixerfinder*")
                print("...Comment Posted")
                break
        #Counter
        x+=1
        if x>(max_searching-1):
            break


#-------------------Main Script-------------------------
sleep=60
max_searching=15
if __name__ == "__main__":
    #Login & Connection
    r = praw.Reddit(user_agent="fixerfinder")
    r.login(username="fixerfinder")
    done = [] #Stores Checked Submission ID
    fixed = [] #Stores FIXED Submission ID
    keywords = ["[fixed]", "(fixed)"] #Keywords to check for
    subreddit = r.get_subreddit('all')
    #Continuous Iterations
    while True:
        print("Beginning Scan...")
        #Find FIXED Submissions
        findFixed()
        print("...Scan Complete")
        #Shorten Done to Include Only End Points
        done = [done.pop(0), done.pop(-1)]
        print("Entering Sleep (" + str(sleep) + "s)")
        time.sleep(sleep)