#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For automatic conversion between Python lists and C++ STL containers
#include <string>
#include <vector>
#include <iostream>
#include <pokerstove/penum/ShowdownEnumerator.h>
// #include "../../lib/pokerstove/penum/ShowdownEnumerator.h"

using namespace pokerstove;
using namespace std;

namespace py = pybind11;

double equity(const std::string &myhand, const std::string &board, const std::vector<std::string> &exclude)
{
	boost::shared_ptr<PokerHandEvaluator> evaluator =
		PokerHandEvaluator::alloc("h");
	vector<CardDistribution> handDists;

	handDists.emplace_back();
	handDists.back().parse(myhand);

	// parse opponent dead CardSets
	handDists.emplace_back();
	handDists.back().fill(evaluator->handSize());
	for (const string &ex : exclude)
	{
		// cout << ex << endl;
		handDists.back().removeHand(CardSet(ex));
	}
	// cout << handDists.back().str() << endl;

	ShowdownEnumerator showdown;
	vector<EquityResult> results =
		showdown.calculateEquity(handDists, CardSet(board), evaluator);

	double total = 0.0;
	for (const EquityResult &result : results)
	{
		total += result.winShares + result.tieShares;
	}

	double equity =
		(results[0].winShares + results[0].tieShares) / total;

	return equity;
}

PYBIND11_MODULE(example, m)
{
	m.def("equity", &equity, "calculate equity",
		  py::arg("myhand"), py::arg("board"), py::arg("exclude"));
}