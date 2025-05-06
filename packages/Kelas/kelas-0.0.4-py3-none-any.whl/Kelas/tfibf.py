def TextClassification():
    print("""import pandas as pd
data = pd.read_csv('/content/Restaurant_Reviews.tsv',delimiter = '\t', quoting = 3)
data

import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
# Import additional classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

corpus = []
for i in range(0, 1000):
    review = re.sub('[^a-zA-Z]', ' ', data['Review'][i])
    review = review.lower()
    review = review.split()
    ps = PorterStemmer()
    all_stop = stopwords.words('english')
    all_stop.remove('not')
    review = [ps.stem(word) for word in review if not word in set(all_stop)]
    review = ' '.join(review)
    corpus.append(review)

tfidf = TfidfVectorizer(max_features = 1500,smooth_idf=False)
X = tfidf.fit_transform(corpus).toarray()
y = data.iloc[:, 1].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 0)

classifiers = {
    "Naive Bayes": GaussianNB(),
    "Random Forest": RandomForestClassifier(),
    "SVC": SVC(kernel='poly',degree=2),
    "Logistic Regression": LogisticRegression(),
    "Decision Tree": DecisionTreeClassifier()
}

results = {}

for name, classifier in classifiers.items():
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)

    results[name] = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred)
    }

# Print results
for name, metrics in results.items():
    print(f"Classifier: {name}")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    print()

""")