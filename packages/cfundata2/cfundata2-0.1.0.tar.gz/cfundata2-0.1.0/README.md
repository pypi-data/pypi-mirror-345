
## cfundata2 

该包定义了两个数据集的路径（含数据集）

Attribution:

   - FREQUENCY_PATH (pathlib.Path): 频率数据集路径, 没有含百度百科, 两列: word(str), count(int)
   
   - FREQUENCY2_PATH (pathlib.Path): 频率数据集路径， 含百度百科，词和语料库都丰富很多, 两列: word(str), count(int)

参考：[https://github.com/zoushucai/textfrequency](https://github.com/zoushucai/textfrequency)


- 只是导出了数据的路径，并未读取

```python
from cfundata2 import FREQUENCY_PATH, FREQUENCY2_PATH
print(FREQUENCY_PATH) 
print(FREQUENCY2_PATH)

# 如果要读取
import pandas as pd
df = pd.read_parquet(FREQUENCY_PATH)
print(df.head())
```
