class Leaderboard:
    ''' A colletion of Rakning objects that is sent via a Discord embed'''
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.rankings = []

    def addRanking(self, ranking):
        ''' Adds a Ranking object to the Ranking array'''
        self.rankings.append(ranking)

    def getTitle(self):
        ''' Returns the title of the Leaderboard'''
        return self.title
    
    def getDescription(self):
        ''' Returns the description of a Leaderboard'''
        return self.description
    
    def getRankings(self):
        ''' Returns the rankings array'''
        return self.rankings

    
    
