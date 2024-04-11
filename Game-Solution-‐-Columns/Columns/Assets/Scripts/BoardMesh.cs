using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BoardMesh
{
    public List<List<List<int[]>>> allDirections { get; private set; }

    public BoardMesh(int[] bounds){
        int xMax = bounds[0], yMax = bounds[1];
        allDirections = new List<List<List<int[]>>>();
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

    private void Printer(List<List<int[]>> list){
        Debug.Log("Board Mesh Entry: ");
        foreach (var line in list){
            string lineString = "";
            foreach (var point in line){
                lineString += point[0] + "," + point[1] + "; ";
            }
            Debug.Log(lineString);
        }
    }
}
