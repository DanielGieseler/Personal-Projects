using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

public class Ghost : MonoBehaviour
{
    public GameObject boardGM;
    private Board board;
    private Piece activePiece;
    public Tilemap tilemap;
    public Vector3Int droppedPosition;

    void Awake()
    {
        board = boardGM.GetComponent<Board>();
        tilemap = GetComponentInChildren<Tilemap>();
    }

    void LateUpdate()
    {
        activePiece = board.activePiece;
        tilemap.ClearAllTiles();
        if (Drop()){
            Set();
        }
    }

    public bool Drop()
    {
        droppedPosition = activePiece.position;
        droppedPosition.y += -2;
        while (!board.tilemap.HasTile(droppedPosition) & droppedPosition.y >= 0){
            droppedPosition.y += -1;
        }
        droppedPosition.y += 2;

        int moved = activePiece.position.y - droppedPosition.y;
        return (moved >= 5);
    }

    public void Set()
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = droppedPosition + board.columnPiece[i];
            Tile tile = activePiece.getTile(i);
            var color = tile.color;
            color = new Color(1f,1f,1f,1f);
            tilemap.SetTile(absPosition, tile);
        }
    }

}
