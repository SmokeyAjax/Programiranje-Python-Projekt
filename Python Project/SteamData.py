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
        self.numberOfGamesOwned = numberOfGamesOwned[0].split(" ")[0]


    def __repr__(self):
        return self.__class__.__name__ + "(" + self.steamUserID + ")"


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
        return len(self.getFriends()[0])


    def getFeaturedGames(self):
        '''
            vrne "Featured Games"
            igre ka jih ima uporabnik "raskzane", ponavad njegove najljubše/ najbol igrane
            raskazane ima lahko od 0-4
        '''
        featuredGames = re.findall(r'<div class="showcase_slot showcase_gamecollector_game[^h]+href="https://steamcommunity.com/app/[^"]+', self.steamProfileText)
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
        gamesText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/games/?tab=all", self.steamProfileText).text
        gamesText = re.findall(r'<script language="javascript">[^<]+</script>', gamesText)

        # igre
        games = re.findall(r'"name":"[^"]+"', gamesText[0])
        games = [re.sub(r'"name":"', "", game) for game in games]
        games = [re.sub(r'"', "", game) for game in games]
        games = [re.sub(r"\\[\w\d]+", "", game) for game in games]

        # čas igrane igre
        gameTime = re.findall(r'"hours_forever":"[^"]+"', gamesText[0])
        gameTime = [re.sub(r'"hours_forever":"', "", time) for time in gameTime]
        gameTime = [re.sub(r'"', "", time) for time in gameTime]

        gameDict = dict()
        for i, game in enumerate(games):
            try:
                gameDict[game] = gameTime[i]
            except:
                gameDict[game] = '0'

        return gameDict


    def getPlayedTime(self):
        '''
            returnes how many hours a gamer spend playing games
        '''
        gamesWithHours = self.getOwnedGames()
        hours = 0
        for gameHours in gamesWithHours.values():
            try:
                hours += int(gameHours)
            except:
                hours += float(gameHours)
        return int(hours)
        

    def getMostPopularGames(self):
        '''
            returns 10 the most played games (acording to the playing times),
            among which are always all his featured games (regardless to the playing times)
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
            returns all games that user has played for more than 50 hour
        '''
        liked = []
        ownedGames = self.getOwnedGames()
        for game in ownedGames:
            if float(ownedGames[game]) <= 50:
                break
            liked.append(game)
        return liked
    

### mogoče bova nucala.. nism zih
##class Friend(SteamUser):
##    # friends of our user
##    
##    def __init__(self, userID):
##        super().__init__(userID)



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

def surch(self, n, informations):
    '''
        function starts with persone self. It randomly chooses one of it's friends
        and gets wanted informations about this friend and saves them. It does this
        surch n times. It returnes wanted informations.

        informations is a list of function names that we want to apply on our gamers
    '''
    persone = self
    tab = list({info:[]} for i, info in enumerate(informations))

    for _ in range(n):
        # gather wanted informations about our gamers
        for i, info in enumerate(informations):
            f = operator.methodcaller(info)
            try:
                numberOfFriends = f(persone)
                tab[i][info].append(numberOfFriends)
            except:
                persone = self
  
        # set new gamer
        friends = persone.getFriends()[1]
        notFound = True
        while notFound:
            try:
                chosenFriendID = str(random.choice(friends))
                persone = SteamUser(chosenFriendID)
                notFound = False
            except:
                pass

        ### ta random izbira ni najboljša..
        ### mogla bi upoštevat še neke uteži pa sm mal pozabla kako že
        ### (pomembno je št. prijateljev, ker prek prjatlov prideva do polj. igralca..
        ### sam ne vem kako to upoštevat pr preiskovanju)

    return tab




















'''
    za vsakega prijatelja našga uporabnika ustvariva svoj objekt Friend..
    definirava:
        skupni prijatelji (samo direktni)
        top 3 prijatelji glede na
            level
            št. imetih iger
        katere so najbolj igrane igre med prijatelji
'''




# ID mojga Steam Accounta ("Ajax")
self, selfID = 'Ajax', "76561198069577640"
other, otherID = 'Losos', '76561198055621752'
jaz = SteamUser(selfID)
#print(SteamUser(otherID))
# print(jaz)

# TESTI METOD
# print(jaz.getLevel())
# print(jaz.getFriends())
# print(jaz.howManyFriends())
# print(jaz.getOwnedGames())
# print(jaz.getFeaturedGames())
# print(jaz.getMostPopularGames())
# print(jaz.getLikedGames())
# print(jaz.getPlayedTime())

# TESTI FUNKCIJ
# print(commonFriends(selfID, otherID))
print(surch(jaz, 5, ['getPlayedTime', 'howManyFriends', 'getMostPopularGames']))

