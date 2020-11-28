from classifiers import DictClassifier

ds = DictClassifier()
a_sentence = "有意思"
result = ds.analyse_sentence(a_sentence)
print(result)