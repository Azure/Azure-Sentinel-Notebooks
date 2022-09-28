
# Authoring automated Sentinel notebooks

Sentinel notebooks automation is build on the top of Azure Synapse Analytics pipeline platform. 

In this article, we will discuss a few topics:
1. How to enable authentication for automated notebooks
2. How to handle errors and exceptions in notebooks
3. How to persist key findings in Sentinel through REST API


Here is the generic information about [Azure Synapse notebooks](https://docs.microsoft.com/en-us/azure/synapse-analytics/spark/apache-spark-development-using-notebooks).

---

## Authentication of Automated notebooks
Automated notebooks are different from interactive notebooks in terms of granting notebooks to access various data sources.  Interactive notebooks usually have users to manually log into the system and then use users' permissions to access Azure resources including data sources.  Automated notebooks have no users' permissions to use, so they depend on system accounts, either managed identities, or service principals.  Azure Synapse Analytics provides spark utility library to assist AAD authentication in notebooks.  The following code snippets show how to retrieve secrets of service princioal from Azure Key Vault and then use the credentials to initialize the Azure storage client.

```
client_id = mssparkutils.credentials.getSecret(akv_name, client_id_name, akv_link_name)
client_secret = mssparkutils.credentials.getSecret(akv_name, client_secret_name, akv_link_name)
```
Secrets saved in Azure Key Vault are fetched through Synapse linked service.
```
credential = ClientSecretCredential(
    tenant_id=tenant_id, 
    client_id=client_id, 
    client_secret=client_secret)
cred = AzureIdentityCredentialAdapter(credential)
```
Using the secret to generate credential.
```
storage_client = StorageManagementClient(cred, subscription_id=subscription_id)
```
Then Azure storage client is initialized using the credential.

## Errors and exceptions handling in notebooks

When using automation notebooks, users will regularly check the status of notebook runs.  It is important to provide accurate and meaningful statuses to users.  When a notebook encounters error/exception, the notebook execution status should reflect the problem, so that user can take appropriate actions to check out the problem and fix it if necessary.

There are a few ways to raise exceptions at pipeline level.  And also a way to supress exceptions.

<h4>try - except</h4>
You may use try except blocks to catch exceptios and log the exceptiosns then re-throw the exception.  This will cause Synapse pipeline status to be failed.

```
try:
    x = 10
    y = 0
    result = x / y
except ZeroDivisionError:
    print("division by zero")
    throw
```

if no re-throw in the except block, then the exception is supressed and the pipeline will continue without failure. This is when the author decides that the specific exception is minimal and the flow can tolerate the exception.
<h4>No try- except blocks</h4>
If you don't use try except blocks, an uncaught exception will fail the Synapse pipeline.

```
dividedbyzero = 5 / 0
```
<h4>MsSparkUtils</h4>
Using mssparkutils.notebook.exit will not fail the pipeline, but provide an output value in the pipeline's output result section.

```
mssparkutils.notebook.exit("Auth failed")
```
As a notebook developer, you need to decide which way is the right way to handle exceptions based on your scenarios. 

---

# More Information

- [Azure Synapse Studio Notebooks](https://github.com/Azure-Samples/Synapse/blob/main/Notebooks/Introduction%20to%20Azure%20Synapse%20Studio%20Notebooks.ipynb)
- [Develop Synapse notebooks in Azure Synapse Analytics](https://docs.microsoft.com/en-us/azure/synapse-analytics/spark/apache-spark-development-using-notebooks).
- [Intro to Microsoft Spark Utilities](https://docs.microsoft.com/en-us/azure/synapse-analytics/spark/microsoft-spark-utilities?pivots=programming-language-python)

---

# Feedback

For questions or feedback, please file an issue or contact [asinotebooks@service.microsoft.com](mailto:asinotebooks@service.microsoft.com)

