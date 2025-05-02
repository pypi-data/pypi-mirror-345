import pandas as pd
import warnings
import numpy as np
import seaborn as sns
from sklearn import metrics
import shap

def model_metrics(
    model,
    x_train:pd.DataFrame,
    y_train:pd.DataFrame,
    x_test:pd.DataFrame,
    y_test:pd.DataFrame,
    show_graphs:bool=True,
    f_score:float=0.50,
    classification:bool=True,
    algo=None,
    decile_n:int = 10,
    top_features_n:int=20,
):

    """
    Display a variety of model metrics for linear and logistic predictive models.

    See https://pypi.org/project/gitlabds/ for more information and example calls.
    """

    warnings.warn(
        "The model_metrics function will be deprecated in a future release. "
        "Please use the ModelEvaluator class instead for more comprehensive "
        "model evaluation capabilities.",
        DeprecationWarning, 
        stacklevel=2
    )

    pd.set_option("display.float_format", lambda x: "%.5f" % x)

    # Feature Importance
    if algo == "mars":
        print("\nFeature Importance")
        features = pd.DataFrame()
        features["features"] = model.named_steps["earth"].xlabels_
        features["importance"] = np.round(
            model.named_steps["earth"].feature_importances_, 4
        )
        features.sort_values(by=["importance"], ascending=False, inplace=True)
        display(features)

    elif (algo == "xgb"):

        # explain the model's predictions using SHAP
        explainer = shap.Explainer(model)
        shap_values = explainer(x_train)

        # mean absolute value of the SHAP values
        print("Feature Importance")
        shap.plots.bar(shap_values, max_display=20)

        # visualize the first prediction's explanation with a force plot
        shap.plots.beeswarm(shap_values, max_display=20)

        # Assign shap values based on test dataset
        shap_values = explainer.shap_values(x_test)

        importance = pd.DataFrame(np.abs(shap_values).mean(0))
        features = pd.DataFrame(x_test.columns)
        result = pd.concat([features, importance], axis=1)
        result.columns = ["features", "importance"]
        features = result.sort_values(by=["importance"], ascending=False).head(top_features_n)
        # display(features)

    elif algo == "rf":

        importance = pd.DataFrame(model.feature_importances_)

        features = pd.DataFrame(x_test.columns)

        result = pd.concat([features, importance], axis=1)
        result.columns = ["features", "importance"]
        features = result.sort_values(by=["importance"], ascending=False).head(top_features_n)
        display(features)

        sns.set_theme(style="whitegrid")
        sns.set(rc={"figure.figsize": (11, 8)})
        ax = sns.barplot(x="features", y="importance", data=features)
        #ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set(title="Top 20 features for account expansion")
        
        
    else:
        try:
            masker = shap.maskers.Independent(data = x_test)
            explainer = shap.Explainer(model, masker)
            shap_values = explainer(x_train)

            # mean absolute value of the SHAP values
            print("Feature Importance")
            shap.plots.bar(shap_values, max_display=20)

            # visualize the first prediction's explanation with a force plot
            shap.plots.beeswarm(shap_values, max_display=20)

            # Assign shap values based on test dataset
            shap_values = explainer.shap_values(x_test)

            importance = pd.DataFrame(np.abs(shap_values).mean(0))
            features = pd.DataFrame(x_test.columns)
            result = pd.concat([features, importance], axis=1)
            result.columns = ["features", "importance"]
            features = result.sort_values(by=["importance"], ascending=False).head(top_features_n)
            display(features)
            
        except:
            warnings.warn('Feature Importance could not be computed.')

    if classification:
        # TRAIN DATA: Get Predicted and Actual
        score_train = model.predict_proba(x_train)
        score_train = pd.DataFrame([item[1] for item in score_train], columns=["predicted"])
        score_train.index = x_train.index
        score_train = pd.concat([score_train, pd.DataFrame(y_train)], axis=1)
        score_train.rename(columns={score_train.columns[1]: "actual"}, inplace=True)

        # TEST DATA: Get Predicted and Actual
        score_test = model.predict_proba(x_test)
        score_test = pd.DataFrame([item[1] for item in score_test], columns=["predicted"])
        score_test.index = x_test.index
        score_test = pd.concat([score_test, pd.DataFrame(y_test)], axis=1)
        score_test.rename(columns={score_test.columns[1]: "actual"}, inplace=True)
        
    else:
        # TRAIN DATA: Get Predicted and Actual
        score_train = model.predict(x_train)
        score_train = pd.DataFrame(score_train, columns=["predicted"])
        score_train.index = x_train.index
        score_train = pd.concat([score_train, pd.DataFrame(y_train)], axis=1)
        score_train.rename(columns={score_train.columns[1]: "actual"}, inplace=True)

        # TEST DATA: Get Predicted and Actual
        score_test = model.predict(x_test)
        score_test = pd.DataFrame(score_test, columns=["predicted"])
        score_test.index = x_test.index
        score_test = pd.concat([score_test, pd.DataFrame(y_test)], axis=1)
        score_test.rename(columns={score_test.columns[1]: "actual"}, inplace=True)
        

    # Model Metrics
    if classification:
        metricx = [
            (
                "AUC",
                metrics.roc_auc_score(score_train["actual"], score_train["predicted"]),
                metrics.roc_auc_score(score_test["actual"], score_test["predicted"]),
            ),
            (
                "R2",
                metrics.r2_score(score_train["actual"], score_train["predicted"]),
                metrics.r2_score(score_test["actual"], score_test["predicted"]),
            ),
            (
                "Adj R2",
                1
                - (1 - metrics.r2_score(score_train["actual"], score_train["predicted"]))
                * (len(score_train["predicted"]) - 1)
                / (len(score_train["predicted"]) - x_train.shape[1] - 1),
                1
                - (1 - metrics.r2_score(score_test["actual"], score_test["predicted"]))
                * (len(score_test["predicted"]) - 1)
                / (len(score_test["predicted"]) - x_test.shape[1] - 1),
            ),
            (
                "LogLoss",
                metrics.log_loss(score_train["actual"], score_train["predicted"]),
                metrics.log_loss(score_test["actual"], score_test["predicted"]),
            ),
            (
                "MSE",
                metrics.mean_squared_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.mean_squared_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            (
                "RMSE",
                metrics.root_mean_squared_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.root_mean_squared_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            (
                "MSLE",
                metrics.mean_squared_log_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.mean_squared_log_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            ("Actual Mean", score_train["actual"].mean(), score_test["actual"].mean()),
            (
                "Predicted Mean",
                score_train["predicted"].mean(),
                score_test["predicted"].mean(),
            ),
        ]
        
    else:
        metricx = [
            (
                "R2",
                metrics.r2_score(score_train["actual"], score_train["predicted"]),
                metrics.r2_score(score_test["actual"], score_test["predicted"]),
            ),
            (
                "Adj R2",
                1
                - (1 - metrics.r2_score(score_train["actual"], score_train["predicted"]))
                * (len(score_train["predicted"]) - 1)
                / (len(score_train["predicted"]) - x_train.shape[1] - 1),
                1
                - (1 - metrics.r2_score(score_test["actual"], score_test["predicted"]))
                * (len(score_test["predicted"]) - 1)
                / (len(score_test["predicted"]) - x_test.shape[1] - 1),
            ),
            (
                "MSE",
                metrics.mean_squared_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.mean_squared_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            (
                "RMSE",
                metrics.root_mean_squared_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.root_mean_squared_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            (
                "MAE",
                metrics.mean_absolute_error(
                    score_train["actual"], score_train["predicted"]
                ),
                metrics.mean_absolute_error(
                    score_test["actual"], score_test["predicted"]
                ),
            ),
            ("Actual Mean", score_train["actual"].mean(), score_test["actual"].mean()),
            (
                "Predicted Mean",
                score_train["predicted"].mean(),
                score_test["predicted"].mean(),
            ),
        ]

    metricx = pd.DataFrame(metricx, columns=["metric", "train", "test"])
    metricx["deviation_pct"] = (metricx["test"] - metricx["train"]) / metricx["train"]

    print("\nModel Metrics")
    format_dict = {"train": "{0:,.4}", "test": "{0:.4}", "deviation_pct": "{:.2%}"}

    metricx.set_index("metric", inplace=True)
    display(metricx.style.format(format_dict))

    if classification:
        # Determine log-loss cutpoint
        actual = score_test["actual"].mean()
        multi = 100000
        class_ratio = [actual, 1 - actual]
        class_ratio = [round(i, 3) for i in class_ratio]

        actuals = []
        for i, val in enumerate(class_ratio):
            actuals = actuals + [i for x in range(int(val * multi))]

        preds = []
        for i in range(multi):
            preds += [class_ratio]

        try:
            print(
                f"log-loss: values below {metrics.log_loss(actuals, preds)} are better than chance.\n\n"
            )
        except ValueError:
            try:
                multi = 10000
                print(
                    f"log-loss: values below {metrics.log_loss(actuals, preds)} are better than chance.\n\n"
                )
            except ValueError:
                print("Log-loss threshold could not be computed")

    # Classification Metrics
    if classification:

        score_train["classification"] = np.where(
            score_train["predicted"] > f_score, 1, 0
        )
        score_test["classification"] = np.where(score_test["predicted"] > f_score, 1, 0)

        classification_metricx = [
            (
                "accuracy",
                metrics.accuracy_score(
                    score_train["actual"], score_train["classification"]
                ),
                metrics.accuracy_score(
                    score_test["actual"], score_test["classification"]
                ),
            ),
            (
                "precision",
                metrics.precision_score(
                    score_train["actual"], score_train["classification"]
                ),
                metrics.precision_score(
                    score_test["actual"], score_test["classification"]
                ),
            ),
            (
                "recall",
                metrics.recall_score(
                    score_train["actual"], score_train["classification"]
                ),
                metrics.recall_score(
                    score_test["actual"], score_test["classification"]
                ),
            ),
            (
                "F1 Score",
                metrics.f1_score(score_train["actual"], score_train["classification"]),
                metrics.f1_score(score_test["actual"], score_test["classification"]),
            ),
        ]

        classification_metricx = pd.DataFrame(
            classification_metricx, columns=["metric", "train", "test"]
        )
        classification_metricx["deviation_pct"] = (
            classification_metricx["test"] - classification_metricx["train"]
        ) / classification_metricx["train"]

        print("Classification Metrics")
        print(f"Using an F-Score of {f_score}")
        format_dict = {"train": "{0:,.4}", "test": "{0:.4}", "deviation_pct": "{:.2%}"}
        classification_metricx.set_index("metric", inplace=True)
        display(classification_metricx.style.format(format_dict))

        print(
            "Accuracy: % of Accurate Predictions. (True Positives + True Negatives) / Total Population"
        )
        print(
            "Precision: % of true positives to all positives. True Positives / (True Positives + False Positives)"
        )
        print(
            "Recall: % of postive cases accurately classified. True Positives / (True Positives + False Negatives)"
        )
        print("F1 Score: The harmonic mean between precision and recall.")



    # Lift Table
    if classification:
        # Compute Deciles
        temp, decile_breaks = pd.qcut(
            score_train["predicted"], decile_n, retbins=True, duplicates="drop", precision=10
        )
        score_train["decile"], decile_breaks = pd.qcut(
            score_train["predicted"],
            decile_n,
            labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
            retbins=True,
            duplicates="drop",
            precision=10,
        )

        score_train["decile"] = pd.to_numeric(score_train["decile"], downcast="integer")
        decile_breaks = np.round(decile_breaks, decile_n)
        decile_breaks = [
            float(i) for i in decile_breaks
        ]  # Convert to Float from Sci Notation

        # For Logistic Regression we want to set the lower and upper bounds to 0 and 1 so we can properly decile test records that may exceed the values shown in training
        try:

            #Set decile score limits to 0 and 1
            decile_breaks[0] = 0
            decile_breaks[decile_n] = 1

            # Apply Deciles to Test
            score_test["decile"] = pd.cut(
                score_test["predicted"],
                decile_breaks,
                labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
                include_lowest=True,
            )
            score_test["decile"] = pd.to_numeric(score_test["decile"], downcast="integer")



            # Construct Lift Table
            lift = score_test.groupby(["decile"]).agg(
                {
                    "decile": ["count"],
                    "actual": [lambda value: sum(value == 1), "mean"],
                    "predicted": ["mean", "min", "max"],
                }
            )
            lift.columns = [
                "count",
                "actual_instances",
                "actual_mean",
                "predicted_mean",
                "predicted_min",
                "predicted_max",
            ]

            lift["cume_count"] = lift["count"].cumsum()
            lift["cume_actual_instances"] = lift["actual_instances"].cumsum()
            lift["cume_actual_mean"] = lift["cume_actual_instances"] / lift["cume_count"]
            lift["cume_pct_actual"] = (
                lift["cume_actual_instances"] / lift["actual_instances"].sum()
            )

            # Lift = Resp Mean for each Decile / Total Cume Responses (i.e. last Row of Cume Resp Mean).
            # This shows how much more likely the outcome is to happe to that decile compared to the average.
            # 300 Lift = 3x (or 300%) more likely to respond/attrite/engage/etc.
            # 40 Lift = 60% (100 - 40)less likely to respond/attrite/engage/etc.
            lift["lift"] = (
                lift["actual_mean"]
                / (lift["actual_instances"].sum() / lift["count"].sum())
                * 100
            )
            lift["lift"] = lift["lift"].astype(int)

            # Cume Lift = Cume. Resp n for each Decile / Total Cume Responses (i.e. last row of cume resp n)
            # This shows how "deep" you can go in the model while still gettting better results than randomly selecting records for treatment
            # Cume Lift 100 = Would expect to get as many posititve instances of the outcome as chance/random guessing
            lift["cume_lift"] = (
                lift["cume_actual_mean"]
                / (lift["actual_instances"].sum() / lift["count"].sum())
                * 100
            )
            lift["cume_lift"] = lift["cume_lift"].astype(int)

            computed_deciles = True
            
            print(f"\nCreated {decile_n} decile breaks: \n{decile_breaks}\n")

        except IndexError:

            warnings.warn(
                "Decile breaks cannot be computed because there is not enough variation in model scores"
            )

            decile_breaks = []

            computed_deciles = False

    if show_graphs:

        import matplotlib
        import matplotlib.pyplot as plt
        import seaborn as seaborn

        # Score Distribution
        score_train["predicted"].plot.hist(bins=decile_n, label="jlkj")
        score_test["predicted"].plot.hist(bins=decile_n)
        plt.title("Train/Test Predicted Value Distribution")
        plt.show()

        if classification:
            
            # ROC
            metrics.RocCurveDisplay.from_estimator(model, x_test, y_test)
            plt.title("ROC")
            plt.show()

            # Precision vs Recall
            metrics.PrecisionRecallDisplay.from_estimator(model, x_test, y_test)
            plt.title("2-class Precision-Recall curve")
            plt.show()
            

            # Confusion Matrix Prep
            score_test["pred_class"] = np.where(
                score_test["predicted"] >= f_score, 1, 0
            )

            cfm = metrics.confusion_matrix(
                score_test["actual"], score_test["pred_class"]
            )
            class_names = [0, 1]  # name  of classes
            fig, ax = plt.subplots()
            tick_marks = np.arange(len(class_names))
            plt.xticks(tick_marks, class_names)
            plt.yticks(tick_marks, class_names)

            # Confusion Matrix Heatmap
            seaborn.heatmap(pd.DataFrame(cfm), annot=True, cmap="YlGnBu", fmt="g")
            ax.xaxis.set_label_position("bottom")
            plt.tight_layout()
            plt.title("Confusion matrix", y=1.1)
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.show()

            # Lift

            if computed_deciles:

                score_train["decile"].plot.hist(bins=19)
                score_test["decile"].plot.hist(bins=19)
                plt.xlabel("Decile")
                plt.title("Distribution")
                plt.show()

                lift["actual_mean"].plot(kind="line", grid=False, legend=True)
                lift["predicted_mean"].plot(kind="line", grid=False, legend=True)
                plt.title("Actual vs Predicted")
                plt.ylabel("Outcome %")
                plt.xticks(np.arange(1, decile_n+1, step=1))
                plt.show()

                lift["cume_lift"].plot(kind="line", grid=False, legend=True)
                plt.title("Cume. Lift")
                plt.ylabel("Lift")
                plt.xticks(np.arange(1, decile_n+1, step=1))
                plt.show()

                lift["cume_pct_actual"].plot(kind="line", grid=False, legend=True)
                plt.title("lift")
                plt.ylabel("% of Total Outcome")
                plt.xticks(np.arange(1, decile_n+1, step=1))
                plt.show()

                print("\nLift/Gains Table")
                display(lift)

            else:
                lift = pd.DataFrame()
                warnings.warn(
                    "Lift cannot be calculated because model deciles do not exist!"
                )
                    
    # Model Descriptives
    if not classification:
        score_train['decile'] = np.nan
        score_test['decile'] = np.nan
    
    print("\nTrain Descriptives:")
    display(score_train[["predicted", "actual", "decile"]].describe())
    display(x_train.describe())

    print("\nTest Descriptives:")
    display(score_test[["predicted", "actual", "decile"]].describe())
    display(x_test.describe())
        
    try:
        top_features = features
    except:
        top_features = x_test.columns.tolist()
        
    print(f"\n\nAll features in model: \n{x_test.columns.tolist()}\n")
            
    if classification:
        return metricx, lift, classification_metricx, top_features, decile_breaks

    else:
        return metricx, top_features