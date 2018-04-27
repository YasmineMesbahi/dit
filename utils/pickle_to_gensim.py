import pickle

deserialized = pickle.load(open('wikifrdict.pkl','rb')) #type dict

file_path = "wikifrdict_deserializing.gensim"
with open(file_path,"w", encoding = "utf8") as f:
    line1 = str(len(deserialized))+ " " + "300" + "\n"
    f.write(line1)
    for word, vector in deserialized.items():
        line = word
        for vector_elem in vector:
            line += " " + str(vector_elem)
        line += "\n"
        f.write(line)
