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
        #Make search_result title lowercase
        search_result.title = search_result.title.lower()
        #Find date created
        created_date = datetime.date(search_result.created)
        created_time = datetime.time(search_result.created)
        #Identify if search_result isFixed
        fixed = isFixed(search_result.title, keywords)
        #DEBUG
        print("Search Result " + str(x+1) + ": " + str(search_result.title) + "\n"
              + "-- ID: " + str(search_result.id) + "\n"
              + "-- Created (day): " + str(created_date) + "\n"
              + "-- Created (time): " + str(created_time) + "\n"
              + "-- Contains Fixed: " + str(fixed))
        #Compare search_result with fixed
        if (created_date.day == datetime.datetime.now().date().day):
            print("Same day match...")
            if (search_result.title == title):
                print("MATCH FOUND: \n" 
                    + search_result.title + "\n"
                    + title)
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