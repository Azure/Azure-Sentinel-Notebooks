
# Azure Sentinel Notebooks

Jupyter notebooks are an interactive development and data analysis
environment hosted in a browser. The open API supported by Azure Sentinel
allows you to use Jupyter notebooks to query, transform, analyze
and visualize Azure Sentinel data. This makes notebooks a powerful
addition to Azure Sentinel and is especially well-suited to ad-hoc
investigations, hunting or customized workflows.

<img src="./images/network_graph.png"
alt="Network Timeline" title="Msticpy Timeline Control" width="500" height="400" />

More information on getting started with
[Azure Sentinel and Azure Notebooks](https://docs.microsoft.com/en-us/azure/sentinel/notebooks)

This repository contains notebooks contributed by Microsoft and the community
to assist hunting and investigation tasks in Azure Sentinel.

The notebooks are mostly one of several types:

- Exploration notebooks. These are meant to be used as they are or with
  your own customizations to explore specific hunting and investigation
  scenarios. Examples of this type include the Entity explorer series.
  (“Entity” refers to items such as hosts, IP addresses, accounts, URLs, etc.)
- Guided hunting and guided investigation notebooks that follow a specific
  CyberSec scenario
- How-To notebooks like the Get Started and ConfigureNotebookEnvironment notebooks.
- Sample notebooks. These are longer and are meant to be instructional
  examples following a real or simulated hunt or investigation. They typically
  have save sample data so that you can see what they are meant to do.


## More Information

- [Getting Started](https://nbviewer.jupyter.org/github/Azure/Azure-Sentinel-Notebooks/blob/master/A%20Getting%20Started%20Guide%20For%20Azure%20Sentinel%20ML%20Notebooks.ipynb)
  notebook.
- [Configuring notebook environment](https://nbviewer.jupyter.org/github/Azure/Azure-Sentinel-Notebooks/blob/master/ConfiguringNotebookEnvironment.ipynb)
  notebook.
- Run a demonstration notebook in [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Azure/Azure-Sentinel-Notebooks/master?filepath=nbdemo%2Fmsticpy%20demo.ipynb)
- Read more about the use of Jupyter notebooks in Azure Sentinel on the
  [Azure Sentinel Technical Community blog](https://techcommunity.microsoft.com/t5/azure-sentinel/bg-p/AzureSentinelBlog/label-name/Notebooks).
- Read more about the [Azure ML Notebooks Service](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-run-jupyter-notebooks).
- Read more about [MSTICPy](https://msticpy.readthedocs.io/en/latest/index.html) - the CyberSecurity Python library that powers most of the notebooks


## Feedback

For questions or feedback, please contact AzureSentinel@microsoft.com

---

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
