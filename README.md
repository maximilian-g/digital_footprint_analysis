<div align="center">
  <h1>Method for Intelligent Management and Cataloging of Learning Digital Footprint Objects based on Data Labeling and Natural Language Processing</h1>
<!--   <img src="https://github.com/maximilian-g/digital_footprint_analysis/assets/77752922/fc29573c-3249-47d3-b117-74219e99c843"> -->
</div>

## Dataset description

* **dataset/dataset.json** - JSON file containing array of digital footprints - videos and presentations. In that case videos are protected resources, presentations are publicly available ones. Each object contains "**link**", "**type**", "**additional_info**" properties, protected ones have additional object "**auth_data**".


## Source code files description

* **upload_dataset.ipynb** - is used to upload digital footprints without labels into the storage, for further processing. **NOTE** - for executing notebooks which are using "Storage" component there should be file named "db_host" with single line - MongoDB database host URL.
* **pipeline.py** - implementation of "**Pipeline**", orchestrates "Extractor", "Annotator", "Storage" component during labeling objects of digital footprint.
* **extractor.py** - implementation of "**Extractor**" component, downloads content of digital footprint and extracts data types from the content.
* **annotation.py, annotation_types.py** - files with implementation of "**Annotator**" component, responsible for creating labels with of help NLP techniques.
* **storage.py, service.py** - implementation of "**Storage**" component, files provide classes for working with MongoDB (database of storage component) including different variations of queries for digital footprint objects.
* **digital_footprint.py** - file with classes of different footprint types and associated methods.
* **auth_methods.py** - file with different authentication and authorization methods for accessing protected resources.
* **time_measurement.py, utils.py** - files with utility methods for time measurement and working with objects in Python programming language.
* **Diploma_experiment.ipynb** - notebook with experiment. Here we configure pipeline with its internal components and after that we query for not labeled digital footprint objects that were uploaded previously in **upload_dataset.ipynb**, then we pass all digital footprint object to the pipeline for labeling them. As the result, pipeline saves annotated objects of digital footprint.
* **evaluation_metrics.ipynb** - notebook which evaluates labels that we extracted using metrics.
* **results_visualization.ipynb** - notebook which evaluates labels that we extracted using visualizatoins - word clouds, heatmap.
* **linking_digital_footprints.ipynb** - part of the experiment where we are trying to connect digital footprint objects between themselves, results show that video digital footprints can be connected exactly to their presentations with mean keywords similarity **0.643**.
* **data_management.ipynb** - notebook which shows possibilities of querying for digital footprint objects by their attributes using different queries.


## Result files description

* **evaluation_and_results/Results.json** - file with list of JSON objects - labeled digital footprint objects.
* **evaluation_and_results/Results.docx** - docx file containing keywords, topics, summary and extracted text for VIDEO footprints as a Word document. Only videos are included here because it may be hard to read large texts as extracted text or summary by reading JSON file.
* **evaluation_and_results/metrics.csv** - csv file containing values of evaluation metrics.
* **evaluation_and_results/references.json** - file with list of JSON objects containing reference values for evaluation.
