import time
import datetime
import praw
import math
import difflib

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
            doc = open('C:/Users/Daniel/Documents/GitHub/fixerfinder/fixerfinder/Base/posted.txt', 'rU')
            if submission.id in doc:
                print("Skipped - ID in DOC")
                doc.close()
            else:
                fixed.append(submission.id)
                print("isFixed: (" + submission.id + ") " + title_lwr)
                findOriginal(title_lwr, submission)
                doc.close()
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
        created_year = created.year
        created_month = created.month
        created_day = created.day
        #Get current date
        time = datetime.datetime.now().date()
        time_year = time.year
        time_month = time.month
        time_day = time.day
        #Identify if search_result isFixed
        fixed = isFixed(search_result_title, keywords)
        #DEBUG
        print("Search Result " + str(x+1) + ": " + str(search_result_title) + "\n"
              + "-- ID: " + str(search_result.id) + "\n"
              + "-- Created Date: " + str(created) + "\n"
              + "-- Current Date: " + str(time) + "\n"
              + "-- Contains Fixed: " + str(fixed))
        #Compare search_result with fixed
        if (created_year == time_year) and (created_month == time_month) and (math.fabs(created_day - time_day) < 2):
            print("Same day (+-1) match...")
            if fixed == False:
                print("Not Fixed...")
                search_result_title = " ".join(search_result_title.split())
                fixed_title = " ".join(title.split())
                match = difflib.SequenceMatcher(None, search_result_title, fixed_title).ratio()
                if match > 0.80:
                    print("MATCH FOUND: \n   " 
                        + search_result.title + "\n   "
                        + title)
                    matched_url = search_result.short_link
                    matched_title = search_result.title
                    doc = open('C:/Users/Daniel/Documents/GitHub/fixerfinder/fixerfinder/Base/posted.txt', 'a')
                    doc.write('\n' + str(original_submission.id))
                    doc.close()
                    print("Posting Comment...")
                    original_submission.add_comment("**Original Post** (" + match + "%) \n\n" +
                                           "-------------\n\n" + 
                                           "**Title**: " + matched_title + "\n\n"
                                           "**Link**: [" + matched_url + "](" + matched_url + ")\n\n" +
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
        done = [done[0], done[-1]]
        print("Entering Sleep (" + str(sleep) + "s)")
        time.sleep(sleep)