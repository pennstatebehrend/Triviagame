import random
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

fileName = 'questions.json'

def initializeApp():
    cred = credentials.Certificate('triviaGameServiceAccountCredentials.json')
    default_app = firebase_admin.initialize_app(cred, {'databaseURL': "https://triviagame-d3550.firebaseio.com/"})
    print(default_app.name)
    
    resetUsersToDefault()
    setUsers()


def getNewID(problemIDs: list): 
    if(len(problemIDs) == 0):
       return -1
    id = random.randrange(0, len(problemIDs))
    return problemIDs.pop(id)

def getCurrentProblem(id: int): 
    
    with open(fileName) as json_file:
        problems = json.load(json_file)
        problem = problems["Problems"][str(id)]
        question = problem["Question"]
        answer = problem["Answer"]
        print(question)
        print("A:", problem["A"])
        print("B:", problem["B"])
        print("C:", problem["C"])
        print("D:", problem["D"])
    
        db.reference().update({
           "Question": {
               "Text": question,
               "A": problem["A"],
               "B": problem["B"],
               "C": problem["C"],
               "D": problem["D"]
               },
           "Answer": {
               answer: problem[answer]
               } 
           })
        return question
    
    
def getCurrentAnswerValue(id: int): 

    with open(fileName) as json_file:
        problems = json.load(json_file)
        answer = problems["Problems"][str(id)]["Answer"]
 
        return answer


def importProblems(problemIDs):
    with open(fileName) as json_file:
        problems = json.load(json_file)
        problemIDs = []
        for p in problems["Problems"]:
            problemIDs.append(p)
        return problemIDs
    

def displayUsers():
    user = db.reference("User")
    leaderlist = user.order_by_value().get()
    for key, val in leaderlist.items():
        print("{} has {} points".format(key, val))



def getUserPoints(userId: int):
    user = db.reference().child("User/" + str(userId))
    userPoints = user.get()
    return int(userPoints)

def addPointToUser(userId: int):
    user = db.reference().child("User/" + str(userId))
    userPoints = getUserPoints(userId)
    userPoints += 1
    user.set(userPoints)
    print("User " + str(userId) + " now has " + str(userPoints) + " points!")

def resetUsersToDefault():
    User = db.reference("User")
    User.set({
        "User": 0
        })
    users = User.get()

    for key in users:
        user = db.reference().child("User/{}".format(key))
        user.delete()      
   
    print("Users Successfully reset")

def setUsers():
    User = db.reference("User")
    User.set({
        "User": 0
        })
    User.set({
            "Default": 0
            
            })


def main():
    #Initialize
    initializeApp()
    gameOver = False

   
    user =  db.reference("User")
    
    ProblemIDs = []
    ProblemIDs = importProblems(ProblemIDs)

    pointLimit = 0
    
    print("The amount of questions are ", len(ProblemIDs))

    while(pointLimit < 1 or pointLimit > len(ProblemIDs)):
        print("Please enter the amount of points to win out of", len(ProblemIDs))
        pointLimit = int(input())       
        if(pointLimit < 1):
            print("Point Limit can not be less than 1")

        elif(pointLimit > len(ProblemIDs)):
            print("Point Limit can not be more than the amount of questions")


    
    while gameOver != True:
        
        id = getNewID(ProblemIDs)
        if(id == -1):
            print("Ran out of problems")
            break

        getCurrentProblem(id)

         


        
        userInput = input().capitalize()

        if (userInput == getCurrentAnswerValue(id)): 
            print("You got the question right!")
            addPointToUser("Default")
            displayUsers()
            if (getUserPoints("Default") == pointLimit):
                gameOver = True
    
        else: 
            print("You got the question wrong!")

    userListByScore =  db.reference("User").order_by_value().get()
    print("User", list(userListByScore.keys())[0], "Has Won")

    displayUsers()
 
main()