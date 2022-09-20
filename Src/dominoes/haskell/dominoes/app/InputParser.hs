module InputParser
  ( DominoList,
    dominoListParser,
    dominoParser,
    parseInput ) where

{-# LANGUAGE OverloadedStrings #-}

import Control.Monad.Combinators
import Data.Text (Text)
import Data.Maybe
import Data.Void
import Text.Megaparsec
import Text.Megaparsec.Char
import Text.Megaparsec.Char.Lexer (decimal)

import qualified Data.Text                  as T
import qualified Text.Megaparsec.Char.Lexer as L


type Parser = Parsec Void Text
type DominoList = [(Int, Int)]

dominoParser :: Parser (Int, Int)
dominoParser = do
  a <- decimal
  space
  oneOf [':', '/', '-']
  space
  b <- decimal
  return (a, b)

dominoSep = space >> char ',' >> space

dominoListParser :: Parser DominoList
dominoListParser = sepBy dominoParser dominoSep

parseInput :: Text -> Maybe DominoList
parseInput = parseMaybe dominoListParser
