from setuptools import setup

setup(name='GmagonAPI',
      version='1.0',
      description='OpenShift App',
      author='Ian sun',
      author_email='lauer3912@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask>=0.12.2', 'Flask_SQLAlchemy>=2.2',
                        'Flask-RESTful>=0.3.6', 'SQLAlchemy-Utils>=0.32.14',
                        'MySQL-python>=1.2.5', 'Flask-Login>=0.4.0'],
     )
