import re
import requests
import random
import matplotlib.pyplot as plt

class SteamUser:
    # en igralec

    def __init__(self, userID):
        self.steamUserID = userID
        self.steamProfileText = requests.get("https://steamcommunity.com/profiles/" + userID).text

        # ime uporabnika
        self.steamUserName = re.findall(r'<title>Steam Community :: .+</title>', self.steamProfileText)
        if len(self.steamUserName) == 0:
            self.private = True
            return
        else:
            self.private = False

        self.steamUserName = re.sub(r'<[^>]+>', "", self.steamUserName[0])
        self.steamUserName = re.sub(r'.+ :: ', "", self.steamUserName)

        # koliko iger ima uporabnik
        numberOfGamesOwned = re.findall(r"\d+ games owned", self.steamProfileText)

        # pogledamo če je profil privaten
        if len(numberOfGamesOwned) == 0:
            self.private = True
        else:
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
            return 0
        return self.numberOfFriends


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
        self.gameDict = self.getOwnedGames()
        self.totalPlayTime = 0

        if self.gameDict == None:
            self.private = True
            return 0

        for singlePlayTime in self.gameDict.values():
            self.totalPlayTime += float(singlePlayTime)

        return int(self.totalPlayTime)


# preiskovanje omrežja
def createUserObjects(establishedUsers, removedObjects, pivotList):
    """
    iz enega uporabnika ustvari nov objekt za vsakega prijatelja
    hkrati dela slovar že narejenih uporabnikov
    """

    # izberemo naključnega uporabnika, iz katerega bomo pridobili podatke
    keyArray = list()
    for key in establishedUsers.keys():
        keyArray.append(key)

    pivot = 0
    end = False

    try:
        length = random.randint(0, len(establishedUsers) - 1)
        pivot = keyArray[length]
    except:
        print("You've made too many calls. Please try again later.")
        end = True
        return establishedUsers, removedObjects, end, pivotList

    # delamo seznam že uporabljenih pivotov, da njih ne kličemo še enkrat in s tem proces malo pospešimo
    while pivot in pivotList:
        length = random.randint(0, len(establishedUsers) - 1)
        pivot = keyArray[length]

    pivotList.append(pivot)

    # naredi objekt za vse prijatelje, ki nimajo privatne profile
    friendsID = establishedUsers[pivot].getFriends()
    for friend in friendsID[1]:
        if friend not in establishedUsers:
            friendObject = SteamUser(friend)

            # pogledamo če je privaten
            private = friendObject.privateProfile()

            if not private and friend not in removedObjects:
                establishedUsers[friend] = friendObject

    # pogledamo še če ima kakšne določene podatke skrite, če jih imajo, jih tud ne uporabimo
    for name, object in establishedUsers.items():
        if int(object.getPlayTime()) == 0 or int(object.howManyFriends()) == 0:
            try:
                removedObjects.append(name)
            except:
                pass

    # jih še zbrišemo
    for name in removedObjects:
        try:
            del establishedUsers[name]
        except:
            pass

    return establishedUsers, removedObjects, end, pivotList


def setUpDataSet(size, selfID):
    """
    vrne seznam objektov, kjer vsak objekt prikazuje določenega uporabnika
    """
    # določimo od koga dobimo ostale uporabnika
    pivot = SteamUser(selfID)

    establishedUsers = dict()
    establishedUsers[selfID] = pivot

    removedObjects = list()
    pivotList = list()

    # kličemo metodo za generiranje objektov, dokler velikost baze ni večja od Size
    while len(establishedUsers) < size:
        establishedUsers, removedObjects, end, pivotList = createUserObjects(establishedUsers, removedObjects, pivotList)
        if end == True:
            break
        if (int(len(establishedUsers) / int(size))* 100 ) >= 100:
            print("Data collected!")
        else:
            print("Progress: {0:d} %".format( int(len(establishedUsers) / int(size)* 100) ) )

    return establishedUsers

def displayData(establishedUsers):
    """
    predstavimo in vizualiziramo podatke
    naredi: eno tektovno datoteko
            dva diagrama: stolpični ter tortni diagram
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

    combinedGamesDict = dict()

    for name, object in establishedUsers.items():
        try:
            # nekateri uporabniki vsebujejo znake v imenu, ki jih ne moremo izpisati (npr: \u272a)
            file.write("{0:>28s} | '{1:s}'\n".format("User Name", object.steamUserName))
        except:
            file.write("{0:>28s} | '{1:s}'\n".format("User Name", "*Unwritable name*"))
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

        for game, time in object.gameDict.items():
            if game in combinedGamesDict.keys():
                combinedGamesDict[game] += float(time)
            else:
                combinedGamesDict[game] = float(time)


    file.write("{0:>28s} | '{1:d}'\n".format("Number of users", int(numberOfUsers)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of levels", int(totalLevel)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of games", int(totalGames)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total play time of all users", int(totalHours)))
    file.write("{0:>28s} | '{1:d}'\n".format("Total number of friends", int(totalFriends)))

    file.write("\n")

    file.close()

    # še grafi, prvo stolpični diagram
    # top 30 games by play time
    x = sorted(combinedGamesDict, key=combinedGamesDict.get, reverse=True)[:30]
    x.append("Other")

    y = list()
    otherTime = 0

    for game, time in combinedGamesDict.items():
        if game in x:
            y.append(int(time))
        else:
            otherTime += int(time)

    y.sort()
    y = y[::-1]
    y.append(otherTime)

    fig, ax = plt.subplots(figsize=(15, 12), dpi=100)
    plt.title("Most Played Games by Time")
    plt.xlabel("Games")
    plt.ylabel("Play Time [hours]")
    barPLot = plt.bar(x, y, width=0.5)
    plt.xticks(x, rotation='vertical')
    plt.subplots_adjust(bottom=0.3, top=0.9)

    # da se nad stolpcem izpiše še količino oz. višino stolpca
    for i, rect in enumerate(barPLot):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                y[i],
                ha='center', va='bottom', rotation=0)

    plt.savefig("Most Played Games by Time.pdf")

    # top 20 games [%]
    # Tortni diagram
    x = sorted(combinedGamesDict, key=combinedGamesDict.get, reverse=True)[:20]
    x.append("Other")

    y = list()
    otherTime = 0

    for game, time in combinedGamesDict.items():
        if game in x:
            y.append(int(time))
        else:
            otherTime += int(time)

    y.sort()
    y = y[::-1]
    y.append(otherTime)

    explode = list()
    for i in range(1, len(y)):
        explode.append(0)
    explode.append(0.1)

    fig, ax = plt.subplots(figsize=(15, 12), dpi=100)
    plt.title("Most Played Games by Time [%]")
    plt.pie(y, labels=x, explode=explode, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.savefig("Most Played Games by Time [%].pdf")


# Naredimo nekaj čez SIZE-objektov, kjer vsak objekt prikazuje določenega uporabnika. Size je spodnja meja.
# Podamo poljubno število (ne preveliko, ker je število klicev na stran omejeno).
SIZE = 15

# ID mojga Steam Accounta ("Ajax")
# tukaj podamo uporabnika iz katerega bomo pridobil vse podatke
# v resnici potrebujemo samo ID
SELF, ID = 'Ajax', "76561198069577640"

# kličemo metode za uspostavitev bazem ki nam jo tudi vrne
establishedUsers = setUpDataSet(SIZE, ID)
# kličemo še metodo da dobljene podatjke predtavi
displayData(establishedUsers)
