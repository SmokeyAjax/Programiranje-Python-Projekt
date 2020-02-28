import re
import requests


class SteamUser:  # kaj če bi dala ime Gamer al kj tazga? Ker ga definirava kot enga igralca ne kot skupino
    # en igralec

    def __init__(self, userid):
        """
            initializira...
            dobi ID uporabnika, shrani njegove podatke (njegovo stran, ime, št. iger, imena in id njegovih prijateljev)
        """
        self.steamUserID = userid  # št. uporabnika (ID)
        self.steamProfileText = requests.get("https://steamcommunity.com/profiles/" + userid).text  # link

        # ime uporabnika
        self.steamUserName = re.findall(r'<title>Steam Community :: .+</title>', self.steamProfileText)
        self.steamUserName = re.sub(r'<[^>]+>', "", self.steamUserName[0])
        self.steamUserName = re.sub(r'.+ :: ', "", self.steamUserName)

        # koliko iger ima uporabnik
        self.numberOfGamesOwned = re.findall(r"\d+ games owned", self.steamProfileText)
        self.numberOfGamesOwned = self.numberOfGamesOwned[0].split(" ")[0]


    def __repr__(self):
        return f'SteamUser({self.steamUserID})'

    def __str__(self):
        return f'Uporabnik {self.steamUserName} igra {self.numberOfGamesOwned} različnih iger.' # mogoče se da "ima" namest "igra"

    # poleg imen so bi lahko še dobila podatke za njihov ID, Profilno sliko,
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
        ##print(self.steamFriendIDs, len(self.steamFriendIDs))

        return self.steamFriendNames, self.steamFriendIDs  # (ime, ID)

    def howManyFriends(self):
        '''
            vrne število prijateljev
        '''
        return len(self.getFriends()[0])

    def getSteamUserLevel(self):
        '''
            vrne level uporabnika
        '''
        self.steamUserLevel = re.findall(r'<span class="friendPlayerLevelNum">\d+</span></div>', self.steamProfileText)
        self.steamUserLevel = re.sub(r'<[^>]+>', "", self.steamUserLevel[0])
        return self.steamUserLevel

    def getFeaturedGames(self):
        '''
            vrne "Featured Games"
            igre ka jih ima uporabnik "raskzane", ponavad njegove najljubše/ najbol igrane
            raskazane ima lahko od 0-4
        '''
        # še pride

    def getUserGames(self):
        '''
            vrne seznam iger uporabnika, ter število ur na posamezni igri
        '''
        self.steamGamesText = requests.get("https://steamcommunity.com/profiles/" + self.steamUserID + "/games/?tab=all", self.steamProfileText).text
        self.steamGamesText = re.findall(r'<script language="javascript">[^<]+</script>', self.steamGamesText)

        # možn da se da bol simpl sam to deluje :D
        # igre
        self.steamGames = re.findall(r'"name":"[^"]+"', self.steamGamesText[0])
        self.steamGames = [re.sub(r'"name":"', "", game) for game in self.steamGames]
        self.steamGames = [re.sub(r'"', "", game) for game in self.steamGames]
        self.steamGames = [re.sub(r"\\[\w\d]+", "", game) for game in self.steamGames]

        # čas igrane igre
        self.steamGameTime = re.findall(r'"hours_forever":"[^"]+"', self.steamGamesText[0])
        self.steamGameTime = [re.sub(r'"hours_forever":"', "", time) for time in self.steamGameTime]
        self.steamGameTime = [re.sub(r'"', "", time) for time in self.steamGameTime]

        self.steamGameDict = dict()
        for i, game in enumerate(self.steamGames):
            try:
                self.steamGameDict[game] = self.steamGameTime[i]
            except:
                self.steamGameDict[game] = '0'

        return self.steamGameDict
        # ...


# ID mojga Steam Accounta ("Ajax")
userID = "76561198069577640"
jaz = SteamUser(userID)
print(jaz)

#print(jaz.getFriends())  # test
#print(jaz.howManyFriends())  # test
#print(jaz.getSteamUserLevel())  # test
print(jaz.getUserGames()) # test



# for ID in self.steamFriendIDs:
# SteamData(ID)
# sam morva še dodat, da se enkrat prekine
