#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <iomanip>

// Function to print the 2D array as a definition
void printPreflopChartAsArray(double chart[13][13])
{
	std::cout << "double preflopChart[13][13] = {" << std::endl;
	for (int i = 0; i < 13; ++i)
	{
		std::cout << "    {";
		for (int j = 0; j < 13; ++j)
		{
			std::cout << std::fixed << std::setprecision(5) << chart[i][j];
			if (j < 12)
				std::cout << ", ";
		}
		std::cout << "}";
		if (i < 12)
			std::cout << ",";
		std::cout << std::endl;
	}
	std::cout << "};" << std::endl;
}

int getRankIndex(char rank)
{
	std::string ranks = "23456789TJQKA";
	return ranks.find(rank);
}

int main()
{
	// Initialize the preflop chart with zeros
	double preflopChart[13][13] = {0};

	// Open the file
	std::ifstream inputFile("preflop.txt");
	if (!inputFile)
	{
		std::cerr << "Error opening file." << std::endl;
		return 1;
	}

	std::string line;
	while (std::getline(inputFile, line))
	{
		std::istringstream lineStream(line);
		std::string hand;
		double strength;
		lineStream >> hand >> strength;

		char rank1 = hand[0];
		char rank2 = hand[1];
		char suit = hand[2];

		int index1 = getRankIndex(rank1);
		int index2 = getRankIndex(rank2);

		if (suit == 'o')
		{
			preflopChart[index1][index2] = strength;
		}
		else if (suit == 's')
		{
			preflopChart[index2][index1] = strength;
		}
	}

	// Close the file
	inputFile.close();

	// Print the preflop chart as a 2D array definition
	printPreflopChartAsArray(preflopChart);

	return 0;
}
