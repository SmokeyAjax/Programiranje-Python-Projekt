import re
import requests
import random
import operator


class SteamUser:
    # en igralec

    def __init__(self, userID):
        self.steamUserID = userID
        self.steamProfileText = requests.get("https://steamcommunity.com/profiles/" + userID).text

        # ime uporabnika
        steamUserName = re.findall(r'<title>Steam Community :: .+</title>', self.steamProfileText)
        steamUserName = re.sub(r'<[^>]+>', "", steamUserName[0])
        self.steamUserName = re.sub(r'.+ :: ', "", steamUserName)

        # koliko iger ima uporabnik
        numberOfGamesOwned = re.findall(r"\d+ games owned", self.steamProfileText)

        # pogledamo če je profil privaten
        if len(numberOfGamesOwned) == 0:
            self.private = True
        else:
            self.private = False
            self.numberOfGamesOwned = numberOfGamesOwned[0].split(" ")[0]



    def __repr__(self):
        return self.__class__.__name__ + "(" + self.steamUserID + ")"

    def privateProfile(self):
        """
        zbriše objekt, če je privaten profil in vrne stanje privatnosti
        """
        if self.private == True:
            del self
            return True
        else:
            return False


    def getLevel(self):
        '''
            vrne level uporabnika
        '''
        level = re.findall(r'<span class="friendPlayerLevelNum">\d+</span></div>', self.steamProfileText)
        level = re.sub(r'<[^>]+>', "", level[0])
        return level

    def __str__(self):
        # pomembna sta nam predvsem level in število iger
        return f'Uporabnik {self.steamUserName} je level {self.getLevel()} in ima {self.numberOfGamesOwned} različnih iger.'

    def getFriends(self):
        '''
            vrne 2 tebeli: tabelo imen in tabelo id prijateljev
        '''
        # gre na stran uporabnika, kjer so prikazani vsi njegovi prijatelji
        steamFriendsText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/friends/").text

        # dobi imena vseh prijateljev in jih shrani v tabelo
        steamFriendNames = re.findall(r'<div class="friend_block_content">.+<br>', steamFriendsText)
        steamFriendNames = [re.sub(r'<[^>]+>', "", name) for name in steamFriendNames]
        ##print(self.steamFriendNames, len(self.steamFriendNames))

        # dobi ID
        steamFriendIDs = re.findall(r'data-steamid="\d+"', steamFriendsText)
        steamFriendIDs = [re.sub(r'[^0-9]+', "", ID) for ID in steamFriendIDs]

        return steamFriendNames, steamFriendIDs  # (ime, ID)

    def howManyFriends(self):
        '''
            vrne število prijateljev
        '''
        if len(self.getFriends()[0]) == 0:
            self.private = True
        return len(self.getFriends()[0])

    def getFeaturedGames(self):
        '''
            vrne "Featured Games"
            igre ka jih ima uporabnik "raskzane", ponavad njegove najljubše/ najbol igrane
            raskazane ima lahko od 0-4
        '''
        featuredGames = re.findall(
            r'<div class="showcase_slot showcase_gamecollector_game[^h]+href="https://steamcommunity.com/app/[^"]+',
            self.steamProfileText)
        for i, game in enumerate(featuredGames):
            thisGame = game.split('href="')[1]
            thisGame = re.findall(r'<title>Steam Community :: .+</title>', requests.get(thisGame).text)
            thisGame = re.sub(r'<[^>]+>', "", thisGame[0])
            thisGame = re.sub(r'.+ :: ', "", thisGame)
            thisGame = re.sub('™', '', thisGame)
            featuredGames[i] = re.sub('®', '', thisGame)

        return sorted(featuredGames, key=lambda x: x[1])

    def getOwnedGames(self):
        '''
            vrne urejen slovar iger uporabnika ter pripadajoča števila ur (urejen glede na št. igranih ur)
        '''
        gamesText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/games/?tab=all",
                                 self.steamProfileText).text
        gamesText = re.findall(r'<script language="javascript">[^<]+</script>', gamesText)

        # če je profil privaten, se vrnemo
        if len(gamesText) == 0:
            return

        # igre
        games = re.findall(r'"name":"[^"]+"', gamesText[0])
        games = [re.sub(r'"name":"', "", game) for game in games]
        games = [re.sub(r'"', "", game) for game in games]
        games = [re.sub(r"\\[\w\d]+", "", game) for game in games]

        # čas igrane igre
        gameTime = re.findall(r'"hours_forever":"[^"]+"', gamesText[0])
        gameTime = [re.sub(r'"hours_forever":"', "", time) for time in gameTime]
        gameTime = [re.sub(r'"', "", time) for time in gameTime]
        gameTime = [re.sub(r',', "", time) for time in gameTime]

        gameDict = dict()
        for i, game in enumerate(games):
            try:
                gameDict[game] = gameTime[i]
            except:
                gameDict[game] = '0'

        return gameDict

    def getPlayTime(self):
        '''
            vrne število preigranih ur od vseh iger
        '''
        playTime = self.getOwnedGames()
        totalPlayTime = 0
        for singlePlayTime in playTime.values():

            totalPlayTime += float(singlePlayTime)

        if totalPlayTime == 0:
            self.private = True
        return int(totalPlayTime)

    def getMostPopularGames(self):
        '''
            vrne seznam
            seznam vsebuje 10 iger, med katerimi so vedno "featured games"
            in igre, ki so največ časa bile igrane
        '''
        top = set(self.getFeaturedGames())
        games = list(self.getOwnedGames().keys())
        lenght = len(top)
        for i, game in enumerate(games):
            if lenght + i > 10:
                break
            top.add(game)
        return sorted(top)

    def getLikedGames(self):
        '''
            vrne seznam, ki vsebuje vse igre, ki so bile igrane več kot 50 ur
        '''
        liked = []
        ownedGames = self.getOwnedGames()
        for game in ownedGames:
            if float(ownedGames[game]) <= 50:
                break
            liked.append(game)
        return liked

def commonFriends(self, other):
    '''
        returns friends that 2 users have incommon
    '''
    selfFriends = SteamUser(self).getFriends()[0]
    otherFriends = SteamUser(other).getFriends()[0]
    incommon = []
    for friend in selfFriends:
        if friend in otherFriends:
            incommon.append(friend)
    return incommon


# preiskovanje omrežja

def createUserObjects(establishedUsers, removedObjects):
    """
    iz enega uporabnika ustvari nov objekt za vsakega prijatelja
    hkrati dela slovar že narejenih uporabnikov
    """

    # izberemo naključnega uporabnika, iz katerega bomo pridobili podatke
    keyArray = list()
    for key in establishedUsers.keys():
        keyArray.append(key)

    length = random.randint(0, len(establishedUsers) - 1)
    pivot = keyArray[length]

    # naredi objekt za vse prijatelje, ki nimajo privatne profile
    friendsID = establishedUsers[pivot].getFriends()
    for friend in friendsID[1]:
        if friend not in establishedUsers:
            friendObject = SteamUser(friend)

            # pogledamo če je privaten
            private = friendObject.privateProfile()

            if not private and friend not in removedObjects:
                establishedUsers[friend] = friendObject
    try:
        for name, object in establishedUsers.items():
            if int(object.getPlayTime()) == 0 or int(object.howManyFriends()) == 0:
                removedObjects.append(name)
    except:
        pass

    # se znebimo še uporabnikov, kjer majo določene podatke skrite
    for name in removedObjects:
        try:
            del establishedUsers[name]
        except:
            pass

    return establishedUsers, removedObjects


def setUpDataSet(size, selfID):
    """
    vrne seznam objektov, kjer vsak objekt prikazuje določenega uporabnika
    """
    pivot = SteamUser(selfID)

    establishedUsers = dict()
    establishedUsers[selfID] = pivot

    removedObjects = list()

    while len(establishedUsers) < size:
        establishedUsers, removedObjects = createUserObjects(establishedUsers, removedObjects)
        print(len(establishedUsers), len(removedObjects))

    return establishedUsers

def displayData(establishedUsers):
    """
    predstavimo in vizualiziramo podatke
    """
    try:
        file = open("Stem Data.txt", "x")
    except:
        file = open("myfile.txt", "w")

    numberOfUsers = 0
    totalHours = 0
    totalGames = 0
    totalFriends = 0
    totalLevel = 0

    for name, object in establishedUsers.items():
        try:
            file.write("{0:>28s} | '{1:s}'".format("User Name" ,object.steamUserName))
            file.write("{0:>28s} | '{1:s}'".format("User ID", object.steamUserID))
            file.write("{0:>28s} | '{1:d}'".format("Level", int(object.getLevel())))
            file.write("{0:>28s} | '{1:d}'".format("Number of games", int(object.numberOfGamesOwned)))
            file.write("{0:>28s} | '{1:d}'".format("Total play time", int(object.getPlayTime())))
            file.write("{0:>28s} | '{1:d}'".format("Number of friends", int(object.howManyFriends())))

            file.write("")

            numberOfUsers += 1
            totalLevel += int(object.getLevel())
            totalGames += int(object.numberOfGamesOwned)
            totalHours += int(object.getPlayTime())
            totalFriends += int(object.howManyFriends())
        except:
            print("to many calls")

    file.write("{0:>28s} | '{1:d}'".format("Number of users", int(numberOfUsers)))
    file.write("{0:>28s} | '{1:d}'".format("Total number of levels", int(totalLevel)))
    file.write("{0:>28s} | '{1:d}'".format("Total number of games", int(totalGames)))
    file.write("{0:>28s} | '{1:d}'".format("Total play time of all users", int(totalHours)))
    file.write("{0:>28s} | '{1:d}'".format("Total number of friends", int(totalFriends)))

    file.write("")

    file.close()



'''
    za vsakega prijatelja našga uporabnika ustvariva svoj objekt Friend..
    definirava:
        skupni prijatelji (samo direktni)
        top 3 prijatelji glede na
            level
            št. imetih iger
        katere so najbolj igrane igre med prijatelji
'''


# naredimo nekaj čez SIZE-objektov, kjer vsak objekt prikazuje določenega uporabnika
# podamo poljubno število, ki bo predstavljala spodno mejo za velikost baze
SIZE = 10

# ID mojga Steam Accounta ("Ajax")
# tukaj podamo uporabnika iz katerega bomo pridobil vse podatke
SELF, ID = 'Ajax', "76561198069577640"


establishedUsers = setUpDataSet(SIZE, ID)
displayData(establishedUsers)
