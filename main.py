import copy
import socket
import random
import pickle
import sys

lettersCoord = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
printNums = ['1   ', '2   ', '3   ', '4   ', '5   ', '6   ', '7   ', '8   ', '9   ', '10  ']
occupiedSpaces = []
hitSpots = []
messages = ["PLAYER_DISCONNECT",
            "PASS",
            "RESPONSE",
            "ATTACK_COORDS",
            "PLAYER_WON"]
ships = {
    "Aircraft Carrier": 5,
    "Battleship": 4,
    "Submarine": 3,
    "Destroyer": 3,
    "Patrol Boat": 2
}
destroyedShips = []


def setupBoard():
    return [['·' for c in range(10)] for r in range(10)]


def printBoard(boardC):
    board = copy.deepcopy(boardC)
    tempLetterCoord = ['    '] + lettersCoord
    for counter, i in enumerate(board):
        board[counter].insert(0, printNums[counter])

    board.insert(0, tempLetterCoord)
    board.insert(1, [])
    for i in board:
        print(' '.join(i))


def isInt(x):
    try:
        int(x)
        return True

    except BaseException:
        return False


def isInBoard(x):
    return 0 <= x <= 9


def changeBoard(board, coords, piece):
    if not coords:
        return board

    tempBoard = copy.deepcopy(board)
    for col, row in coords:
        tempBoard[col][row] = piece

    return tempBoard


def convertCoords(coords):
    try:
        coords = coords.split(';')

        if len(coords) != 2:
            return False

        if not (isInt(coords[0][1:]) and isInt(coords[1][1:])):
            return False

        iY = int(coords[0][1:]) - 1
        iX = lettersCoord.index(coords[0][0].upper())
        fY = int(coords[1][1:]) - 1
        fX = lettersCoord.index(coords[1][0].upper())

        return [iY, iX, fY, fX]

    except BaseException:
        return False


def convertCoord(coord):
    try:
        lenC = len(coord)

        if not (lenC == 2 or lenC == 3):
            return False

        if not isInt(coord[1:]):
            return False

        Y = int(coord[1:]) - 1
        X = lettersCoord.index(coord[0].upper())

        if not isInBoard(X) or not isInBoard(Y):
            return False

        return [Y, X]

    except BaseException:
        return False


def checkShipInput(board, coords, amount, ship):
    global occupiedSpaces

    ID = ship[0]

    try:
        coords = convertCoords(coords)

        if coords:
            iY = coords[0]
            iX = coords[1]
            fY = coords[2]
            fX = coords[3]

        else:
            return False

        if isInBoard(iY) and isInBoard(iX) and isInBoard(fY) and isInBoard(fX):
            difY = abs(iY - fY)
            difX = abs(iX - fX)

        else:
            return False

        if difY and difX:
            return False

        if difY + 1 != amount and difX + 1 != amount:
            return False

        toChange = []

        if difX:
            if iX < fX:
                rangeCoord = list(range(iX, fX + 1))
            else:
                rangeCoord = list(range(fX, iX + 1))
            for z in rangeCoord:
                toChange.append([iY, z])
        else:
            if iY < fY:
                rangeCoord = list(range(iY, fY + 1))
            else:
                rangeCoord = list(range(fY, iY + 1))
            for z in rangeCoord:
                toChange.append([z, iX])

        if [z for z in toChange if z in occupiedSpaces]:
            return False

        occupiedSpaces += toChange

        return changeBoard(board, toChange, ID)

    except BaseException:
        return False


def setupBoats(board):
    for key, value in ships.items():
        printBoard(board)
        while True:
            inpB = input(f"Please enter a valid coord range (eg. B1;B5) for the {key} with {value} spots: ")

            tempBoard = checkShipInput(copy.deepcopy(board), inpB, value, key)

            if tempBoard:
                board = copy.deepcopy(tempBoard)
                break
            else:
                print("Invalid input")
                continue

    return board


def getAttackCoord():
    global hitSpots

    while True:
        print(f"Current hit spots:")
        printBoard(changeBoard(setupBoard(), hitSpots, 'X'))

        inpA = input("Please enter a valid coord (eg. B1) which hasn't already been targeted: ")

        coord = convertCoord(inpA)

        if not coord:
            continue

        if coord in hitSpots or not (isInBoard(coord[0]) and isInBoard(coord[1])):
            continue

        hitSpots.append(coord)

        return coord


def getResponse(coord):
    global _BOARD, destroyedShips

    print(f"The enemy shot at {lettersCoord[coord[0]]}{coord[1]}!")

    hitSpot = _BOARD[coord[0]][coord[1]]

    hitShip = None

    sunkShip = False

    if hitSpot != '·':
        _BOARD[coord[0]][coord[1]] = 'X'

        if hitSpot == 'A':
            hitShip = "Aircraft Carrier"
            if not any('A' in sub for sub in _BOARD) and 'A' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('A')
        elif hitSpot == 'B':
            hitShip = "Battleship"
            if not any('B' in sub for sub in _BOARD) and 'B' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('B')
        elif hitSpot == 'S':
            hitShip = "Submarine"
            if not any('S' in sub for sub in _BOARD) and 'S' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('S')
        elif hitSpot == 'D':
            hitShip = "Destroyer"
            if not any('D' in sub for sub in _BOARD) and 'D' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('D')
        elif hitSpot == 'P':
            hitShip = "Patrol Boat"
            if not any('P' in sub for sub in _BOARD) and 'P' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('P')

    _BOARD[coord[0]][coord[1]] = 'X'

    if len(destroyedShips) == 5:
        print("The opponent wins, he sunk all the ships!")
        return messages[4]

    if hitShip:
        print(f"They hit the {hitShip}!")
        toReturn = "You hit a ship!"
        if sunkShip:
            print("And they sunk it!")
            toReturn = "You sunk a ship!"

    else:
        print("They hit nothing!")
        toReturn = "You hit nothing!"

    print("Your current board:")
    printBoard(_BOARD)

    return toReturn


def processResponse(message):
    if message == messages[4]:
        print("You sunk all the ships, you win!")
        sys.exit()

    print(message)


def whoStarts():
    return random.randint(0, 100) < 50


print('''
INSTRUCTIONS:

to play against someone, one must be a server and the other to be a client.

The server must start the network first (when it asks you to be a client or server),
then the client.

You can't message each other during the game.

Your game will disconnect when someone quits or wins the game.
''')

_BOARD = setupBoard()
_BOARD = setupBoats(_BOARD)

print("This is your board:: ")
printBoard(_BOARD)

isServer = False
try:
    while True:
        inp = input("Are you the (S)erver or the (C)lient? ")
        if inp.upper() == 'C':
            print("You are set as the client")
            break
        elif inp.upper() == 'S':
            print("You are set as the Server")
            isServer = True
            break

    if isServer:

        pName = input("Please enter your name: ")

        print("\nInitiating SERVER")

        s = socket.socket()
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = 2222
        s.bind((host, port))

        print(f"\nThis computer: {host} - {ip}")

        s.listen(1)

        print("\nWaiting for connections")
        conn, addr = s.accept()
        print(f"\nreceived connection from {addr[0]} - {addr[1]}")

        oName = conn.recv(1024).decode()

        print(f"\n{oName} has joined the game")

        conn.send(pName.encode())

        startOfGame = True
        while True:
            if startOfGame:
                if whoStarts():
                    conn.send(pickle.dumps([None, messages[1]]))

                else:
                    conn.send(pickle.dumps([getAttackCoord(), messages[3]]))

            startOfGame = False

            resp = conn.recv(4096)

            resp = pickle.loads(resp)

            if resp[1] == messages[1]:
                print("\n\n\n")
                conn.send(pickle.dumps([getAttackCoord(), messages[3]]))

            elif resp[1] == messages[2]:
                processResponse(resp[0])
                conn.send(pickle.dumps([None, messages[1]]))
                print("\n\n\n")

            elif resp[1] == messages[3]:
                conn.send(pickle.dumps([getResponse(resp[0]), messages[2]]))

    else:
        pName = input("Please enter your name: ")

        print("\nInitiating CLIENT")

        s = socket.socket()
        hostClient = socket.gethostname()
        ipClient = socket.gethostbyname(hostClient)
        port = 2222

        print(f"\nThis computer: {hostClient} - {ipClient}")
        host = input("Enter the server address: ")
        print(f"\nTrying to connect to {host} by port {port}")

        s.connect((host, port))
        print("\nConnected successfully")

        s.send(pName.encode())
        oName = s.recv(1024).decode()

        print(f"You are playing against {oName}")

        while True:
            resp = s.recv(4096)

            resp = pickle.loads(resp)

            if resp[1] == messages[1]:
                print("\n\n\n")
                s.send(pickle.dumps([getAttackCoord(), messages[3]]))

            elif resp[1] == messages[2]:
                processResponse(resp[0])
                s.send(pickle.dumps([None, messages[1]]))
                print("\n\n\n")

            elif resp[1] == messages[3]:
                s.send(pickle.dumps([getResponse(resp[0]), messages[2]]))

except BaseException as error:
    print(f"Something went wrong - connection lost. error: {error}")
