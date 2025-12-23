import pandas as pd
df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
df.to_csv('merge_test_1.csv', index=False)
df = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
df.to_csv('merge_test_2.csv', index=False)
