--------------------------------------------------------------------------------
-- Day 01: Historian Hysteria
--------------------------------------------------------------------------------
import Data.List (transpose, sort)
import System.CPUTime (getCPUTime, cpuTimePrecision)
import System.Environment (getArgs)
import System.IO (readFile)
import Text.Printf (printf)
import Text.Read (readMaybe)
import qualified Data.Map as Map

--------------------------------------------------------------------------------
day01 :: [(Int, Int)] -> IO ()
day01 pairs = do
    let precision = toMillsec cpuTimePrecision
    -- Part 1
    start <- getCPUTime
    let (list1, list2) = unzip pairs
    let distance x y   = abs (x - y)
    let total          = sum $ zipWith distance (sort list1) (sort list2)
    end <- getCPUTime
    let elapsed = toMillsec (end - start)
    printf "Part 1: %d [%.3f +/- %.0f ms]\n" total elapsed precision

    -- Part 2
    start <- getCPUTime
    let counts     = countOccurrences list2
    let getCount x = Map.findWithDefault 0 x counts
    let score      = sum $ zipWith (*) list1 (map getCount list1)
    end <- getCPUTime
    let elapsed = toMillsec (end - start)
    printf "Part 2: %d [%.3f +/- %.0f ms]\n" score elapsed precision

countOccurrences :: (Ord k) => [k] -> Map.Map k Int
countOccurrences = foldr (\x -> Map.insertWith (+) x 1) Map.empty

--------------------------------------------------------------------------------
toMillsec :: Integer -> Double
toMillsec time = fromIntegral time / 1e9 -- getCPUTime returns picoseconds

--------------------------------------------------------------------------------
main :: IO ()
main = do
    args <- getArgs
    case args of
        [fileName] -> do
            text <- readFile fileName
            case parseText text of
                Just pairs -> do day01 pairs
                _ -> putStrLn "ERROR | Failed to parse inputs"
        _ -> putStrLn "Usage: ColumnSum <input file>"

parseText = traverse parseLine . lines

parseLine :: String -> Maybe (Int, Int)
parseLine line =
    case words line of
        [x, y] -> do
            x' <- readMaybe x
            y' <- readMaybe y
            return (x', y')
        _ -> Nothing

