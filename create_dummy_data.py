import pandas as pd
import numpy as np

# Create a dummy dataframe with 5005 rows to test the splitting (5000 per file)
df = pd.DataFrame(np.random.randint(0,100,size=(5005, 4)), columns=list('ABCD'))
df.to_excel("your_file.xlsx", index=False)
print("Created your_file.xlsx with 5005 rows")
