from setuptools import find_packages, setup

PACKAGE_NAME = 'pf_reasoning_tool'

setup(
    name=PACKAGE_NAME,
    version='0.4.1',
    description='Custom PromptFlow tools for Hall & Wilcox',
    packages=find_packages(),
    entry_points={
        # all YAMLs are discovered dynamically – nothing else to edit
        'package_tools': [
            'pf_reasoning_tool = pf_reasoning_tool.tools.utils:list_package_tools'
        ],
    },
    install_requires=[
        'promptflow-core>=1.0.0',
        'jinja2>=3.0',
        'ruamel.yaml>=0.17',
        'openai>=1.0',
        'langchain>=0.2.0',
        'langchain-openai>=0.1.5',
        'langchain-community>=0.0.32',
        'azure-search-documents>=11.4.0b7'
    ],
    extras_require={
        'weaviate': ['weaviate-client>=4.5.4'],
        'faiss': [
            'faiss-cpu>=1.7.4; platform_system!="Darwin"',
            'faiss-metal>=1.7.4; platform_system=="Darwin"',
        ],
        'chroma': ['chromadb>=0.5.0'],
        'all_backends': [
            'azure-search-documents>=11.4.0b7',
            'weaviate-client>=4.5.4',
            'faiss-cpu>=1.7.4; platform_system!="Darwin"',
            'faiss-metal>=1.7.4; platform_system=="Darwin"',
            'chromadb>=0.5.0',
        ],
    },
    include_package_data=True,
)
