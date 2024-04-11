using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

public class Game : MonoBehaviour
{
    // GAME STATE
    public BoardState board;
    public PieceState activePiece;
    public PieceState nextPiece;
    public double score;
    
    // GAME DISPLAY // ------------------- need to set it somehow
    public Tile[] possibleTiles; 
    public Tilemap tilemap; 

    // SPACE
    private int[] bounds = {9, 19};
    private BoardMesh boardMesh;
    private int[] spawnPosition;
    private int[] nextPosition = {-4, 9};

    // TIME
    private float stepTime;
    private float stepDelay = 1f;
    private float moveTime;
    private float moveDelayStart = 0.25f;
    private float moveDelay = 0.05f;

    private void Start(){
        ResizeGameObjects();
        boardMesh = new BoardMesh(bounds);
        InitialSetUp();
        //tilemap = GetComponentInChildren<Tilemap>();
    }

    private void ResizeGameObjects(){
        int x = bounds[0], y = bounds[1];
        spawnPosition = new int[]{x/2, y-2};
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
    }

    private void InitialSetUp(){
        board = new BoardState(boardMesh, bounds);
        nextPiece = new PieceState(GenerateRandomValues(), nextPosition);
        activePiece = new PieceState(GenerateRandomValues(), spawnPosition);
        score = 0;
        SetPiece(nextPiece);
        SetPiece(activePiece);
        stepTime = Time.time + stepDelay;
        moveTime = Time.time;
    }

    private int[] GenerateRandomValues(){
        int[] values = new int[3];
        for (int i = 0; i < 3; i++){
            values[i] = Random.Range(1, 7);
        }
        return values;
    }

    public void SpawnNextPiece(){
        if (!board.IsRedZoneFilled()) {
            activePiece = nextPiece;  // ------------------------------------------------ is it deep copy??
            nextPiece = new PieceState(GenerateRandomValues(), nextPosition);
            SetPiece(nextPiece);
            SetPiece(activePiece);
        } else {
            GameOver();
        }
    }

    public void GameOver(){
        InitialSetUp();
        SetTilemap();
    }

    public void SetPiece(PieceState pieceState){
        for (int i = 0; i < 3; i++){
            Vector3Int position = new Vector3Int(pieceState.position[0], pieceState.position[1] + (1-i), 0);
            int tileIndex = pieceState.GetWrappedValue(i) - 1;
            Tile tile = possibleTiles[tileIndex];
            tilemap.SetTile(position, tile);
        }
    }

    public void ClearPiece(PieceState pieceState){
        for (int i = 0; i < 3; i++){
            Vector3Int position = new Vector3Int(pieceState.position[0], pieceState.position[1] + (1-i), 0);
            tilemap.SetTile(position, null);
        }
    }

    public void SetTilemap(){
        for (int x = 0; x < bounds[0]; x++){
            for (int y = 0; y < bounds[1]; y++){
                Vector3Int position = new Vector3Int(x, y, 0);
                int tileIndex = board.values[x, y] - 1;
                Tile tile = tileIndex != -1 ? possibleTiles[tileIndex] : null;
                tilemap.SetTile(position, tile);
            }
        }
    }

    //------------------------------------- PLAYER INPUT -------------------------------------//
    private void Update()
    {
        ClearPiece(activePiece);
        if (Input.GetKeyDown(KeyCode.A)) {
            activePiece.Move(board, -1, 0);
            moveTime = Time.time + moveDelayStart;
        } else if (Input.GetKeyDown(KeyCode.D)) {
            activePiece.Move(board, 1, 0);
            moveTime = Time.time + moveDelayStart;
        } else if (Input.GetKeyDown(KeyCode.S)) {
            moveTime = Time.time + moveDelayStart;
            Drop();
        }
        if (Input.GetKeyDown(KeyCode.Space)) {
            while (Drop()){
                continue;
            }
        }
        if (Input.GetKeyDown(KeyCode.P)) {
            activePiece.Rotate(1);
        } else if (Input.GetKeyDown(KeyCode.L)) {
            activePiece.Rotate(-1);
        }
        if (Time.time > moveTime) {
            HandleMoveInputs();
        }
        if (Time.time > stepTime) {
            stepTime = Time.time + stepDelay;
            Drop();
        }
        SetPiece(activePiece);
    }

    private bool Drop(){
        bool valid = activePiece.Move(board, 0, -1);
        if (!valid) {
            SetPiece(activePiece);
            double reward = board.Stabilize();
            score += reward;
            SetTilemap();
            SpawnNextPiece();
        }
        return valid;
    }

    private void HandleMoveInputs(){
        if (Input.GetKey(KeyCode.A)) {
            activePiece.Move(board, -1, 0);
            moveTime = Time.time + moveDelay;
        } else if (Input.GetKey(KeyCode.D)) {
            activePiece.Move(board, 1, 0);
            moveTime = Time.time + moveDelay;
        } else if (Input.GetKey(KeyCode.S)) {
            moveTime = Time.time + moveDelay;
            Drop();
        }
    }

}
