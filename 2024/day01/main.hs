--------------------------------------------------------------------------------
-- Day 01: Historian Hysteria
--------------------------------------------------------------------------------
-- Standard library
import Data.Foldable (traverse_)
import Data.Function (on)
import Data.List (sort)
import Data.Maybe (listToMaybe)
import System.Environment (getArgs)
import System.IO (readFile)
import Text.Printf (printf)
import Text.Read (readMaybe)
import qualified Data.Map as Map

--------------------------------------------------------------------------------
-- Solution
type InputData = [(Int, Int)]
type Solution = InputData -> IO ()

main :: IO ()
main = runSolution day01

day01 :: Solution
day01 input = do
    let total = part1 input
    printf "Part 1: %d\n" total
    let score = part2 input
    printf "Part 2: %d\n" score

part1    = uncurry getTotal . unzip
getTotal = sum ... zipWith distance `on` sort
distance = abs ... (-)

part2 input = do 
    let (listL, listR) = unzip input
    let listLCounts    = map (getCountFrom listR) listL
    let score          = getScore listL listLCounts
    score

getCountFrom     = findCount . countOccurrences
getScore         = sum ... zipWith (*)
findCount        = flip (Map.findWithDefault 0)
countOccurrences = foldr updateCount Map.empty
updateCount      = flip (Map.insertWith (+)) 1

--------------------------------------------------------------------------------
-- Problem specific input parsing
parseText :: String -> Maybe InputData
parseText = traverse parseLine . lines

parseLine x = toPair =<< parseLineInt x

toPair [a, b] = Just (a, b)
toPair _      = Nothing

--------------------------------------------------------------------------------
-- General supporting functions
-- TODO: Move to library and import
--------------------------------------------------------------------------------

-- Useful combinators
(...) :: (c -> d) -> (a -> b -> c) -> a -> b -> d
f ... g = \x y -> f (g x y)

runSolution :: Solution -> IO ()
-- Option 1: Procedural style
-- runSolution solution = do
--     (fileName:_)   <- getArgs
--     text           <- readFile fileName
--     let parsedText = parseText text
--     traverse_ solution parsedText

-- Option 2: Almost point-free functional (but more readable)
runSolution f = traverse_ f . parseFileText =<< readUserFile getArg

-- Option 3: Point-free functional (can't think of a way to make this readable)
-- runSolution = (readUserFile getArg >>=) . (. parseFileText) . traverse_
-- runSolution = (readUserFile getArg >>=) . (parseFileText .:. traverse_)
-- (.:.) :: (a1 -> b) -> (a -> b -> c) -> (a -> a1 -> c)
-- f .:. g = \x y -> g x (f y)

-- General input parsing utilities
getArg        = fmap listToMaybe getArgs
readUserFile  = (traverse readFile =<<)
parseFileText = (parseText =<<)
parseLineInt = traverse readMaybe . words

