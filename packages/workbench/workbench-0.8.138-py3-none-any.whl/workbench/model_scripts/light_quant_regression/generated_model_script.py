# Template Placeholders
TEMPLATE_PARAMS = {
    "model_type": "quantile_regressor",
    "target_column": "udm_asy_res_value",
    "feature_list": ['bcut2d_logplow', 'numradicalelectrons', 'smr_vsa5', 'fr_lactam', 'fr_morpholine', 'fr_aldehyde', 'slogp_vsa1', 'fr_amidine', 'bpol', 'fr_ester', 'fr_azo', 'kappa3', 'peoe_vsa5', 'fr_ketone_topliss', 'vsa_estate9', 'estate_vsa9', 'bcut2d_mrhi', 'fr_ndealkylation1', 'numrotatablebonds', 'minestateindex', 'fr_quatn', 'peoe_vsa3', 'fr_epoxide', 'fr_aniline', 'minpartialcharge', 'fr_nitroso', 'fpdensitymorgan2', 'fr_oxime', 'fr_sulfone', 'smr_vsa1', 'kappa1', 'fr_pyridine', 'numaromaticrings', 'vsa_estate6', 'molmr', 'estate_vsa1', 'fr_dihydropyridine', 'vsa_estate10', 'fr_alkyl_halide', 'chi2n', 'fr_thiocyan', 'fpdensitymorgan1', 'fr_unbrch_alkane', 'slogp_vsa9', 'chi4n', 'fr_nitro_arom', 'fr_al_oh', 'fr_furan', 'fr_c_s', 'peoe_vsa8', 'peoe_vsa14', 'numheteroatoms', 'fr_ndealkylation2', 'maxabspartialcharge', 'vsa_estate2', 'peoe_vsa7', 'apol', 'numhacceptors', 'fr_tetrazole', 'vsa_estate1', 'peoe_vsa9', 'naromatom', 'bcut2d_chghi', 'fr_sh', 'fr_halogen', 'slogp_vsa4', 'fr_benzodiazepine', 'molwt', 'fr_isocyan', 'fr_prisulfonamd', 'maxabsestateindex', 'minabsestateindex', 'peoe_vsa11', 'slogp_vsa12', 'estate_vsa5', 'numaliphaticcarbocycles', 'bcut2d_mwlow', 'slogp_vsa7', 'fr_allylic_oxid', 'fr_methoxy', 'fr_nh0', 'fr_coo2', 'fr_phenol', 'nacid', 'nbase', 'chi3v', 'fr_ar_nh', 'fr_nitrile', 'fr_imidazole', 'fr_urea', 'bcut2d_mrlow', 'chi1', 'smr_vsa6', 'fr_aryl_methyl', 'narombond', 'fr_alkyl_carbamate', 'fr_piperzine', 'exactmolwt', 'qed', 'chi0n', 'fr_sulfonamd', 'fr_thiazole', 'numvalenceelectrons', 'fr_phos_acid', 'peoe_vsa12', 'fr_nh1', 'fr_hdrzine', 'fr_c_o_nocoo', 'fr_lactone', 'estate_vsa6', 'bcut2d_logphi', 'vsa_estate7', 'peoe_vsa13', 'numsaturatedcarbocycles', 'fr_nitro', 'fr_phenol_noorthohbond', 'rotratio', 'fr_barbitur', 'fr_isothiocyan', 'balabanj', 'fr_arn', 'fr_imine', 'maxpartialcharge', 'fr_sulfide', 'slogp_vsa11', 'fr_hoccn', 'fr_n_o', 'peoe_vsa1', 'slogp_vsa6', 'heavyatommolwt', 'fractioncsp3', 'estate_vsa8', 'peoe_vsa10', 'numaliphaticrings', 'fr_thiophene', 'maxestateindex', 'smr_vsa10', 'labuteasa', 'smr_vsa2', 'fpdensitymorgan3', 'smr_vsa9', 'slogp_vsa10', 'numaromaticheterocycles', 'fr_nh2', 'fr_diazo', 'chi3n', 'fr_ar_coo', 'slogp_vsa5', 'fr_bicyclic', 'fr_amide', 'estate_vsa10', 'fr_guanido', 'chi1n', 'numsaturatedrings', 'fr_piperdine', 'fr_term_acetylene', 'estate_vsa4', 'slogp_vsa3', 'fr_coo', 'fr_ether', 'estate_vsa7', 'bcut2d_chglo', 'fr_oxazole', 'peoe_vsa6', 'hallkieralpha', 'peoe_vsa2', 'chi2v', 'nocount', 'vsa_estate5', 'fr_nhpyrrole', 'fr_al_coo', 'bertzct', 'estate_vsa11', 'minabspartialcharge', 'slogp_vsa8', 'fr_imide', 'kappa2', 'numaliphaticheterocycles', 'numsaturatedheterocycles', 'fr_hdrzone', 'smr_vsa4', 'fr_ar_n', 'nrot', 'smr_vsa8', 'slogp_vsa2', 'chi4v', 'fr_phos_ester', 'fr_para_hydroxylation', 'smr_vsa3', 'nhohcount', 'estate_vsa2', 'mollogp', 'tpsa', 'fr_azide', 'peoe_vsa4', 'numhdonors', 'fr_al_oh_notert', 'fr_c_o', 'chi0', 'fr_nitro_arom_nonortho', 'vsa_estate3', 'fr_benzene', 'fr_ketone', 'vsa_estate8', 'smr_vsa7', 'fr_ar_oh', 'fr_priamide', 'ringcount', 'estate_vsa3', 'numaromaticcarbocycles', 'bcut2d_mwhi', 'chi1v', 'heavyatomcount', 'vsa_estate4', 'chi0v', 'chiral_centers', 'r_cnt', 's_cnt', 'db_stereo', 'e_cnt', 'z_cnt', 'chiral_fp', 'db_fp'],
    "model_metrics_s3_path": "s3://ideaya-sageworks-bucket/models/training/logd-stereo-quantiles",
    "train_all_data": True
}

# Imports for XGB Model
import xgboost as xgb
import awswrangler as wr

# Model Performance Scores
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error
)

from io import StringIO
import json
import argparse
import os
import pandas as pd


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """
    Check if the provided dataframe is empty and raise an exception if it is.

    Args:
        df (pd.DataFrame): DataFrame to check
        df_name (str): Name of the DataFrame
    """
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)

def match_features_case_insensitive(df: pd.DataFrame, model_features: list) -> pd.DataFrame:
    """
    Matches and renames the DataFrame's column names to match the model's feature names (case-insensitive).
    Prioritizes exact case matches first, then falls back to case-insensitive matching if no exact match exists.

    Args:
        df (pd.DataFrame): The DataFrame with the original columns.
        model_features (list): The desired list of feature names (mixed case allowed).

    Returns:
        pd.DataFrame: The DataFrame with renamed columns to match the model's feature names.
    """
    # Create a mapping for exact and case-insensitive matching
    exact_match_set = set(df.columns)
    column_map = {}

    # Build the case-insensitive map (if we have any duplicate columns, the first one wins)
    for col in df.columns:
        lower_col = col.lower()
        if lower_col not in column_map:
            column_map[lower_col] = col

    # Create a dictionary for renaming
    rename_dict = {}
    for feature in model_features:
        # Check for an exact match first
        if feature in exact_match_set:
            rename_dict[feature] = feature

        # If not an exact match, fall back to case-insensitive matching
        elif feature.lower() in column_map:
            rename_dict[column_map[feature.lower()]] = feature

    # Rename the columns in the DataFrame to match the model's feature names
    return df.rename(columns=rename_dict)


if __name__ == "__main__":
    """The main function is for training the XGBoost Quantile Regression models"""

    # Harness Template Parameters
    target = TEMPLATE_PARAMS["target_column"]
    feature_list = TEMPLATE_PARAMS["feature_list"]
    model_metrics_s3_path = TEMPLATE_PARAMS["model_metrics_s3_path"]
    quantiles = [0.05, 0.25, 0.50, 0.75, 0.95]
    q_models = {}

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Read the training data into DataFrames
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train)
        if file.endswith(".csv")
    ]
    print(f"Training Files: {training_files}")

    # Combine files and read them all into a single pandas dataframe
    df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the dataframe is empty
    check_dataframe(df, "training_df")

    # Features/Target output
    print(f"Target: {target}")
    print(f"Features: {str(feature_list)}")
    print(f"Data Shape: {df.shape}")

    # Grab our Features and Target with traditional X, y handles
    y = df[target]
    X = df[feature_list]

    # Train models for each of the quantiles
    for q in quantiles:
        params = {
            "objective": "reg:quantileerror",
            "quantile_alpha": q,
            "n_estimators": 5000, # Number of trees
            "max_depth": 1,       # Limit tree depth
            "reg_lambda": 100,    # Heavy L2 regularization
        }
        params = {
            "objective": "reg:quantileerror",
            "quantile_alpha": q,
        }
        model = xgb.XGBRegressor(**params)
        model.fit(X, y)

        # Convert quantile to string
        q_str = f"q_{int(q * 100):02}"

        # Store the model
        q_models[q_str] = model

    # Train a model for RMSE predictions
    params = {"objective": "reg:squarederror"}
    rmse_model = xgb.XGBRegressor(**params)
    rmse_model.fit(X, y)

    # Run predictions for each quantile
    quantile_predictions = {q: model.predict(X) for q, model in q_models.items()}

    # Create a copy of the provided DataFrame and add the new columns
    result_df = df[[target]].copy()

    # Add the quantile predictions to the DataFrame
    for name, preds in quantile_predictions.items():
        result_df[name] = preds

    # Add the RMSE predictions (mean) to the DataFrame
    result_df["mean"] = rmse_model.predict(X)
    result_df["prediction"] = result_df["mean"]

    # Now compute residuals on the rmse prediction
    result_df["residual"] = result_df[target] - result_df["prediction"]
    result_df["residual_abs"] = result_df["residual"].abs()


    # Save the results dataframe to S3
    wr.s3.to_csv(
        result_df,
        path=f"{model_metrics_s3_path}/validation_predictions.csv",
        index=False,
    )

    # Report Performance Metrics
    rmse = root_mean_squared_error(result_df[target], result_df["prediction"])
    mae = mean_absolute_error(result_df[target], result_df["prediction"])
    r2 = r2_score(result_df[target], result_df["prediction"])
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R2: {r2:.3f}")
    print(f"NumRows: {len(result_df)}")

    # Now save the quantile models
    for name, model in q_models.items():
        model_path = os.path.join(args.model_dir, f"{name}.json")
        print(f"Saving model:  {model_path}")
        model.save_model(model_path)

    # Save the RMSE model
    model_path = os.path.join(args.model_dir, "rmse.json")
    print(f"Saving model:  {model_path}")
    rmse_model.save_model(model_path)

    # Also save the features (this will validate input during predictions)
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(feature_list, fp)


def model_fn(model_dir) -> dict:
    """Deserialized and return all the fitted models from the model directory.

    Args:
        model_dir (str): The directory where the models are stored.

    Returns:
        dict: A dictionary of the models.
    """

    # Load ALL the Quantile models from the model directory
    models = {}
    for file in os.listdir(model_dir):
        if file.startswith("q") and file.endswith(".json"):  # The Quantile models
            # Load the model
            model_path = os.path.join(model_dir, file)
            print(f"Loading model: {model_path}")
            model = xgb.XGBRegressor()
            model.load_model(model_path)

            # Store the quantile model
            q_name = os.path.splitext(file)[0]
            models[q_name] = model

    # Now load the RMSE model
    models["rsme"] = xgb.XGBRegressor()
    model_path = os.path.join(model_dir, "rmse.json")
    print(f"Loading model: {model_path}")
    models["rsme"].load_model(model_path)

    # Return all the models
    return models


def input_fn(input_data, content_type):
    """Parse input data and return a DataFrame."""
    if not input_data:
        raise ValueError("Empty input data is not supported!")
    
    # Decode bytes to string if necessary
    if isinstance(input_data, bytes):
        input_data = input_data.decode("utf-8")

    if "text/csv" in content_type:
        return pd.read_csv(StringIO(input_data))
    elif "application/json" in content_type:
        return pd.DataFrame(json.loads(input_data))  # Assumes JSON array of records
    else:
        raise ValueError(f"{content_type} not supported!")


def output_fn(output_df, accept_type):
    """Supports both CSV and JSON output formats."""
    if "text/csv" in accept_type:
        csv_output = output_df.fillna("N/A").to_csv(index=False)  # CSV with N/A for missing values
        return csv_output, "text/csv"
    elif "application/json" in accept_type:
        return output_df.to_json(orient="records"), "application/json"  # JSON array of records (NaNs -> null)
    else:
        raise RuntimeError(f"{accept_type} accept type is not supported by this script.")


def predict_fn(df, models) -> pd.DataFrame:
    """Make Predictions with our XGB Quantile Regression Model

    Args:
        df (pd.DataFrame): The input DataFrame
        models (dict): The dictionary of models to use for predictions

    Returns:
        pd.DataFrame: The DataFrame with the predictions added
    """

    # Grab our feature columns (from training)
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        model_features = json.load(fp)
    print(f"Model Features: {model_features}")

    # We're going match features in a case-insensitive manner, accounting for all the permutations
    # - Model has a feature list that's any case ("Id", "taCos", "cOunT", "likes_tacos")
    # - Incoming data has columns that are mixed case ("ID", "Tacos", "Count", "Likes_Tacos")
    matched_df = match_features_case_insensitive(df, model_features)

    # Predict the features against all the models
    for name, model in models.items():
        if name == "rsme":
            df["mean"] = model.predict(matched_df[model_features])
            df["prediction"] = df["mean"]
        else:
            df[name] = model.predict(matched_df[model_features])

    # Reorganize the columns so they are in alphabetical order
    df = df.reindex(sorted(df.columns), axis=1)

    # All done, return the DataFrame
    return df
