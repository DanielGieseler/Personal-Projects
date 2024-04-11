using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.Tilemaps;

/*
public class AbstractTileMap
{
    public Tile[,] aTilemap;

    public void Initialize(Tilemap tilemap){
        for (int x = 0; x < 9; x++) {
            for (int y = 0; y < 19; y++) {
                var position = new Vector3Int(x, y, 0);
                var tile = tilemap.GetTile(position);
                if (tile == null){
                    break;
                }
                aTilemap[x, y] = tile;
            }
        }
    }

    public bool HasTile(Vector3Int pos){
        return (aTilemap[pos.x, pos.y] != null);
    }
    public void SetTile(Vector3Int pos, Tile tile){
        aTilemap[pos.x, pos.y] = tile;
    }
    public Tile GetTile(Vector3Int pos){
        return aTilemap[pos.x, pos.y];
    }
    public void ClearAllTiles(){
        aTilemap.Clear();
    }

}

*/

public class AbstractModel
{
    //public float abstractScore;
    //public int[] abstractNextPiece = new int[3];
    //public int[] abstractActivePiece = new int[3];
    public Tile[,] abstractTilemap { get; private set; }


    public AbstractModel(Tilemap tilemap){
        abstractTilemap = new Tile[10,20];
        for (int x = 0; x < 9; x++) {
            for (int y = 0; y < 19; y++) {
                var position = new Vector3Int(x, y, 0);
                var tile = tilemap.GetTile<Tile>(position);
                if (tile == null){
                    break;
                }
                abstractTilemap[x, y] = tile;
            }
        }
    }

}