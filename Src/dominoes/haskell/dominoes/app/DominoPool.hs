-- DominoPool.hs - An immutable pool of available objects indexed by exposed ends

module DominoPool where

import qualified Data.Map as M

type Dots = Int
type Domino = (Dots, Dots)  
type Pool = M.Map Dots (M.Map Dots Int)

emptyPool :: Pool
emptyPool = M.empty

assocDomino :: Domino -> Pool -> Pool
assocDomino (m, n) = if m /= n then add m n . add n m else add m m
  where
    add :: Dots -> Dots -> Pool -> Pool
    add j k pool =
      case M.lookup j pool of
        Nothing -> M.insert j (M.singleton k 1) pool
        Just ds -> M.insert j (M.insertWith (+) k 1 ds) pool
  
dissocDomino :: Domino -> Pool -> Pool
dissocDomino (m, n) = if m /= n then remove m n . remove n m else remove m m
  where
    remove :: Dots -> Dots -> Pool -> Pool
    remove j k pool =
      case M.lookup j pool of
        Nothing -> pool
        Just ds -> case M.lookup k ds of
                     Nothing -> pool
                     Just cnts -> M.update (decr k) j pool
    decr :: Dots -> M.Map Dots Int -> Maybe (M.Map Dots Int)
    decr k cnts = case M.lookup k cnts of
                    Nothing -> Just cnts
                    Just 1 -> if M.size cnts == 1 then Nothing else Just (M.delete k cnts)
                    Just n -> Just (M.insert k (n - 1) cnts)

initializePool :: [Domino] -> Pool
initializePool = foldr assocDomino emptyPool
