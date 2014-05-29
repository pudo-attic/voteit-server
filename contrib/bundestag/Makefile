
all: download build

download:
	curl -o data/persons.json http://daten.offenesparlament.de/misc/popit_person.json
	curl -o data/votes.json http://daten.offenesparlament.de/misc/voteit_vote.json

build:
	python gendata.py
