using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class Score : MonoBehaviour
{
    public TMP_Text textScore;
    public GameObject boardGM;
    private Board board;

    // Start is called before the first frame update
    void Start()
    {
        board = boardGM.GetComponent<Board>();
        textScore.text = board.score.ToString();  
    }

    // Update is called once per frame
    void Update()
    {
        textScore.text = board.score.ToString();
    }
}
