import pandas as pd
import pickle

with open("best_mode.pickle", "rb") as file:
    data = pickle.load(file)
    model = data['best_model']
    scaler = data['scaler']
    poly_transformer = data['poly_transformer']


def preprocess_data(item: dict) -> pd.DataFrame:
    '''
    переводит 'mileage', 'engine', 'max_power' из строки в float
    'engine' и 'seats' в int
    оставляет только вещественные признаки
    преобразовывает данные согласно согласно сохраненной модели
    '''
    df = pd.DataFrame.from_dict(item, orient='index').T
    for col in ['mileage', 'engine', 'max_power']:
        df[col] = df[col].astype('float32')

    for col in ['year', 'km_driven', 'seats']:
        df[col] = df[col].astype('int32')

    medians = {
        'mileage': 19.37,
        'engine': 1248.0,
        'max_power': 81.86,
        'seats': 5
    }

    for col, median in medians.items():
        df[col] = df[col].replace(0, median)

    df = df.select_dtypes('number')

    df_poly = poly_transformer.transform(df)
    df_scaled = scaler.transform(df_poly)
    return df_scaled


def predict_item(item: dict) -> float:
    df = preprocess_data(item)
    return model.predict(df)
