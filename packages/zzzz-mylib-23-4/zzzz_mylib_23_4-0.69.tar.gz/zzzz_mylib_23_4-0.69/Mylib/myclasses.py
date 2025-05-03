import pandas as pd
import numpy as np
import matplotlib.cm as cm
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from Mylib import myfuncs
from sklearn import metrics
import os
from sklearn.decomposition import IncrementalPCA, KernelPCA
from sklearn.manifold import LocallyLinearEmbedding


class ColumnsDeleter(BaseEstimator, TransformerMixin):
    """Xóa cột

    Attributes:
        columns: tên các cột cần xóa
    """

    def __init__(self, columns) -> None:
        super().__init__()
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):

        X = X.drop(columns=self.columns)

        self.cols = X.columns.tolist()
        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.cols


class ClassifierEvaluator:
    """Đánh giá model cho tập train-val hoặc tập test cho bài toán classification

    Hàm chính:
    - evaluate():

    Lưu ý:
    - KHi đánh giá 1 tập (vd: đánh giá tập test) thì truyền cho train_feature_data, train_target_data, còn val_feature_data và val_target_data **bỏ trống**

    Attributes:
        model (_type_):
        class_names (_type_): Các label
        train_feature_data (_type_):
        train_target_data (_type_):
        val_feature_data (_type_, optional): Defaults to None.
        val_target_data (_type_, optional):  Defaults to None.

    """

    def __init__(
        self,
        model,
        class_names,
        train_feature_data,
        train_target_data,
        val_feature_data=None,
        val_target_data=None,
    ):
        self.model = model
        self.class_names = class_names
        self.train_feature_data = train_feature_data
        self.train_target_data = train_target_data
        self.val_feature_data = val_feature_data
        self.val_target_data = val_target_data

    def evaluate_train_classifier(self):
        # Dự đoán
        train_pred = self.model.predict(self.train_feature_data)
        train_pred = [int(item) for item in train_pred]

        val_pred = self.model.predict(self.val_feature_data)
        val_pred = [int(item) for item in val_pred]

        # Accuracy
        train_accuracy = metrics.accuracy_score(self.train_target_data, train_pred)
        val_accuracy = metrics.accuracy_score(self.val_target_data, val_pred)

        # Classification report
        class_names = np.asarray(self.class_names)
        train_target_data = [int(item) for item in self.train_target_data]
        val_target_data = [int(item) for item in self.val_target_data]

        named_train_target_data = class_names[train_target_data]
        named_train_pred = class_names[train_pred]
        named_val_target_data = class_names[val_target_data]
        named_val_pred = class_names[val_pred]

        train_classification_report = metrics.classification_report(
            named_train_target_data, named_train_pred
        )
        val_classification_report = metrics.classification_report(
            named_val_target_data, named_val_pred
        )

        # Confusion matrix
        train_confusion_matrix = metrics.confusion_matrix(
            named_train_target_data, named_train_pred, labels=class_names
        )
        np.fill_diagonal(train_confusion_matrix, 0)
        train_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            train_confusion_matrix, class_names
        )

        val_confusion_matrix = metrics.confusion_matrix(
            named_val_target_data, named_val_pred, labels=class_names
        )
        np.fill_diagonal(val_confusion_matrix, 0)
        val_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            val_confusion_matrix, class_names
        )

        model_results_text = f"Train accuracy: {train_accuracy}\n"
        model_results_text += f"Val accuracy: {val_accuracy}\n"
        model_results_text += (
            f"Train classification_report: \n{train_classification_report}\n"
        )
        model_results_text += (
            f"Val classification_report: \n{val_classification_report}"
        )

        return model_results_text, train_confusion_matrix, val_confusion_matrix

    def evaluate_test_classifier(self):
        test_pred = self.model.predict(self.train_feature_data)
        test_pred = [int(item) for item in test_pred]

        # Accuracy
        test_accuracy = metrics.accuracy_score(self.train_target_data, test_pred)

        # Classification report
        class_names = np.asarray(self.class_names)
        train_target_data = [int(item) for item in self.train_target_data]

        named_train_target_data = class_names[train_target_data]
        named_train_pred = class_names[test_pred]

        test_classification_report = metrics.classification_report(
            named_train_target_data, named_train_pred
        )

        # Confusion matrix
        test_confusion_matrix = metrics.confusion_matrix(
            named_train_target_data, named_train_pred, labels=class_names
        )
        np.fill_diagonal(test_confusion_matrix, 0)
        test_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            test_confusion_matrix, class_names
        )

        model_results_text = f"Test Accuracy: {test_accuracy}\n"
        model_results_text += (
            f"Test Classification_report: \n{test_classification_report}\n"
        )

        return model_results_text, test_confusion_matrix

    def evaluate(self):
        return (
            self.evaluate_train_classifier()
            if self.val_feature_data is not None
            else self.evaluate_test_classifier()
        )


class RegressorEvaluator:
    """Đánh giá model cho tập train-val hoặc tập test cho bài toán regression

    Hàm chính:
    - evaluate():

    Lưu ý:
    - KHi đánh giá 1 tập (vd: đánh giá tập test) thì truyền cho train_feature_data, train_target_data, còn val_feature_data và val_target_data **bỏ trống**

    Attributes:
        model (_type_):
        train_feature_data (_type_):
        train_target_data (_type_):
        val_feature_data (_type_, optional): Defaults to None.
        val_target_data (_type_, optional):  Defaults to None.

    """

    def __init__(
        self,
        model,
        train_feature_data,
        train_target_data,
        val_feature_data=None,
        val_target_data=None,
    ):
        self.model = model
        self.train_feature_data = train_feature_data
        self.train_target_data = train_target_data
        self.val_feature_data = val_feature_data
        self.val_target_data = val_target_data

    def evaluate_train_regressor(self):
        train_pred = self.model.predict(self.train_target_data)
        val_pred = self.model.predict(self.val_target_data)

        # RMSE
        train_rmse = np.sqrt(
            metrics.mean_squared_error(self.train_target_data, train_pred)
        )
        val_rmse = np.sqrt(metrics.mean_squared_error(self.val_target_data, val_pred))

        # MAE
        train_mae = metrics.mean_absolute_error(self.train_target_data, train_pred)
        val_mae = metrics.mean_absolute_error(self.val_target_data, val_pred)

        model_results_text = f"Train RMSE: {train_rmse}\n"
        model_results_text += f"Val RMSE: {val_rmse}\n"
        model_results_text += f"Train MAE: {train_mae}\n"
        model_results_text += f"Val MAE: {val_mae}\n"

        return model_results_text

    def evaluate_test_regressor(self):
        test_pred = self.model.predict(self.train_target_data)

        # RMSE
        test_rmse = np.sqrt(
            metrics.mean_squared_error(self.train_target_data, test_pred)
        )

        # MAE
        test_mae = metrics.mean_absolute_error(self.train_target_data, test_pred)

        model_results_text = f"Test RMSE: {test_rmse}\n"
        model_results_text = f"Test MAE: {test_mae}\n"

        return model_results_text


class BestModelSearcher:
    """Searcher đi tìm model tốt nhất và train, val scoring tương ứng

    Hàm chính:
        - next()

    Examples:
        Với **scoring = accuracy và target_score = 0.99**

        Tìm model thỏa val_accuracy > 0.99 và train_accuracy > 0.99 (1) và val_accuracy là lớn nhất trong số đó

        Nếu không thỏa (1) thì lấy theo val_accuracy lớn nhất

    Attributes:
        models (_type_): Model tốt nhất đang ở trong này
        train_scorings (_type_):
        val_scorings (_type_):
        target_score (_type_): Chỉ tiêu đề ra
        scoring (_type_): Chỉ số đánh giá


    """

    def __init__(self, models, train_scorings, val_scorings, target_score, scoring):
        self.models = models
        self.train_scorings = train_scorings
        self.val_scorings = val_scorings
        self.target_score = target_score
        self.scoring = scoring

    def find_train_val_scorings_to_find_the_best(self):
        sign_for_score = 1  # Nếu scoring cần min thì lấy âm -> quy về tìm lớn nhất thôi
        if self.scoring in myfuncs.SCORINGS_PREFER_MININUM:
            self.target_score = -self.target_score
            sign_for_score = -1

        self.train_scorings_to_find_the_best = np.asarray(
            [item * sign_for_score for item in self.train_scorings]
        )
        self.val_scorings_to_find_the_best = np.asarray(
            [item * sign_for_score for item in self.val_scorings]
        )

    def next(self):
        self.find_train_val_scorings_to_find_the_best()

        indexs_good_model = np.where(
            (self.val_scorings_to_find_the_best > self.target_score)
            & (self.train_scorings_to_find_the_best > self.target_score)
        )[0]

        index_best_model = None
        if (
            len(indexs_good_model) == 0
        ):  # Nếu ko có model nào đạt chỉ tiêu thì lấy cái tốt nhất
            index_best_model = np.argmax(self.val_scorings_to_find_the_best)
        else:
            val_series = pd.Series(
                self.val_scorings_to_find_the_best[indexs_good_model],
                index=indexs_good_model,
            )
            index_best_model = val_series.idxmax()

        best_model = self.models[index_best_model]
        train_scoring = self.train_scorings[index_best_model]
        val_scoring = self.val_scorings[index_best_model]

        return best_model, index_best_model, train_scoring, val_scoring


class CustomStackingClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, estimators, final_estimator, weights=None):
        self.estimators = estimators
        self.final_estimator = final_estimator
        self.weights = weights

        if self.weights is None:
            self.weights = [1] * len(self.estimators)

    def fit(self, X, y):
        for estimator in self.estimators:
            estimator.fit(X, y)

        new_feature = self.get_new_feature_through_estimators(X)

        self.final_estimator.fit(new_feature, y)

        return self

    def fit_on_batches(self, X, y, i):
        for estimator in self.estimators:
            myfuncs.fit_model_incremental_53(estimator, i, X, y)

        new_feature = self.get_new_feature_through_estimators(X)

        myfuncs.fit_model_incremental_53(self.final_estimator, i, new_feature, y)

        return self

    def predict(self, X):
        new_feature = self.get_new_feature_through_estimators(X)

        return self.final_estimator.predict(new_feature)

    def predict_proba(self, X):

        new_feature = self.get_new_feature_through_estimators(X)

        return self.final_estimator.predict_proba(new_feature)

    def get_new_feature_through_estimators(self, X):
        """Get new feature thông qua các estimators

        VD: nếu có 3 estimators và có 4 label cần phân loại thì kích thước của kết quả là (N, 3 * 4) = (N, 12)

        với N: số sample
        """
        list_predict_proba = [
            estimator.predict_proba(X) * weight
            for estimator, weight in zip(self.estimators, self.weights)
        ]
        new_feature = np.hstack(list_predict_proba)

        return new_feature


class CustomDataPipeline:
    def __init__(self, transformers):
        self.transformers = transformers

    def transform(self, df, data_type):
        for transformer in self.transformers:
            transformer.data_type = data_type

        for transformer in self.transformers:
            df = transformer.transform(df)

        return df


class TrainingBatchClassifierEvaluator:
    """Thực hiện đánh giá classifier với chế độ training trên từng batch, khác với thông thường là train trên full data

    Hàm chính: evaluate()

    Attributes:
        model (_type_): _description_
        train_batch_folder_path (_type_): đường dẫn đến thư mục chứa các batch
        num_batch (_type_): số lượng batch hiện có
        val_feature_data (_type_): _description_
        val_target_data (_type_): _description_
        class_names (_type_): _description_
    """

    def __init__(
        self,
        model,
        train_batch_folder_path,
        num_batch,
        val_feature_data,
        val_target_data,
        class_names,
    ):

        self.model = model
        self.train_batch_folder_path = train_batch_folder_path
        self.num_batch = num_batch
        self.val_feature_data = val_feature_data
        self.val_target_data = val_target_data
        self.class_names = np.asarray(class_names)

    def evaluate(self):
        list_train_accuracy = []
        list_train_classification_report = []
        list_train_confusion_matrix = []

        for i in range(self.num_batch):
            feature_batch = myfuncs.load_python_object(
                os.path.join(self.train_batch_folder_path, f"train_features_{i}.pkl")
            )
            target_batch = myfuncs.load_python_object(
                os.path.join(self.train_batch_folder_path, f"train_target_{i}.pkl")
            )
            train_target_data = [int(item) for item in target_batch]
            train_pred = self.model.predict(feature_batch)
            train_pred = [int(item) for item in train_pred]

            train_accuracy = metrics.accuracy_score(target_batch, train_pred)

            named_train_target_data = self.class_names[train_target_data]
            named_train_pred = self.class_names[train_pred]

            train_classification_report = metrics.classification_report(
                named_train_target_data, named_train_pred
            )
            train_confusion_matrix = metrics.confusion_matrix(
                named_train_target_data, named_train_pred, labels=self.class_names
            )

            list_train_accuracy.append(train_accuracy)
            list_train_classification_report.append(train_classification_report)
            list_train_confusion_matrix.append(train_confusion_matrix)

        index_best_train_accuracy = np.argmax(list_train_accuracy)
        train_accuracy = list_train_accuracy[index_best_train_accuracy]
        train_classification_report = list_train_classification_report[
            index_best_train_accuracy
        ]
        train_confusion_matrix = list_train_confusion_matrix[index_best_train_accuracy]

        np.fill_diagonal(train_confusion_matrix, 0)
        train_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            train_confusion_matrix, self.class_names
        )

        val_pred = self.model.predict(self.val_feature_data)
        val_pred = [int(item) for item in val_pred]
        val_target_data = [int(item) for item in self.val_target_data]

        val_accuracy = metrics.accuracy_score(val_target_data, val_pred)

        named_val_target_data = self.class_names[val_target_data]
        named_val_pred = self.class_names[val_pred]

        val_classification_report = metrics.classification_report(
            named_val_target_data, named_val_pred
        )
        val_confusion_matrix = metrics.confusion_matrix(
            named_val_target_data, named_val_pred, labels=self.class_names
        )

        np.fill_diagonal(val_confusion_matrix, 0)
        val_confusion_matrix = myfuncs.get_heatmap_for_confusion_matrix_30(
            val_confusion_matrix, self.class_names
        )

        model_results_text = f"Train accuracy: {train_accuracy}\n"
        model_results_text += f"Val accuracy: {val_accuracy}\n"
        model_results_text += (
            f"Train classification_report: \n{train_classification_report}\n"
        )
        model_results_text += (
            f"Val classification_report: \n{val_classification_report}"
        )

        return model_results_text, train_confusion_matrix, val_confusion_matrix


class CustomIncrementalPCA(BaseEstimator, TransformerMixin):
    def __init__(self, n_components, batch_size) -> None:
        super().__init__()
        self.n_components = n_components
        self.batch_size = batch_size

    def fit(self, X, y=None):
        X = np.asarray(X)

        self.transformer = IncrementalPCA(n_components=self.n_components)

        num_train_samples = len(X)
        list_X_batch = [
            X[i : i + self.batch_size, :]
            for i in range(0, num_train_samples, self.batch_size)
        ]

        for X_batch in list_X_batch:
            self.transformer.partial_fit(X_batch)

    def transform(self, X, y=None):
        X = self.transformer.transform(X)

        X = pd.DataFrame(X)

        self.cols = X.columns

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.cols


class BatchRBFKernelPCA(BaseEstimator, TransformerMixin):
    def __init__(self, n_components, batch_size, gamma="scale") -> None:
        super().__init__()
        self.n_components = n_components
        self.batch_size = batch_size
        self.gamma = gamma

    def fit(self, X, y=None):
        X = np.asarray(X)

        self.transformer = KernelPCA(
            kernel="rbf", n_components=self.n_components, gamma=self.gamma
        )

        num_train_samples = len(X)
        list_X_batch = [
            X[i : i + self.batch_size, :]
            for i in range(0, num_train_samples, self.batch_size)
        ]

        for X_batch in list_X_batch:
            self.transformer.fit(X_batch)

    def transform(self, X, y=None):
        X = self.transformer.transform(X)

        X = pd.DataFrame(X)

        self.cols = X.columns

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.cols


class CustomLocallyLinearEmbedding(BaseEstimator, TransformerMixin):
    def __init__(self, n_components, n_neighbors, batch_size) -> None:
        super().__init__()
        self.n_components = n_components
        self.batch_size = batch_size
        self.n_neighbors = n_neighbors

    def fit(self, X, y=None):
        X = np.asarray(X)

        self.transformer = LocallyLinearEmbedding(
            n_components=self.n_components, n_neighbors=self.n_neighbors
        )

        num_train_samples = len(X)
        list_X_batch = [
            X[i : i + self.batch_size, :]
            for i in range(0, num_train_samples, self.batch_size)
        ]

        for X_batch in list_X_batch:
            self.transformer.fit(X_batch)

    def transform(self, X, y=None):
        X = self.transformer.transform(X)

        X = pd.DataFrame(X)

        self.cols = X.columns

        return X

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.cols
