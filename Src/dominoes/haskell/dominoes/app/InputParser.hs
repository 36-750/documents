module InputParser
  ( DominoList,
    dominoListParser,
    dominoParser,
    parseInput ) where

{-# LANGUAGE OverloadedStrings #-}

import Control.Monad.Combinators
import Data.Text (Text)
import Data.Void
import Text.Megaparsec
import Text.Megaparsec.Char
import Text.Megaparsec.Char.Lexer (decimal)


type Parser = Parsec Void Text
type DominoList = [(Int, Int)]

dominoParser :: Parser (Int, Int)
dominoParser = do
  a <- decimal
  space
  _ <- oneOf [':', '/', '-']
  space
  b <- decimal
  return (a, b)

dominoSep :: Parser ()
dominoSep = space >> char ',' >> space

dominoListParser :: Parser DominoList
dominoListParser = sepBy dominoParser dominoSep

parseInput :: Text -> Maybe DominoList
parseInput = parseMaybe dominoListParser
