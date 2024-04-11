using System.Collections;
using System.Collections.Generic;

public class PieceState
{
    public int[] position { get; private set; }
    private int[] values;
    private int rotIndex = 0;

    public PieceState(int[] initValues, int[] initPosition){
        values = initValues;
        position = initPosition;
    }

    public void Rotate(int sign){
        rotIndex += 1*sign;
    }

    public bool Move(BoardState boardState, int dx, int dy){
        int[] newPosition = {position[0] + dx, position[1] + dy};
        if (boardState.IsValidPosition(newPosition)){
            position = newPosition;
            return true;    
        }
        return false;
    }

    public int GetWrappedValue(int index){
        int wrappedIndex = Wrap(index + rotIndex);
        return values[wrappedIndex];
    }

    private static int Wrap(int index){
        int remainder = index % 3;
        return (remainder < 0) ? remainder + 3 : remainder;
    }

}
