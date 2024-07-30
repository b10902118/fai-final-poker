for i in {1..20}; do
	python start_game.py |grep -A 10 -B 10 -e '^"me".*Invalid'
done
