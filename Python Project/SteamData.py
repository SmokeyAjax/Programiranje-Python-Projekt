import re
import requests


# sm dav class, ka se mi zdi, da bo za vnaprej najbolj primerno, sam za enkrat še ni tok...
# imena splemenljivk bi mogoče lahko ble bolše...
class SteamData:  # kaj če bi dala ime Gamer al kj tazga? Ker ga definirava kot enga igralca ne kot skupino
    # en igralec

    def __init__(self, userid):
        """
            initializira...
            dobi ID uporabnika, shrani njegove podatke (njegovo stran, ime, št. iger, imena in id njegovih prijateljev)
        """
        self.steamUserID = userid  # št. uporabnika
        self.steamProfileText = requests.get("https://steamcommunity.com/profiles/" + userid).text  # link

        # ime uporabnika
        self.steamUserName = re.findall(r'<title>Steam Community :: .+</title>', self.steamProfileText)
        self.steamUserName = re.sub(r'<[^>]+>', "", self.steamUserName[0])
        self.steamUserName = re.sub(r'.+ :: ', "", self.steamUserName)

        # koliko iger ima uporabnik
        self.numberOfGamesOwned = re.findall(r"\d+ games owned", self.steamProfileText)
        self.numberOfGamesOwned = self.numberOfGamesOwned[0].split(" ")[0]


    def __repr__(self):
        return f'SteamData({self.steamUserID})'
    

    def __str__(self):
        return f'Uporabnik {self.steamUserName} igra {self.numberOfGamesOwned} različnih iger.'

       

    # poleg imen so bi lahko še dobila podatke za njihov ID, Profilno sliko,
    def getFriends(self):
        '''
            vrne 2 tebeli: tabelo imen in tabelo id prijateljev
        '''
        # gre na stran uporabnika, kjer so prikazani vsi njegovi prijatelji
        self.steamFriendsLink = requests.get("https://steamcommunity.com/profiles/" + userid + "/friends/").text

        # dobi imena vseh prijateljev in jih shrani v tabelo
        self.steamFriendNames = re.findall(r'<div class="friend_block_content">.+<br>', self.steamFriendsText)
        self.steamFriendNames = [re.sub(r'<[^>]+>', "", name) for name in self.steamFriendNames]
        ##print(self.steamFriendNames, len(self.steamFriendNames))

        # dobi ID
        self.steamFriendIDs = re.findall(r'data-steamid="\d+"', self.steamFriendsText)
        self.steamFriendIDs = [re.sub(r'[^0-9]+', "", ID) for ID in self.steamFriendIDs]
        ##print(self.steamFriendIDs, len(self.steamFriendIDs))

        return self.steamFriendNames, self.steamFriendIDs  # (imena, id)


    def howManyFriends(self):
        '''
            vrne število prijateljev
        '''
        return len(self.getFriends()[0])

    
        
        # zdej ka mava ID od vseh bi lahko za vsakega
        #for ID in self.steamFriendIDs:
            #SteamData(ID)
        # sam morva še dodat, da se enkrat prekine
        



# ID mojga Steam Accounta ("Ajax")
userID = "76561198069577640"
jaz = SteamData(userID)
print(jaz)

# tko za enkrat neki malga narejenga
