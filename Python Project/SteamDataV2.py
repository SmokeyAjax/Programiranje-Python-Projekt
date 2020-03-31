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
        self.level = re.findall(r'<span class="friendPlayerLevelNum">\d+</span></div>', self.steamProfileText)
        self.level = re.sub(r'<[^>]+>', "", self.level[0])
        return self.level

    def __str__(self):
        # pomembna sta nam predvsem level in število iger
        return f'Uporabnik {self.steamUserName} je level {self.getLevel()} in ima {self.numberOfGamesOwned} različnih iger.'

    def getFriends(self):
        '''
            vrne 2 tebeli: tabelo imen in tabelo id prijateljev
        '''
        # gre na stran uporabnika, kjer so prikazani vsi njegovi prijatelji
        self.steamFriendsText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/friends/").text

        # dobi imena vseh prijateljev in jih shrani v tabelo
        self.steamFriendNames = re.findall(r'<div class="friend_block_content">.+<br>', self.steamFriendsText)
        self.steamFriendNames = [re.sub(r'<[^>]+>', "", name) for name in self.steamFriendNames]
        ##print(self.steamFriendNames, len(self.steamFriendNames))

        # dobi ID
        self.steamFriendIDs = re.findall(r'data-steamid="\d+"', self.steamFriendsText)
        self.steamFriendIDs = [re.sub(r'[^0-9]+', "", ID) for ID in self.steamFriendIDs]

        return self.steamFriendNames, self.steamFriendIDs  # (ime, ID)

    def howManyFriends(self):
        '''
            vrne število prijateljev
        '''

        self.numberOfFriends = len(self.getFriends()[0])
        if self.numberOfFriends == 0:
            self.private = True
        return self.numberOfFriends

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

        self.featuredGames = sorted(featuredGames, key=lambda x: x[1])
        return self.featuredGames

    def getOwnedGames(self):
        '''
            vrne urejen slovar iger uporabnika ter pripadajoča števila ur (urejen glede na št. igranih ur)
        '''
        self.gamesText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/games/?tab=all",
                                 self.steamProfileText).text
        self.gamesText = re.findall(r'<script language="javascript">[^<]+</script>', self.gamesText)

        # če je profil privaten, se vrnemo
        if len(self.gamesText) == 0:
            return

        # igre
        self.games = re.findall(r'"name":"[^"]+"', self.gamesText[0])
        self.games = [re.sub(r'"name":"', "", game) for game in self.games]
        self.games = [re.sub(r'"', "", game) for game in self.games]
        self.games = [re.sub(r"\\[\w\d]+", "", game) for game in self.games]

        # čas igrane igre
        self.gameTime = re.findall(r'"hours_forever":"[^"]+"', self.gamesText[0])
        self.gameTime = [re.sub(r'"hours_forever":"', "", time) for time in self.gameTime]
        self.gameTime = [re.sub(r'"', "", time) for time in self.gameTime]
        self.gameTime = [re.sub(r',', "", time) for time in self.gameTime]

        self.gameDict = dict()
        for i, game in enumerate(self.games):
            try:
                self.gameDict[game] = self.gameTime[i]
            except:
                self.gameDict[game] = '0'

        return self.gameDict

    def getPlayTime(self):
        '''
            vrne število preigranih ur od vseh iger
        '''
        self.playTime = self.getOwnedGames()
        self.totalPlayTime = 0
        for singlePlayTime in self.playTime.values():

            self.totalPlayTime += float(singlePlayTime)

        if self.totalPlayTime == 0:
            self.private = True
        return int(self.totalPlayTime)

    def getMostPopularGames(self):
        '''
            vrne seznam
            seznam vsebuje 10 iger, med katerimi so vedno "featured games"
            in igre, ki so največ časa bile igrane
        '''
        top = set(self.getFeaturedGames())
        games = list(self.gameDict.keys())
        lenght = len(top)
        for i, game in enumerate(games):
            if lenght + i > 10:
                break
            top.add(game)
        self.top = sorted(top)
        return self.top

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

        self.liked = liked
        return self.liked

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
            print(friend)
            friendObject = SteamUser(friend)

            # pogledamo če je privaten
            private = friendObject.privateProfile()

            if not private and friend not in removedObjects:
                establishedUsers[friend] = friendObject

    for name, object in establishedUsers.items():
        if int(object.getPlayTime()) == 0 or int(object.howManyFriends()) == 0:
            try:
                removedObjects.append(name)
            except:
                pass

    # se znebimo še uporabnikov, kjer imajo določene podatke skrite
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
        file = open("Stem Data.txt", "w")

    numberOfUsers = 0
    totalHours = 0
    totalGames = 0
    totalFriends = 0
    totalLevel = 0

    for name, object in establishedUsers.items():

        file.write("{0:>28s} | '{1:s}'\n".format("User Name", object.steamUserName))
        file.write("{0:>28s} | '{1:s}'\n".format("User ID", object.steamUserID))
        file.write("{0:>28s} | '{1:d}'\n".format("Level", int(object.getLevel())))
        file.write("{0:>28s} | '{1:d}'\n".format("Number of games", int(object.numberOfGamesOwned)))
        file.write("{0:>28s} | '{1:d}'\n".format("Total play time", int(object.totalPlayTime)))
        file.write("{0:>28s} | '{1:d}'\n".format("Number of friends", int(object.numberOfFriends)))

        file.write("\n")

        numberOfUsers += 1
        totalLevel += int(object.getLevel())
        totalGames += int(object.numberOfGamesOwned)
        totalHours += int(object.totalPlayTime)
        totalFriends += int(object.numberOfFriends)


    file.write("{0:>28s} | '{1:d}'\n".format("Number of users", int(numberOfUsers)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of levels", int(totalLevel)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of games", int(totalGames)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total play time of all users", int(totalHours)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of friends", int(totalFriends)))

    file.write("\n")

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
SIZE = 2

# ID mojga Steam Accounta ("Ajax")
# tukaj podamo uporabnika iz katerega bomo pridobil vse podatke
SELF, ID = 'Ajax', "76561198069577640"


establishedUsers = setUpDataSet(SIZE, ID)
displayData(establishedUsers)
