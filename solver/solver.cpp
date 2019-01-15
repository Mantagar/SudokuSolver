#include "pch.h"
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

class Sudoku
{
private:
	int board[9][9];
	bool fixed[9][9];
	bool solutionFound;

public:
	Sudoku()
	{
		Init();
	}

	void Init()
	{
		solutionFound = false;
		int i = 0;
		for (int x = 0; x < 9; x++)
			for (int y = 0; y < 9; y++)
			{
				board[x][y] = 0;
				fixed[x][y] = false;
			}
	}

	void Solve(int x, int y)
	{
		if (solutionFound) return;
		if (x == 9)
		{
			Print();
			solutionFound = true;
			return;
		}
		if (fixed[x][y])
			if (y == 8) Solve(x + 1, 0);
			else Solve(x, y + 1);
		for (int n = 1; n <= 9; n++)
		{
			if (Verify(x, y, n))
			{
				board[x][y] = n;
				if (y == 8) Solve(x + 1, 0);
				else Solve(x, y + 1);
				board[x][y] = 0;
			}
		}

	}

	bool Verify(int x, int y, int n)
	{
		for (int i = 0; i < 9; i++) if (board[x][i] == n) return false;
		for (int i = 0; i < 9; i++) if (board[i][y] == n) return false;
		x = x / 3 * 3;
		y = y / 3 * 3;
		for (int i = 0; i < 9; i++) if (board[x + i / 3][y + i % 3] == n) return false;
		return true;
	}

	void Print()
	{
		for (int x = 0; x < 9; x++)
		{
			for (int y = 0; y < 9; y++)
			{
				if (fixed[x][y]) cout << board[x][y] << "";
				else if (board[x][y] != 0) cout << board[x][y] << "";
				else cout << "";
				if (y == 2 or y == 5) cout << "";
			}
			//if (x == 2 or x == 5) cout << endl;
			cout << endl;
		}
	}

	void LoadFromFile(char* path)
	{
		string line;
		ifstream file(path);
		if (file.is_open())
		{
			for (int x = 0; x < 9; x++)
			{
				getline(file, line);
				for (int y = 0; y < 9; y++)
				{
					int n = (int)(line[y] - '0');
					board[x][y] = n;
					if (board[x][y] != 0) fixed[x][y] = true;
				}
			}
			file.close();
		}
		else throw "File cannot be opened!";

	}
};


int main(int argc, char** argv)
{
	Sudoku game;
	if (argc > 1)
	{
		try
		{
			game.LoadFromFile(argv[1]);
		}
		catch (const char* msg)
		{
			cerr << msg << endl;
			return 1;
		}
	}
	
	game.Solve(0, 0);

	return 0;
}
