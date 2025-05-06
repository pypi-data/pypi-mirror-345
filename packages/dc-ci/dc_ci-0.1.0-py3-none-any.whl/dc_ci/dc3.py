text = ''' # mapper_char_count.py
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    for char in line.strip():
        print(f"{char}\t1")


# reducer_char_count.py
#!/usr/bin/env python3
import sys
from collections import defaultdict

char_counts = defaultdict(int)
for line in sys.stdin:
    try:
        char, count = line.strip().split('\t')
        char_counts[char] += int(count)
    except:
        continue

for char in sorted(char_counts):
    print(f"{char}\t{char_counts[char]}")


-----------------------------------------------

# mapper_word_count.py
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        print(f"{word}\t1")

# reducer_word_count.py
#!/usr/bin/env python3
import sys
from collections import defaultdict

word_counts = defaultdict(int)
for line in sys.stdin:
    try:
        word, count = line.strip().split('\t')
        word_counts[word] += int(count)
    except:
        continue

for word in sorted(word_counts):
    print(f"{word}\t{word_counts[word]}")
'''

print(text)