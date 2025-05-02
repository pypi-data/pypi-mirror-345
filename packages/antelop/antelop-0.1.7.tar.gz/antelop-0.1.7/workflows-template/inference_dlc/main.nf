#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

params.key

process QueryData {

	input:
		val(key)

	output:
		path 'data.txt'

	script:
	if (key != null)
		"""
		python '${workflow.projectDir}'/bin/query_data.py --key '$key'
		"""

	else
		"""
		echo "No parameter specified"
		"""
}

process DownloadData {

	input:
		val(key)

	output:
        tuple val(key), path('dlc')

	script:
	if (key != null)
		"""
		python '${workflow.projectDir}'/bin/download_data.py --key '$key'
		"""

	else
		"""
		echo "No parameter specified"
		"""
}

process RunInference {

    input:
        tuple val(key), path('dlc')

    output:
        tuple val(key), path('result')

    script:
    """
    python '${workflow.projectDir}'/bin/run_inference.py --data '$dlc'
    """

}

process UploadResult {

    input:
        tuple val(key), path('result')

    output:

    script:
    """
    python '${workflow.projectDir}'/bin/upload_result.py --key '$key' --data '$result'
    """

}

workflow {

    QueryData(params.key)

	Data = QueryData.out.splitText()

	DownloadData(Data)

    RunInference(DownloadData.out)

    UploadResult(RunInference.out)

}
