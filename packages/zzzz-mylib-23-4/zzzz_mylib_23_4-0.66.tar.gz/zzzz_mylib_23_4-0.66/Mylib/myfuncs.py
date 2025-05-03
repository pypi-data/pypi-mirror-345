from datetime import datetime, timedelta
from zipfile import ZipFile
import shutil
import urllib.request
import pickle
import numbers
import itertools
import re
import math
from box.exceptions import BoxValueError
import yaml
import json
from box import ConfigBox
from pathlib import Path
from typing import Any
import base64
import pickle
import pandas as pd
import os
from sklearn.model_selection import PredefinedSplit
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import permutation_importance
from collections import Counter
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from typing import Union
from sklearn import metrics
import random
import pandas as pd
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import chi2_contingency
from scipy import stats
from sklearn.feature_selection import (
    SelectKBest,
    mutual_info_regression,
    mutual_info_classif,
)
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from Mylib import stringToObjectConverter
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from Mylib.myclasses import CustomStackingClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier


SCORINGS_PREFER_MININUM = ["log_loss", "mse", "mae"]
SCORINGS_PREFER_MAXIMUM = ["accuracy"]


def get_sum(a, b):
    """Demo function for the library"""
    return a + b


def get_index_of_outliers(data: Union[np.ndarray, list]):
    """Lấy **index** các giá trị outlier nằm ngoài khoảng Q1 - 1.5*IQR và Q3 + 1.5*IQR

    Args:
        data (Union[np.ndarray, list]): dữ liệu

    Returns:
        list:
    """
    data = np.asarray(data)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    result = np.where((data < lower_bound) | (data > upper_bound))[0].tolist()

    return result


def get_index_of_outliers_on_series(data: pd.Series):
    """Lấy **index** các giá trị outlier nằm ngoài khoảng Q1 - 1.5*IQR và Q3 + 1.5*IQR

    Args:
        data (pd.Series): dữ liệu kiểu **pd.Series**

    Returns:
        list:
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    result = data.index[(data < lower_bound) | (data > upper_bound)].tolist()

    return result


def get_lower_and_upper_bound_of_series(data: pd.Series):
    """Tìm lowerbound, upperbound của 1 tập dữ liệu

    Công thức:
    - lower_bound = Q1 - 1.5 * IQR
    - upper_bound = Q3 + 1.5 * IQR

    Returns:
        (lower_bound, upper_bound): _description_
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound


def get_exact_day(seconds_since_epoch: int):
    """Get the exact day from 1/1/1970

    Args:
        seconds_since_epoch (int): seconds

    Returns:
        datetime: the exact day
    """

    epoch = datetime(1970, 1, 1)
    return epoch + timedelta(seconds=seconds_since_epoch)


def is_number(string_to_check: str):
    """Check if string_to_check is a number"""

    try:
        float(string_to_check)
        return True
    except ValueError:
        return False


def is_integer_str(s: str):
    """Check if str is an integer

    Args:
        s (str): _description_
    """

    regex = "^[+-]?\d+$"
    return bool(re.match(regex, s))


def is_natural_number_str(s: str):
    """Check if str is a natural_number

    Args:
        s (str): _description_
    """

    regex = "^\+?\d+$"
    return re.match(regex, s) is not None


def is_natural_number(num: numbers.Real):
    """Check if num is a natural number

    Args:
        num (numbers.Real): _description_

    """

    return is_integer(num) and num >= 0


def is_integer(number: numbers.Real):
    """Check if number is a integer

    Args:
        number (numbers.Real): _description_
    """

    return pd.isnull(number) == False and number == int(number)


def get_combinations_k_of_n(arr, k):
    """Get the combinations k of arr having n elements"""

    return list(itertools.combinations(arr, k))


def show_frequency_table(arr):
    """Show the frequency table of arr"""
    counts, bin_edges = np.histogram(arr, bins="auto")

    frequency_table = pd.DataFrame(
        {"Bin Start": bin_edges[:-1], "Bin End": bin_edges[1:], "Count": counts}
    )

    frequency_table["Percent"] = frequency_table["Count"] / len(arr) * 100
    frequency_table["Percent"] = frequency_table["Percent"].round(2)

    return frequency_table


def extract_zip_file(zip_file_path, unzip_path):
    """Extract zip file

    Args:
        zip_file_path (str): file path of zip file
        unzip_path (str): folder path of unzip components
    """

    with ZipFile(zip_file_path, "r") as zip:
        zip.extractall(path=unzip_path)


def create_sub_folder_from_dataset(path, data_proportion, root_dir):
    """
    Args:
        path: the path to the folder to create
        root_dir : the path to the folder Dataset
        data_proportion: the proportion of taken data
    Returns:
        _str_: result
    Examples:
        vd tạo thư mục train là 70% dữ liệu, thư mục val là 15% dữ liệu, thư mục test là 15% dữ liệu

        lưu ý là di chuyển các ảnh chứ không phải copy

        nên tập val lấy 0.5 = 0.5 đối với dữ liệu còn lại

        Code:
        ```python
        dataset_path = './Dataset'

        path = './train'
        create_sub_folder_from_dataset(path, 0.7, dataset_path)

        path = './val'
        create_sub_folder_from_dataset(path, 0.5, dataset_path)

        path = './test'
        create_sub_folder_from_dataset(path, 1, dataset_path)
        ```
    """

    if not os.path.exists(path):
        os.mkdir(path)

        for dir in os.listdir(root_dir):
            os.makedirs(os.path.join(path, dir))

            img_names = np.random.permutation(os.listdir(os.path.join(root_dir, dir)))
            count_selected_img_names = int(data_proportion * len(img_names))
            selected_img_names = img_names[:count_selected_img_names]

            for img in selected_img_names:
                src = os.path.join(root_dir, dir, img)
                dest = os.path.join(path, dir)
                shutil.move(src, dest)

        return "Create the sub-folder successfully"
    else:
        return "The sub-folder existed"


def fetch_source_url_to_zip_file(source_url, local_zip_path):
    """Download file from url to local

    Returns:
        filename: the name of file
        headers: info about the file
    """

    os.makedirs(local_zip_path, exist_ok=True)
    filename, headers = urllib.request.urlretrieve(source_url, local_zip_path)

    return filename, headers


def split_numpy_array(
    data: np.ndarray, ratios: list, dimension=1, shuffle: bool = True
):
    """

    Args:
        data (np.ndarray): _description_
        ratios (list): Tỉ lệ các phần. Tổng phải bằng 1
        dimension (int, optional): Chiều của dữ liệu. nếu dữ liệu 2 chiều thì gán = 2. Defaults to 1.
        shuffle(bool, optional): có xáo trộn dữ liệu trước khi chia không

    Returns:
        list: list các mảng numpy

    vd:
    với dữ liệu 2 chiều:
    ```python
    split_ratios = [0.5, 0.2, 0.2, 0.1]  # Tỷ lệ mong muốn
    subsets = split_data(data, split_ratios, 2)
    ```
    """
    if sum(ratios) != 1:
        raise ValueError("Tổng của ratios phải bằng 1")

    if shuffle:
        data = np.random.permutation(data)

    len_data = len(data) if dimension == 1 else data.shape[0]
    split_indices = np.cumsum(ratios)[:-1] * len_data
    split_indices = split_indices.astype(int)
    return (
        np.split(data, split_indices)
        if dimension == 1
        else np.split(data, split_indices, axis=0)
    )


def split_dataframe_data(data: pd.DataFrame, ratios: list, shuffle: bool = True):
    """

    Args:
        data (pd.DataFrame): _description_
        ratios (list): Tỉ lệ các phần. Tổng phải bằng 1
        shuffle(bool, optional): có xáo trộn dữ liệu trước khi chia không. Defaults to True

    Returns:
        list: list các dataframe

    VD:
        ```python
    split_ratios = [0.5, 0.2, 0.2, 0.1]  # Tỷ lệ mong muốn
    subsets = split_data(data, split_ratios)
    """
    if sum(ratios) != 1:
        raise ValueError("Tổng của ratios phải bằng 1")

    if shuffle:
        data = data.sample(frac=1.0, random_state=42).reset_index(drop=True)

    split_indices = np.cumsum(ratios)[:-1] * len(data)
    split_indices = split_indices.astype(int)

    subsets = np.split(data, split_indices, axis=0)

    return [pd.DataFrame(item, columns=data.columns) for item in subsets]


def load_python_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise e


def save_python_object(file_path, obj):
    """Save python object in a file

    Args:
        file_path (_type_): ends with .pkl
    """

    try:
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    except Exception as e:
        raise e


def np_arange_int(start, end, step):
    """Tạo ra dãy số nguyên cách nhau step"""

    return np.arange(start, end + step, step)


def np_arange_float(start, end, step):
    """Tạo ra dãy số thực cách nhau step"""

    return np.arange(start, end, step)


def np_arange(start, end, step):
    """Create numbers from start to end with step, used for both **float** and **int** number <br>
    used for int: start, end, step must be int <br>
    used for float: start must be float <br>
    """

    if is_integer(start) and is_integer(end) and is_integer(step):
        return np_arange_int(int(start), int(end), int(step))

    return np_arange_float(start, end, step)


def get_range_for_param(param_str):
    """Create values range from param_str

    VD:
        param_str = format=start-end-step 12-15-1
        param_str = format=num 12
        param_str = format=start-end start, mean, end vd: 12-15 -> 12 13 15



    """
    if "-" not in param_str:
        if is_integer_str(param_str):
            return [int(param_str)]

        return [float(param_str)]

    if param_str.count("-") == 2:
        nums = param_str.split("-")
        num_min = float(nums[0])
        num_max = float(nums[1])
        num_step = float(nums[2])

        return np_arange(num_min, num_max, num_step)

    nums = param_str.split("-")
    num_min = float(nums[0])
    num_max = float(nums[1])

    num_mean = None
    if is_integer(num_min) and is_integer(num_max):
        num_min = int(num_min)
        num_max = int(num_max)

        num_mean = int((num_min + num_max) / 2)
    else:
        num_mean = (num_min + num_max) / 2

    return [num_min, num_mean, num_max]


def generate_grid_search_params(param_grid: dict):
    """Generate all combinations of params like grid search

    Returns:
        list:
    """

    keys = param_grid.keys()
    values = (param_grid[key] for key in keys)
    return [dict(zip(keys, v)) for v in itertools.product(*values)]


def get_num_de_cac_combinations(list_of_list):
    """Count the number of De cac combinations of list_of_list, which is the list of list"""

    return math.prod(map(len, list_of_list))


def get_features_target_spliter_for_CV_train_val(
    train_features, train_target, val_features, val_target
):
    """Get total features, target, spliter to do GridSearchCV or RandomisedSearchCV with type is **train-val**

    Args:
        train_features (dataframe): _description_
        train_target (dataframe): _description_
        val_features (dataframe): _description_
        val_target (dataframe): _description_
    Returns:
        features, target,       spliter


    """

    features = pd.concat([train_features, val_features], axis=0)
    target = pd.concat([train_target, val_target], axis=0)
    spliter = PredefinedSplit(
        test_fold=[-1] * len(train_features) + [0] * len(val_features)
    )

    return features, target, spliter


def get_features_target_spliter_for_CV_train_train(train_features, train_target):
    """Get total features, target, spliter to do GridSearchCV or RandomisedSearchCV with type is **train-train** <br>
    When you want to train on training set and assess on that training set


    Args:
        train_features (dataframe): _description_
        train_target (dataframe): _description_
        val_features (dataframe): _description_
        val_target (dataframe): _description_
    """

    features = pd.concat([train_features, train_features], axis=0)
    target = pd.concat([train_target, train_target], axis=0)
    spliter = PredefinedSplit(
        test_fold=[-1] * len(train_features) + [0] * len(train_features)
    )

    return features, target, spliter


def read_yaml(path_to_yaml: str) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (Path): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: _description_
    """
    try:
        with open(path_to_yaml, "r", encoding="utf-8") as yaml_file:
            content = yaml.safe_load(yaml_file)
            print(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e


def create_directories(path_to_directories: list, verbose=True):
    """create list of directories

    Args:
        path_to_directories (list): list of path of directories
        verbose (bool, optional): ignore if multiple dirs is to be created. Defaults to True.

    """

    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            print(f"created directory at: {path}")


def save_json(path: Path, data: dict):
    """save json data

    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"json file saved at {path}")


def load_json(path: Path) -> ConfigBox:
    """load json files data

    Args:
        path (Path): path to json file

    Returns:
        ConfigBox: data as class attributes instead of dict
    """
    with open(path) as f:
        content = json.load(f)

    print(f"json file loaded succesfully from: {path}")
    return ConfigBox(content)


def save_bin(data: Any, path: Path):
    """save binary file

    Args:
        data (Any): data to be saved as binary
        path (Path): path to binary file
    """
    joblib.dump(value=data, filename=path)
    print(f"binary file saved at: {path}")


def load_bin(path: Path) -> Any:
    """load binary data

    Args:
        path (Path): path to binary file

    Returns:
        Any: object stored in the file
    """
    data = joblib.load(path)
    print(f"binary file loaded from: {path}")
    return data


def get_size_inKB(path: Path) -> str:
    """get size in KB

    Args:
        path (Path): path of the file

    Returns:
        str: size in KB
    """
    size_in_kb = round(os.path.getsize(path) / 1024)
    return f"~ {size_in_kb} KB"


def decodeImage(imgstring, fileName):
    imgdata = base64.b64decode(imgstring)
    with open(fileName, "wb") as f:
        f.write(imgdata)


def encodeImageIntoBase64(croppedImagePath):
    with open(croppedImagePath, "rb") as f:
        return base64.b64encode(f.read())


def unindent_all_lines(content):
    content = content.strip("\n")
    lines = content.split("\n")
    lines = [item.strip() for item in lines]
    content_processed = "\n".join(lines)

    return content_processed


def insert_br_html_at_the_end_of_line(lines):
    return [f"{item} <br>" for item in lines]


def get_monitor_desc(param_grid_model_desc: dict):
    result = ""

    for key, value in param_grid_model_desc.items():
        key_processed = process_param_name(key)
        line = f"{key_processed}: {value}<br>"
        result += line

    return result


def process_param_name(name):
    """if param name is max_depth -> max

    if param name is C -> C\_\_

    """

    if len(name) == 3:
        return name

    if len(name) > 3:
        return name[:3]

    return name + "_" * (3 - len(name))


def get_param_grid_model(param_grid_model: dict):
    """Get param grid from file params.yaml

    VD:
    In params.yaml
    ```python
    param_grid_model_desc:
      alpha: 0.2-0.7-0.1
      l1_ratio: 0.2-0.4
    ``

    convert to
    ```python
    param_grid = {
        "alpha": np.arange(0.2, 0.7, 0.1)
        "l1_ratio": [0.2, 0.3, 0.4]
    }
    ```
    """

    values = param_grid_model.values()

    values = [get_range_for_param(str(item)) for item in values]

    return dict(zip(list(param_grid_model.keys()), values))


def sub_param_for_yaml_file(src_path: str, des_path: str, replace_dict: dict):
    """Substitue params in src_path and save in des_path

    Args:
        replace_dict (dict): key: item needed to replace, value: item to replace
        VD:
        ```python
        replace_dict = {
            "${P}": data_transformation,
            "${T}": model_name,
            "${E}": evaluation,
        }

        ```
    """

    with open(src_path, "r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)

    config_str = yaml.dump(config_data, default_flow_style=False)

    for key, value in replace_dict.items():
        config_str = config_str.replace(key, value)

    with open(des_path, "w", encoding="utf-8") as file:
        file.write(config_str)

    print(f"Đã thay thế các tham số trong {src_path} lưu vào {des_path}")


def get_real_column_name(column):
    """After using ColumnTransformer, the column name has format = bla__Age, so only take Age"""

    start_index = column.find("__") + 2
    column = column[start_index:]
    return column


def get_real_column_name_from_get_feature_names_out(columns):
    """Take the exact name from the list retrieved by method get_feature_names_out() of ColumnTransformer"""

    return [get_real_column_name(item) for item in columns]


def fix_name_by_LGBM_standard(cols):
    """LGBM standard state that columns name can only contain characters among letters, digit and '_'

    Returns:
        list: _description_
    """

    cols = pd.Series(cols)
    cols = cols.str.replace(r"[^A-Za-z0-9_]", "_", regex=True)
    return list(cols)


def find_feature_importances(train_data, model):
    """Find the feature importances of some models like: RF, GD, SGD, LGBM

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": model.feature_importances_,
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_coef_with_classifier(train_data, model):
    """Find the feature importances of some models like: LR1, LRe

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": np.abs(model.coef_[0]),
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_coef_with_regressor(train_data, model):
    """Find the feature importances of some models like: ElasticNet, Lasso

    Returns:
        pd.DataFrame:
    """

    score = pd.DataFrame(
        data={
            "feature": train_data.columns.tolist(),
            "score": np.abs(model.coef_),
        }
    )
    score = score.sort_values(by="score", ascending=False)
    return score


def find_best_n_components_of_PCA(
    train_features,
    train_target,
    val_features,
    val_target,
    placeholdout_model,
    list_n_components,
    scoring="accuracy",
):
    """Find best n_components of PCA

    Args:
        placeholdout_model (_type_): model like LR, XGB, ... without hyperparameters except random_state
        list_n_components (_type_): list of n_components used
        scoring (str, optional): scoring. Defaults to "accuracy".

    Returns:
        _type_: best n_components
    """
    features, target, splitter = get_features_target_spliter_for_CV_train_val(
        train_features, train_target, val_features, val_target
    )
    param_grid = {"1__n_components": list_n_components}
    pp = Pipeline(
        steps=[
            ("1", PCA(random_state=42)),
            ("2", placeholdout_model),
        ]
    )
    gs = GridSearchCV(pp, param_grid=param_grid, cv=splitter, scoring=scoring)
    gs.fit(features, target)
    return gs.best_params_


def find_feature_score_by_permutation_importance(
    train_features, train_target, fitted_model
):
    """Find the feature score by doing permutation_importance

    Args:
        fitted_model (_type_): fitted model, not base model

    Returns:
        DataFrame: _description_
    """
    result = permutation_importance(
        fitted_model, train_features, train_target, n_repeats=10, random_state=42
    )
    result_df = pd.DataFrame(
        data={
            "feature": train_features.columns.tolist(),
            "score": result.importances_mean * 100,
        }
    )
    result_df = result_df.sort_values(by="score", ascending=False)
    return result_df


def get_params_transform_list_to_1_value(param_grid):
    """Create params with key and one value not a list with one value

    Args:
        param_grid (_type_): value is a list with only one value

    Returns:
        dict: _description_

    VD:
    ```python
    param_grid = {
    "C": [1],
    "A": [2],
    }

    Convert to

    param_grid = {
    "C": 1,
    "A": 2,
    }
    ```
    """

    values = [item[0] for item in param_grid.values()]
    return dict(zip(param_grid.keys(), values))


def get_describe_stats_for_numeric_cat_cols(data):
    """Get descriptive statistics of numeric cat cols, including min, max, median

    Args:
        data (_type_): numeric cat cols
    Returns:
        Dataframe: min, max, median
    """

    min_of_cols = data.min().to_frame(name="min")
    max_of_cols = data.max().to_frame(name="max")
    median_of_cols = data.quantile([0.5]).T.rename(columns={0.5: "median"})

    result = pd.concat([min_of_cols, max_of_cols, median_of_cols], axis=1).T

    return result


def do_list_subtraction_3(a: list, b: list):
    """Thực hiện trừ a cho b

    Ở đây hay hơn dùng phép trừ trong set, vì hàm này giúp bảo tồn vị trí các phần tử trong list **a** sau khi trừ

    ```python
    a = ['z', 'a', 'b', 'c']
    b = ['b']
    c= do_list_subtraction_3(a, b)
    print(c) -> ['z', 'a', 'c']
    ```


    """

    # Sử dụng Counter để đếm các phần tử trong a và b
    a_counter = Counter(a)
    b_counter = Counter(b)

    # Loại bỏ các phần tử trong b từ a
    result = list((a_counter - b_counter).elements())

    return result


def get_different_types_cols_from_df_4(df: pd.DataFrame):
    """Tìm các cột kiểu numeric, numericCat, cat, binary, nominal, ordinal  target từ df

    Lưu ý: có tìm luôn cột **target**

    Returns:
        (numeric_cols, numericCat_cols, cat_cols, binary_cols, nominal_cols, ordinal_cols, target_col):
    """

    cols = pd.Series(df.columns)
    numeric_cols = cols[cols.str.endswith("num")].tolist()
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols
    target_col = cols[cols.str.endswith("target")].tolist()[0]

    return (
        numeric_cols,
        numericCat_cols,
        cat_cols,
        binary_cols,
        nominal_cols,
        ordinal_cols,
        target_col,
    )


def get_object_from_string_using_eval_6(text: str, module):
    """Get đối tượng từ 1 chuối

    Example:
        text = 'LogisticRegression(C=144,penalty="l1",solver="saga",max_iter=10000,dual=True)' -> các chuỗi phải được bọc trong cặp ""

        module = sklearn.linear_model

        -> đối tượng LogisticRegression(C=144, dual=True, max_iter=10000, penalty='l1',solver='saga')

    Args:
        text (str): _description_


    """

    # Tách tên lớp và tham số
    class_name, params = text.split("(", 1)
    params = params.rstrip(")")

    class_name = getattr(module, class_name)

    # Tạo đối tượng bằng eval (không khuyến khích nếu có dữ liệu không đáng tin cậy)
    return eval(f"class_name({params})")


# def plot_many_lines_on_1plane_7(
#     df: pd.DataFrame,
#     id_var: str,
#     value_vars: list,
#     color_value_vars: list,
#     xaxis_title=None,
#     yaxis_title=None,
# ):
#     """Vẽ biểu đồ multiple lines

#     Examples:
#         |Ngày | Hạng A | Hạng B |
#         |---|---|---|
#         |1|15|16|
#         |2|10|20|
#         |3|20|40|
#         |4|30|90|

#         Khi đó vẽ biểu đồ thể hiện doanh thu các hạng theo từng ngày

#         ```python
#         plot_many_lines_on_1plane_7(df, 'Ngày', ['Hạng A','Hạng B'], ['blue', 'gray'])
#         ```


#     Args:
#         df (pd.DataFrame): Dữ liệu chứa các cột cần vẽ
#         id_var (str): Tên cột mà sẽ ở trục **x**
#         value_vars (list): Tên các cột sẽ hiện thành đường
#         color_value_vars (list): Màu ứng với các đường
#         xaxis_title (list): Title cho trục x
#         yaxis_title (list): Title cho trục y

#     Returns:
#         _type_: Đối tượng **fig** để sau này lưu file, ...
#     """

#     # Chuyển đổi dữ liệu từ wide format sang long format
#     df_long = df.melt(
#         id_vars=[id_var], value_vars=value_vars, var_name="Category", value_name="y"
#     )

#     fig = px.line(
#         df_long,
#         x=id_var,
#         y="y",
#         color="Category",
#         markers=True,
#         color_discrete_map=dict(zip(value_vars, color_value_vars)),
#     )

#     xaxis_title = id_var if xaxis_title is None else xaxis_title
#     yaxis_title = "y" if yaxis_title is None else yaxis_title

#     fig.update_layout(
#         xaxis_title=xaxis_title,
#         yaxis_title=yaxis_title,
#     )

#     print("Đã cập nhật")

#     return fig


# def plot_grouped_bar_chart_8(
#     df: pd.DataFrame,
#     id_var,
#     value_vars,
#     xaxis_title=None,
#     yaxis_title=None,
# ):
#     """Vẽ biểu đồ grouped bar chart

#     Examples:
#         |Ngày | Hạng A | Hạng B |
#         |---|---|---|
#         |1|15|16|
#         |2|10|20|
#         |3|20|40|
#         |4|30|90|

#         Khi đó vẽ biểu đồ thể hiện doanh thu các hạng theo từng ngày, mỗi ngày sẽ có 2 cột ứng với 2 hạng A, B

#         ```python
#         plot_grouped_bar_chart_8(df, 'Ngày', ['Hạng A','Hạng B'])
#         ```


#     Args:
#         df (pd.DataFrame): Dữ liệu chứa các cột cần vẽ
#         id_var (str): Tên cột mà sẽ ở trục **x**
#         value_vars (list): Tên các cột sẽ hiện thành đường
#         xaxis_title (list): Title cho trục x
#         yaxis_title (list): Title cho trục y

#     Returns:
#         _type_: Đối tượng **fig** để sau này lưu file, ...
#     """
#     # Chuyển đổi dữ liệu sang định dạng dài (long format)
#     data_melted = df.melt(
#         id_vars=[id_var],
#         value_vars=value_vars,
#         var_name="Category",
#         value_name="y",
#     )

#     # Vẽ Grouped Bar Chart
#     fig = px.bar(
#         data_melted,
#         x=id_var,
#         y="y",
#         color="Category",  # Màu sắc theo năm
#         barmode="group",  # Hiển thị dạng cột nhóm
#     )

#     xaxis_title = id_var if xaxis_title is None else xaxis_title
#     yaxis_title = "y" if yaxis_title is None else yaxis_title

#     fig.update_layout(
#         xaxis_title=xaxis_title,
#         yaxis_title=yaxis_title,
#     )

#     return fig


# def plot_radar_chart_9(categories: list, values: list):
#     """Vẽ radar chart

#     Examples:
#     ```python
#     categories = ['Kỹ năng A', 'Kỹ năng B', 'Kỹ năng C', 'Kỹ năng D', 'Kỹ năng E']
#     values = [80, 90, 70, 85, 60]
#     ```

#     Returns:
#         _type_: Đối tượng **fig**
#     """

#     values += values[:1]
#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatterpolar(
#             r=values,
#             theta=categories,
#             fill="toself",
#         )
#     )
#     fig.update_layout(
#         polar=dict(
#             radialaxis=dict(
#                 visible=True, range=[0, 100]
#             )  # Hiển thị trục và đặt giới hạn
#         ),
#     )

#     return fig


# def plot_full100percent_area_chart_10(df: pd.DataFrame, time_col, group, value):
#     """Vẽ biểu đồ full 100% area chart

#     Examples:
#     ```python
#     data = pd.DataFrame({
#         "Thời gian": ["Q1", "Q2", "Q3", "Q4"] * 3,
#         "Nhóm": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
#         "Giá trị": np.random.randint(10, 100, 12)
#     })
#     ```

#     Vẽ biểu đồ miền thể hiện tỉ trọng của từng **Nhóm** qua từng **Thời gian** (Các quý Q1, Q2, ...)

#     ```python
#     plot_full100percent_area_chart(data, "Thời gian", "Nhóm", "Giá trị")
#     ```


#     Args:
#         df (pd.DataFrame): _description_
#         time_col (_type_): Tên cột ở trục x, thông thường là thời gian
#         group (_type_): Tên cột chứa category được chia ra trong biểu đồ
#         value (_type_): Tên cột giá trị

#     Returns:
#         _type_: Đối tượng **fig**
#     """

#     # Tính tổng ứng với mỗi điểm trục X
#     data_grouped = df.groupby(time_col)[value].transform("sum")

#     # Tính tỷ lệ phần trăm cho từng nhóm
#     df["percent"] = (df[value] / data_grouped) * 100

#     # Vẽ Full 100% Area Chart
#     fig = px.area(
#         df,
#         x=time_col,
#         y="percent",
#         color=group,
#     )

#     return fig


def show_img_11(img_path):
    """Show ảnh lên

    Args:
        img_path (str): đường dẫn đến file
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    img = mpimg.imread(img_path)
    ax.imshow(img)
    ax.axis("off")


def convert_numpy_image_array_to_jpg_files_12(
    numpy_array: np.ndarray, folder_path: str
):
    """Chuyển đổi mảng numpy (trước đó đã từng chuyển ảnh sang) về lại file ảnh và lưu trong 1 thư mục **folder_path**

    Args:
        numpy_array (np.ndarray): các giá trị từ **0 -> 255**,  shape = (n, height, width, channels), với n là số lượng ảnh
        folder_path (str): đường dẫn thư mục
    """

    for idx, image_array in enumerate(numpy_array):
        image = Image.fromarray(image_array.astype("uint8"))

        image.save(f"{folder_path}/image_{idx}.jpg")


def get_different_types_feature_cols_from_df_14(df: pd.DataFrame):
    """Tìm các cột kiểu numeric, numericCat, cat, binary, nominal, ordinal từ df

    Lưu ý: Chỉ các cột **feature** không có cột **target**
    Returns:
        (numeric_cols, numericCat_cols, cat_cols, binary_cols, nominal_cols, ordinal_cols):
    """
    cols = pd.Series(df.columns)
    numeric_cols = cols[cols.str.endswith("num")].tolist()
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols

    return (
        numeric_cols,
        numericCat_cols,
        cat_cols,
        binary_cols,
        nominal_cols,
        ordinal_cols,
    )


def evaluate_model_on_one_scoring_17(model, feature, target, scoring):
    if scoring == "accuracy":
        prediction = model.predict(feature)
        return metrics.accuracy_score(target, prediction)

    if scoring == "log_loss":
        prediction = model.predict_proba(feature)
        return metrics.log_loss(target, prediction)

    if scoring == "mse":
        prediction = model.predict(feature)
        return np.sqrt(metrics.mean_squared_error(target, prediction))

    if scoring == "mae":
        prediction = model.predict(feature)
        return metrics.mean_absolute_error(target, prediction)

    raise ValueError(
        "===== Chỉ mới định nghĩa cho accuracy, log_loss, mse, mae =============="
    )


def get_classification_report_18(model, feature, target, class_names: list):
    """Tạo classfication report cho classifier"""
    class_names = np.asarray(class_names)

    target = [int(item) for item in target]
    target = class_names[target]

    prediction = model.predict(feature)
    prediction = [int(item) for item in prediction]
    prediction = class_names[prediction]

    return metrics.classification_report(target, prediction)


def find_best_model_train_val_scoring_when_using_RandomisedSearch_GridSearch_19(
    cv_results, scoring
):
    """Tìm chỉ số train-val cho mô hình tốt nhất sau khi sử dụng RandomisedSearch hoặc GridSearch

    Args:
        cv_results (_type_): Kết quả từ searcher
        scoring (_type_): Chỉ tiêu đánh giá

    Returns:
        (train_scoring, val_scoring):
    """
    cv_results = zip(cv_results["mean_test_score"], cv_results["mean_train_score"])
    cv_results = sorted(cv_results, key=lambda x: x[0], reverse=True)
    val_scoring, train_scoring = cv_results[0]

    if scoring in SCORINGS_PREFER_MININUM:
        val_scoring, train_scoring = (
            -val_scoring,
            -train_scoring,
        )

    return train_scoring, val_scoring


def convert_list_string_to_list_object_20(list_string: list):
    """Chuyển list chuỗi thành list object tương ứng

    Args:
        list_string (list):

    """
    return [convert_string_to_object_4(item) for item in list_string]


def get_classification_report_for_DLmodel_21(model, ds, class_names, batch_size):
    """Get classification_report cho DL model

    Args:
        model (_type_): _description_
        ds (_type_): _description_
        class_names (_type_): _description_
        batch_size (_type_): _description_

    """
    y_true = []
    y_pred = []

    class_names = np.asarray(class_names)

    # Lặp qua các batch trong train_ds
    for images, labels in ds:
        # Dự đoán bằng mô hình
        predictions = model.predict(images, batch_size=batch_size, verbose=0)

        y_pred_batch = class_names[np.argmax(predictions, axis=-1)].tolist()
        y_true_batch = class_names[np.asarray(labels)].tolist()
        y_true += y_true_batch
        y_pred += y_pred_batch

    return metrics.classification_report(y_true, y_pred)


def plot_train_val_metric_per_epoch_for_DLtraining_22(history, metric):
    """Vẽ biểu đồ train-val metric theo từng epoch của Deep Learning model

    Args:
        history (_type_): _description_
        metric (_type_): Chỉ số cần vẽ, vd: loss, accuracy, mse, ...

    Returns:
        fig: _description_
    """
    num_epochs = len(history["loss"])
    epochs = range(1, num_epochs + 1)
    epochs = [str(i) for i in epochs]

    fig, ax = plt.subplots()
    ax.plot(epochs, history[metric], color="gray", label=metric)
    ax.plot(epochs, history["val_" + metric], color="blue", label="val_" + metric)
    ax.set_ylim(bottom=0)

    return fig


def split_classification_folder_23(
    src_dir: str, dest_dir: str, categories: list, dest_size=0.2
):
    """Chia classfication thư mục thành thư mục có size = **dest_size**

    Thư mục classfication có dạng sau:
    ```python
    train/
    ......pos/
    ......neg/
    ```

    Args:
        src_dir (str): Path thư mục nguồn
        dest_dir (str): Path thư mục đích
        categories (list): Các labels
        dest_size (float, optional): . Defaults to 0.2.
    """
    for category in categories:
        os.makedirs(os.path.join(dest_dir, category))
        files = os.listdir(os.path.join(dest_dir, category))
        random.Random(1337).shuffle(files)

        num_dest_samples = int(dest_size * len(files))
        dest_files = files[:num_dest_samples]
        for file_name in dest_files:
            shutil.move(
                os.path.join(src_dir, category, file_name),
                os.path.join(dest_dir, category, file_name),
            )


def get_target_col_from_df_26(df):
    """Get cột target từ df
    Returns:
        target_col: _description_
    """

    cols = pd.Series(df.columns)
    target_col = cols[cols.str.endswith("target")].tolist()[0]
    return target_col


def get_feature_cols_and_target_col_from_df_27(df):
    """Get các cột feature và cột target từ df

    Returns:
        (feature_cols, target_col): _description_
    """
    cols = pd.Series(df.columns)
    target_col = cols[cols.str.endswith("target")]
    feature_cols = cols.drop(target_col.index).tolist()
    target_col = target_col.tolist()[0]

    return feature_cols, target_col


def get_value_with_the_meaning_28(scores: tuple, scoring):
    """Get chỉ số theo ý nghĩa

    Nếu scoring = 'accuracy' thì phải nhân cho 100 mới đúng ý nghĩa

    Examples:
    ```python
    a= 0.34
    b = 0.45
    c, d = get_value_with_the_meaning((a,b), 'accuracy')
    ```

    Args:
        scores (tuple): tuple các chỉ số cần điều chỉnh
        scoring (str): Tên chỉ số

    Returns:
        scores: _description_
    """
    if scoring == "accuracy":
        scores = (item * 100 for item in scores)

    return scores


def get_confusion_matrix_heatmap_29(model, feature, target, class_names: list):
    """Vẽ confustion matrix heatmap

    Returns:
        fig: _description_
    """
    class_names = np.asarray(class_names)

    target = [int(item) for item in target]
    target = class_names[target]

    prediction = model.predict(feature)
    prediction = [int(item) for item in prediction]
    prediction = class_names[prediction]

    labels = np.unique(target)
    cm = metrics.confusion_matrix(target, prediction, labels=labels)
    np.fill_diagonal(cm, 0)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        cbar=True,
        annot=True,
        cmap="YlOrRd",
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
    )

    return fig


def get_heatmap_for_confusion_matrix_30(confusion_matrix, labels):
    """Get heatmap cho confusion matrix

    Returns:
        fig: đối tượng chart
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        confusion_matrix,
        cbar=True,
        annot=True,
        cmap="YlOrRd",
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
    )

    return fig


def get_model_desc_for_CustomStackingClassifier_31(model_desc: dict):
    res = f"class_name: {model_desc['class_name']}\n"
    res += "estimators:\n"
    space = "   "
    for item in model_desc["estimators"]:
        res += f"{space}- {item}\n"
    res += f"final_estimator: {model_desc['final_estimator']}"
    return res


def get_model_desc_for_model_32(model_desc):
    if isinstance(model_desc, dict):
        return get_model_desc_for_CustomStackingClassifier_31(model_desc)

    return model_desc


def replace_in_category_series_33(series, replace_value_list: list):
    """Replace giá trị trong các cột kiểu category"""
    series = series.astype("string")

    new_replace_value_list = [
        [item[0], [item[1]] * len(item[0])] for item in replace_value_list
    ]
    replace_value_dict_keys = itertools.chain(
        *[item[0] for item in new_replace_value_list]
    )
    replace_value_dict_values = itertools.chain(
        *[item[1] for item in new_replace_value_list]
    )
    replace_value_dict = dict(zip(replace_value_dict_keys, replace_value_dict_values))
    series = series.replace(replace_value_dict)
    series = series.astype("category")
    return series


def replace_outliers_with_new_value_34(series, new_value):
    """Thay thế các outliers trong 1 series thành giá trị mới"""
    lb, ub = get_lower_and_upper_bound_of_series(series)
    series[series.index[(series < lb) | (series > ub)]] = new_value
    return series


def get_label_percent_in_categorical_column_35(series):
    """Phần trăm các label trong cột categorical"""
    return series.value_counts() / len(series) * 100


def get_correlation_between_numeric_cols_36(df, numeric_cols):
    """Get hệ số tương quan của các cột numeric

    Returns:
        df: item0, item1, correlation
    """
    combinations_2 = list(itertools.combinations(numeric_cols, 2))
    res = [np.abs(df[item[0]].corr(df[item[1]])) for item in combinations_2]

    res = pd.Series(res, index=combinations_2)
    res = res.sort_values(ascending=False)

    # TODO: d
    print(f"Kết quả là: {res}")
    # d

    return res


def get_correlation_between_numeric_features_and_numeric_target_37(
    df, numeric_cols, target_col
):
    correlations = [np.abs(df[col].corr(df[target_col])) for col in numeric_cols]
    res = pd.Series(correlations, index=numeric_cols)
    res = res.sort_values(ascending=False)


def plot_hist_box_violin_plots_for_numeric_cols_37(df, numeric_cols):
    """Vẽ hist, boxplot, violin cho các cột số trong df

    Returns:
        fig: _description_
    """
    subplot_titles = sum(([item, "", ""] for item in numeric_cols), [])

    fig = make_subplots(rows=len(numeric_cols), cols=3, subplot_titles=subplot_titles)

    for row, col in enumerate(numeric_cols, 1):
        data = df[col]

        # Vẽ Histogram
        fig_hist = px.histogram(
            x=data,
            nbins=100,
        )

        # Thêm đường viền cho các cột histogram
        fig_hist.update_traces(marker=dict(line=dict(width=1, color="black")))

        # Vẽ box plot
        fig_box = px.box(
            y=data,
        )

        # Vẽ violin plot
        fig_violin = px.violin(
            y=data,
            box=True,
        )

        fig.add_trace(fig_hist.data[0], row=row, col=1)
        fig.add_trace(fig_box.data[0], row=row, col=2)
        fig.add_trace(fig_violin.data[0], row=row, col=3)

    fig.update_layout(
        width=300 * 3,  # Độ rộng biểu đồ (px)
        height=len(numeric_cols) * 400,  # Độ cao biểu đồ (px)
    )

    return fig


def plot_label_percent_for_categorical_cols_38(cat_cols, df):
    """Vẽ phần trăm các label trong các cột categorical

    Returns:
        fig: _description_
    """
    fig = make_subplots(rows=len(cat_cols), cols=1, subplot_titles=cat_cols)

    for row, col in enumerate(cat_cols, 1):
        data = df[col]

        # Vẽ phân phối các label
        label_percent = data.value_counts() / len(data) * 100
        fig_bar = px.bar(x=label_percent.values, y=label_percent.index, orientation="h")

        fig.add_trace(fig_bar.data[0], row=row, col=1)

    fig.update_layout(
        width=300,  # Độ rộng biểu đồ (px)
        height=len(cat_cols) * 400,  # Độ cao biểu đồ (px)
    )

    return fig


def do_chi_square_test_for_2_variables_39(df, cat_col1, cat_col2):
    """Thực hiện kiểm định chi square cho 2 biến categorical trong df

    Args:
        df (_type_):
        cat_col1 (_type_): cột thứ 1
        cat_col2 (_type_): cột thứ 2

    Returns:
        p_value: Giá trị p_value của kiểm định
    """
    table = df.groupby([cat_col1, cat_col2]).size().unstack()
    return chi2_contingency(table.values)[1]


def do_chi_square_test_for_categorical_cols_40(df, cat_cols):
    """Thực hiện kiểm định cho các cột categoricals trong df

    Args:
        df (_type_): _description_
        cat_cols (_type_): tên các cột categorical

    Returns:
        df: Gồm có 3 cột, item0, item1, p_value
    """
    combinations_2 = list(itertools.combinations(cat_cols, 2))
    list_p_value = [
        do_chi_square_test_for_2_variables_39(df, item[0], item[1])
        for item in combinations_2
    ]
    res = pd.Series(list_p_value, index=combinations_2)

    # list_item0, list_item1, list_pvalue = zip(*combinations_2)
    # res = pd.DataFrame(
    #     data={
    #         "item0": list_item0,
    #         "item1": list_item1,
    #         "p_value": list_pvalue,
    #     }
    # )
    res = res.sort_values(ascending=True)

    return res


def do_chi_square_test_between_categorical_cols_and_target_col_41(
    df, cat_cols, target_col
):
    list_p_value = [
        do_chi_square_test_for_2_variables_39(df, col, target_col) for col in cat_cols
    ]

    res = pd.Series(list_p_value, index=cat_cols)
    res = res.sort_values(ascending=True)
    return res


def get_outlier_percent_of_numeric_cols_42(df, numeric_cols):
    """Get phần trăm các outlier ở trong các cột numeric

    Returns:
        series:
    """
    list_outlier_percent = []
    for col in numeric_cols:
        lb, ub = get_lower_and_upper_bound_of_series(df[col])
        count_outlier = np.sum((df[col] < lb) | (df[col] > ub))
        outlier_percent = count_outlier / len(df[col]) * 100
        list_outlier_percent.append(outlier_percent)

    res = pd.Series(list_outlier_percent, index=numeric_cols)
    res = res.sort_values(ascending=False)
    return res


def test_relation_between_cat_col_and_numeric_col_43(df, cat_col, numeric_col):
    """Test mức độ ảnh hưởng của 1 biến categorical đến biến numeric target

    Args:
        df (_type_): _description_
        cat_col (_type_): _description_
        target_col (_type_): Phải là biến numeric !!!!!

    Returns:
        p_value: _description_
    """
    data = df.groupby(cat_col)[numeric_col].apply(list)
    p_value = stats.kruskal(*list(data.values)).pvalue
    return p_value


def test_relation_between_numeric_features_and_cat_target_44(
    df, numeric_cols, target_col
):
    """Kiểm định mức độ ảnh hưởng của các biến numeric đến biến target phân loại

    Args:
        df (_type_): _description_
        numeric_cols (_type_): _description_
        target_col (_type_): Phải là biến phân loại

    Returns:
        series: _description_
    """
    list_p_value = [
        test_relation_between_cat_col_and_numeric_col_43(df, target_col, col)
        for col in numeric_cols
    ]
    res = pd.Series(list_p_value, index=numeric_cols)
    res = res.sort_values(ascending=True)
    return res


def get_skew_on_numeric_cols_44(df, numeric_cols):
    """Get hệ số skew của các cột numeric


    Returns:
        series: _description_
    """
    list_skew = [np.abs(stats.skew(df[col])) for col in numeric_cols]
    res = pd.Series(list_skew, index=numeric_cols)
    res = res.sort_values(ascending=False)
    return res


def do_kbest_feature_selection_for_classification_45(transformed_features, target):
    """Thực hiện select kbest choa bài toán classification

    Args:
        transformed_features (_type_): **Phải được transformed trước**
        target (_type_): _description_

    Returns:
        series: _description_
    """
    # Khởi tạo selector
    selector = SelectKBest(score_func=mutual_info_classif, k="all")  # Classification

    # Fit cái đã
    selector.fit(transformed_features, target)  # features phải được transformed trước

    # Ghi lại kết quả điểm số
    res = pd.Series(selector.scores_, index=transformed_features.columns)
    res = res.sort_values(ascending=False)
    return res


def do_kbest_feature_selection_for_regression_46(transformed_features, target):
    """Thực hiện select kbest choa bài toán regression

    Args:
        transformed_features (_type_): **Phải được transformed trước**
        target (_type_): _description_

    Returns:
        series: _description_
    """
    # Khởi tạo selector
    selector = SelectKBest(score_func=mutual_info_regression, k="all")  # Regression

    # Fit cái đã
    selector.fit(transformed_features, target)  # features phải được transformed trước

    # Ghi lại kết quả điểm số
    res = pd.Series(selector.scores_, index=transformed_features.columns)
    res = res.sort_values(ascending=False)
    return res


def find_silhouette_score_for_each_param_for_DBSCAN_47(features, list_param):
    """Get chỉ số silhouette_score cho từng cặp tham số của DBSCAN

    Args:
        features (_type_): dữ liệu các đặc trưng
        list_param (_type_): list các tuple dạng (eps, min_samples)

    Returns:
        series: _description_
    """
    scores = []

    for param in list_param:
        eps, min_samples = param
        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(features)

        # Tính silhouette score chỉ khi có ít nhất 2 cụm
        score = silhouette_score(features, labels) if len(set(labels)) > 1 else None
        scores.append(score)

    res = pd.Series(scores, index=list_param)
    res = res.sort_values(ascending=False)
    return res


def get_noise_sample_by_DBSCAN_48(features, dbscan_model):
    """Tìm các điểm noise bằng thuật toán DBSCAN

    Args:
        features (_type_): _description_
        dbscan_model (_type_): _description_

    Returns:
        df: _description_
    """
    labels = dbscan_model.fit_predict(features)
    res = features[labels == -1, :]
    return res


def get_cat_cols_from_df_49(df):
    """Get các cột categorical"""
    cols = pd.Series(df.columns)
    binary_cols = cols[cols.str.endswith("bin")].tolist()
    nominal_cols = cols[cols.str.endswith("nom")].tolist()
    ordinal_cols = cols[cols.str.endswith("ord")].tolist()
    cat_cols = binary_cols + nominal_cols + ordinal_cols

    return cat_cols


def get_numericcat_cols_from_df_50(df):
    """Get numericcat cột"""
    cols = pd.Series(df.columns)
    numericCat_cols = cols[cols.str.endswith("numcat")].tolist()

    return numericCat_cols


def get_min_max_of_numeric_cols_51(df, numeric_cols):
    """Get giá trị min, max của các cột numeric

    Returns:
        df: _description_
    """
    return df[numeric_cols].describe().loc[["min", "max"]].T


def get_model_from_yaml_52(yaml):
    """Get model từ yaml gồm model + index của model <br>

    Có các dạng sau:

    1.
    ```
    XGBClassifier(n_estimators=300,max_depth=40)|0
    ```

    2.
    ```
    class_name: CustomStackingClassifier|0
    estimators:
        - LogisticRegression(C = 0.1)
        - GaussianNB(var_smoothing=1e-8)
        - SGDClassifier(alpha=10, loss='log_loss')
    final_estimator: LogisticRegression(C = 0.1)
    ```

    Returns:
        (model, model_index): _description_
    """
    if isinstance(yaml, dict):
        model_index = yaml["class_name"].split("|")[1]
        yaml["class_name"] = yaml["class_name"].split("|")[0]
        model = stringToObjectConverter.convert_MLmodel_yaml_to_object(yaml)

        return model, model_index

    model_index = yaml.split("|")[1]
    model = stringToObjectConverter.convert_MLmodel_yaml_to_object(yaml.split("|")[0])
    return model, model_index


def get_models_from_yaml_52(yaml: list):
    """Get các models từ yaml, gồm có  model và index của model, có dạng sau:

    ```
    - LogisticRegression(C = 0.1)|0
    -
        class_name: CustomStackingClassifier|1
        estimators:
            - LogisticRegression(C = 0.1)
            - GaussianNB(var_smoothing=1e-8)
            - SGDClassifier(alpha=10, loss='log_loss')
        final_estimator: LogisticRegression(C = 0.1)
    ```


    Returns:
        (models, model_indices): _description_
    """
    a = [get_model_from_yaml_52(item) for item in yaml]
    models, model_indices = zip(*a)
    return list(models), list(model_indices)


def fit_model_incremental_53(model, i, feature, target):
    """Fit model theo kiểu train từng batch

    Args:
        model (_type_): _description_
        i (_type_): lần train này là thứ mấy, thứ 2 trở đi thì phải khác
        feature (_type_): _description_
        target (_type_): _description_
    """
    if isinstance(model, XGBClassifier):
        if i == 0:
            model.fit(feature, target)
        else:
            model.fit(feature, target, xgb_model=model.get_booster())

        return

    if isinstance(model, LGBMClassifier):
        if i == 0:
            model.fit(feature, target)
        else:
            model.fit(feature, target, init_model=model.booster_)

        return

    if isinstance(model, CustomStackingClassifier):
        if i == 0:
            model.fit(feature, target)
        else:
            model.fit_on_batches(feature, target, i)

        return

    if isinstance(model, RandomForestClassifier):
        if i == 0:
            model.fit(feature, target)
        else:
            model.n_estimators += 50
            model.fit(feature, target)

        return

    if isinstance(model, ExtraTreesClassifier):
        if i == 0:
            model.fit(feature, target)
        else:
            model.n_estimators += 50
            model.fit(feature, target)

        return

    model.fit(feature, target)


def get_numeric_cols_from_df_54(df):
    """Get numeric cột"""
    cols = pd.Series(df.columns)
    res = cols[cols.str.endswith("num")].tolist()

    return res
