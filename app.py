import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import polars as pl
import glob
import time
from openai import OpenAI


st.set_page_config(layout='wide')


# model = 'gpt-5-mini-2025-08-07'
model='gpt-4.1-mini-2025-04-14',
# model='gpt-4o-2024-11-20',
# model="o3-mini-2025-01-31",
# model='gpt-4o-mini-2024-07-18',

keywords = ['worst',
'horrible',
'amazing',
'great',
 'delicious',
 'bad',
 'rude',
 'best',
 'love',
 'order',
 'friendly',
 'terrible',
 'reviews',
 'never',
 'highly',
 'ordered',
 'ok',
 'money',
 'sickening',
 'said',
 'spot',
 'charge',
 'robbed',
 'asked',
 'fast',
 'minutes',
 'favorite',
 'nice',
 'gem',
 'told',
 'perfect',
 'stolen',
 'fresh',
 'recommend',
 'overpriced',
 'phone',
 'really',
 'delivery',
 'waste',
 'super',
 'staff',
 'poor',
 'manager',
 'restaurant',
 'definitely',
 'called',
 'dinero',
 'excellent',
 'garbage',
 'try',
 'okay',
 'disgusting',
 'welcoming',
 'shame',
 'expensive',
 'also',
 'waited',
 'customer']


word_combinations = [('ever', 'worst'),
 ('food', 'worst'),
 ('service', 'worst'),
 ('order', 'worst'),
 ('service', 'horrible'),
 ('food', 'horrible'),
 ('customer', 'horrible'),
 ('order', 'horrible'),
 ('food', 'amazing'),
 ('service', 'amazing'),
 ('great', 'amazing'),
 ('place', 'amazing'),
 ('food', 'great'),
 ('service', 'great'),
 ('place', 'great'),
 ('good', 'great'),
 ('food', 'delicious'),
 ('service', 'delicious'),
 ('great', 'delicious'),
 ('friendly', 'delicious'),
 ('service', 'bad'),
 ('food', 'bad'),
 ('good', 'bad'),
 ('place', 'bad'),
 ('service', 'rude'),
 ('order', 'rude'),
 ('food', 'rude'),
 ('customer', 'rude'),
 ('ever', 'best'),
 ('food', 'best'),
 ('place', 'best'),
 ('service', 'best'),
 ('place', 'love'),
 ('food', 'love'),
 ('great', 'love'),
 ('always', 'love'),
 ('food', 'order'),
 ('time', 'order'),
 ('get', 'order'),
 ('service', 'order'),
 ('staff', 'friendly'),
 ('food', 'friendly'),
 ('great', 'friendly'),
 ('service', 'friendly'),
 ('service', 'terrible'),
 ('food', 'terrible'),
 ('order', 'terrible'),
 ('customer', 'terrible'),
 ('food', 'reviews'),
 ('place', 'reviews'),
 ('good', 'reviews'),
 ('bad', 'reviews'),
 ('food', 'never'),
 ('order', 'never'),
 ('always', 'never'),
 ('place', 'never'),
 ('recommend', 'highly'),
 ('food', 'highly'),
 ('great', 'highly'),
 ('recommended', 'highly'),
 ('food', 'ordered'),
 ('good', 'ordered'),
 ('order', 'ordered'),
 ('chicken', 'ordered'),
 ('food', 'ok'),
 ('good', 'ok'),
 ('service', 'ok'),
 ('place', 'ok'),
 ('food', 'money'),
 ('waste', 'money'),
 ('worth', 'money'),
 ('order', 'money'),
 ('food', 'sickening'),
 ('place', 'sickening'),
 ('get', 'sickening'),
 ('it', 'sickening'),
 ('order', 'said'),
 ('asked', 'said'),
 ('food', 'said'),
 ('back', 'said'),
 ('great', 'spot'),
 ('food', 'spot'),
 ('good', 'spot'),
 ('service', 'spot'),
 ('extra', 'charge'),
 ('food', 'charge'),
 ('order', 'charge'),
 ('service', 'charge'),
 ('got', 'robbed'),
 ('feel', 'robbed'),
 ('like', 'robbed'),
 ('order', 'robbed'),
 ('order', 'asked'),
 ('said', 'asked'),
 ('food', 'asked'),
 ('us', 'asked'),
 ('service', 'fast'),
 ('food', 'fast'),
 ('good', 'fast'),
 ('friendly', 'fast'),
 ('order', 'minutes'),
 ('food', 'minutes'),
 ('wait', 'minutes'),
 ('waited', 'minutes'),
 ('place', 'favorite'),
 ('one', 'favorite'),
 ('food', 'favorite'),
 ('great', 'favorite'),
 ('food', 'nice'),
 ('good', 'nice'),
 ('place', 'nice'),
 ('great', 'nice'),
 ('hidden', 'gem'),
 ('food', 'gem'),
 ('great', 'gem'),
 ('place', 'gem'),
 ('order', 'told'),
 ('us', 'told'),
 ('asked', 'told'),
 ('food', 'told'),
 ('food', 'perfect'),
 ('great', 'perfect'),
 ('place', 'perfect'),
 ('service', 'perfect'),
 ('phone', 'stolen'),
 ('card', 'stolen'),
 ('got', 'stolen'),
 ('order', 'stolen'),
 ('food', 'fresh'),
 ('always', 'fresh'),
 ('delicious', 'fresh'),
 ('great', 'fresh'),
 ('highly', 'recommend'),
 ('food', 'recommend'),
 ('great', 'recommend'),
 ('place', 'recommend'),
 ('food', 'overpriced'),
 ('good', 'overpriced'),
 ('service', 'overpriced'),
 ('place', 'overpriced'),
 ('order', 'phone'),
 ('answer', 'phone'),
 ('food', 'phone'),
 ('called', 'phone'),
 ('good', 'really'),
 ('food', 'really'),
 ('great', 'really'),
 ('place', 'really'),
 ('order', 'delivery'),
 ('food', 'delivery'),
 ('pizza', 'delivery'),
 ('fast', 'delivery'),
 ('money', 'waste'),
 ('time', 'waste'),
 ('dont', 'waste'),
 ('food', 'waste'),
 ('friendly', 'super'),
 ('food', 'super'),
 ('staff', 'super'),
 ('great', 'super'),
 ('friendly', 'staff'),
 ('great', 'staff'),
 ('food', 'staff'),
 ('good', 'staff'),
 ('service', 'poor'),
 ('customer', 'poor'),
 ('food', 'poor'),
 ('order', 'poor'),
 ('order', 'manager'),
 ('food', 'manager'),
 ('service', 'manager'),
 ('us', 'manager'),
 ('food', 'restaurant'),
 ('great', 'restaurant'),
 ('good', 'restaurant'),
 ('service', 'restaurant'),
 ('back', 'definitely'),
 ('food', 'definitely'),
 ('great', 'definitely'),
 ('service', 'definitely'),
 ('order', 'called'),
 ('said', 'called'),
 ('told', 'called'),
 ('food', 'called'),
 ('service', 'excellent'),
 ('food', 'excellent'),
 ('great', 'excellent'),
 ('good', 'excellent'),
 ('food', 'garbage'),
 ('like', 'garbage'),
 ('place', 'garbage'),
 ('pizza', 'garbage'),
 ('food', 'try'),
 ('place', 'try'),
 ('good', 'try'),
 ('great', 'try'),
 ('food', 'okay'),
 ('good', 'okay'),
 ('service', 'okay'),
 ('place', 'okay'),
 ('food', 'disgusting'),
 ('never', 'disgusting'),
 ('place', 'disgusting'),
 ('like', 'disgusting'),
 ('staff', 'welcoming'),
 ('food', 'welcoming'),
 ('great', 'welcoming'),
 ('friendly', 'welcoming'),
 ('food', 'shame'),
 ('place', 'shame'),
 ('order', 'shame'),
 ('its', 'shame'),
 ('good', 'expensive'),
 ('food', 'expensive'),
 ('little', 'expensive'),
 ('place', 'expensive'),
 ('good', 'also'),
 ('food', 'also'),
 ('great', 'also'),
 ('place', 'also'),
 ('minutes', 'waited'),
 ('order', 'waited'),
 ('food', 'waited'),
 ('hour', 'waited'),
 ('service', 'customer'),
 ('great', 'customer'),
 ('food', 'customer'),
 ('good', 'customer')]

word_combinations = [('rude', 'order'),
 ('great', 'love'),
 ('worst', 'order'),
 ('worst', 'rude'),
 ('great', 'amazing'),
 ('amazing', 'best'),
 ('great', 'good'),
 ('worst', 'bad'),
 ('worst', 'horrible'),
 ('horrible', 'bad'),
 ('bad', 'order'),
 ('great', 'best'),
 ('bad', 'never'),
 ('amazing', 'highly'),
 ('reviews', 'never'),
 ('amazing', 'perfect'),
 ('amazing', 'definitely'),
 ('amazing', 'love'),
 ('worst', 'terrible'),
 ('horrible', 'rude'),
 ('great', 'nice'),
 ('horrible', 'order'),
 ('bad', 'rude'),
 ('reviews', 'store'),
 ('worst', 'good'),
 ('horrible', 'terrible'),
 ('worst', 'reviews'),
 ('bad', 'ok'),
 ('great', 'always'),
 ('order', 'ok'),
 ('rude', 'ordered'),
 ('bad', 'good'),
 ('worst', 'never'),
 ('good', '差评'),
 ('waste', 'got'),
 ('best', 'highly'),
 ('best', 'love'),
 ('good', 'negative'),
 ('good', 'always'),
 ('best', 'good'),
 ('rude', 'like'),
 ('money', 'told'),
 ('bad', 'like'),
 ('great', 'place'),
 ('bad', 'terrible'),
 ('love', 'highly'),
 ('love', 'excellent'),
 ('amazing', 'always'),
 ('worst', 'ordered'),
 ('amazing', 'super'),
 ('horrible', 'good'),
 ('great', 'service'),
 ('love', 'definitely'),
 ('love', 'perfect'),
 ('amazing', 'gem'),
 ('terrible', 'money'),
 ('rude', 'good'),
 ('great', 'definitely'),
 ('great', 'really'),
 ('love', 'nice'),
 ('worst', 'money'),
 ('good', 'love'),
 ('best', 'definitely'),
 ('amazing', 'favorite'),
 ('literally', 'gave'),
 ('best', 'place'),
 ('order', 'good'),
 ('even', 'decent'),
 ('great', 'favorite'),
 ('ok', 'good'),
 ('gem', 'highly'),
 ('nice', 'like'),
 ('best', 'favorite'),
 ('nice', 'always'),
 ('good', 'service'),
 ('reviews', 'told'),
 ('good', 'place'),
 ('worst', 'like'),
 ('horrible', 'money'),
 ('best', 'super'),
 ('good', 'like'),
 ('good', 'nice'),
 ('got', 'okay'),
 ('bad', 'asked'),
 ('highly', 'super'),
 ('best', 'excellent'),
 ('horrible', 'never'),
 ('good', 'food'),
 ('never', 'money'),
 ('favorite', 'perfect'),
 ('ok', 'like'),
 ('worst', 'overpriced'),
 ('best', 'always'),
 ('horrible', 'even'),
 ('love', 'place'),
 ('favorite', 'definitely'),
 ('great', 'highly'),
 ('good', 'definitely'),
 ('best', 'nice'),
 ('love', 'really'),
 ('bad', 'money'),
 ('order', 'food'),
 ('attitude', 'workers'),
 ('worst', 'disgusting'),
 ('even', 'time'),
 ('great', 'super'),
 ('order', 'never'),
 ('rude', 'terrible'),
 ('love', 'super'),
 ('best', 'perfect'),
 ('workers', 'like'),
 ('best', 'gem'),
 ('best', 'service'),
 ('bad', 'workers'),
 ('never', 'store'),
 ('called', 'store'),
 ('called', 'even'),
 ('love', 'favorite'),
 ('love', 'always'),
 ('highly', 'favorite'),
 ('great', 'excellent'),
 ('ok', 'ordered'),
 ('reviews', 'overpriced'),
 ('best', 'really'),
 ('like', 'dirty'),
 ('great', 'food'),
 ('good', 'ordered'),
 ('terrible', 'even'),
 ('bad', 'ordered'),
 ('good', 'never'),
 ('good', 'time'),
 ('never', 'food'),
 ('rude', 'even'),
 ('highly', 'perfect'),
 ('favorite', 'excellent'),
 ('worst', 'even'),
 ('always', 'service'),
 ('bad', 'food'),
 ('rude', 'money'),
 ('terrible', 'ordered'),
 ('terrible', 'reviews'),
 ('highly', 'spot'),
 ('great', 'spot'),
 ('amazing', 'spot'),
 ('asked', 'like'),
 ('gem', 'super'),
 ('bad', 'disgusting'),
 ('bad', 'reviews'),
 ('attitude', 'like'),
 ('terrible', 'waste'),
 ('food', 'like'),
 ('waste', 'even'),
 ('reviews', 'avoid'),
 ('rude', 'never'),
 ('amazing', 'excellent'),
 ('always', 'clean'),
 ('amazing', 'good'),
 ('pésimo', 'mal'),
 ('worst', 'store'),
 ('good', 'even'),
 ('order', 'even'),
 ('ok', 'never'),
 ('good', 'asked'),
 ('horrible', 'said'),
 ('money', 'asked'),
 ('love', 'clean'),
 ('great', 'fresh'),
 ('great', 'like'),
 ('excellent', 'nice'),
 ('amazing', 'place'),
 ('reviews', 'said'),
 ('terrible', 'like'),
 ('place', 'service'),
 ('worst', 'food'),
 ('definitely', 'super'),
 ('terrible', 'never'),
 ('place', 'food'),
 ('money', 'said'),
 ('excellent', 'service'),
 ('always', 'perfect'),
 ('definitely', 'always'),
 ('food', 'service'),
 ('nice', 'fresh'),
 ('worst', 'phone'),
 ('order', 'like'),
 ('worst', 'expensive'),
 ('avoid', 'expensive'),
 ('order', 'ordered'),
 ('even', 'ordered'),
 ('love', 'service'),
 ('great', 'order'),
 ('reviews', 'expensive'),
 ('excellent', 'always'),
 ('never', 'like'),
 ('bad', 'said'),
 ('rude', 'food'),
 ('like', 'time'),
 ('love', 'time'),
 ('best', 'like'),
 ('ordered', 'food'),
 ('great', 'perfect'),
 ('horrible', 'like'),
 ('rude', 'ok'),
 ('always', 'really'),
 ('great', 'bad'),
 ('asked', 'ordered'),
 ('best', 'fresh'),
 ('best', 'spot'),
 ('store', 'got'),
 ('favorite', 'clean'),
 ('order', 'nice'),
 ('place', 'nice'),
 ('best', 'time'),
 ('food', 'time'),
 ('super', 'spot'),
 ('favorite', 'always'),
 ('excellent', 'super'),
 ('nice', 'food'),
 ('reviews', '30'),
 ('horrible', 'ordered'),
 ('nice', 'time'),
 ('favorite', 'really'),
 ('overpriced', 'avoid'),
 ('place', 'got'),
 ('decent', 'expensive'),
 ('disgusting', 'food'),
 ('got', 'phone'),
 ('bad', 'even'),
 ('terrible', 'called'),
 ('terrible', 'told'),
 ('terrible', 'good'),
 ('place', 'like'),
 ('terrible', 'poor'),
 ('amazing', 'really'),
 ('terrible', 'disgusting'),
 ('horrible', 'disgusting'),
 ('nice', 'definitely'),
 ('terrible', 'phone'),
 ('ok', 'money'),
 ('like', 'service'),
 ('horrible', 'got'),
 ('great', 'clean'),
 ('worst', 'asked'),
 ('horrible', 'service'),
 ('money', 'airport'),
 ('place', 'always'),
 ('worst', 'got'),
 ('money', 'food'),
 ('amazing', 'service'),
 ('ordered', 'expensive'),
 ('good', 'clean'),
 ('amazing', 'nice'),
 ('never', 'ordered'),
 ('good', 'really'),
 ('overpriced', 'poor'),
 ('ok', 'food'),
 ('terrible', 'said'),
 ('rude', 'waste'),
 ('love', 'gem'),
 ('always', 'like'),
 ('great', 'got'),
 ('never', 'phone'),
 ('rude', 'disgusting'),
 ('order', 'said'),
 ('always', 'super'),
 ('rude', 'service'),
 ('great', 'time'),
 ('love', 'like'),
 ('worst', 'said'),
 ('horrible', 'waste'),
 ('favorite', 'super'),
 ('favorite', 'nice'),
 ('love', 'spot'),
 ('definitely', 'spot'),
 ('ordered', 'like'),
 ('good', 'mal'),
 ('order', 'service'),
 ('amazing', 'fresh'),
 ('order', 'told'),
 ('really', 'like'),
 ('place', 'time'),
 ('waste', 'time'),
 ('excellent', 'really'),
 ('bad', 'service'),
 ('definitely', 'fresh'),
 ('nice', 'service'),
 ('terrible', 'expensive'),
 ('nice', 'clean'),
 ('place', 'really'),
 ('order', 'money'),
 ('good', 'fresh'),
 ('terrible', 'decent'),
 ('money', 'like'),
 ('nice', 'really'),
 ('food', 'really'),
 ('highly', 'excellent'),
 ('got', 'time'),
 ('service', 'time'),
 ('highly', 'definitely'),
 ('terrible', 'store'),
 ('love', 'food'),
 ('place', 'definitely'),
 ('ordered', 'day'),
 ('food', 'fresh'),
 ('horrible', 'reviews'),
 ('order', 'terrible'),
 ('love', 'fresh'),
 ('never', 'time'),
 ('store', 'delivery'),
 ('even', 'like'),
 ('even', '30'),
 ('worst', 'ok'),
 ('really', 'service'),
 ('always', 'food'),
 ('order', 'love'),
 ('got', 'food'),
 ('bad', 'time'),
 ('horrible', 'food'),
 ('highly', 'nice'),
 ('never', 'even'),
 ('highly', 'always'),
 ('even', 'food'),
 ('amazing', 'like'),
 ('worst', 'waste'),
 ('favorite', 'even'),
 ('best', 'food'),
 ('bad', 'attitude'),
 ('even', 'always'),
 ('nice', 'super'),
 ('excellent', 'food'),
 ('reviews', 'phone'),
 ('amazing', 'clean'),
 ('always', 'fresh'),
 ('money', 'store'),
 ('always', 'time'),
 ('nice', 'got'),
 ('bad', 'place'),
 ('bad', 'poor'),
 ('love', 'got'),
 ('money', 'ordered'),
 ('order', 'time'),
 ('money', 'expensive'),
 ('ok', 'expensive'),
 ('order', 'asked'),
 ('ok', 'even'),
 ('rude', 'gave'),
 ('terrible', 'okay'),
 ('excellent', 'definitely'),
 ('told', 'food'),
 ('order', 'place'),
 ('definitely', 'really'),
 ('horrible', 'asked'),
 ('perfect', 'fresh'),
 ('order', 'expensive'),
 ('rude', 'got'),
 ('place', 'perfect'),
 ('super', 'really'),
 ('gem', 'favorite'),
 ('place', 'excellent'),
 ('spot', 'clean'),
 ('called', 'decent'),
 ('definitely', 'time'),
 ('really', 'clean'),
 ('favorite', 'service'),
 ('decent', 'like'),
 ('rude', 'asked'),
 ('ordered', 'said'),
 ('terrible', 'ok'),
 ('asked', 'even'),
 ('even', 'expensive'),
 ('always', 'spot'),
 ('super', 'clean'),
 ('great', 'ordered'),
 ('nice', 'spot'),
 ('perfect', 'super'),
 ('best', 'order'),
 ('worst', 'place'),
 ('even', 'got'),
 ('good', 'money'),
 ('favorite', 'spot'),
 ('terrible', 'asked'),
 ('bad', 'okay'),
 ('rude', 'said'),
 ('bad', 'overpriced'),
 ('really', 'time'),
 ('love', 'even'),
 ('rude', 'store'),
 ('place', 'super'),
 ('horrible', 'told'),
 ('horrible', 'ok'),
 ('horrible', 'delivery'),
 ('never', 'attitude'),
 ('food', 'clean'),
 ('never', 'nice'),
 ('ordered', 'poor'),
 ('definitely', 'perfect'),
 ('worst', '30'),
 ('like', 'fresh'),
 ('never', 'service'),
 ('worst', 'told'),
 ('great', 'never'),
 ('definitely', 'service'),
 ('never', 'got'),
 ('disgusting', 'waste'),
 ('reviews', 'ordered'),
 ('even', 'open'),
 ('asked', '30'),
 ('bad', 'got'),
 ('told', 'ordered'),
 ('terrible', 'food'),
 ('ordered', 'decent'),
 ('money', 'called'),
 ('asked', 'expensive'),
 ('never', 'negative'),
 ('excellent', 'spot'),
 ('money', 'got'),
 ('amazing', 'got'),
 ('bad', 'expensive'),
 ('good', 'said'),
 ('reviews', 'even'),
 ('overpriced', 'expensive'),
 ('bad', 'avoid'),
 ('ordered', 'time'),
 ('store', 'ordered'),
 ('waste', 'place'),
 ('rude', 'reviews'),
 ('ok', 'decent'),
 ('rude', 'expensive'),
 ('amazing', 'time'),
 ('order', 'always'),
 ('decent', 'minutes'),
 ('bad', 'love'),
 ('store', 'place'),
 ('even', 'place'),
 ('good', 'got'),
 ('spot', 'fresh'),
 ('got', 'really'),
 ('never', 'waste'),
 ('never', 'told'),
 ('got', 'always'),
 ('amazing', 'expensive'),
 ('store', 'food'),
 ('super', 'fresh'),
 ('fresh', 'service'),
 ('never', 'asked'),
 ('worst', 'decent'),
 ('spot', 'time'),
 ('even', 'service'),
 ('rude', 'phone'),
 ('excellent', 'clean'),
 ('ordered', 'place'),
 ('excellent', 'fresh'),
 ('order', 'clean'),
 ('definitely', 'clean'),
 ('place', 'spot'),
 ('good', 'super'),
 ('disgusting', 'negative'),
 ('order', 'really'),
 ('asked', 'food'),
 ('ordered', 'service'),
 ('gem', 'definitely'),
 ('asked', 'got'),
 ('perfect', 'spot'),
 ('reviews', 'waste'),
 ('highly', 'place'),
 ('money', 'even'),
 ('avoid', 'really'),
 ('food', 'expensive'),
 ('order', 'fresh'),
 ('money', 'overpriced'),
 ('highly', 'really'),
 ('disgusting', 'said'),
 ('love', 'ordered'),
 ('best', 'got'),
 ('like', 'gave'),
 ('bad', 'delivery'),
 ('terrible', 'delivery'),
 ('asked', 'nice'),
 ('horrible', 'poor'),
 ('reviews', 'literally'),
 ('great', 'fuzhou'),
 ('bad', 'decent'),
 ('excellent', 'time'),
 ('clean', 'service'),
 ('ordered', 'always'),
 ('asked', 'dirty'),
 ('amazing', 'food'),
 ('ordered', 'okay'),
 ('ordered', 'got'),
 ('great', 'store'),
 ('bad', 'really'),
 ('bad', 'always'),
 ('order', 'got'),
 ('food', 'day'),
 ('bad', 'called'),
 ('reviews', 'disgusting'),
 ('ok', 'asked'),
 ('overpriced', 'even'),
 ('excellent', 'perfect'),
 ('place', 'fresh'),
 ('told', 'expensive'),
 ('never', 'love'),
 ('definitely', 'like'),
 ('horrible', 'place'),
 ('best', 'clean'),
 ('best', 'even'),
 ('never', 'expensive'),
 ('ordered', 'nice'),
 ('charge', 'dirty'),
 ('gem', 'perfect'),
 ('overpriced', 'ordered'),
 ('great', 'gem'),
 ('order', 'minutes'),
 ('gem', 'excellent'),
 ('worst', 'avoid'),
 ('worst', 'called'),
 ('waste', 'like'),
 ('said', 'food'),
 ('money', 'minutes'),
 ('money', 'service'),
 ('highly', 'service'),
 ('amazing', 'never'),
 ('phone', 'time'),
 ('money', 'time'),
 ('never', 'place'),
 ('really', 'fresh'),
 ('love', 'day'),
 ('waste', 'avoid'),
 ('super', 'service'),
 ('terrible', 'avoid'),
 ('order', 'waste'),
 ('waste', 'ordered'),
 ('worst', 'service'),
 ('said', 'service'),
 ('good', 'minutes'),
 ('said', 'like'),
 ('place', 'clean'),
 ('great', 'even'),
 ('good', 'favorite'),
 ('terrible', 'place'),
 ('excellent', 'like'),
 ('waste', 'expensive'),
 ('got', 'fresh'),
 ('terrible', 'got'),
 ('horrible', 'expensive'),
 ('terrible', '30'),
 ('never', 'clean'),
 ('horrible', '30'),
 ('store', 'time'),
 ('good', 'spot'),
 ('bad', 'best'),
 ('literally', 'overpriced'),
 ('rude', 'poor'),
 ('reviews', 'poor'),
 ('gem', 'spot'),
 ('reviews', 'money'),
 ('worst', 'time'),
 ('rude', 'told'),
 ('terrible', 'overpriced'),
 ('expensive', 'clean'),
 ('spot', 'service'),
 ('worst', 'charge'),
 ('dirty', 'time'),
 ('ordered', 'phone'),
 ('fresh', 'time'),
 ('spot', 'really'),
 ('store', 'even'),
 ('money', 'decent'),
 ('good', 'highly'),
 ('never', 'disgusting'),
 ('bad', 'told'),
 ('amazing', 'order'),
 ('rude', 'minutes'),
 ('rude', 'called'),
 ('order', 'called'),
 ('horrible', 'decent'),
 ('favorite', 'like'),
 ('definitely', 'food'),
 ('excellent', 'got'),
 ('super', 'time'),
 ('terrible', 'attitude'),
 ('amazing', 'store'),
 ('even', 'told'),
 ('good', 'fuzhou'),
 ('super', 'food'),
 ('asked', 'waste'),
 ('even', 'really'),
 ('bad', 'day'),
 ('ordered', 'delivery'),
 ('30', 'like'),
 ('called', 'ordered'),
 ('like', 'clean'),
 ('worst', 'hour'),
 ('day', 'fresh'),
 ('rude', '30'),
 ('waste', 'negative'),
 ('always', 'day'),
 ('asked', 'said'),
 ('worst', 'amazing'),
 ('disgusting', 'like'),
 ('money', 'phone'),
 ('order', 'definitely'),
 ('asked', 'time'),
 ('never', 'said'),
 ('nice', 'perfect'),
 ('highly', 'got'),
 ('highly', 'fresh'),
 ('rude', 'place'),
 ('food', 'gave'),
 ('ordered', 'really'),
 ('store', 'open'),
 ('best', 'asked'),
 ('even', 'nice'),
 ('fresh', 'clean'),
 ('waste', 'gave'),
 ('even', 'said'),
 ('good', 'excellent'),
 ('told', 'said'),
 ('best', 'never'),
 ('best', 'ok'),
 ('love', 'said'),
 ('never', 'always'),
 ('order', 'decent'),
 ('good', 'decent'),
 ('good', 'dirty'),
 ('reviews', 'asked'),
 ('reviews', 'got'),
 ('got', 'clean'),
 ('overpriced', 'said'),
 ('never', '30'),
 ('literally', 'like'),
 ('asked', 'overpriced'),
 ('reviews', 'charge'),
 ('great', 'told'),
 ('good', 'called'),
 ('disgusting', 'attitude'),
 ('amazing', 'even'),
 ('ordered', 'minutes'),
 ('super', 'like'),
 ('amazing', 'phone'),
 ('amazing', 'bad'),
 ('favorite', 'fresh'),
 ('horrible', 'minutes'),
 ('expensive', 'like'),
 ('horrible', 'overpriced'),
 ('never', 'perfect'),
 ('even', 'spot'),
 ('money', 'disgusting'),
 ('got', 'super'),
 ('perfect', 'day'),
 ('definitely', 'got'),
 ('even', 'super'),
 ('got', 'service'),
 ('good', 'told'),
 ('never', 'definitely'),
 ('overpriced', 'told'),
 ('horrible', 'definitely'),
 ('bad', 'waste'),
 ('got', 'said'),
 ('even', 'poor'),
 ('ok', 'told'),
 ('disgusting', 'got'),
 ('favorite', 'day'),
 ('highly', 'clean'),
 ('bad', '30'),
 ('day', 'like'),
 ('bad', 'charge'),
 ('asked', 'place'),
 ('good', 'day'),
 ('ok', 'said'),
 ('poor', 'got'),
 ('store', 'looks'),
 ('overpriced', 'got'),
 ('worst', 'airport'),
 ('best', 'said'),
 ('ok', 'okay'),
 ('good', 'perfect'),
 ('order', 'attitude'),
 ('worst', 'definitely'),
 ('worst', 'delivery'),
 ('even', 'excellent'),
 ('place', 'day'),
 ('30', 'expensive'),
 ('got', 'like'),
 ('asked', 'gave'),
 ('bad', 'super'),
 ('got', 'spot'),
 ('told', 'got'),
 ('order', 'open'),
 ('food', 'mal'),
 ('told', 'place'),
 ('amazing', 'rude'),
 ('literally', 'dirty'),
 ('expensive', 'time'),
 ('favorite', 'time'),
 ('disgusting', 'even'),
 ('spot', 'day'),
 ('worst', 'poor'),
 ('highly', 'like'),
 ('order', 'okay'),
 ('horrible', 'attitude'),
 ('favorite', 'ordered'),
 ('great', '30'),
 ('even', 'avoid'),
 ('rude', 'time'),
 ('horrible', 'hour'),
 ('amazing', 'ordered'),
 ('overpriced', 'okay'),
 ('asked', 'decent'),
 ('nice', 'said'),
 ('bad', 'gave'),
 ('money', 'okay'),
 ('literally', 'even'),
 ('place', 'said'),
 ('ok', 'time'),
 ('decent', 'okay'),
 ('waste', 'said'),
 ('bad', 'minutes'),
 ('money', 'place'),
 ('disgusting', 'overpriced'),
 ('attitude', 'ordered'),
 ('ordered', 'clean'),
 ('looks', 'like'),
 ('best', 'ordered'),
 ('favorite', 'place'),
 ('best', 'day'),
 ('great', 'horrible'),
 ('store', '30'),
 ('order', 'disgusting'),
 ('worst', 'gave'),
 ('got', 'expensive'),
 ('money', 'poor'),
 ('overpriced', 'like'),
 ('great', 'terrible'),
 ('good', 'expensive'),
 ('asked', 'really'),
 ('order', 'super'),
 ('bad', 'fresh'),
 ('rude', 'okay'),
 ('expensive', 'minutes'),
 ('good', 'store'),
 ('favorite', 'food'),
 ('waste', 'phone'),
 ('rude', 'avoid'),
 ('super', 'day'),
 ('amazing', 'terrible'),
 ('called', 'food'),
 ('rude', 'literally'),
 ('expensive', 'gave'),
 ('30', 'service'),
 ('said', 'decent'),
 ('ordered', 'excellent'),
 ('amazing', 'asked'),
 ('rude', 'nice'),
 ('food', 'spot'),
 ('food', 'dirty'),
 ('never', 'really'),
 ('store', 'waste'),
 ('order', 'excellent'),
 ('ordered', 'fresh'),
 ('rude', 'best'),
 ('like', 'minutes'),
 ('store', 'told'),
 ('rude', 'really'),
 ('reviews', 'looks'),
 ('even', 'fresh'),
 ('amazing', 'said'),
 ('rude', 'overpriced'),
 ('day', 'service'),
 ('poor', 'said'),
 ('highly', 'day'),
 ('decent', 'time'),
 ('bad', 'highly'),
 ('good', 'attitude'),
 ('favorite', 'got'),
 ('asked', 'minutes'),
 ('order', 'dirty'),
 ('worst', 'literally'),
 ('30', 'minutes'),
 ('never', 'fresh'),
 ('expensive', 'service'),
 ('attitude', 'airport'),
 ('never', 'hour'),
 ('terrible', 'gave'),
 ('horrible', 'store'),
 ('said', 'time'),
 ('horrible', 'phone'),
 ('place', 'gave'),
 ('love', 'money'),
 ('day', 'time'),
 ('gave', 'delivery'),
 ('terrible', 'time'),
 ('terrible', 'service'),
 ('order', 'spot'),
 ('always', 'said'),
 ('spot', 'like'),
 ('literally', 'delivery'),
 ('reviews', 'definitely'),
 ('store', 'spot'),
 ('food', 'charge'),
 ('ok', 'minutes'),
 ('store', 'always'),
 ('rude', 'decent'),
 ('nice', 'day'),
 ('never', 'minutes'),
 ('horrible', 'super'),
 ('never', 'highly'),
 ('told', 'phone'),
 ('clean', 'time'),
 ('never', 'excellent'),
 ('day', 'really'),
 ('food', 'decent'),
 ('horrible', 'gave'),
 ('horrible', 'literally'),
 ('great', 'day'),
 ('okay', 'minutes'),
 ('even', 'gave'),
 ('bad', 'nice'),
 ('rude', 'open'),
 ('bad', 'definitely'),
 ('store', 'phone'),
 ('told', 'like'),
 ('ok', 'nice'),
 ('disgusting', 'store'),
 ('told', 'time'),
 ('money', 'charge'),
 ('horrible', 'time'),
 ('store', 'fresh'),
 ('store', 'like'),
 ('got', 'dirty'),
 ('amazing', 'day'),
 ('excellent', 'day'),
 ('told', 'okay'),
 ('poor', 'service'),
 ('asked', 'clean'),
 ('great', 'money'),
 ('rude', 'love'),
 ('rude', 'delivery'),
 ('literally', 'waste'),
 ('best', 'gave'),
 ('waste', 'service'),
 ('worst', 'best'),
 ('food', 'fuzhou'),
 ('ordered', 'avoid'),
 ('good', 'phone'),
 ('day', 'clean'),
 ('store', 'definitely'),
 ('horrible', 'best'),
 ('terrible', 'really'),
 ('gave', 'time'),
 ('poor', 'clean'),
 ('avoid', 'service'),
 ('order', 'reviews'),
 ('terrible', 'nice'),
 ('disgusting', 'phone'),
 ('horrible', 'fresh'),
 ('never', 'decent'),
 ('perfect', 'really'),
 ('reviews', 'really'),
 ('told', 'charge'),
 ('good', 'disgusting'),
 ('attitude', 'service'),
 ('disgusting', 'expensive'),
 ('asked', 'service'),
 ('food', 'minutes'),
 ('asked', 'always'),
 ('asked', 'okay'),
 ('attitude', 'said'),
 ('never', 'avoid'),
 ('ok', 'poor'),
 ('rude', 'fresh'),
 ('money', 'nice'),
 ('gem', 'like'),
 ('asked', 'favorite'),
 ('horrible', 'called'),
 ('told', 'minutes'),
 ('terrible', 'minutes'),
 ('highly', 'food'),
 ('poor', 'expensive'),
 ('reviews', 'hour'),
 ('bad', 'looks'),
 ('never', 'spot'),
 ('bad', 'store'),
 ('attitude', 'food'),
 ('waste', 'minutes'),
 ('told', 'decent'),
 ('waste', 'looks'),
 ('never', 'favorite'),
 ('order', 'perfect'),
 ('money', 'clean'),
 ('charge', 'decent'),
 ('ok', 'spot'),
 ('best', 'money'),
 ('never', 'open'),
 ('good', 'gave'),
 ('disgusting', 'place'),
 ('waste', 'overpriced'),
 ('money', 'delivery'),
 ('even', 'definitely'),
 ('asked', 'fresh'),
 ('even', 'phone'),
 ('worst', 'really'),
 ('poor', 'like'),
 ('worst', 'looks'),
 ('love', 'store'),
 ('ok', 'place'),
 ('horrible', 'always'),
 ('terrible', 'literally'),
 ('open', 'clean'),
 ('gem', 'fresh'),
 ('told', 'clean'),
 ('love', 'gave'),
 ('highly', 'even'),
 ('nice', 'gave'),
 ('never', 'called'),
 ('perfect', 'time'),
 ('great', 'asked'),
 ('store', 'service'),
 ('asked', 'super'),
 ('perfect', 'like'),
 ('reviews', 'attitude'),
 ('food', 'okay'),
 ('best', 'charge'),
 ('overpriced', 'time'),
 ('ok', 'service'),
 ('30', 'okay'),
 ('never', 'super'),
 ('rude', 'always'),
 ('reviews', 'place'),
 ('horrible', 'okay'),
 ('reviews', 'food'),
 ('asked', 'poor'),
 ('got', 'minutes'),
 ('open', 'fresh'),
 ('money', 'waste'),
 ('good', 'poor'),
 ('ok', 'day'),
 ('disgusting', 'ordered')]



######### DEFINE VARS #########
import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
openai_key = st.secrets['openai_key']
client = OpenAI(api_key=openai_key)


patterns = [rf"\b{word1}\b.*\b{word2}\b" for word1, word2 in word_combinations]
keywords = '|'.join(keywords)
review_paths = glob.glob('data/all/reviews/*.parquet')

######### LOAD DATA ######### 
establishments = (
    pl.scan_parquet('data/all/all_establishments.parquet')
    # .filter(pl.col('latitude').is_not_null())
    # .unique()
)
reviews = pl.concat([pl.scan_parquet(path) for path in review_paths])

# only return establishments that have reviews available
valid_fac_ids = reviews.unique('facility_id').select('facility_id').collect()
nyc_establishments = (
    establishments
    .filter(
        (True==True)
        & (pl.col('state') == "NY")
        & (pl.col('longitude').is_not_null())
        & (pl.col('average_rating').is_not_null())
        & (pl.col('facility_id').is_in(valid_fac_ids))
        )
    )


######### SESSION STATES #########
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    st.session_state['messages'].append({'role': 'assistant', 'content': 'Hi! Please enter your abstract.'})


######### DEFINE FUNCTIONS ######### 

def load_categories():
    query = """
    with category_counts as (
    select
        category,
        count(category) as count
    from read_parquet('data/all/all_establishments.parquet') 
    where state = 'NY'
    group by category
    )

    select distinct category
    FROM category_counts
    where count >= 50
    order by category asc
    """ 
    return duckdb.query(query).df()


def load_filtered_reviews(fac_ids):
    query = f"""
    SELECT
        facility_id,
        text,
        rating
    FROM read_parquet('data/all/reviews/*.parquet')
    WHERE 
        True
        AND facility_id IN {fac_ids}    
        -- AND REGEXP_MATCHES(text, '{keywords}')
        AND text NOT NULL
    """
    return duckdb.query(query).df()


def single_query_llm(review_str):
    prompt = f"""
    Tell me the strengths and weaknesses of this places.
    Give a analysis of what customers like and dislike: {review_str}.
    """
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', "content": "You are an authority on food and beverage establishments. Help me anaylze review texts."},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, "content"): 
            yield chunk.choices[0].delta.content
            time.sleep(0.02)



def query_llm(review_str):
    prompt = f"""
    Tell me the strengths and weaknesses of these places. Don't mention specific places. 
    Give a general analysis of what customers like and dislike: {review_str}.
    Then tell me the speicifc best place by name and why it's the best. Then the specific worst place by name and why it's the worst.
    Then tell me the best strategy to exploit the weaknesses of these places such that I can open my own place nearby and be successful.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', "content": "You are an authority on food and beverage establishments. Help me anaylze review texts."},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, "content"): 
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                time.sleep(0.02)


######### LAYOUT #########
st.header('Dishing Out Data: Restaurant Analytics')
main_filter_col, _ = st.columns([6, 6])

map_col, agg_col = st.columns([6, 6])

######### FILTERS #########
with main_filter_col:
    with st.popover('Filters', use_container_width=True):
        filter_col1, filter_col2= st.columns([3, 3])
        with filter_col1:
            # categories = st.multiselect(label='Choose categories', options=load_categories())
            categories = st.pills(label='Choose categories', options=load_categories(), selection_mode='multi')
        with filter_col2:
            st.write('placeholder')



######### MAP #########
with map_col:
    map_df = nyc_establishments.collect().to_pandas()
    if categories:
        map_df = map_df.query('category.isin(@categories)')

    color_min = map_df['average_rating'].quantile(0.025)
    color_max = map_df['average_rating'].quantile(0.85)
    map_selection = st.plotly_chart(
        px.scatter_map(
            data_frame=map_df, 
            lat='latitude', 
            lon='longitude',
            zoom=12,
            center=dict(lat=40.7473666, lon=-73.9902979),
            color='average_rating',
            color_continuous_scale="RdYlGn",
            range_color=[color_min, color_max],
            opacity=0.75,
            map_style='carto-darkmatter',
            hover_name='restaurant_name',
            custom_data=['restaurant_name', 'average_rating', 'score']
            ).update_traces(
                hovertemplate=('%{customdata[0]}<br>'
                                'GoogleMaps Rating: %{customdata[1]}<br>'
                                ),
                marker=dict(size=10)
            ).update_layout(
                width=800,
                height=800
            ).update_coloraxes(
                showscale=False
            )
            , 
        on_select='rerun',
        use_container_width=True
        )

######### AGGREGATIONS #########
with agg_col:
    tab1, tab2, tab3 = st.tabs(["📈 Ratings Over Time", ":star: Reviews", ":left_speech_bubble: DeepInsights"])

    with tab1:
        ######### LINE CHART #########
        if map_selection.selection['point_indices']:
            map_selection_idx = map_selection.selection['point_indices']
            fac_ids = map_df.iloc[map_selection_idx]['facility_id'].unique()
        else:
            fac_ids = map_df.facility_id.unique()
        fac_ids = tuple(fac_ids)
        
        ratings_timeseries = (nyc_establishments
                            .filter(pl.col('facility_id').is_in(fac_ids))
                            .select('facility_id')
                            .join(reviews, on='facility_id')
                            .with_columns(pl.col('timestamp').cast(pl.Datetime('us')))
                            .with_columns(pl.col('timestamp').dt.strftime('%Y-%m').alias('year_month'))
                            .filter(pl.col('timestamp').dt.year() >= 2020)
                            .group_by('year_month')
                            .agg(pl.col('rating').mean().alias('monthly_rating'))
                            .sort(by='year_month')
                            .with_columns(rolling_mean=pl.col('monthly_rating').rolling_mean(window_size=6))
                            .collect()
                            )

        st.plotly_chart(
            px.line(
                data_frame=ratings_timeseries,
                x='year_month',
                y='rolling_mean'
            ).update_layout(
                yaxis=dict(range=[2, 5]),
                height=600
            )
        )

    with tab2:
        ######### REVIEWS #########
        filtered_reviews = load_filtered_reviews(fac_ids)
        if map_selection.selection['point_indices']:
            agg_df = map_df.iloc[map_selection_idx].sort_values(by='average_rating', ascending=False)

            agg_df = pd.merge(agg_df[['facility_id', 'google_name']], 
                              filtered_reviews, 
                              left_on='facility_id', 
                              right_on='facility_id')
            st.dataframe(agg_df, hide_index=False, column_config={'facility_id': None, 'google_name': 'Restaurant', 'text': 'review'})

            concise_reviews = (
                reviews
                .join(establishments.select('facility_id', 'restaurant_name', 'average_rating'), on='facility_id')
                .filter(
                    (True == True)
                    & pl.col('facility_id').is_in(agg_df['facility_id'].to_list())
                ) 
                .head(100000)
                .with_columns(
                    pl.sum_horizontal([pl.col("text").str.count_matches(p, literal=False) for p in patterns]).alias("match_count")
                    )
                .with_columns((pl.col('match_count') / pl.col('text').str.len_chars()).alias('match_ratio'))
                .filter(pl.col("match_count") > 0)
                .sort(by='match_ratio', descending=True)
                .collect()
                .unique(['facility_id', 'text', 'timestamp', 'rating'])
                )

            st.dataframe(
                concise_reviews
                # .filter(
                #     (True == True)
                #     & (pl.col.match_ratio.is_between(0.0001, 0.02)) 
                # )
                .unique(['facility_id', 'text', 'timestamp', 'rating'])
                .with_row_index('id')
            )
            st.dataframe(
                concise_reviews
                # .filter(
                #     (True == True)
                #     & (pl.col.match_ratio.is_between(0.0001, 0.01)) 
                # )
                .unique(['facility_id', 'text', 'timestamp', 'rating'])
                .select(pl.col('rating').value_counts())
            )

            # else:
            #     st.dataframe(filtered_reviews[['text', 'rating']], hide_index=True)
        else:
            st.markdown('# Please make selections on the map.')

        

    with tab3:
        ######### CHAT #########
        filtered_reviews = load_filtered_reviews(fac_ids)
        if map_selection.selection['point_indices']:
            agg_df = map_df.iloc[map_selection_idx].sort_values(by='average_rating', ascending=False)
 

            agg_df = pd.merge(agg_df[['facility_id', 'google_name']], 
                                filtered_reviews, 
                                left_on='facility_id', 
                                right_on='facility_id')

            tab2_reviews = (
                reviews
                .join(establishments.select('facility_id', 'restaurant_name', 'average_rating'), on='facility_id')
                .filter(
                    (True == True)
                    & pl.col('facility_id').is_in(agg_df['facility_id'].to_list())
                ) 
                .head(100000)
                .with_columns(
                    pl.sum_horizontal([pl.col("text").str.count_matches(p, literal=False) for p in patterns]).alias("match_count")
                    )
                .with_columns((pl.col('match_count') / pl.col('text').str.len_chars()).alias('match_ratio'))
                .filter(pl.col("match_count") > 0)
                .sort(by='match_ratio', descending=True)
                .collect()
                .unique()
                )

            reviews_str = (
                tab2_reviews
                .filter(
                    (True == True)
                    & (pl.col.match_ratio.is_between(0.001, 0.01)) 
                )
                .with_columns(reviews_str=pl.concat_str([pl.col('restaurant_name'), pl.col('text')], separator='\n'))
                .sort(by='rating')
                .unique()
                .head(700)
                .select(pl.col('reviews_str').str.join('\n\n').alias('reviews_str'))
            )

            if len(reviews_str) < 700:
                reviews_str = (
                    tab2_reviews
                    .filter(
                        (True == True)
                        & (pl.col.match_ratio.is_between(0.0001, 0.50)) 
                    )
                    .with_columns(reviews_str=pl.concat_str([pl.col('restaurant_name'), pl.col('text')], separator='\n'))
                    .sort(by='rating')
                    .unique()
                    .head(700)
                )


            # reviews_str = (
            #     tab2_reviews
            #     .filter(
            #         (True == True)
            #         & (pl.col.match_ratio.is_between(0.001, 0.01)) 
            #     )
            #     .with_row_index('id')
            # )


            response_container = st.container(height=600)
            with response_container:
                if len(map_selection.selection['point_indices']) == 1:
                    st.write_stream(single_query_llm(reviews_str))
                else:
                    st.write_stream(query_llm(reviews_str))
                # with st.chat_message('Gordon Ramsay'):
                #     st.markdown(openai_response)

        # response_container = st.container(height=600)
        # input_container = st.container()


        # with input_container:
        #     if prompt := st.chat_input('Enter your abstract', max_chars=3000):
        #         # with st.chat_message('user'):
        #         #     st.write(prompt)
        #         st.session_state['messages'].append({'role': 'user', 'content': prompt})
        #         # with st.chat_message("assistant"):
        #         #     response = st.write(prompt)
        # with response_container:
        #     for i, message in enumerate(st.session_state['messages']):
        #         with st.chat_message(message['role']):
        #             st.markdown(message['content'])