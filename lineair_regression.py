import numpy as np
import pandas as pd
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def generate_data():
    np.random.seed(683475)

    n = 300
    x = np.random.normal(size=n)
    y = np.random.normal(loc=2, scale=0.5, size=n) + 0.3 * x

    df = pd.DataFrame({"x": x, "y": y})
    return df


def plot(df, x_grid, y_hat, ci_low, ci_high):

    # --- Plotly scatter + fit + CI ---
    fig = px.scatter(
        df, x="x", y="y", title="Linear Regression with 95% Confidence Interval"
    )

    fig.add_trace(go.Scatter(x=x_grid, y=y_hat, mode="lines", name="Fit"))

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([x_grid, x_grid[::-1]]),
            y=np.concatenate([ci_high, ci_low[::-1]]),
            fill="toself",
            name="95% CI",
            line=dict(width=0),
        )
    )

    st.plotly_chart(fig)


def info(model):
    intercept = model.params["const"]
    beta = model.params["x"]
    p_intercept = model.pvalues["const"]
    p_beta = model.pvalues["x"]
    r2 = model.rsquared

    st.write("Full summary:")
    st.write(model.summary())

    st.write("Coefficients:")
    st.write(f"(Intercept) = {intercept:.4f}   p-value = {p_intercept:.4g}")
    st.write(f"x           = {beta:.4f}   p-value = {p_beta:.4g}")
    st.write()
    st.write(f"R-squared   = {r2:.4f}")
    st.write()


def main():
    st.title("Linear Regression Example")
    df = generate_data()

    # --- Linear regression ---
    X = sm.add_constant(df["x"])
    model = sm.OLS(df["y"], X).fit()

    # --- Predictions + 95% CI band ---
    x_grid = np.linspace(df["x"].min(), df["x"].max(), 200)
    X_pred = sm.add_constant(x_grid)

    pred = model.get_prediction(X_pred).summary_frame(alpha=0.05)

    y_hat = pred["mean"]
    ci_low = pred["mean_ci_lower"]
    ci_high = pred["mean_ci_upper"]

    plot(df, x_grid, y_hat, ci_low, ci_high)
    info(model)


if __name__ == "__main__":
    main()
