#!/usr/bin/python3
import argparse
import sys
parser = argparse.ArgumentParser(description='Обработчик входных данных')
parser.add_argument('-input', help='Файл входных данных',default='input')
parser.add_argument('-output', help='Файл выходных данных',default='output.csv')
parser.add_argument('--minimal_score',type=int,choices=range(2,5),default='3', help='Minimal score of article')
