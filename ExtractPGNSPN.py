#!/Users/brandt/anaconda/bin/python
if __name__ == "__main__":
    import pandas as pd
    import sys
    df = pd.read_csv(sys.argv[1])
    pgnspn = df.keys()[1:]
    with open(sys.argv[2], 'w') as fout:
        for i in pgnspn:
            print('{}'.format(i), file=fout)
    fout.close()