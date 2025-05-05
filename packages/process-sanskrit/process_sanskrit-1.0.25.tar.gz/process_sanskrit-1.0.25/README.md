# Process-Sanskrit

Process-Sanskrit is a light-computing library for Sanskrit text analysis, annotation and inflected dictionary search. 

The library has two main use cases: 

1. **Dictionary search:** multi dictionary lookup with grammatical annotation for words exactly as they are written in texts: in **any transliteration format, inflected, compounded and with sandhi**. 
2. **Automatic Text Annotation:** generate automatically version of Sanskrit texts without sandhi and with split compounds, with grammatical annotations and dictionary entries for each word. 

`The architecture of the library is based on a cascading approach to Sanskrit text analysis, as described in our NAACL 2025 paper:`*Accessible Sanskrit: A Cascading System for Text Analysis and Dictionary*
*Access.*

## Demo:

The library can be employed live on the [(***Sanskrit Voyager*** website)[https://www.sanskritvoyager.com/].](https://www.sanskritvoyager.com/)

Select a book or paste some text, click on the words and see the library in action! 

Or search some inflected and sandhi-ed words in the search bar to get the dictionary entries. 

*The following is the Quickstart guide. For a more detailed documentation and advanced features refer to the [documentation website](sanskritvoyager.com/docs).* 

## Installation

To install the library use the standard *pip install* command, then call ***update-ps-database*** in the terminal to setup the database.

A venv, colab, environment or docker is highly recommended to use gensim. 
For the experimental BYT5 version 

```bash
pip install process-sanskrit[gensim]
update-ps-database

or
pip install process-sanskrit[BYT5]
update-ps-database
```

The command downloads and setup the database with the dictionaries and the inflection tables in the resources folder (150 mb download, 583 mb uncompressed, (Creative Commons NC license)[[https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)]): 

```python

## if inside jupyter or colab use:

!pip install process-sanskrit[gensim]
!update-ps-database

```

*only **transliterate** works without the database!*


## Process Function:

The core of the library is the **process** function, that accepts text in Sanskrit as input and executes an entire text processing pipeline for the text.

```python
import process-sanskrit as ps 

ps.process("pratiprasave")
```

Process returns a list that contains for each word contained in the text or compounds: 

![Screenshot 2025-04-26 at 15.45.17.png](Process-Sanskrit%201e1612d83c5180a8ac4bd8918e716d4b/Screenshot_2025-04-26_at_15.45.17.png)

![Screenshot 2025-04-26 at 15.45.55.png](Process-Sanskrit%201e1612d83c5180a8ac4bd8918e716d4b/Screenshot_2025-04-26_at_15.45.55.png)

1. **Word stem**: ‘pratiprasava’
2. **Grammatical tagging**: masculine noun/adjective ending in a
3. **Case** (for nouns) **or Inflection** (for verbs): [('Loc', 'Sg')]
4. **Inflection table** for the word as a list:  ['pratiprasavaḥ', 'pratiprasavau', 'pratiprasavāḥ', 'pratiprasavam', 'pratiprasavau', 'pratiprasavān', 'pratiprasavena', 'pratiprasavābhyām', 'pratiprasavaiḥ', 'pratiprasavāya', 'pratiprasavābhyām', 'pratiprasavebhyaḥ', 'pratiprasavāt', 'pratiprasavābhyām', 'pratiprasavebhyaḥ', 'pratiprasavasya', 'pratiprasavayoḥ', 'pratiprasavānām', 'pratiprasave', 'pratiprasavayoḥ', 'pratiprasaveṣu', 'pratiprasava', 'pratiprasavau', 'pratiprasavāḥ']
5. **Original word**: 'pratiprasave’
6. **Word Components** according to the Monnier Williams: (in this case none) 'prati—prasava’
7. **Dictionary entries** in XML format. In the form of a dictionary for all the selected dictionaries: {'mw': {'pratiprasava': ['<s>prati—prasava</s> <hom>a</hom>   See under <s>prati-pra-</s> √ <hom>1.</hom> <s>sū</s>.', '<s>prati-°prasava</s> <hom>b</hom>   <lex>m.</lex> counter-order, suspension of a general prohibition in a particular case, <ls>Śaṃkarācārya  </ls>; <ls>Kātyāyana-śrauta-sūtra </ls>, <ab>Scholiast or Commentator</ab>; <ls>Manvarthamuktāvalī, KullūkaBhaṭṭa\'s commentary on Manu-smṛti </ls><info lex="m"/>', '  an exception to an exception, <ls>Taittirīya-prātiśākhya </ls>, <ab>Scholiast or Commentator</ab><info lex="inh"/>', '  return to the original state, <ls>Yoga-sūtra </ls><info lex="inh"/>']}

### Dictionary Selection:

**By default, only the Monnier Williams dictionary is selected.** 

If there are words that are outside the MW (i.E. ‘dvandva’) the dictionaries that have the word are automatically selected. In this example the word is found in the Macdonnell dictionary. 

![Screenshot 2025-04-26 at 15.27.25.png](Process-Sanskrit%201e1612d83c5180a8ac4bd8918e716d4b/Screenshot_2025-04-26_at_15.27.25.png)

```python
## additional dictionaries can be returned in the output by adding them as
## arguments after the main text input. 

import process-sanskrit as ps

ps.process('saṃskāra', 'ap90', 'cae', 'gra', 'bhs')
```

Available Dictionaries: 

- 'mw': 'Monier-Williams Sanskrit-English Dictionary' ,
- 'ap90': 'Apte Practical Sanskrit-English Dictionary'
- ‘cae': 'Cappeller Sanskrit-English Dictionary'
- 'ddsa': 'Macdonell A Practical Sanskrit Dictionary'
- 'gra': 'Grassmann Wörterbuch zum Rig Veda'
- 'bhs': 'Edgerton Buddhist Hybrid Sanskrit Dictionary'
- 'cped': 'Concise Pali English Dictionary'

All the dictionaries are slightly modified version of the *Cologne Digital Sanskrit Dictionaries, apart from the* (The Concise Pali-English Dictionary By Buddhadatta Mahathera)[https://buddhistuniversity.net/content/reference/concise-pali-dictionary] The Pali dictionary was added in to handle words that appears in the late Buddhist authors. 

```
Cologne Digital Sanskrit Dictionaries, version 2.7.286,
Cologne University, accessed on February 19, 2025,
https://www.sanskrit-lexicon.uni-koeln.de
```

### Stemming:

To use the process function just for sandhi/compound split and stemming, use the process function with the flag: *output=’roots’*.

```python
import process-sanskrit as ps

ps.process('yamaniyamāsanaprāṇāyāmapratyāhāradhāraṇādhyānasamādhayo', output='roots')

## output:
## ['yama', 'niyama', 'asana', 'prāṇāyāma', 'pratyāhāra', 'dhāraṇa', 'dhyāna', 'samādhi']
```

![Screenshot 2025-04-26 at 15.58.49.png](Process-Sanskrit%201e1612d83c5180a8ac4bd8918e716d4b/Screenshot_2025-04-26_at_15.58.49.png)

*!it is to note that in case of ambiguity the process function does not select between the two (or three) possibilities, but returns all of them as a tuple.*

![Screenshot 2025-04-26 at 16.15.10.png](Process-Sanskrit%201e1612d83c5180a8ac4bd8918e716d4b/Screenshot_2025-04-26_at_16.15.10.png)

### Transliteration API:

The library offers a function to transliterate texts with auto-detection for the transliteration input format. This function is a slight adaptation from (*Indic-Transliteration Detect)[”*[https://github.com/indic-transliteration/detect.py](https://github.com/indic-transliteration/detect.py)”].

```python
import process_sanskrit as ps

# Transliteration
ps.transliterate("patañjali", "DEVANAGARI") ## IAST 
ps.transliterate("pataJjali", "DEVANAGARI") ## HK format

## same output:
## पतञ्जलि

## In case you need to manually select the input scheme, you can force it using
## the input_scheme flag, it's not case sensitive: 

ps.transliterate('pataYjali', 'tamil', input_scheme='slp1')

## output: பதஞ்ஜலி
```

### Dictionary Search:

The library provides the *dict_search* function to retrieve dictionary entries. 

Pass to the dict_search a list of strings to be searched on and (optionally) a list of dictionary tags. 

```python
import process_sanskrit as ps

## unlike the process function, the dict_search wants the input in IAST format. 

# example usage for Dictionary lookup
ps.dict_search(['pratiprasava', 'saṃskāra'])

# after a list of entries, optionally add dictionary tags to search in multiple dictionaries. 

# search in Edgerton Buddhist Hybrid Sanskrit Dictionary
# and Grassmann Wörterbuch zum Rig Veda:
ps.dict_search(['pratiprasava', 'saṃskāra'], 'gra', 'bhs')
```

*The library automatically handles the fact that the Apte records nominatives instead of un-inflected stems (i.E. yogaḥ instead of yoga)*. 

## Sources:

**CLS inflect** for the inflection tables: [https://github.com/sanskrit-lexicon/csl-inflect](https://github.com/sanskrit-lexicon/csl-inflect)

The **Sanskrit Parser** library handles part of the Sandhi Splitting: [https://github.com/kmadathil/sanskrit_parser?tab=readme-ov-file](https://github.com/kmadathil/sanskrit_parser?tab=readme-ov-file)

The **BYT5 model** used in the experimental version of the process function is from the [https://huggingface.co/buddhist-nlp/byt5-sanskrit](https://huggingface.co/buddhist-nlp/byt5-sanskrit) discussed in the paper: 

**One Model is All You Need: ByT5-Sanskrit, a Unified Model for Sanskrit NLP Tasks**

[Sebastian Nehrdich](https://arxiv.org/search/cs?searchtype=author&query=Nehrdich,+S), [Oliver Hellwig](https://arxiv.org/search/cs?searchtype=author&query=Hellwig,+O), [Kurt Keutzer](https://arxiv.org/search/cs?searchtype=author&query=Keutzer,+K)

[https://arxiv.org/abs/2409.13920](https://arxiv.org/abs/2409.13920)

