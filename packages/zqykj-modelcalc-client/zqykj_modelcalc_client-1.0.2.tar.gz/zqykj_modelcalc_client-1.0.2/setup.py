from setuptools import setup, find_packages

setup(
    #项目名称引入时或pip时就是此名
    name='zqykj_modelcalc_client',
    #版本号
    version='1.0.2',
    #根据当前目录自动获取路径
    packages=find_packages(),
    install_requires=[
        #包依赖的其他包
        'requests>=2.0.0'
    ],
    python_requires='>=3.6',
    author='cxx',
    author_email='cuixiaoxiao@zqykj.com',
    description='lbsys',
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mypackage',
)
