class Leaderboard:
    def __init__(self, title, description, url=None):
        self.title = title
        self.description = description
        self.rankings = []
        self.url = url

    def addRanking(self, ranking):
        self.rankings.append(ranking)

    def getTitle(self):
        return self.title
    
    def getDescription(self):
        return self.description
    
    def getRankings(self):
        return self.rankings
    
    def getUrl(self):
        return self.url
    
    
