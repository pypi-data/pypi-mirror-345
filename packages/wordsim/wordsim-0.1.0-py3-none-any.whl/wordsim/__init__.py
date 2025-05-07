class wordSim:
    def __init__(self):
        pass
    def train(self, reference_list:list[str]):
        if not isinstance(reference_list, list):
            raise ValueError(f"Wrong datatype is entered '{reference_list=}'. Please insert a list.")
        for element in reference_list:
            if not isinstance(element, str):
                raise ValueError(f"Wrong datatype is entered '{reference_list=}'. Please insert a list having elements of a string datatype.")
        self.reference_list = reference_list
        self._processed_ref_list = [string.lower() for string in reference_list]

    def predict(self, word:str, tunner:int=2):
        if not isinstance(word, str):
            raise ValueError(f"Wrong datatype is entered '{word=}'. Please insert a string.")
        if not isinstance(tunner, int):
            raise ValueError(f"Wrong datatype is entered '{tunner=}'. Please insert an integer.")
        if tunner < 1:
            raise ValueError(f"Wrong value is entered '{tunner=}'. Please insert a value greater than zero.")
        if tunner > len(word):
            raise ValueError(f"Wrong value is entered '{tunner=}'. Please insert a value less then the length of entered word '{word=}'.")
        
        word = word.lower()

        # predictions:
        for index, element in enumerate(self._processed_ref_list):
            if word == element:
                exact_match = dict(word=word, word_match=self.reference_list[index], status='successful', score=1.0)
                return exact_match # return the original matching word if similarity is exact.
            
            sim = Similarity(word, element)
            sim.predict(tunner=tunner)
            
            if index == 0: # first loop.
                best = dict(word=word, word_match=self.reference_list[index], status='pending', score=sim.get_score())
            else:
                if sim.get_score() > best["score"]:
                    best = dict(word=word, word_match=self.reference_list[index], status='pending', score=sim.get_score())
        
        if best['score'] == 0.0: # meaning the algorithm couldn't find a match.
            best['status'] = 'unsuccessful'
            best['word_match'] = 'None'
        else:
            best['status'] = 'successful'
            
        self._best = best
        return best   

    def get_best(self):
        return self._best

class Counter:
    def __init__(self, init:int):
        if not isinstance(init, int):
            raise ValueError("Wrong data type is entered. Please insert an integer.")
        if init < 0:
            raise ValueError("Wrong value is entered. Please insert values more than or equal to zero.")

        self.init = init
        self._count = init

    def increment(self):
        self._count += 1
        return self._count

    def decrement(self):
        self._count -= 1
        return self._count

    def get_count(self):
        return self._count
        
class Similarity:
    def __init__(self, word, reference_word):
        self.word = word
        self.reference_word = reference_word
    
    def predict(self, tunner:int=2):
        num_loops = len(self.word) - tunner + 1
        score = Counter(0)
        for loop in range(num_loops):
            segment = self.word[loop:loop + tunner]
            if segment in self.reference_word:
                score.increment()

        word_len = len(self.word)
        ref_word_len = len(self.reference_word)
        total_len = word_len + ref_word_len
        normalized_score = score.get_count() / total_len

        self._score = normalized_score
        return normalized_score

    def get_score(self):
        return self._score
