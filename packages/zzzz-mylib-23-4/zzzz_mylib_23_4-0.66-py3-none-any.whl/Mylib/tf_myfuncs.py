import tensorflow as tf
import pandas as pd


def split_tfdataset_into_tranvaltest_1(
    ds: tf.data.Dataset,
    train_size=0.8,
    val_size=0.1,
    shuffle=True,
    shuffle_size=10000,
):
    """Chia dataset thành tập train, val, test theo tỉ lệ nhất định

    Args:
        ds (tf.data.Dataset): _description_
        train_size (float, optional): _description_. Defaults to 0.8.
        val_size (float, optional): _description_. Defaults to 0.1.
        shuffle (bool, optional): _description_. Defaults to True.
        shuffle_size (int, optional): _description_. Defaults to 10000.

    Returns:
        train, val, test
    """
    ds_size = len(ds)

    if shuffle:
        ds = ds.shuffle(shuffle_size, seed=42)

    train_size = int(train_size * ds_size)
    val_size = int(val_size * ds_size)

    train_ds = ds.take(train_size)
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)

    return train_ds, val_ds, test_ds


def cache_prefetch_tfdataset_2(ds: tf.data.Dataset, shuffle_size=1000):
    return ds.cache().shuffle(shuffle_size).prefetch(buffer_size=tf.data.AUTOTUNE)


def train_test_split_tfdataset_3(
    ds: tf.data.Dataset, test_size=0.2, shuffle=True, shuffle_size=10000
):
    """Chia dataset thành tập train, test theo tỉ lệ của tập test

    Returns:
        _type_: train_ds, test_ds
    """
    ds_size = len(ds)

    if shuffle:
        ds = ds.shuffle(shuffle_size, seed=42)

    test_size = int(test_size * ds_size)

    test_ds = ds.take(test_size)
    train_ds = ds.skip(test_size)

    return train_ds, test_ds


def convert_pdDataframe_to_tfDataset_13(
    df: pd.DataFrame, target_col: str, batch_size: int
):
    """Chuyển pd.Dataframe thành tf.Dataset có chia sẵn các batch, phục vụ cho sử dụng Deep learning đối với dữ liệu đầu vào dạng bảng
    Args:
        df (pd.DataFrame): bảng
        target_col (str): tên cột mục tiêu
        batch_size (int):

    Returns:
        dataset:
    """
    # Tách các đặc trưng và nhãn mục tiêu
    features = df.drop(columns=[target_col]).values
    target = df[target_col].values

    # Tạo tf.data.Dataset từ các đặc trưng và nhãn
    dataset = tf.data.Dataset.from_tensor_slices((features, target))

    # Phân batch với batch_size=2
    dataset = dataset.batch(batch_size)

    return dataset
