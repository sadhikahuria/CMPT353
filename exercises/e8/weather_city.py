import sys
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC


def main():

    labelled = pd.read_csv(sys.argv[1])
    unlabelled = pd.read_csv(sys.argv[2])

    X = labelled.drop(columns=['city', 'year']).values
    y = labelled['city'].values

    X_unlabelled = unlabelled.drop(columns=['city', 'year']).values

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,y, random_state=42, stratify=y,)

    model = make_pipeline(
        MinMaxScaler(),
        SVC(kernel='rbf', C=5),
    )


    model.fit(X_train, y_train)
    print(model.score(X_valid, y_valid))


    model.fit(X, y)
    predictions = model.predict(X_unlabelled)

    pd.Series(predictions).to_csv(
        sys.argv[3],
        index=False,
        header=False,
    )


if __name__ == '__main__':
    main()