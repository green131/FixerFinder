import time
import praw

global done
global fixed
global keywords

def isFixed(title):
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
        if submission.id not in done and isFixed(title_lwr):
            fixed.append(submission.id)
            print("isFixed: (" + submission.id + ") " + title_lwr)
            findOriginal(title_lwr)
        done.append(submission.id)
        
def findOriginal(title):
    #Format Title to Find Original Post
    print("Before: " + str(title))
    for word in keywords:
        if word in title:
            title = title.replace(word, "")
            print("After: " + str(title))
            break
    x=0
    for search_result in r.search(title):
        fixed = 0
        if isFixed(search_result):
            fixed = 1
        print("Search Result " + str(x+1) + ":" + str(search_result) + "\n"
              + "-- ID: " + str(search_result.id) + "\n"
              + "-- Created: " + str(search_result.created) + "\n"
              + "-- Contains Fixed: " + str(fixed))
        x+=1
        if x>9:
            break


#-------------------Main Script-------------------------
sleep=60
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