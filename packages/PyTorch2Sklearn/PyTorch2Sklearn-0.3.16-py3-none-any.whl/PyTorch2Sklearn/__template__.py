from PyTorch2Sklearn.environment import *
from PyTorch2Sklearn.utils import *
from PyTorch2Sklearn.environment import *


class TorchToSklearn_Model(object):
    # serves both for sklearn model class framework for classification and regression
    class Model:
        def _init_(self, CFG):
            pass

    def __init__(self, CFG, name="Model"):
        """Initialise the model"""

        super().__init__()
        self.CFG = CFG
        self.name = name
        self._is_fitted = False

        assert self.CFG["mode"] in [
            "Classification",
            "Regression",
        ], "mode must be either Classification or Regression"

        self.model = self.Model(self.CFG)  # initialise model

        torch.manual_seed(self.CFG["random_state"])

        self.optimizer = AdamW(self.model.parameters(), lr=self.CFG["lr"])
        self.criterion = self.CFG["loss"]

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.CFG["device"] = self.device
        self.model.to(self.device)
        self.criterion.to(self.device)

        if self.CFG["mode"] == "Classification":
            self._estimator_type = "classifier"
            self.classes_ = [x for x in range(self.CFG["output_dim"])]
        elif self.CFG["mode"] == "Regression":
            self._estimator_type = "regressor"

    def __str__(self):
        return self.name

    def save(self, mark: str = ""):
        """Save the model"""

        mark = " " + mark if mark else mark
        torch.save(
            self.model.state_dict(),
            os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
        )

    def load(self, mark: str = ""):
        """Load the model"""

        mark = " " + mark if mark else mark
        self.model.load_state_dict(
            torch.load(
                os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
                map_location=self.device,
            )
        )

    def fit(self, train_x: pd.DataFrame, train_y: pd.Series):
        """Fit the model

        Input:
            - train_x: pd.DataFrame, containing features
            - train_y: pd.DataFrame, containing targets
        """

        self.model.train()

        try:
            nan_in_train_x = train_x.isna().sum()

            if nan_in_train_x.any():
                print("train_x contains NaN values in the following columns:")
                print(nan_in_train_x[nan_in_train_x > 0])

            nan_in_train_y = train_y.isna().sum()
            if nan_in_train_y.any():
                print("train_y contains NaN values in the following columns:")
                print(nan_in_train_y[nan_in_train_y > 0])

        except AttributeError:
            if self.CFG['verbose']:
                print(
                    "train_x and train_y are not pandas dataframes, skipping NaN check")

        # if classification turn labels into e.g. 0 1 2 3 so data factory can turn into probability vectors
        if self.CFG["mode"] == "Classification":
            label_list = list(set(train_y))
            label_list.sort()
            self.encode_label_dict = {
                label: i for i, label in enumerate(label_list)}
            self.decode_label_dict = {
                i: label for i, label in enumerate(label_list)}

            train_y = [self.encode_label_dict[y] for y in train_y]

        x_list, y_list = self.CFG["TabularDataFactory"](
            train_x, train_y, self.CFG["mode"]
        )  # might want to do batch number as well
        tabular_dataset = self.CFG["TabularDataset"](x_list, y_list)

        np.random.seed(self.CFG["random_state"])
        torch.manual_seed(self.CFG["random_state"])
        seeds = [np.random.randint(1, 1000) for _ in range(self.CFG["epochs"])]

        if self.CFG["verbose"] == True:
            for epoch in tqdm(range(self.CFG["epochs"])):

                tabular_dataloader = DataLoader(
                    tabular_dataset,
                    batch_size=self.CFG["batch_size"],
                    shuffle=True,
                    generator=torch.Generator().manual_seed(seeds[epoch]),
                )

                for batch in tabular_dataloader:
                    X, y = batch[0].to(self.device), batch[1].to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()
                    pred = self.model(X)

                    if torch.isnan(pred).any():

                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred, y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        else:
            for epoch in range(self.CFG["epochs"]):

                tabular_dataloader = DataLoader(
                    tabular_dataset,
                    batch_size=self.CFG["batch_size"],
                    shuffle=True,
                    generator=torch.Generator().manual_seed(seeds[epoch]),
                )

                for batch in tabular_dataloader:
                    X, y = batch[0].to(self.device), batch[1].to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()
                    pred = self.model(X)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred, y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        self._is_fitted = True

    def predict(self, val_x: pd.DataFrame) -> list:
        """Predict labels for classification tasks and values for regression tasks.

        Input:
            - val_x: pd.DataFrame, containing features

        Output:
            - valid_pred: list, containing predicted labels or values

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        self.model.eval()

        with torch.no_grad():

            x_list = self.CFG["TabularDataFactory"](
                val_x, mode=self.CFG["mode"]
            )  # create the instances
            tabular_dataset = self.CFG["TabularDataset"](x_list)

            val_dataloader = DataLoader(
                tabular_dataset, batch_size=self.CFG["batch_size"], shuffle=False
            )

            valid_pred = []

            for batch in val_dataloader:
                x_batch = batch.to(self.device)

                pred = self.model(x_batch)

                # if regression, squeeze the dimension, if classification, argmax.
                predicted_labels = (
                    torch.argmax(pred, dim=1)
                    if self.CFG["mode"] == "Classification"
                    else pred.squeeze(1)
                )
                valid_pred += predicted_labels.detach().cpu().tolist()

        if self.CFG["mode"] == "Classification":  # turn labels back to normal
            valid_pred = [self.decode_label_dict[pred] for pred in valid_pred]

        return np.array(valid_pred)

    def predict_proba(self, val_x: pd.DataFrame) -> np.ndarray:
        """Predict probabilities for classification tasks.

        Input:

            - val_x: pd.DataFrame, containing features

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        assert (
            self.CFG["mode"] == "Classification"
        ), "predict_proba is only available for classification tasks"
        self.model.eval()

        with torch.no_grad():
            x_list = self.CFG["TabularDataFactory"](
                val_x, mode=self.CFG["mode"])
            tabular_dataset = self.CFG["TabularDataset"](x_list)
            val_dataloader = DataLoader(
                tabular_dataset, batch_size=self.CFG["batch_size"], shuffle=False
            )

            valid_pred_probs = []

            for batch in val_dataloader:
                x_batch = batch.to(self.device)
                pred_probs = self.model(x_batch).softmax(dim=1)
                valid_pred_probs.append(pred_probs.detach().cpu().numpy())

            valid_pred_probs = np.concatenate(valid_pred_probs, axis=0)

        return np.array(valid_pred_probs)

    def __sklearn_is_fitted__(self):
        """
        Check fitted status and return a Boolean value.
        """
        return hasattr(self, "_is_fitted") and self._is_fitted


class TorchToSklearn_GraphModel(object):
    # serves both for sklearn model class framework for classification and regression
    class Model:
        def _init_(self, CFG):
            pass

    def __init__(self, CFG, name="Model"):
        """Initialise the model"""

        super().__init__()
        self.CFG = CFG
        self.name = name
        self._is_fitted = False

        assert self.CFG["mode"] in [
            "Classification",
            "Regression",
        ], "mode must be either Classification or Regression"

        self.model = self.Model(self.CFG)  # initialise model

        torch.manual_seed(self.CFG["random_state"])

        self.optimizer = AdamW(self.model.parameters(), lr=self.CFG["lr"])
        self.criterion = self.CFG["loss"]

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.CFG["device"] = self.device
        self.model.to(self.device)
        self.criterion.to(self.device)

        if self.CFG["mode"] == "Classification":
            self._estimator_type = "classifier"
            self.classes_ = [x for x in range(self.CFG["output_dim"])]
        elif self.CFG["mode"] == "Regression":
            self._estimator_type = "regressor"

    def __str__(self):
        return self.name

    def save(self, mark: str = ""):
        """Save the model"""

        mark = " " + mark if mark else mark
        torch.save(
            self.model.state_dict(),
            os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
        )

    def load(self, mark: str = ""):
        """Load the model"""

        mark = " " + mark if mark else mark
        self.model.load_state_dict(
            torch.load(
                os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
                map_location=self.device,
            )
        )

    def fit(self, train_x: pd.DataFrame, train_y: pd.Series):
        """Fit the model

        Input:
            - train_x: pd.DataFrame, containing features
            - train_y: pd.DataFrame, containing targets
        """

        self.model.train()

        try:
            nan_in_train_x = train_x.isna().sum()

            if nan_in_train_x.any():
                print("train_x contains NaN values in the following columns:")
                print(nan_in_train_x[nan_in_train_x > 0])

            nan_in_train_y = train_y.isna().sum()
            if nan_in_train_y.any():
                print("train_y contains NaN values in the following columns:")
                print(nan_in_train_y[nan_in_train_y > 0])

        except AttributeError:
            if self.CFG['verbose']:
                print(
                    "train_x and train_y are not pandas dataframes, skipping NaN check")

        self.CFG["target"] = [
            column for column in train_y.columns if "idx" != column]

        # if classification turn labels into e.g. 0 1 2 3 so data factory can turn into probability vectors
        if self.CFG["mode"] == "Classification":
            label_list = list(set(train_y[self.CFG["target"][0]]))
            label_list.sort()
            self.encode_label_dict = {
                label: i for i, label in enumerate(label_list)}
            self.decode_label_dict = {
                i: label for i, label in enumerate(label_list)}

            train_y[self.CFG["target"][0]] = [
                self.encode_label_dict[y] for y in train_y[self.CFG["target"][0]].values
            ]

        x_list, y_list = self.CFG["GraphDataFactory"](
            train_x, train_y, self.CFG["mode"], self.CFG
        )  # might want to do batch number as well

        np.random.seed(self.CFG["random_state"])
        torch.manual_seed(self.CFG["random_state"])
        seeds = [np.random.randint(1, 1000) for _ in range(self.CFG["epochs"])]

        if self.CFG["verbose"] == True:
            for epoch in tqdm(range(self.CFG["epochs"])):

                np.random.seed(seeds[epoch])
                np.random.shuffle(x_list)
                np.random.seed(
                    seeds[epoch]
                )  # reset seed so that they are shuffled in same order
                np.random.shuffle(y_list)

                for mini_batch_number in range(len(x_list)):
                    X, y = torch.FloatTensor(np.array(x_list[mini_batch_number])).to(
                        self.device
                    ).squeeze(0), torch.FloatTensor(
                        np.array(y_list[mini_batch_number])
                    ).to(
                        self.device
                    ).squeeze(
                        0
                    )

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()
                    graph = (
                        (torch.ones(len(X)).unsqueeze(0).T @
                         torch.ones(len(X)).unsqueeze(0)).to(self.device)
                        if self.CFG["graph"] == "J"
                        else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                        else self.CFG["graph"].to(self.device)
                    )
                    pred = self.model(X, graph)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred, y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break
        else:
            for epoch in range(self.CFG["epochs"]):

                np.random.seed(seeds[epoch])
                np.random.shuffle(x_list)
                np.random.seed(
                    seeds[epoch]
                )  # reset seed so that they are shuffled in same order
                np.random.shuffle(y_list)

                for mini_batch_number in range(len(x_list)):
                    X, y = torch.FloatTensor(x_list[mini_batch_number]).to(
                        self.device
                    ), torch.FloatTensor(y_list[mini_batch_number]).to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()

                    graph = (
                        (torch.ones(len(X)).unsqueeze(0).T @
                         torch.ones(len(X)).unsqueeze(0)).to(self.device)
                        if self.CFG["graph"] == "J"
                        else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                        else self.CFG["graph"].to(self.device)
                    )
                    pred = self.model(X, graph)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:

                        loss = self.criterion(pred, y)

                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        self._is_fitted = True

    def predict(self, val_x: pd.DataFrame) -> list:
        """Predict labels for classification tasks and values for regression tasks.

        Input:
            - val_x: pd.DataFrame, containing features

        Output:
            - valid_pred: list, containing predicted labels or values

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        self.model.eval()

        with torch.no_grad():

            x_list = self.CFG["GraphDataFactory"](
                val_x, mode=self.CFG["mode"], CFG=self.CFG
            )  # create the instances

            valid_pred = []

            for mini_batch_number in range(len(x_list)):
                x_batch = (
                    torch.FloatTensor(x_list[mini_batch_number])
                    .to(self.device)
                    .squeeze(0)
                )

                graph = (
                        (torch.ones(len(x_batch)).unsqueeze(0).T @
                         torch.ones(len(x_batch)).unsqueeze(0)).to(self.device)
                    if self.CFG["graph"] == "J"
                    else (1/len(x_batch) * torch.ones(len(x_batch)).unsqueeze(0).T @ torch.ones(len(x_batch)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                    else self.CFG["graph"].to(self.device)
                )

                pred = self.model(x_batch, graph)
                # if regression, squeeze the dimension, if classification, argmax.
                predicted_labels = (
                    torch.argmax(pred, dim=1)
                    if self.CFG["mode"] == "Classification"
                    else pred.squeeze(1)
                )
                valid_pred += predicted_labels.detach().cpu().tolist()

        if self.CFG["mode"] == "Classification":  # turn labels back to normal
            valid_pred = [self.decode_label_dict[pred] for pred in valid_pred]

        return np.array(valid_pred)

    def predict_proba(self, val_x: pd.DataFrame) -> np.ndarray:
        """Predict probabilities for classification tasks.

        Input:

            - val_x: pd.DataFrame, containing features

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        assert (
            self.CFG["mode"] == "Classification"
        ), "predict_proba is only available for classification tasks"

        self.model.eval()

        with torch.no_grad():
            x_list = self.CFG["GraphDataFactory"](
                val_x, mode=self.CFG["mode"], CFG=self.CFG
            )

            valid_pred_probs = []

            for mini_batch_number in range(len(x_list)):
                x_batch = torch.FloatTensor(
                    x_list[mini_batch_number]).to(self.device).squeeze(0)

                graph = (
                    (torch.ones(len(x_batch)).unsqueeze(0).T @
                        torch.ones(len(x_batch)).unsqueeze(0)).to(self.device)
                    if self.CFG["graph"] == "J"
                    else (1/len(x_batch) * torch.ones(len(x_batch)).unsqueeze(0).T @ torch.ones(len(x_batch)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                    else self.CFG["graph"].to(self.device)
                )

                pred_probs = self.model(x_batch, graph).softmax(dim=1)
                valid_pred_probs.append(pred_probs.detach().cpu().numpy())

            valid_pred_probs = np.concatenate(valid_pred_probs, axis=0)

        return np.array(valid_pred_probs)

    def __sklearn_is_fitted__(self):
        """
        Check fitted status and return a Boolean value.
        """
        return hasattr(self, "_is_fitted") and self._is_fitted


class TorchToSklearn_ImageGraphModel(object):
    # serves both for sklearn model class framework for classification and regression
    class Model:
        def _init_(self, CFG):
            pass

    def __init__(self, CFG, name="Model"):
        """Initialise the model"""

        super().__init__()
        self.CFG = CFG
        self.name = name
        self._is_fitted = False

        assert self.CFG["mode"] in [
            "Classification",
            "Regression",
        ], "mode must be either Classification or Regression"

        self.model = self.Model(self.CFG)  # initialise model

        torch.manual_seed(self.CFG["random_state"])

        self.optimizer = AdamW(self.model.parameters(), lr=self.CFG["lr"])
        self.criterion = self.CFG["loss"]

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.CFG["device"] = self.device
        self.model.to(self.device)
        self.criterion.to(self.device)

        if self.CFG["mode"] == "Classification":
            self._estimator_type = "classifier"
            self.classes_ = [x for x in range(self.CFG["output_dim"])]
        elif self.CFG["mode"] == "Regression":
            self._estimator_type = "regressor"

    def __str__(self):
        return self.name

    def save(self, mark: str = ""):
        """Save the model"""

        mark = " " + mark if mark else mark
        torch.save(
            self.model.state_dict(),
            os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
        )

    def load(self, mark: str = ""):
        """Load the model"""

        mark = " " + mark if mark else mark
        self.model.load_state_dict(
            torch.load(
                os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
                map_location=self.device,
            )
        )

    def fit(self, train_x: pd.DataFrame, train_y: pd.Series):
        """Fit the model

        Input:
            - train_x: pd.DataFrame, containing features
            - train_y: pd.DataFrame, containing targets
        """

        self.model.train()

        try:
            nan_in_train_x = train_x.isna().sum()

            if nan_in_train_x.any():
                print("train_x contains NaN values in the following columns:")
                print(nan_in_train_x[nan_in_train_x > 0])

            nan_in_train_y = train_y.isna().sum()
            if nan_in_train_y.any():
                print("train_y contains NaN values in the following columns:")
                print(nan_in_train_y[nan_in_train_y > 0])

        except AttributeError:
            if self.CFG['verbose']:
                print(
                    "train_x and train_y are not pandas dataframes, skipping NaN check")

        self.CFG["target"] = [
            column for column in train_y.columns if "idx" != column]

        # if classification turn labels into e.g. 0 1 2 3 so data factory can turn into probability vectors
        if self.CFG["mode"] == "Classification":
            label_list = list(set(train_y[self.CFG["target"][0]]))
            label_list.sort()
            self.encode_label_dict = {
                label: i for i, label in enumerate(label_list)}
            self.decode_label_dict = {
                i: label for i, label in enumerate(label_list)}

            train_y[self.CFG["target"][0]] = [
                self.encode_label_dict[y] for y in train_y[self.CFG["target"][0]].values
            ]

        x_list, x_images_list, y_list = self.CFG["ImageGraphDataFactory"](
            train_x, train_y, self.CFG["mode"], self.CFG
        )  # might want to do batch number as well

        np.random.seed(self.CFG["random_state"])
        torch.manual_seed(self.CFG["random_state"])
        seeds = [np.random.randint(1, 1000) for _ in range(self.CFG["epochs"])]

        if self.CFG["verbose"] == True:
            for epoch in tqdm(range(self.CFG["epochs"])):

                np.random.seed(seeds[epoch])
                np.random.shuffle(x_list)
                np.random.seed(seeds[epoch])
                np.random.shuffle(x_images_list)
                np.random.seed(
                    seeds[epoch]
                )  # reset seed so that they are shuffled in same order
                np.random.shuffle(y_list)

                for mini_batch_number in range(len(x_list)):
                    X, X_images, y = torch.FloatTensor(np.array(x_list[mini_batch_number])).to(
                        self.device
                    ).squeeze(0), torch.FloatTensor(np.array(x_images_list[mini_batch_number], dtype=np.float32) / 255.0).to(
                        self.device
                    ).squeeze(0), torch.FloatTensor(
                        np.array(y_list[mini_batch_number])
                    ).to(
                        self.device
                    ).squeeze(
                        0
                    )

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()
                    graph = (
                        (torch.ones(len(X)).unsqueeze(0).T @
                         torch.ones(len(X)).unsqueeze(0)).to(self.device)
                        if self.CFG["graph"] == "J"
                        else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                        else self.CFG["graph"].to(self.device)
                    )
                    pred = self.model(X, X_images, graph)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred.squeeze(0), y)

                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        else:
            for epoch in range(self.CFG["epochs"]):

                np.random.seed(seeds[epoch])
                np.random.shuffle(x_list)
                np.random.seed(seeds[epoch])
                np.random.shuffle(x_images_list)
                np.random.seed(
                    seeds[epoch]
                )  # reset seed so that they are shuffled in same order
                np.random.shuffle(y_list)

                for mini_batch_number in range(len(x_list)):
                    X, X_images, y = torch.FloatTensor(x_list[mini_batch_number]).to(
                        self.device
                    ), torch.FloatTensor(np.array(x_images_list[mini_batch_number], dtype=np.float32) / 255.0).to(
                        self.device
                    ), torch.FloatTensor(
                        y_list[mini_batch_number]).to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()

                    graph = (
                        (torch.ones(len(X)).unsqueeze(0).T @
                         torch.ones(len(X)).unsqueeze(0)).to(self.device)
                        if self.CFG["graph"] == "J"
                        else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                        else self.CFG["graph"].to(self.device)
                    )
                    pred = self.model(X, X_images, graph)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred, y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        self._is_fitted = True

    def predict(self, val_x: pd.DataFrame) -> list:
        """Predict labels for classification tasks and values for regression tasks.

        Input:
            - val_x: pd.DataFrame, containing features

        Output:
            - valid_pred: list, containing predicted labels or values

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        self.model.eval()

        with torch.no_grad():

            x_list, x_images_list = self.CFG["ImageGraphDataFactory"](
                val_x, mode=self.CFG["mode"], CFG=self.CFG
            )  # create the instances

            valid_pred = []

            for mini_batch_number in range(len(x_list)):
                X, X_images = torch.FloatTensor(np.array(x_list[mini_batch_number])).to(
                    self.device
                ).squeeze(0), torch.FloatTensor(np.array(x_images_list[mini_batch_number], dtype=np.float32) / 255.0).to(
                    self.device
                ).squeeze(0)

                graph = (
                        (torch.ones(len(X)).unsqueeze(0).T @
                         torch.ones(len(X)).unsqueeze(0)).to(self.device)
                    if self.CFG["graph"] == "J"
                    else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                    else self.CFG["graph"].to(self.device)
                )

                pred = self.model(X, X_images, graph)
                # if regression, squeeze the dimension, if classification, argmax.
                predicted_labels = (
                    torch.argmax(pred, dim=1)
                    if self.CFG["mode"] == "Classification"
                    else pred.squeeze(1)
                )
                valid_pred += predicted_labels.detach().cpu().tolist()

        if self.CFG["mode"] == "Classification":  # turn labels back to normal
            valid_pred = [self.decode_label_dict[pred] for pred in valid_pred]

        return np.array(valid_pred)

    def predict_proba(self, val_x: pd.DataFrame) -> np.ndarray:
        """Predict probabilities for classification tasks.

        Input:

            - val_x: pd.DataFrame, containing features

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        assert (
            self.CFG["mode"] == "Classification"
        ), "predict_proba is only available for classification tasks"

        self.model.eval()

        with torch.no_grad():
            x_list, x_images_list = self.CFG["ImageGraphDataFactory"](
                val_x, mode=self.CFG["mode"], CFG=self.CFG
            )  # create the instances

            valid_pred_probs = []

            for mini_batch_number in range(len(x_list)):
                X, X_images = torch.FloatTensor(np.array(x_list[mini_batch_number])).to(
                    self.device
                ).squeeze(0), torch.FloatTensor(np.array(x_images_list[mini_batch_number], dtype=np.float32) / 255.0).to(
                    self.device
                ).squeeze(0)

                graph = (
                    (torch.ones(len(X)).unsqueeze(0).T @
                        torch.ones(len(X)).unsqueeze(0)).to(self.device)
                    if self.CFG["graph"] == "J"
                    else (1/len(X) * torch.ones(len(X)).unsqueeze(0).T @ torch.ones(len(X)).unsqueeze(0)).to(self.device) if self.CFG["graph"] == "U"
                    else self.CFG["graph"].to(self.device)
                )

                pred_probs = self.model(
                    X, X_images, graph).softmax(dim=1)
                valid_pred_probs.append(pred_probs.detach().cpu().numpy())

            valid_pred_probs = np.concatenate(valid_pred_probs, axis=0)

        return np.array(valid_pred_probs)

    def __sklearn_is_fitted__(self):
        """
        Check fitted status and return a Boolean value.
        """
        return hasattr(self, "_is_fitted") and self._is_fitted


class TorchToSklearn_ImageTabularModel(object):
    # serves both for sklearn model class framework for classification and regression
    class Model:
        def _init_(self, CFG):
            pass

    def __init__(self, CFG, name="Model"):
        """Initialise the model"""

        super().__init__()
        self.CFG = CFG
        self.name = name
        self._is_fitted = False

        assert self.CFG["mode"] in [
            "Classification",
            "Regression",
        ], "mode must be either Classification or Regression"

        self.model = self.Model(self.CFG)  # initialise model

        torch.manual_seed(self.CFG["random_state"])

        self.optimizer = AdamW(self.model.parameters(), lr=self.CFG["lr"])
        self.criterion = self.CFG["loss"]

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.CFG["device"] = self.device
        self.model.to(self.device)
        self.criterion.to(self.device)

        if self.CFG["mode"] == "Classification":
            self._estimator_type = "classifier"
            self.classes_ = [x for x in range(self.CFG["output_dim"])]
        elif self.CFG["mode"] == "Regression":
            self._estimator_type = "regressor"

    def __str__(self):
        return self.name

    def save(self, mark: str = ""):
        """Save the model"""

        mark = " " + mark if mark else mark
        torch.save(
            self.model.state_dict(),
            os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
        )

    def load(self, mark: str = ""):
        """Load the model"""

        mark = " " + mark if mark else mark
        self.model.load_state_dict(
            torch.load(
                os.path.join(self.CFG["rootpath"], f"state/{self}{mark}.pt"),
                map_location=self.device,
            )
        )

    def fit(self, train_x: pd.DataFrame, train_y: pd.Series):
        """Fit the model

        Input:
            - train_x: pd.DataFrame, containing features
            - train_y: pd.DataFrame, containing targets
        """

        self.model.train()

        try:
            nan_in_train_x = train_x.isna().sum()

            if nan_in_train_x.any():
                print("train_x contains NaN values in the following columns:")
                print(nan_in_train_x[nan_in_train_x > 0])

            nan_in_train_y = train_y.isna().sum()
            if nan_in_train_y.any():
                print("train_y contains NaN values in the following columns:")
                print(nan_in_train_y[nan_in_train_y > 0])

        except AttributeError:
            if self.CFG['verbose']:
                print(
                    "train_x and train_y are not pandas dataframes, skipping NaN check")

        # if classification turn labels into e.g. 0 1 2 3 so data factory can turn into probability vectors
        if self.CFG["mode"] == "Classification":
            label_list = list(set(train_y[self.CFG["target"][0]]))
            label_list.sort()
            self.encode_label_dict = {
                label: i for i, label in enumerate(label_list)}
            self.decode_label_dict = {
                i: label for i, label in enumerate(label_list)}

            train_y[self.CFG["target"][0]] = [
                self.encode_label_dict[y] for y in train_y[self.CFG["target"][0]].values
            ]

        x_list, y_list = self.CFG["TabularImageDataFactory"](
            train_x, train_y, self.CFG["mode"]
        )  # might want to do batch number as well
        tabularimage_dataset = self.CFG["TabularImageDataset"](x_list, y_list)

        np.random.seed(self.CFG["random_state"])
        torch.manual_seed(self.CFG["random_state"])
        seeds = [np.random.randint(1, 1000) for _ in range(self.CFG["epochs"])]

        if self.CFG["verbose"] == True:
            for epoch in tqdm(range(self.CFG["epochs"])):

                tabularimage_dataloader = DataLoader(
                    tabularimage_dataset,
                    batch_size=self.CFG["batch_size"],
                    shuffle=True,
                    generator=torch.Generator().manual_seed(seeds[epoch]),
                )

                for batch in tabularimage_dataloader:
                    X, X_images, y = batch[0].to(self.device), batch[1].to(
                        self.device), batch[2].to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()

                    pred = self.model(X, X_images)
                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred.squeeze(0), y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        else:
            for epoch in range(self.CFG["epochs"]):

                tabularimage_dataloader = DataLoader(
                    tabularimage_dataset,
                    batch_size=self.CFG["batch_size"],
                    shuffle=True,
                    generator=torch.Generator().manual_seed(seeds[epoch]),
                )

                for batch in tabularimage_dataloader:
                    X, X_images, y = batch[0].to(self.device), batch[1].to(
                        self.device), batch[2].to(self.device)

                    # special case error handling: batchnorm needs more than 2 instances to be meaningful
                    if self.CFG["batchnorm"] == True and X.shape[0] <= 2:
                        continue

                    if self.CFG["mode"] == "Regression":
                        y = y.view(-1, self.CFG["output_dim"])

                    self.optimizer.zero_grad()

                    pred = self.model(X, X_images)

                    if torch.isnan(pred).any():
                        print(f"Epoch {epoch}: NaN losses encountered.")
                        break
                    else:
                        loss = self.criterion(pred, y)
                        loss.backward()
                        if self.CFG["grad_clip"]:
                            nn.utils.clip_grad_norm_(
                                self.model.parameters(), 2.0)
                        self.optimizer.step()

                if self.CFG['nan_break']:
                    print(
                        "Terminating Training: NaN loss.")
                    break

        self._is_fitted = True

    def predict(self, val_x: pd.DataFrame) -> list:
        """Predict labels for classification tasks and values for regression tasks.

        Input:
            - val_x: pd.DataFrame, containing features

        Output:
            - valid_pred: list, containing predicted labels or values

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        self.model.eval()

        with torch.no_grad():

            x_list = self.CFG["TabularImageDataFactory"](
                val_x, mode=self.CFG["mode"]
            )  # create the instances
            tabularimage_dataset = self.CFG["TabularImageDataset"](x_list)

            val_dataloader = DataLoader(
                tabularimage_dataset, batch_size=self.CFG["batch_size"], shuffle=False
            )

            valid_pred = []

            for batch in val_dataloader:
                x_batch, x_images_batch = batch[0].to(self.device), batch[1].to(
                    self.device)

                pred = self.model(x_batch, x_images_batch)
                # if regression, squeeze the dimension, if classification, argmax.
                predicted_labels = (
                    torch.argmax(pred, dim=1)
                    if self.CFG["mode"] == "Classification"
                    else pred.squeeze(1)
                )
                valid_pred += predicted_labels.detach().cpu().tolist()

        if self.CFG["mode"] == "Classification":  # turn labels back to normal
            valid_pred = [self.decode_label_dict[pred] for pred in valid_pred]

        return np.array(valid_pred)

    def predict_proba(self, val_x: pd.DataFrame) -> np.ndarray:
        """Predict probabilities for classification tasks.

        Input:

            - val_x: pd.DataFrame, containing features

        """

        if not self.__sklearn_is_fitted__():
            print(
                'Warning: Model is not fitted yet. It is advisable to call fit() before predict().')

        assert (
            self.CFG["mode"] == "Classification"
        ), "predict_proba is only available for classification tasks"

        self.model.eval()

        with torch.no_grad():
            x_list = self.CFG["TabularImageDataFactory"](
                val_x, mode=self.CFG["mode"])
            tabular_dataset = self.CFG["TabularImageDataset"](x_list)
            val_dataloader = DataLoader(
                tabular_dataset, batch_size=self.CFG["batch_size"], shuffle=False
            )

            valid_pred_probs = []

            for batch in val_dataloader:
                x_batch, x_images_batch = batch[0].to(self.device), batch[1].to(
                    self.device)

                pred_probs = self.model(
                    x_batch, x_images_batch).softmax(dim=1)
                valid_pred_probs.append(pred_probs.detach().cpu().numpy())

            valid_pred_probs = np.concatenate(valid_pred_probs, axis=0)

        return np.array(valid_pred_probs)

    def __sklearn_is_fitted__(self):
        """
        Check fitted status and return a Boolean value.
        """
        return hasattr(self, "_is_fitted") and self._is_fitted
