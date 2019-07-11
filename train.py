import pickle
import math

stats = {}
max_ngrams = 1


def ngram(line, n):
	output = []
	for i, char in enumerate(line):
		if i - n < 0:
			buff = ''
			for j in range(abs(i - n)):
				buff += 'Ω'
			buff += str(line[0:i])
			output.append((buff, char))
		else:
			output.append((line[i - n:i], char))
	#print(output)
	return output

def DelLastChar(str):
	str_list=list(str)
	str_list.pop()
	return "".join(str_list)

readfile = input("Please enter the path of the dictionary to be trained (e.g: C:/1.txt): ")
with open(readfile,'rb') as file:
	for line in file:
		line = line.decode("latin-1")
		line = line.replace('\n','å')
		#line = DelLastChar(line)


		for i in range(max_ngrams):
			for gram in ngram(line, i + 1):
				prev = gram[0] # previous characters, ngram
				nxt = gram[1] # next character
				if not prev in stats:
					stats[prev] = {}
				if not nxt in stats[prev]:
					stats[prev][nxt] = 0
				
				stats[prev][nxt] += 1

for ngram in stats:
	total = 0

	for key, value in stats[ngram].items():
		total += value

	for key, value in stats[ngram].items():
		stats[ngram][key] = value / float(total)

with open('./{}-gram.pickle'.format(max_ngrams), 'wb') as file:
	pickle.dump(stats, file)
print(stats)
