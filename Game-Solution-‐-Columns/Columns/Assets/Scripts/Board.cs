using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Tilemaps;

[System.Serializable]
public class Board : MonoBehaviour
{
    public Tilemap tilemap { get; private set; }
    public Tile[] nextTilePiece { get; private set; }
    public Piece activePiece { get; private set; }
    public Tile[] possibleTiles;
    private Vector3Int spawnPosition;
    private Vector3Int nextTilePiecePos = new Vector3Int(-4, 9, 0);
    public Vector3Int[] columnPiece = new Vector3Int[]{new Vector3Int(0,1,0), new Vector3Int(0,0,0), new Vector3Int(0,-1,0)};
    public Vector2Int bounds = new Vector2Int(9, 19);

    public Mechanics M { get; private set; }
    public double score { get; set; }

    private void Awake()
    {
        int x = bounds.x, y = bounds.y;
        // Resize game objects to specified bounds
        spawnPosition = new Vector3Int(x/2, y-2, 0);
        var gridObj = GameObject.Find("Grid");
        gridObj.GetComponent<Transform>().position = new Vector3(x/2f, y/2f, 0);
        gridObj.GetComponent<SpriteRenderer>().size = new Vector2(x, y);
        var borderObj = GameObject.Find("Border");
        borderObj.GetComponent<Transform>().position = new Vector3(x/2f, y/2f, 0);
        borderObj.GetComponent<Transform>().localScale = new Vector3(x*0.1f, y*0.05f, 1f);
        var dzObj = GameObject.Find("Danger Zone");
        dzObj.GetComponent<Transform>().position = new Vector3(x/2f, y-1.5f, 0);
        dzObj.GetComponent<SpriteRenderer>().size = new Vector2(x, 3f);
        var camObj = GameObject.Find("Main Camera");
        camObj.GetComponent<Transform>().position = new Vector3(x/2f, y/2f, -10);
        camObj.GetComponent<Camera>().orthographicSize = y/2f + 1f;
        
        tilemap = GetComponentInChildren<Tilemap>();
        activePiece = GetComponentInChildren<Piece>();
        M = new Mechanics();
        score = 0;
    }

    private void Start()
    {
        nextTilePiece = generateRandomTiles();
        SpawnPiece();
    }

    public void SpawnPiece()
    {
        if (!isDangerZoneTiled()) {
            activePiece.Initialize(this, spawnPosition, nextTilePiece);
            nextTilePiece = generateRandomTiles();
            setNextTilePiece();
        } else {
            GameOver();
        }
    }

    private bool isDangerZoneTiled(){
        int y = bounds.y - 3;
        for (int x = 0; x <= bounds.x; x++) {
            var position = new Vector3Int(x, y, 0);
            if (tilemap.HasTile(position)){
                return true;
            }
        }
        return false;
    }


    private Tile[] generateRandomTiles()
    {
        Tile[] tiles = new Tile[3];
        for (int i = 0; i < 3; i++){
            int random = Random.Range(0, possibleTiles.Length);
            tiles[i] = possibleTiles[random];
        }
        return tiles;
    }

    public void GameOver()
    {
        tilemap.ClearAllTiles();
        score = 0;
        nextTilePiece = generateRandomTiles();
        SpawnPiece();
    }

    public void setNextTilePiece()
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = nextTilePiecePos + columnPiece[i];
            tilemap.SetTile(absPosition, nextTilePiece[i]);
        }
    }

    public void Set(Piece piece)
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = piece.position + columnPiece[i];
            tilemap.SetTile(absPosition, piece.getTile(i));
        }
    }

    public void Clear(Piece piece)
    {
        for (int i = 0; i < 3; i++){
            Vector3Int absPosition = piece.position + columnPiece[i];
            tilemap.SetTile(absPosition, null);
        }
    }
}
