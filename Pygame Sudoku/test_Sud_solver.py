from unittest import TestCase
import os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
# print(SCRIPT_DIR)
from Sud_solver import SudSolver, Tile, _rem_subset_from_group



class TestSudSolver(TestCase):
    """ example sudokus taken from https://www.sudokuwiki.org"""

    def test_assignPossibleValues(self):


        gameBoard = SudSolver(
            sud="300967001040302080020000070070000090000873000500010003004705100905000207800621004")
        for tile in gameBoard.tiles:
            self.assertIsInstance(tile, Tile)
            self.assertIn(len(tile.possibleValues), (9, 0))

        self.assertTrue(gameBoard.assignPossibleValues())

        for tile in gameBoard.tiles:
            self.assertIsInstance(tile, Tile)
            self.assertNotEquals(len(tile.possibleValues), 9)
        pass

    def test_soleCandidate(self):
        gameBoard = SudSolver(
            sud="300967001040302080020000070070000090000873000500010003004705100905000207800621004")
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertEquals(len(gameBoard.soleCandidate()), 4)

    def test_hiddenSingles(self):
        gameBoard = SudSolver(
            sud="200070038000006070300040600008020700100000006007030400004080009060400000910060002")
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertEquals(len(gameBoard.hiddenSingles()), 9)

    def test_nakedSubset(self):
        """ naked Quad example """
        gameBoard = SudSolver(
            sud="000030086000020040090078520371856294900142375400397618200703859039205467700904132")
        self.assertTrue(gameBoard.assignPossibleValues())
        # l = gameBoard.nakedSubset()
        self.assertTrue(gameBoard.nakedSubset())
        self.assertEquals(gameBoard.tiles.sprites()[1].index, 1)
        self.assertEquals(gameBoard.tiles.sprites()[1].possibleValues,[2,4])
        pass

    def test_hiddenSubset(self):
        """ hidden Quad example https://www.sudokuwiki.org/Intersection_Removal#IR"""
        gameBoard = SudSolver(
            sud="901500046425090081860010020502000000019000460600000002196040253200060817000001694")
        self.assertTrue(gameBoard.assignPossibleValues())
        hs = gameBoard.hiddenSubset(4)
        tiles = gameBoard.tiles.sprites()
        
        self.assertEquals(len(hs[0]), 4)
        self.assertEquals(len(hs[1]), 4)
        _rem_subset_from_group(hs[0], hs[1])
        self.assertEquals(tiles[30].index, 30)
        self.assertEquals(tiles[30].possibleValues,[1,4,6,9])
    
    def test_pointingSubset(self):
        """ example emliminate in row """
        gameBoard = SudSolver(
            sud="930050000200630095856002000003180570005020980080005000000800159508210004000560008")
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertTrue(gameBoard.pointingSubset())

        tiles = gameBoard.tiles.sprites()
        self.assertEquals(tiles[41].index, 41)
        self.assertNotIn(3, tiles[41].possibleValues)

    def test_boxLineReduction(self):
        """ box-line-reduction: https://www.sudokuwiki.org/Intersection_Removal#LBR """
        gameBoard = SudSolver(
            sud="020943715904000600750000040500480000200000453400352000042000081005004260090208504"
        )
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertTrue(gameBoard.pointingSubset())


        tiles = gameBoard.tiles.sprites()

        self.assertEquals(tiles[29].index, 29)
        self.assertNotIn(6, tiles[29].possibleValues)

        self.assertEquals(tiles[64].index, 64)
        self.assertNotIn(3, tiles[64].possibleValues)

    def test_xwing(self):
        gameBoard = SudSolver(
            sud="020000094760910050090002081070050010000709000080031067240100070010090045900000100"
        )
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertTrue(gameBoard.nakedSubset())
        # self.assertTrue(gameBoard.pointingSubset())
        self.assertTrue(gameBoard.xwing())

        tiles = gameBoard.tiles.sprites()

        self.assertEquals(tiles[38].index, 38)
        self.assertNotIn(2, tiles[38].possibleValues)

        self.assertEquals(tiles[36].index, 36)
        self.assertNotIn(3, tiles[38].possibleValues)

    def test_ywing(self):
        gameBoard = SudSolver(
            sud="940700165000501294251946378009004080004100900702890040095008000000210459020059800"
        )
        self.assertTrue(gameBoard.assignPossibleValues())

    def test_simple_coloring_offchain(self):
        gameBoard = SudSolver(
            sud="200041056405602010016095004350129640142060590069504001584216379920408165601950482"
        )
        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertTrue(gameBoard.simple_coloring())

        tiles = gameBoard.tiles.sprites()

        self.assertEquals(tiles[13].index, 13)
        self.assertNotIn(3, tiles[13].possibleValues)

        self.assertEquals(tiles[39].index, 39)
        self.assertNotIn(3, tiles[39].possibleValues)

        self.assertEquals(tiles[17].index, 17)
        self.assertNotIn(8, tiles[17].possibleValues)

    def test_simple_coloring_onchain(self):
        gameBoard = SudSolver(
            sud="289000375364090812517283964893020601145836729726000083451378296072010038038002107"
        )
        tiles = gameBoard.tiles.sprites()

        self.assertTrue(gameBoard.assignPossibleValues())
        self.assertTrue(gameBoard.nakedSubset())

        # Before
        self.assertEquals(tiles[79].index, 79)
        self.assertIn(5, tiles[79].possibleValues)

        self.assertEquals(tiles[51].index, 51)
        self.assertIn(5, tiles[51].possibleValues)

        self.assertEquals(tiles[76].index, 76)
        self.assertIn(5, tiles[76].possibleValues)

        
        self.assertTrue(gameBoard.simple_coloring())

        # After
        self.assertEquals(tiles[79].index, 79)
        self.assertNotIn(5, tiles[79].possibleValues)

        self.assertEquals(tiles[51].index, 51)
        self.assertNotIn(5, tiles[51].possibleValues)

        self.assertEquals(tiles[76].index, 76)
        self.assertNotIn(5, tiles[76].possibleValues)