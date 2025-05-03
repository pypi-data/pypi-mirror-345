mas.devops
==========

|Code style: PEP8| |Flake8: checked| |GitHub Actions Workflow Status|
|PyPI - Version| |PyPI - Python Version| |PyPI - Downloads|

Example
-------

.. code:: python

   from openshift import dynamic
   from kubernetes import config
   from kubernetes.client import api_client

   from mas.devops.ocp import createNamespace
   from mas.devops.tekton import installOpenShiftPipelines, updateTektonDefinitions, launchUpgradePipeline

   instanceId = "mymas"
   pipelinesNamespace = f"mas-{instanceId}-pipelines"

   # Create an OpenShift client
   dynClient = dynamic.DynamicClient(
       api_client.ApiClient(configuration=config.load_kube_config())
   )

   # Install OpenShift Pipelines Operator
   installOpenShiftPipelines(dynamicClient)

   # Create the pipelines namespace and install the MAS tekton definitions
   createNamespace(dynamicClient, pipelinesNamespace)
   updateTektonDefinitions(pipelinesNamespace, "/mascli/templates/ibm-mas-tekton.yaml")

   # Launch the upgrade pipeline and print the URL to view the pipeline run
   pipelineURL = launchUpgradePipeline(self.dynamicClient, instanceId)
   print(pipelineURL)

.. |Code style: PEP8| image:: https://img.shields.io/badge/code%20style-PEP--8-blue.svg
   :target: https://peps.python.org/pep-0008/
.. |Flake8: checked| image:: https://img.shields.io/badge/flake8-checked-blueviolet
   :target: https://flake8.pycqa.org/en/latest/
.. |GitHub Actions Workflow Status| image:: https://img.shields.io/github/actions/workflow/status/ibm-mas/python-devops/python-release.yml
.. |PyPI - Version| image:: https://img.shields.io/pypi/v/mas.devops
   :target: https://pypi.org/project/mas-devops
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/mas.devops
.. |PyPI - Downloads| image:: https://img.shields.io/pypi/dm/mas.devops
