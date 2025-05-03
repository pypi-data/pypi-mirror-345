from setuptools import setup, find_packages

setup(
name='dictease',
version='0.1.0',
author= ['S.Hasini','Deepak Das','Irfan Ahmed'],
author_email=['hasinisingireddy2@gmail.com','dpk.ds3@gmail.com','mdirfanahmed12377@gmail.com'],
description='''A simple way to access the dictionary (nested dictionary).
                   e.g. if our dictionary is the following: 
                   our_dict= {"a":{"b":{"c":{"d":{"e":{"f":{"g":{"h":42}}}}}}}} 
                   then to access any element do the following:
                    (our_dict,"a") to access the values of a.
                    Similarly to access any other key lets say b then do the following:
                    (our_dict,"a","b")''',
packages=find_packages(),
classifiers=[
'Programming Language :: Python :: 3',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
],
python_requires='>=3',
)
