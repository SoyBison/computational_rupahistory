# Computational Rupahistory

This is an ongoing project to create 4X-style simulations of civilizations in a simulated world. This is intended to be a long-term project, that I will add to over the course of a long period, when I have some free time.

## Some Background:

Rupahistory is a portmantau from the Maori word "rūpahu" meaning "fake" or "liar" and the Greek "historia" meaning history.

Warning: The following discussion is boring. I suggest skipping straight to "The Map".

You may notice looking through git logs that this project used to be called "patahistory," as a joke on the French philosophical tradition of pataphysics. In researching this topic I discovered that the name "pataphysics" does not come from the greek for "fake" it's actually a joke in and of itself, and the name comes from: τὰ ἐπὶ τὰ μεταφυσικά, (ta epi ta metaphysika) where the "pata-" prefix is taken as a contraction of 'epi ta meta-'. Thus the prefix actually means "that which is above that which is above", not "fake", as I previously thought. This, I realized, sends the wrong message about my project. I do not intend for my project to make fun of metahistory, although that is probably a project worth undertaking. Patahistory may be a good candidate as some authors have interpreted "pataphysics" as a paronym of "pas ta physique," or "not your physics." "pas ta histore" certainly works, but to avoid confusion, and to embrace my personal love of naming things after words in non-western languages, I went with "rūpahistory."

## The Map:

The map will be a hexagonal grid, defined in cubic coordinates. That being said, it has been implemented using a python dictionary where the key is a tuple of the coordinates, and the value is the tile with all the information needed about it.

## The Output:

The output of a given simulation will be an animation that shows how the simulated cultures change over time. At first this will just be a visual depiction of the map, shaded to show land controlled by the civilizations, as well as changes to the landscape that the cultures make. Currently, `rupahistory.py` outputs an animation which shows the land and water being formed.

## Land and Water:

The land generation algorithm is a cellular automata which starts by randomly assigning cells either land or water. Then, for calculating each step:

- If a cell is water, and it has 4 or more adjacent tiles which are sand, it will become sand.
- If a cell is sand and it borders no water, it will become grass.
- If a cell is grass and it borders any water, it will become sand.
- If a cell is sand and it has 4 or more adjacent tiles which are water, it will become water.

Some experimentation is left to do with Land and Water generation before moving on to creating nations and tribes.