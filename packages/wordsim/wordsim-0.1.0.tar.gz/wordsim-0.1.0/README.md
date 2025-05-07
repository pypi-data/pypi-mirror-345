# wordsim
This is the source code of a smart model that finds the similarity between a given word and a reference list of words. Then it returns the word that has the most similarity.

## How to use:

from wordsim import * # import the module

lst = ['Red', 'Green', 'Blue'] # define a list of strings

model = wordSim() # create an instance of the class 'wordSim'

model.train(lst) # train your model using your list of strings

results = model.predict('blu') # commence prediction

print(results) # print results:

print(model.get_best()) # or print it that way