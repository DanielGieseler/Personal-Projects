using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Tilemaps;

public class Mechanics
{
    public Vector2Int bounds = new Vector2Int(9, 19);
    public Vector3Int[] columnPiece = new Vector3Int[]{new Vector3Int(0,1,0), new Vector3Int(0,0,0), new Vector3Int(0,-1,0)};
    public List<List<List<int[]>>> allDirections = new List<List<List<int[]>>>();
    private int clearMinimumSize = 3;

    public Mechanics(){
        InitScanLines(bounds.x, bounds.y);
    }

    //------------------------------ TILEMAP MECHANICS ------------------------------//

    public void InitScanLines(int xMax, int yMax){
        //---------------- VERTICAL ----------------//
        List<List<int[]>> vertical = new List<List<int[]>>();
        for (int x = 0; x < xMax; x++) {
            var line = new List<int[]>();
            for (int y = 0; y < yMax; y++) {
                int[] point = {x, y};
                line.Add(point);
            }
            vertical.Add(line);
        }
        allDirections.Add(vertical);
        Printer(vertical);

        //---------------- HORIZONTAL ----------------//
        List<List<int[]>> horizontal = new List<List<int[]>>();
        for (int y = 0; y < yMax; y++) {
            var line = new List<int[]>();
            for (int x = 0; x < xMax; x++) {
                int[] point = {x, y};
                line.Add(point);
            }
            horizontal.Add(line);
        }
        allDirections.Add(horizontal);
        Printer(horizontal);

        //-------------- DIAGONAL RIGHT --------------//
        List<List<int[]>> diagonalRight = new List<List<int[]>>();
        for (int x = xMax-1; x >= 0; x--) {
            var line = new List<int[]>{new int[] {x, 0}};
            diagonalRight.Add(line);
        }
        for (int y = 0; y < yMax; y++) {
            var line = new List<int[]>{new int[] {0, y}};
            diagonalRight.Add(line);
        }
        foreach (var line in diagonalRight){
            int x = line[0][0], y = line[0][1];
            line.Clear();
            for (; x < xMax & y < yMax; x++, y++) {
                int[] point = {x, y};
                line.Add(point);
            }
        }
        allDirections.Add(diagonalRight);
        Printer(diagonalRight);

        //-------------- DIAGONAL LEFT --------------//
        List<List<int[]>> diagonalLeft = new List<List<int[]>>();
        for (int x = 0; x < xMax; x++) {
            var line = new List<int[]>{new int[] {x, 0}};
            diagonalLeft.Add(line);
        }
        for (int y = 0; y < yMax; y++) {
            var line = new List<int[]>{new int[] {xMax, y}};
            diagonalLeft.Add(line);
        }
        foreach (var line in diagonalLeft){
            int x = line[0][0], y = line[0][1];
            line.Clear();
            for (; x >= 0 & y < yMax; x--, y++) {
                int[] point = {x, y};
                line.Add(point);
            }
        }
        allDirections.Add(diagonalLeft);
        Printer(diagonalLeft);
    }

    private void Printer(List<List<int[]>> list)
    {
        Debug.Log("NEW ENTRY: ");
        foreach (var line in list){
            string lineString = "";
            foreach (var point in line){
                lineString += point[0] + "," + point[1] + "; ";
            }
            Debug.Log(lineString);
        }
    }

    public double Execute(Tilemap tilemap){
        double reward = 0;
        bool requiresCheck = true;
        while (requiresCheck){
            var countDictionary = new Dictionary<int, int>();
            var cellsToClear = new List<int[]>();
            foreach (var direction in allDirections){
                foreach (var line in direction){
                    var consecutives = Consecutives(tilemap, line);
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
            requiresCheck = ClearLines(tilemap, cellsToClear.Distinct().ToList());
        }
        return reward;
    }

    public double Execute(Tile[,] tilemap){
        double reward = 0;
        bool requiresCheck = true;
        while (requiresCheck){
            var countDictionary = new Dictionary<int, int>();
            var cellsToClear = new List<int[]>();
            foreach (var direction in allDirections){
                foreach (var line in direction){
                    var consecutives = Consecutives(tilemap, line);
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
            requiresCheck = ClearLines(tilemap, cellsToClear.Distinct().ToList());
        }
        return reward;
    }

    private List<List<int[]>> Consecutives(Tilemap tilemap, List<int[]> line){
        var consecutives = new List<List<int[]>>();
        var consec = new List<int[]>();
        Tile lastTile = null;
        foreach (var point in line){
            var position = new Vector3Int(point[0], point[1], 0);
            var currentTile = tilemap.GetTile<Tile>(position);
            if (currentTile != lastTile){
                if (Enumerable.Count(consec) >= clearMinimumSize){
                    consecutives.Add(consec);
                }
                consec = new List<int[]>();
            }
            if (currentTile != null){
                consec.Add(point);
            }
            lastTile = currentTile;
        }
        if (Enumerable.Count(consec) >= clearMinimumSize){
            consecutives.Add(consec);
        }
        return consecutives;
    }

    private List<List<int[]>> Consecutives(Tile[,] tilemap, List<int[]> line){
        var consecutives = new List<List<int[]>>();
        var consec = new List<int[]>();
        Tile lastTile = null;
        foreach (var point in line){
            var currentTile = tilemap[point[0], point[1]];
            if (currentTile != lastTile){
                if (Enumerable.Count(consec) >= clearMinimumSize){
                    consecutives.Add(consec);
                }
                consec = new List<int[]>();
            }
            if (currentTile != null){
                consec.Add(point);
            }
            lastTile = currentTile;
        }
        if (Enumerable.Count(consec) >= clearMinimumSize){
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

    public bool ClearLines(Tilemap tilemap, List<int[]> cellsToClear){
        var changedColumns = new List<int>();
        foreach (var point in cellsToClear){
            var position = new Vector3Int(point[0], point[1], 0);
            changedColumns.Add(point[0]);
            tilemap.SetTile(position, null);
        }
        changedColumns = changedColumns.Distinct().ToList();
        foreach (int x in changedColumns){
            // store all tiles in column, while deleting them
            var columnContent = new List<Tile>();
            for (int y = 0; y < bounds.y; y++){
                var position = new Vector3Int(x, y, 0);
                Tile tile = tilemap.GetTile<Tile>(position);
                if (tile != null){
                    columnContent.Add(tile);
                    tilemap.SetTile(position, null);
                }
            }
            // reset those tiles from the bottom
            for (int y = 0; y < Enumerable.Count(columnContent); y++){
                var position = new Vector3Int(x, y, 0);
                tilemap.SetTile(position, columnContent[y]);
            }
        }
        bool clearedLines = (changedColumns.Count() > 0);
        return clearedLines;
    }

    public bool ClearLines(Tile[,] tilemap, List<int[]> cellsToClear){
        var changedColumns = new List<int>();
        foreach (var point in cellsToClear){
            changedColumns.Add(point[0]);
            tilemap[point[0], point[1]] = null;
        }
        changedColumns = changedColumns.Distinct().ToList();
        foreach (int x in changedColumns){
            // store all tiles in column, while deleting them
            var columnContent = new List<Tile>();
            for (int y = 0; y < bounds.y; y++){
                Tile tile = tilemap[x, y];
                if (tile != null){
                    columnContent.Add(tile);
                    tilemap[x, y] = null;
                }
            }
            // reset those tiles from the bottom
            for (int y = 0; y < Enumerable.Count(columnContent); y++){
                tilemap[x, y] = columnContent[y];
            }
        }
        bool clearedLines = (changedColumns.Count() > 0);
        return clearedLines;
    }

    public bool IsValidPosition(Tilemap tilemap, Vector3Int piecePosition)
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = piecePosition + columnPiece[i];
            int x = absPosition.x, y = absPosition.y;
            if (!(0 <= x & x < bounds.x & 0 <= y & y < bounds.y)) {
                return false;
            }
            if (tilemap.HasTile(absPosition)) {
                return false;
            }
        }
        return true;
    }

    public bool IsValidPosition(Tile[,] tilemap, Vector3Int piecePosition)
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = piecePosition + columnPiece[i];
            int x = absPosition.x, y = absPosition.y;
            if (!(0 <= x & x < bounds.x & 0 <= y & y < bounds.y)) {
                return false;
            }
            if (tilemap[x,y] != null) {
                return false;
            }
        }
        return true;
    }    
}


