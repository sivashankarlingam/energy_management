from django.shortcuts import render, HttpResponse
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import UserRegistrationModel
from django.conf import settings
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib
matplotlib.use('Agg')   # ✅ FIXES main thread error
# import Energy Management

# Global variables
global_model = None
features = None
label_encoder = None

# Utility function to load and preprocess dataset
def load_and_preprocess_dataset():
    path = os.path.join(settings.MEDIA_ROOT, 'smart_building_energy_dataset.csv')
    df = pd.read_csv(path)
    # Ensure numerical columns are properly typed
    numerical_cols = ['Temperature', 'Humidity', 'Wind_Speed', 'Time_of_Day', 'Day_of_Week']
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Drop rows with missing values
    df = df.dropna()
    return df

# User Registration View
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            return render(request, 'UserRegistrations.html', {'form': UserRegistrationForm()})
        else:
            messages.error(request, 'Email or Mobile already existed.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

# User Login Check View
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if check.status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                return render(request, 'users/UserHome.html')
            else:
                messages.warning(request, 'Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login ID or Password.')
    return render(request, 'UserLogin.html')

# User Home View
def UserHome(request):
    return render(request, 'users/UserHome.html')

# Dataset View
def DatasetView(request):
    try:
        df = load_and_preprocess_dataset()
        # Limit to first 100 rows for display
        df_html = df.head(100).to_html(classes='table table-striped')
        return render(request, 'users/viewdataset.html', {'data': df_html})
    except Exception as e:
        return HttpResponse(f"Error loading dataset: {str(e)}")

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

def plot_confusion_matrix(cm, title):
    plt.figure()
    sns.heatmap(cm, annot=True, fmt='d')
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    return base64.b64encode(image_png).decode('utf-8')


from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import base64
from io import BytesIO

def plot_confusion_matrix(cm, title):
    plt.figure()
    sns.heatmap(cm, annot=True, fmt='d')
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    return base64.b64encode(image_png).decode('utf-8')


def training(request):
    global global_model, features, label_encoder

    try:
        df = load_and_preprocess_dataset()

        # 🎯 Target + Features
        target_column = 'Device_Selected'
        features = ['Temperature', 'Humidity', 'Wind_Speed', 'Time_of_Day', 'Day_of_Week']

        # 🔄 Encode target
        label_encoder = LabelEncoder()
        df[target_column] = label_encoder.fit_transform(df[target_column])

        X = df[features]
        y = df[target_column]

        # 📊 Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 🚀 MODELS (Pipeline = best practice)
        models = {
            "Random Forest": Pipeline([
                ('scaler', StandardScaler()),
                ('model', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
            ]),
            "Logistic Regression": Pipeline([
                ('scaler', StandardScaler()),
                ('model', LogisticRegression(max_iter=500))
            ]),
            "Decision Tree": Pipeline([
                ('scaler', StandardScaler()),
                ('model', DecisionTreeClassifier(max_depth=10))
            ])
        }

        results = []
        matrices = {}
        reports = {}

        best_acc = 0
        best_model_name = None
        best_model = None

        # 🔁 Train all models
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            acc = accuracy_score(y_test, preds)

            # 🏆 Best model
            if acc > best_acc:
                best_acc = acc
                best_model_name = name
                best_model = model

            # 📊 Confusion Matrix
            cm = confusion_matrix(y_test, preds)
            matrices[name] = plot_confusion_matrix(cm, name)

            # 📄 Classification Report
            report = classification_report(
                y_test,
                preds,
                target_names=label_encoder.classes_,
                output_dict=True
            )
            report_df = pd.DataFrame(report).transpose()
            reports[name] = report_df.to_html(classes='table table-bordered')

            # 📈 Results table
            results.append({
                "Model": name,
                "Accuracy": round(acc * 100, 2)
            })

        # 💾 SAVE BEST MODEL
        model_path = os.path.join(settings.MEDIA_ROOT, "best_model.pkl")
        joblib.dump(best_model, model_path)

        # Save label encoder
        le_path = os.path.join(settings.MEDIA_ROOT, "label_encoder.pkl")
        joblib.dump(label_encoder, le_path)

        # Save features
        features_path = os.path.join(settings.MEDIA_ROOT, "features.pkl")
        joblib.dump(features, features_path)

        global_model = best_model

        results_df = pd.DataFrame(results)

        return render(request, 'users/training.html', {
            "results": results_df.to_dict(orient='records'),
            "best_model": best_model_name,
            "best_acc": round(best_acc * 100, 2),
            "matrices": matrices,
            "reports": reports
        })

    except Exception as e:
        return HttpResponse(f"Error during training: {str(e)}")


import joblib

import joblib
import os
import pandas as pd
from django.conf import settings

def prediction(request):
    hours = list(range(24))

    # ✅ Load features from file (VERY IMPORTANT)
    features_path = os.path.join(settings.MEDIA_ROOT, "features.pkl")
    try:
        features = joblib.load(features_path)
    except Exception as e:
        return render(request, 'users/predictForm1.html', {
            'output': f"Model needs to be trained. Please go to the User Home and execute ML Prediction Training first.",
            'features': [],
            'hours': hours,
        })

    if request.method == 'POST':
        try:
            # Load model + encoder
            model_path = os.path.join(settings.MEDIA_ROOT, "best_model.pkl")
            le_path = os.path.join(settings.MEDIA_ROOT, "label_encoder.pkl")

            model = joblib.load(model_path)
            label_encoder = joblib.load(le_path)

            # Get input
            input_data = {}
            for feature in features:
                value = request.POST.get(feature)

                if value is None:
                    raise ValueError(f"Missing value for {feature}")

                input_data[feature] = float(value)

            input_df = pd.DataFrame([input_data])

            # ✅ Pipeline handles scaling internally
            prediction = model.predict(input_df)[0]

            prediction_label = label_encoder.inverse_transform([prediction])[0]

            return render(request, 'users/predictForm1.html', {
                'output': f'Predicted Device: {prediction_label}',
                'features': features,
                'hours': hours,
            })

        except Exception as e:
            return render(request, 'users/predictForm1.html', {
                'output': f"Error: {str(e)}",
                'features': features,
                'hours': hours,
            })

    return render(request, 'users/predictForm1.html', {
        'features': features,
        'hours': hours,
    })