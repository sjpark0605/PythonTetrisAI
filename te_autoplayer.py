''' Implement an AI to play tetris '''
from random import Random
from te_settings import Direction, MAXROW, MAXCOL

class AutoPlayer():
    ''' A very simple dumb AutoPlayer controller '''
    def __init__(self, controller):
        self.controller = controller
        self.rand = Random()

    def next_move(self, gamestate):
        ''' next_move() is called by the game, once per move.
            gamestate supplies access to all the state needed to autoplay the game.'''

        moveAttempts = []
        scores = []

        for move in range(-2, 8):
            for rotation in range(0, 3):
                gameClone = gamestate.clone(True)
                has_landed = False
                while not has_landed:
                    self.make_move(gameClone, move, rotation)
                    has_landed = gameClone.update()
                moveAttempts.append((move, rotation))
                self.scoreCalculator(gameClone, scores, rotation)
            idealMove = (self.idealMove(scores, moveAttempts))
        self.make_move(gamestate, idealMove[0], idealMove[1])

    def make_move(self, gamestate, target_pos, target_rot):
        x, y = gamestate.get_falling_block_position()
        direction = None
        if target_pos < x:
            direction = Direction.LEFT
        elif target_pos > x:
            direction = Direction.RIGHT
        if direction != None:
            gamestate.move(direction)
        angle = gamestate.get_falling_block_angle()
        direction = None
        if target_rot == 3 and angle == 0:
            direction = Direction.LEFT
        elif target_rot > angle:
            direction = Direction.RIGHT
        if direction != None:
            gamestate.rotate(direction)

    def fetchHeight(self, gamestate, COL):
        currentTile = gamestate.get_tiles()
        height = 0
        for row in range(0, MAXROW):
            if currentTile[row][COL] != 0:
                if (20 - row) > height:
                    height = 20 - row
                return height

    def convertNone(self, result):
        return int(0 if result is None else result)

    def totalHeights(self, gamestate):
        heights = []
        totalHeight = 0
        for COL in range(0, MAXCOL):
            heights.append(self.convertNone(self.fetchHeight(gamestate, COL)))
            totalHeight += heights[COL]
        return totalHeight

    def heightVariations(self, gamestate):
        heights = []
        heightVariation = 0
        for COL in range(0, MAXCOL):
            heights.append(self.convertNone(self.fetchHeight(gamestate, COL)))
        for pairs in range(0, MAXCOL - 1):
            heightVariation = heightVariation + abs(heights[pairs] - heights[pairs + 1])
        return heightVariation

    def determineHole(self, gamestate):
        currentTile = gamestate.get_tiles()
        hole = 0
        heights = []
        for COL in range(0, MAXCOL):
            heights.append(self.convertNone(self.fetchHeight(gamestate, COL)))
        for COL in range(0, MAXCOL):
            for ROW in range(20 - heights[COL], MAXROW):
                if COL != 0 | COL != MAXCOL:
                    if (currentTile[ROW][COL] == 0) & ((currentTile[ROW - 1][COL + 1] != 0) | (currentTile[ROW - 1][COL - 1] != 0)):
                        hole += 1
                else:
                    if (currentTile[ROW][COL] == 0):
                        hole += 1
        return hole

    def barricade(self, gamestate):
        currentTile = gamestate.get_tiles()
        blockage = 0
        holeY = 0
        heights = []
        for COL in range(0, MAXCOL):
            heights.append(self.convertNone(self.fetchHeight(gamestate, COL)))
        for COL in range(0, MAXCOL):
            holeY = 0
            for ROW in range(20 - heights[COL], 20):
                if currentTile[ROW][COL] == 0:
                    prevROW = 0
                    if ROW > prevROW:
                        holeY = ROW
                        for holeRange in range(20 - heights[COL], holeY):
                            if currentTile[holeRange][COL] != 0:
                                blockage += 1
        return blockage

    def rotateBonus(self, gamestate, rotation):
        block = gamestate.get_falling_block_type()
        rotateScore = 0
        if block == 'T':
            if rotation == 2:
                rotateScore = 10
        return rotateScore



    def scoreCalculator(self, gamestate, scoreList, rotation):
        """totalHeightScore = self.totalHeights(gamestate)"""
        totalVariationScore = self.heightVariations(gamestate)
        totalHole = self.determineHole(gamestate)
        """totalScore = gamestate.get_score()"""
        totalBlocks = self.barricade(gamestate)
        touchScore = self.blockTouchSide(gamestate)
        """blockBonus = self.blockTypeBonus(gamestate)"""
        totalScore = - 3 * totalHole - 1.5 * totalVariationScore - totalBlocks + 0.05 * touchScore
        """- 0.51 * totalHeightScore - 0.18 * totalVariationScore + 0.7 * totalScore - 0.35 * totalHole - 0.2 * totalBlocks + 0.1 * blockBonus"""
        scoreList.append(totalScore)

    def blockTouchSide(self, gamestate):
        currentTile = gamestate.get_tiles()
        touchScore = 0
        for ROW in range(0, 19):
            if (currentTile[ROW][0] != 0) | (currentTile[ROW][9] != 0):
                touchScore += 12
            elif (currentTile [ROW][1] != 0) | (currentTile [ROW][8] != 0):
                touchScore += 8
            elif (currentTile [ROW][2] != 0) | (currentTile [ROW][7] != 0):
                touchScore += 6
            elif (currentTile [ROW][3] != 0) | (currentTile [ROW][6] != 0):
                touchScore += 4
            elif (currentTile [ROW][4] != 0) | (currentTile [ROW][5] != 0):
                touchScore += 2
        return touchScore

    """def blockTypeBonus(self, gamestate):
        x, y = gamestate.get_falling_block_position()
        block = gamestate.get_falling_block_type()
        blockBonus = 0
        if block == 'Z':
            if x == 9:
                blockBonus = 10
        if block == 'S':
            if x == 0:
                blockBonus = 10
        return blockBonus"""

    def idealMove(self, scoreList, moveAttempt):
        maxScore = max(scoreList)
        for iteration in range(0, len(scoreList)):
            if scoreList[iteration] == maxScore:
                element = iteration
                decision = moveAttempt[element]
                moveAttempt = []
                scoreList = []
                return decision