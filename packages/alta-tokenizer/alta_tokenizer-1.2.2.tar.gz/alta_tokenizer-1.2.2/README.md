# ALTA Tokenizer

`alta-tokenizer` is a Python library designed for tokenizing Kinyarwanda language text, it can also tokenizer other languages like English, French or similar languages but with low compression rate since the tokenizer was trained on Kinyarwanda text only.
There is an option for training your own custom tokenizer using defined function or method. It is covered in the section of training your own tokenizer.
Hence, you can use that way to train your own tokenizer using dataset for a different language. It is based on the Byte Pair Encoding (BPE) algorithm.

It can both encode and decode text in Kinyarwanda. The metric used to measure the accuracy of this tokenizer is the **compression rate** and ability to encode and decode texts

**Compression rate** is the ratio of the total original number of characters in the text to the number of tokens in the encoded text.

**Example:**

For the sentence: `"Nagiye gusura abanyeshuri."`

- The sentence has **26 characters**.
- Suppose the sentence is tokenized into the following tokens: `[23, 45, 67, 89, 23, 123, 44, 22, 55, 22, 45]`.
- The total number of tokens is **11**.

$$ \text{Compression Rate} = \frac{26}{11} $$

So, the **compression rate is 2.36X** (where X indicates that the number is approximate).

## Special Tokens

**<|PAD|>** is a special token for padding, it is represented by **0** in the vocab

**<|EOS|>** is a special token for indicating the end of sequence

**<|BOS|>** is a special token for indicating the begining of sequence

**<|SEP|>** is a speical token for separating two sequences

**<|MASK|>** is a spicial token for masking

**<|UNK|>** is a special token for unknown

**<|CLS|>** is a special token for classification

## ALTA-Tokenizer 1.0

Version 1.0 features a vocabulary size of 32,256 with improved words or subwords. It was trained on over 19 millions Kinyarwanda characters and shows a significantly improved compression rate compared to the previous version.

## Installation

You can install the package using pip:

```bash
    pip install alta-tokenizer

```

## Basis Usage

 ```python

    from kin_tokenizer import KinTokenizer  # Importing Tokenizer class
    from kin_tokenizer.utils import create_sequences

    # Creating an instance of tokenizer
    tokenizer = KinTokenizer()

    # Loading the state of the tokenizer (pretrained tokenizer)
    tokenizer.load()

    # Encoding
    text = """
    Nuko Semugeshi akunda uwo mutwe w'abatwa, bitwaga Ishabi, awugira intore ze. Bukeye
bataha biyereka ingabo; dore ko hambere nta mihamirizo yindi yabaga mu Rwanda; guhamiriza
byaje vuba biturutse i Burundi. Ubwo bataha Semugeshi n'abatware be barabitegereza basanga
ari abahanga bose, ariko Waga akaba umuhanga w'imena muri bo; nyamara muri ubwo buhanga
bwe akagiramo intege nke ku mpamvu yo kunanuka, yari afite uruti ruke."""

    tokens = tokenizer.encode(text)
    print(tokens)

    # Calculating compression rate
    text_len = len(text)
    tokens_len = len(tokens)

    compression_rate = text_len / tokens_len
    print(f"Compression rate: {compression_rate:.2f}X")


    # Creating sequences from tokens encoded from text
    x_seq, y_seq = create_sequences(tokens, seq_len=20)

    # Decoding
    decoded_text = tokenizer.decode(tokens)
    print(decoded_text)

    # Decoding one sequence from created sequences
    print(f"Decoded sequence:\n {tokenizer.decode(x_seq[0])}")

    # Printing the vocab size
    print(tokenizer.vocab_size)

    # Print vocabulary (first 200 items)
    count = 0
    for k, v in tokenizer.vocab.items():
        print("{} : {}".format(k, v))
        count += 1
        if count > 100:
            break
```

## Training Your Own Tokenizer

You can also train your own tokenizer using the utils module, which provides two functions: a training function and a function for creating sequences after encoding your text.
**N.B**: Your chosen vocab_size will be met depening on the amount of data you have used for training. The **vocab_size** is a hyperparameter to be adjusted for better vocabularies in your vocab, and also the size of your dataset and diversity matters. The vocab is initialized by count of 256 from 1-255 unicode characters and 0 for <|PAD|>.

```python

    from kin_tokenizer import KinTokenizer
    from kin_tokenizer.utils import train_kin_tokenizer, create_sequences, create_sequences_batch

    # You can use multi-processing version of sequences creation if your have many tokens
    # create_sequences_batch is the function for doing that. You can check documentation of this function

    # Training the tokenizer
    tokenizer = train_kin_tokenizer(training_text, vocab_size=512, save=True, tokenizer_path=SAVE_PATH_ROOT, retrain=False)


    # Encoding text using custom trained tokenizer
    tokens = tokenizer.encode(text)

    # Creating sequences
    x_seq, y_seq = create_sequences(tokens, seq_len=20, step=5)

```

## Contributing

The project is still being updated and contributions are welcome. You can contribute by:

- Reporting bugs
- Suggesting features
- Writing or improving documentation
- Submitting pull requests
  