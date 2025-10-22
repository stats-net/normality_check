
from django.shortcuts import render
from .forms import NumbersForm
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')   # use non-interactive backend for servers
import matplotlib.pyplot as plt
import io, base64

def _arr_stats(arr):
    # arr: numpy array
    n = int(arr.size)
    mean = float(arr.mean())
    median = float(np.median(arr))
    # sample standard deviation
    std_sample = float(arr.std(ddof=1))
    skewness = float(stats.skew(arr, bias=False))
    # fisher=True returns excess kurtosis (0 for normal)
    kurtosis = float(stats.kurtosis(arr, fisher=True, bias=False))
    # Shapiro-Wilk (good for small samples)
    sh_stat, sh_p = stats.shapiro(arr)
    # D'Agostino K^2 normaltest (requires n>=8)
    k2_stat, k2_p = stats.normaltest(arr)

    return {
        "n": n,
        "mean": mean,
        "median": median,
        "std_sample": std_sample,
        "skewness": skewness,
        "kurtosis_excess": kurtosis,
        "shapiro_stat": float(sh_stat),
        "shapiro_p": float(sh_p),
        "dagostino_stat": float(k2_stat),
        "dagostino_p": float(k2_p),
    }

def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.getvalue()
    buf.close()
    return base64.b64encode(img_bytes).decode('ascii')

def analyze_view(request):
    form = NumbersForm(request.POST or None)
    results = None
    hist_img = None
    qq_img = None

    if request.method == "POST" and form.is_valid():
        nums = form.cleaned_data["numbers"]
        arr = np.array(nums)
        results = _arr_stats(arr)

        # Interpretations (alpha = 0.05)
        alpha = 0.05
        results["interpretation_shapiro"] = (
            "No evidence against normality (fail to reject H0)"
            if results["shapiro_p"] > alpha
            else "Evidence of non-normality (reject H0)"
        )
        results["interpretation_dagostino"] = (
            "No evidence against normality (fail to reject H0)"
            if results["dagostino_p"] > alpha
            else "Evidence of non-normality (reject H0)"
        )

        # Histogram
        fig1 = plt.figure()
        plt.hist(arr, bins='auto', edgecolor='black')
        plt.title("Histogram")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        hist_img = _fig_to_base64(fig1)

        # Q-Q plot using scipy.stats.probplot
        fig2 = plt.figure()
        stats.probplot(arr, dist="norm", plot=plt)
        plt.title("Q-Q Plot")
        qq_img = _fig_to_base64(fig2)

    return render(request, "stats/analyze.html", {
        "form": form,
        "results": results,
        "hist_img": hist_img,
        "qq_img": qq_img,
    })

# Create your views here.
