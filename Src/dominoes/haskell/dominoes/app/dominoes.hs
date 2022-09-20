
module Main (main) where

import Data.Text (Text)

import qualified Options.Applicative as Opt

import Control.Applicative ((<**>))
import Data.Text.Conversions (convertText)
import Options.Applicative (option, strOption, infoOption, long, short,
                            help, value, showDefault, metavar)

import DominoPool
import InputParser
import SearchTree
import Objectives

currentVersion :: String
currentVersion = "1.0.0"


-- Input/Output Processing Helpers

joinInput :: String -> Text
joinInput = convertText . unwords . lines

displayResult :: String -> String -> String -> String
displayResult obj score val =
  obj ++ " chain with score " ++ score ++ " is " ++ val


-- Command Line Arguments

data Options = Options { start :: Int, objective :: String }

options :: Opt.Parser Options
options = Options
          <$> option Opt.auto
          ( long "start"
            <> short 's'
            <> help "Number on the fixed, singleton start tile"
            <> value 0
            <> showDefault
            <> metavar "NUMBER" )
          <*> strOption
          ( long "objective"
            <> short 'o'
            <> help "Criterion used to produce output"
            <> value "strongest"
            <> showDefault
            <> metavar "CRITERION" )

versionOption :: Opt.Parser (a -> a)
versionOption = infoOption currentVersion
                ( long "version"
                  <> short 'v'
                  <> help "Show current version" )

progOptions :: Opt.ParserInfo Options
progOptions = Opt.info (options <**> versionOption <**> Opt.helper)
              ( Opt.fullDesc
                <> Opt.progDesc "Solve the Optimal Domino Chain Problem"
                <> Opt.header "dominoes - find the best domino chain from a given set of dominoes" )


-- Main Entry Point

main :: IO ()
main = do
  args <- Opt.execParser progOptions
  dominoesStr <- fmap joinInput getContents
  let dominoesBag = case parseInput dominoesStr of
        Nothing -> []  -- ignore input errors for now
        Just ds -> ds

  let pool = initializePool $ dominoesBag
  let startTile = start args

  putStrLn $ "Available dominoes: " ++ show dominoesBag

  putStrLn $
    case objective args of
    "strongest" -> let (score, _, strongest) = hylo strongestChain build (startTile, pool)
                   in displayResult "strongest" (show score) (show strongest)
    "longest" -> let (len, _, longest) = hylo longestChain build (startTile, pool)
                 in displayResult "longest" (show len) (show longest)
    "all" -> let (_, chains) = hylo allChains build (startTile, pool)
             in "All leaf chains: " ++ show chains
    _ -> "Unrecognized objective"
