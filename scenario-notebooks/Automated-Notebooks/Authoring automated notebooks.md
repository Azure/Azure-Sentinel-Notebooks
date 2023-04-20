
# Authoring automated Sentinel notebooks

Sentinel notebooks automation is build on the top of Azure Synapse Analytics pipeline platform. 

In this article, we will discuss a few topics:
1. How to retrieve secrets saved in Azure Key Vault
2. How to enable authentication for automated notebooks
3. How to handle errors and exceptions in notebooks
4. Permission check in notebooks
5. How to persist key findings in Sentinel through REST API
6. Developing and testing in Synapse Studio

Here is the generic information about [Azure Synapse notebooks](https://docs.microsoft.com/azure/synapse-analytics/spark/apache-spark-development-using-notebooks).

---

## Retrieval of Azure Key Vault secrets 
An instance of Azure Key Vault is created during notebook configuration time.  Project related secrets can be saved there.  From notebooks, it is easy to read the secrets in Azure Key Vault by using Synapse linked service, which is created during notebook configuration time to link Synapse workspace to Azure Key Vault. 

```
secret = mssparkutils.credentials.getSecret(akv_name, secret_name, akv_link_name)
```

## Authentication of automated notebooks
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


## Permission check in notebooks

Azure service principal is used in Sentinel automation notebooks to access various Azure data sources and REST APIs.  The service principal is likely given different roles in different scopes during notebook configuration time.

|      Scope      | Contributor |  Reader   |
|----------------:|:-----------:|:---------:|
|  Subscription   | W/R in sub  | RO in sub |
|  Resource group | W/R in RG   | RO in RG  |

Since each notebook template may access different data sources and REST APIs with different actions (w/r), it is possible that notebooks will fail during execution due to insufficient permissions.  

To avoid the situation, the service principal should be given peoper permissions to execute target notebooks.  At the same time, notebook authors should try to catch the exception and render meaningful error message. Usually, client object initizliation will not throw exception, but when the client object is used to access a resource object, permission exception will be thrown.

=======
## How to persist key findings in Sentinel through REST API
Sentinel Dynamic Summaries REST API is the recommended way to persist notebook execution results to Azure Log Analytics, where the notebook data can be joined with other data for further analysis.  And regular Sentinel users can query the data as long as they have proper permissions. [The cred scan notebook on Azure Log Analytics](https://github.com/Azure/Azure-Sentinel-Notebooks/blob/master/scenario-notebooks/Automated-Notebooks/AutomationGallery-CredentialScanOnAzureLogAnalytics.ipynb) and [The cred scan notebook on Azure blob storage](https://github.com/Azure/Azure-Sentinel-Notebooks/blob/master/scenario-notebooks/Automated-Notebooks/AutomationGallery-CredentialScanOnAzureBlobStorage.ipynb) provide good examples to send the results to the Dynamic Summaries table in an Azure Log Analytics workspace.

During notebook automation provisioning step, an ADLS storage instance is created for Azure Synapse workspace.  So it is possible to upload the result as a file to blob storage, through the build-in MSSparkUtils module via ADLS linked service. Very few individual users have access to the storage, but it can be used for sequential notebooks in later time.

```
mount_name = "testmount"
mssparkutils.fs.mount( 
    "abfss://sentinelfiles@synapse4sentinel.dfs.core.windows.net", 
    "/" + mount_name,
    {"linkedService":"synapse4sentinel-WorkspaceDefaultStorage"} 
) 

job_id = mssparkutils.env.getJobId()

path = "synfs:/" + job_id + "/" + mount_name
mssparkutils.fs.put(path + "/test.txt", "content to write for testing", True)
```

## Developing and testing in Synapse Studio
First, please develop your notebook in Synapse Studio, which will help you to know more about Synapse and test your notebooks in the process.
Lastly, please set up pipelines and triggers to test your notebooks in Synapse automated environment.

# More Information

- [Azure Synapse Studio Notebooks](https://github.com/Azure-Samples/Synapse/blob/main/Notebooks/Introduction%20to%20Azure%20Synapse%20Studio%20Notebooks.ipynb)
- [Develop Synapse notebooks in Azure Synapse Analytics](https://docs.microsoft.com/azure/synapse-analytics/spark/apache-spark-development-using-notebooks).
- [Intro to Microsoft Spark Utilities](https://docs.microsoft.com/azure/synapse-analytics/spark/microsoft-spark-utilities?pivots=programming-language-python)

---

# Feedback

For questions or feedback, please file an issue or contact [asinotebooks@service.microsoft.com](mailto:asinotebooks@service.microsoft.com)

