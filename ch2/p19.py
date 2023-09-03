key = {
  123: 'once',
  199: 'or',
  202: 'maybe',
  221: 'twice',
  233: 'time',
  332: 'upon',
  451: 'a',
}

message = [242, 554, 650, 464, 532, 749, 567]
additives = [119, 222, 199, 231, 333, 547, 346]

for word, additive in zip(message, additives):
    print(key[word - additive] + ' ', end='')