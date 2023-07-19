from pathlib import Path
import os
import re
from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from utils import *
AppPath()


def reformat_address(df: pd.DataFrame, len_address: int) -> pd.DataFrame:
    indexes = df.loc[df['len_address_split'] == len_address].index

    if len_address == 3:
        columns = ['street', 'district', 'city']
    elif len_address == 4:
        columns = ['street', 'ward', 'district', 'city']
    else:
        raise ValueError("The len_address value should be either 3 or 4")

    address_df = pd.DataFrame(
        df.loc[df['len_address_split'] == len_address, 'address_split'].to_list(),
        columns=columns,
        index=indexes
    )
    address_df = address_df.applymap(lambda x: x.strip())

    return address_df

def split_size(size: str) -> list[int, int]:
    size = size.replace(',', '.')

    pattern = r"\(([\d.\d]+)x([\d.\d]+)\)"
    matches = re.search(pattern, size)

    if matches:
        value1 = float(matches.group(1))
        value2 = float(matches.group(2))

        if value1 > value2:
            length = value1
            width = value2
        else:
            length = value2
            width = value1

    return width, length

def list_to_dict(words: list) -> dict:
    columns_dict = {
        'Diện tích đất': 'area',
        'Diện tích sử dụng': 'usable_area',
        'Phòng ngủ': 'num_bedrooms',
        'Nhà tắm': 'num_bathrooms',
        'Pháp lý': 'legal_document',
        'Ngày đăng': 'date_posted',
        'Mã BĐS': 'property_id'
    }

    result_dict = dict()
    for key, value in columns_dict.items():
        try:
            result_dict[value] = words[words.index(key) + 1]
        except ValueError:
            pass

    if len(words) % 2 == 1:
        size = words[words.index('Diện tích đất')+2]
        width, length = split_size(size)
        result_dict['width'] = width
        result_dict['length'] = length

    return result_dict

def word_to_price(words: str):
    words = words.split()

    if len(words) == 2:
        return {
            words[-1]: float(words[0])
        }
    else:
        return {
            words[1]: float(words[0]),
            words[3]: float(words[2])
        }

def remove_outliers_from_column(dataframe: pd.DataFrame, column: str, remove_end: str = 'both'):
    q1 = dataframe[column].quantile(0.25)
    q3 = dataframe[column].quantile(0.75)
    IQR = q3 - q1
    lower = q1 - 1.5 * IQR
    upper = q3 + 1.5 * IQR

    if remove_end == 'both':
        dataframe = dataframe.loc[(dataframe[column] <= upper) & (dataframe[column] >= lower)]
    elif remove_end == 'lower':
        dataframe = dataframe.loc[dataframe[column] >= lower]
    elif remove_end == 'upper':
        dataframe = dataframe.loc[dataframe[column] <= upper]

    return dataframe


def main():
    # Start
    logger = Log(AppConst.CLEAN).log
    logger.info("Started: Cleaning...")

    # Load data
    try:
        df = read_parquet(AppPath.DATA_PQ)
    except FileNotFoundError:
        logger.error(f"Couldn't find {AppPath.DATA_PQ} to read!")
        return
    else:
        logger.info(f"Successfully load data from {AppPath.DATA_PQ}")

    # Cleaning process
    df = df.dropna()
    df = df.reset_index(drop=True)

    # Clean "address" column
    df['address_split'] = df['address'].apply(lambda x: x.split(','))
    df['len_address_split'] = df['address_split'].apply(lambda x: len(x))
    address_df_1 = reformat_address(df, 3)
    address_df_2 = reformat_address(df, 4)
    address_df = pd.concat([address_df_1, address_df_2])
    df = df.join(address_df)
    df = df.drop(columns=['len_address_split', 'address_split'])
    df['city'] = df['city'].apply(lambda x: 'TPHCM' if x == 'TP.HCM' else x)

    # Clean "additional_info" column
    columns_dict = {
        'Diện tích đất': 'area',
        'Diện tích sử dụng': 'usable_area',
        'Phòng ngủ': 'num_bedrooms',
        'Nhà tắm': 'num_bathrooms',
        'Pháp lý': 'legal_document',
        'Ngày đăng': 'date_posted',
        'Mã BĐS': 'property_id'
    }

    df['additional_info_dict'] = df['additional_info'].apply(list_to_dict)
    info_temp_df = pd.json_normalize(df['additional_info_dict'])
    info_temp_df = info_temp_df.rename(columns=columns_dict)

    for col in ['area', 'usable_area']:
        info_temp_df[col] = info_temp_df[col].str.replace('m', '')
        info_temp_df[col] = info_temp_df[col].str.replace(',', '.')
        info_temp_df[col] = info_temp_df[col].str.strip()
        info_temp_df[col] = info_temp_df[col].astype('float')

    for col in ['num_bedrooms', 'num_bathrooms']:
        info_temp_df[col] = info_temp_df[col].astype('float')

    info_temp_df['legal_document'] = info_temp_df['legal_document'].astype('category')
    info_temp_df['date_posted'] = pd.to_datetime(info_temp_df['date_posted'], dayfirst=True)

    df = pd.concat([df, info_temp_df], axis='columns')
    df = df.drop(columns=['additional_info', 'additional_info_dict'])

    # Drop duplicates
    df = df.drop_duplicates()

    # Clean "price" column
    price_temp_df = pd.DataFrame.from_records(df['price'].apply(word_to_price), index=df.index)
    price_temp_df = price_temp_df.fillna(0)
    price_temp_df['price'] = price_temp_df['tỷ'] * 1e9 + price_temp_df['triệu'] * 1e6 + price_temp_df['nghìn'] * 1e3 + price_temp_df['đ']
    price_temp_df['price'] = price_temp_df['price'] / 1e9       # Price (in billion of VND)
    df['price'] = price_temp_df['price']

    # Take properties with price greater than 01.
    # df = df.loc[df['price'] > 0.1]

    # Remove outliers using IQR
    outliers_dict = {
        'price': 'upper',
        'area': 'both',
        'width': 'both',
        'length': 'both',
        'num_bedrooms': 'upper',
        'num_bathrooms': 'upper'
    }
    for column, remove_end in outliers_dict.items():
        df = remove_outliers_from_column(df, column, remove_end)

    # Take properties in the top 10 city
    df = df.loc[df['city'].isin(df['city'].value_counts().iloc[:10].index)]

    # Drop unnecessary columns
    df = df.drop(columns=['ward', 'usable_area'])

    # Save features
    features_column = ['title', 'address', 'content', 'street', 'district', 'city', 'num_bedrooms', 'num_bathrooms',
                       'legal_document', 'date_posted', 'property_id', 'area', 'width', 'length']
    features_df = df.loc[:, features_column]
    to_parquet(features_df, AppPath.FEATURES_PQ)

    # Save entity dataframe
    entity_df = df.loc[:, ['property_id', 'date_posted', 'price']]
    to_parquet(entity_df, AppPath.ENTITY_PQ)

    # End
    if AppPath.FEATURES_PQ.is_file() and AppPath.ENTITY_PQ.is_file():
        logger.info("Finished!")
    else:
        logger.error("Failed to save data files!")


if __name__ == "__main__":
    main()
