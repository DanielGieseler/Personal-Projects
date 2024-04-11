using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class BoardState
{
    public int[,] values { get; private set; }
    private static BoardMesh boardMesh; // dont clone this part!
    private static int[] bounds;

    public BoardState(BoardMesh initBoardMesh, int[] initBounds){
        boardMesh = initBoardMesh;
        bounds = initBounds;
        values = new int[bounds[0], bounds[1]];
    }

    public bool IsValidPosition(int[] position){
        int x = position[0], y = position[1] - 1;
        if (!(0 <= x & x < bounds[0] & 0 <= y & y < bounds[1])){
            return false;
        }
        if (values[x,y] != 0){
            return false;
        }
        return true;
    }

    public bool IsRedZoneFilled(){
        int y = bounds[1] - 3;
        for (int x = 0; x < bounds[0]; x++) {
            if (values[x,y] != 0){
                return true;
            }
        }
        return false;
    }

    public double Stabilize(){
        double reward = 0;
        bool unstable = true;
        while (unstable){
            var countDictionary = new Dictionary<int, int>();
            var cellsToClear = new List<int[]>();
            foreach (var direction in boardMesh.allDirections){
                foreach (var line in direction){
                    var consecutives = Consecutives(line);
                    foreach (var consecutive in consecutives){
                        cellsToClear.AddRange(consecutive);
                        int count = Enumerable.Count(consecutive);
                        if (countDictionary.ContainsKey(count)){
                            countDictionary[count] += 1;
                        } else {
                            countDictionary[count] = 1;
                        }
                    }
                }
            }
            reward += CalculateReward(countDictionary);
            unstable = ClearLines(cellsToClear.Distinct().ToList());
        }
        return reward;
    }

    private List<List<int[]>> Consecutives(List<int[]> line){
        var consecutives = new List<List<int[]>>();
        var consec = new List<int[]>();
        int lastValue = 0;
        foreach (var point in line){
            int currentValue = values[point[0], point[1]];
            if (currentValue != lastValue){
                if (Enumerable.Count(consec) >= 3){
                    consecutives.Add(consec);
                }
                consec = new List<int[]>();
            }
            if (currentValue != 0){
                consec.Add(point);
            }
            lastValue = currentValue;
        }
        if (Enumerable.Count(consec) >= 3){
            consecutives.Add(consec);
        }
        return consecutives;
    }

    private double CalculateReward(Dictionary<int, int> count){
        double reward = 0;
        foreach (var entry in count){
            reward += entry.Value*System.Math.Pow(2, entry.Key - 3);
        }
        return reward;
    }

    private bool ClearLines(List<int[]> cellsToClear){
        var changedColumns = new List<int>();
        foreach (var point in cellsToClear){
            changedColumns.Add(point[0]);
            values[point[0], point[1]] = 0;
        }
        changedColumns = changedColumns.Distinct().ToList();
        foreach (int x in changedColumns){
            // store all values in column, while deleting them
            var columnContent = new List<int>();
            for (int y = 0; y < bounds[1]; y++){
                int value = values[x, y];
                if (value != 0){
                    columnContent.Add(value);
                    values[x, y] = 0;
                }
            }
            // reset those tiles from the bottom
            for (int y = 0; y < Enumerable.Count(columnContent); y++){
                values[x, y] = columnContent[y];
            }
        }
        return (changedColumns.Count() > 0);
    }
}
