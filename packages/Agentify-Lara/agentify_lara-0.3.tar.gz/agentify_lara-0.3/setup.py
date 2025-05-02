from setuptools import setup, find_packages

setup(
    name='Agentify_Lara',  # Package name
    version='0.3',  # Initial version
    packages=find_packages(),  # Automatically find packages
    install_requires=["langchain_groq",'openai','langchain','langchain_community','langchain_google_genai','typing',
                      'langchain_anthropic'],
    test_suite='tests',  # Specify test suite
    author='Ubaid Memon',
    author_email='ubaidmemon530@gmail.com',
    description='An agentic Python package for automating tasks',
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',
    url='https://github.com/ubaid978/Agent_Lara',  # Replace with your repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
