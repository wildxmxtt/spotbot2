import sqlite3


def updateCreds(credSection, data):
    conn = sqlite3.connect('creds.db')
    cursor = conn.cursor()

    sqlString = 'UPDATE creds SET ' + credSection + ' = ? WHERE row_id = ?'
    cursor.execute(sqlString,(data,1))

    conn.commit()
    conn.close()
    return




def readCred(credSection):
    conn = sqlite3.connect('creds.db')
    cursor = conn.cursor()

    sqlString = "Select " + credSection + " from creds where row_id = 1"

    cursor.execute(sqlString)

    placeholderString = cursor.fetchall()

    if not (credSection == 'expires_in' or credSection == 'expires_at'):
        output = str(placeholderString[0])[2:-3]
    else:
        output = str(placeholderString[0])[1:-2]
    conn.close()

    return output


def fakeJson():
    conn = sqlite3.connect('creds.db')
    cursor = conn.cursor()

    data = "{'access_token': '"+ readCred('access_token') + "', 'token_type': '"+ readCred('token_type') + "', 'expires_in': "+ readCred('expires_in') +"', 'refresh_token': '"+ readCred('refresh_token') +"', 'scope': '"+ readCred('scope') +"', 'expires_at': "+ readCred('expires_at') + "}"



    conn.close()
    return data