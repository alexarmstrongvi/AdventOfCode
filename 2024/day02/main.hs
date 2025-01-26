--------------------------------------------------------------------------------
-- Day 02: Red-Nosed Reports
--------------------------------------------------------------------------------
-- Standard library
import Control.Applicative (liftA2)
import Data.Ix (inRange)
import System.Environment (getArgs)
import System.IO (readFile, putStr)
import Text.Printf (printf)
import Text.Read (readMaybe)

--------------------------------------------------------------------------------
-- Solution
type InputData = [[Int]]
main :: IO ()
main = runSolution day02

day02 reports = do
    let n_safe_reports = part1 reports
    printf "Part 1: %d\n" n_safe_reports

    let n_tolerable_reports = part2 reports
    printf "Part 2: %d\n" n_tolerable_reports

    putStr "" -- Needed for IO () return type. Something wierd with printf

part1 = length . filter isSafeReport
part2 = length . filter isTolerableReport

isSafeReport = isSafeReport' Nothing
  where
    isSafeReport' (Just isInc) report = all isSafe (pairwise report)
      where
        isSafe = liftA2 (&&) isMonotonic isSafeDiff
        isMonotonic (a, b) = (a<b) == isInc
        isSafeDiff (a, b) = inRange (1, 3) (abs (a - b))
    isSafeReport' Nothing report@(x:y:_) = isSafeReport' (Just (x<y)) report
    isSafeReport' _ _ = True

-- Option 1: O(n^2)
-- isTolerableReport = any isSafeReport . dropOneSubsets
-- dropOneSubsets [] = []
-- dropOneSubsets [_] = [[]]
-- dropOneSubsets (x:xs) = xs : map (x:) (dropOneSubsets xs)

-- Option 2: O(n)
-- Single pass while counting number of unsafe steps
isTolerableReport r = isTolerableInc r || isTolerableInc (reverse r)
  where
    isTolerableInc = isTolerableInc' 0 Nothing
    isTolerableInc' nUnsafe prev (x:y:z:rest)
        | nUnsafe > 1 = False
        | isSafe x y  = isTolerableInc' nUnsafe     (Just x) (y:z:rest)
        | isSafe x z  = isTolerableInc' (nUnsafe+1) (Just x) (z:rest)
        | otherwise   = isTolerableInc' (nUnsafe+1) Nothing rest'
            where rest' = prev `maybeCons` (y:z:rest)
    isTolerableInc' nUnsafe prev [x,y] = isTolerableInc' (nUnsafe+n) prev []
        where n = if isSafe x y then 0 else 1
    isTolerableInc' nUnsafe _ _ = nUnsafe < 2

isSafe x y = inRange (1, 3) (y-x)

maybeCons x xs = maybe xs (:xs) x

--------------------------------------------------------------------------------
-- Problem specific input parsing
parseText :: String -> InputData
parseText = map parseLineVals . lines

--------------------------------------------------------------------------------
-- General supporting functions
pairwise = zip <*> tail

runSolution f = f . parseText =<< readFile . head =<< getArgs

-- Safer to use readMaybe but its waaaaaaaay slower. Is there safe but fast read?
-- parseLineVals = traverse readMaybe . words
parseLineVals = map read . words

