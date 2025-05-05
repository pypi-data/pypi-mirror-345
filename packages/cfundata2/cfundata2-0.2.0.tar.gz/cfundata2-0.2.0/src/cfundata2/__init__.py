"""该包定义了两个数据集的路径（含数据集）

Attributes:
    FREQUENCY_PATH (pathlib.Path): 频率数据集路径, 没有含百度百科, 两列: `word(str)`, `count(int)`
    FREQUENCY2_PATH (pathlib.Path): 频率数据集路径， 含百度百科，词和语料库都丰富很多, 两列: `word(str)`, `count(int)`

参考：
    https://github.com/zoushucai/textfrequency

Example:
    ```python
    from cfundata2 import FREQUENCY_PATH, FREQUENCY2_PATH
    print(FREQUENCY_PATH)
    print(FREQUENCY2_PATH)

    # 如果要读取
    import pandas as pd
    df = pd.read_parquet(FREQUENCY_PATH)
    print(df.head())
    ```


"""

import importlib.resources as pkg_resources

FREQUENCY_PATH = pkg_resources.files("cfundata2").joinpath("frequency.parquet")
FREQUENCY2_PATH = pkg_resources.files("cfundata2").joinpath("frequency2.parquet")
