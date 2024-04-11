using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Tilemaps;

public class Piece : MonoBehaviour
{
    public Board board { get; private set; }
    public Tile[] tiles { get; private set; }
    public Vector3Int position { get; private set; }
    public int rotationIndex { get; private set; }

    private float stepTime;
    private float stepDelay = 1f;
    private float moveTime;
    private float moveDelayStart = 0.25f;
    private float moveDelay = 0.05f;

    public void Initialize(Board board, Vector3Int spawnPosition, Tile[] tiles)
    {        
        this.board = board;
        this.position = spawnPosition;
        this.tiles = tiles;
        this.rotationIndex = 0;
        this.stepTime = Time.time + this.stepDelay;
        this.moveTime = Time.time;
    }


    private void Update()
    {
        board.Clear(this);

        if (Input.GetKeyDown(KeyCode.G)) {
            AbstractModel absM = new AbstractModel(board.tilemap);
            board.M.Execute(absM.abstractTilemap);
            Debug.Log("abstract tilemap: ");
            for (int y = 0; y < 19; y++) {
                //string lineString = "";
                for (int x = 0; x < 9; x++) {
                    //lineString += x + "," + y + "," + absM.abstractTilemap[x,y] + "; ";
                    Debug.Log(x + "," + y);
                    Debug.Log(absM.abstractTilemap[x,y]);
                }
                //Debug.Log(lineString);
            }
        }


        if (Input.GetKeyDown(KeyCode.A)) {
            Move(-1, 0);
            moveTime = Time.time + moveDelayStart;
        } else if (Input.GetKeyDown(KeyCode.D)) {
            Move(1, 0);
            moveTime = Time.time + moveDelayStart;
        } else if (Input.GetKeyDown(KeyCode.S)) {
            MoveDown();
            moveTime = Time.time + moveDelayStart;
        }
        
        if (Input.GetKeyDown(KeyCode.Space)) {
            HardDrop();
        }

        if (Input.GetKeyDown(KeyCode.P)) {
            Rotate(1);
        } else if (Input.GetKeyDown(KeyCode.L)) {
            Rotate(-1);
        }

        if (Time.time > moveTime) {
            HandleMoveInputs();
        }

        if (Time.time > stepTime) {
            stepTime = Time.time + stepDelay;
            MoveDown();
        }

        board.Set(this);
    }

    private void Rotate(int sign)
    {
        this.rotationIndex += 1*sign;
    }

    private void HandleMoveInputs()
    {
        if (Input.GetKey(KeyCode.A)) {
            Move(-1, 0);
            moveTime = Time.time + moveDelay;
        } else if (Input.GetKey(KeyCode.D)) {
            Move(1, 0);
            moveTime = Time.time + moveDelay;
        } else if (Input.GetKey(KeyCode.S)) {
            MoveDown();
            moveTime = Time.time + moveDelay;
        }
    }

    private bool Move(int dx, int dy)
    {
        Vector3Int newPosition = this.position;
        newPosition.x += dx;
        newPosition.y += dy;

        bool valid = board.M.IsValidPosition(board.tilemap, newPosition);

        if (valid)
        {
            this.position = newPosition;            
        }

        return valid;
    }

    private bool MoveDown()
    {
        bool valid = Move(0, -1);
        if (!valid) {
            board.Set(this);
            var tm = board.tilemap;
            var reward = board.M.Execute(tm);
            board.score += reward;
            board.SpawnPiece();
        }
        return valid;
    }

    private void HardDrop()
    {
        while (MoveDown()) {
            continue;
        }
    }

    public Tile getTile(int index)
    {
        return tiles[Wrap(index + rotationIndex, 3)];
    }

    static int Wrap(int index, int max)
    {
        int remainder = index % max;
        return (remainder < 0) ? remainder + max : remainder;
    }
}
