module DominoesSpec (spec) where

import Test.Hspec

import DominoPool
import SearchTree
import Objectives

spec :: Spec
spec = do
  describe "Simple domino sets" $ do
    it "strongest 1" $ do
      let pool = initializePool [(4,2), (2,5), (5,1), (0, 4)]
      let (score, _, strongest) = hylo strongestChain build (0, pool)
      shouldBe score 23
      shouldMatchList [(0,4),(4,2),(2,5),(5,1)] strongest
    it "strongest 2" $ do
      let pool = initializePool [(4,2), (2,5), (5,1), (0, 4), (5, 7)]
      let (score, _, strongest) = hylo strongestChain build (0, pool)
      shouldBe score 29
      shouldMatchList [(0,4),(4,2),(2,5),(5,7)] strongest
    it "strongest 3" $ do
      let pool = initializePool [(4,2), (2,5), (5,1), (0, 4), (5, 7), (4, 9), (9, 6)]
      let (score, _, strongest) = hylo strongestChain build (0, pool)
      shouldBe score 32
      shouldMatchList [(0,4),(4,9),(9,6)] strongest
    it "strongest 4" $ do
      let pool = initializePool [(0,2), (2,2), (2,3), (3,4), (3,5), (0,1), (10,1), (9, 10)]
      let (score, _, strongest) = hylo strongestChain build (0, pool)
      shouldBe score 31
      shouldMatchList [(0,1),(1,10),(10,9)] strongest
  
