class Ranking:
    '''A Ranking entry in a Leaderboard object.'''
    def __init__(self, user, value):
        self.user = user
        self.value = value 
    
    def getUser(self):
        ''' Returns the user field of the Ranking object'''
        return self.user

    def getValue(self):
        ''' Returns the value field of the Ranking object'''
        return self.value    
    
