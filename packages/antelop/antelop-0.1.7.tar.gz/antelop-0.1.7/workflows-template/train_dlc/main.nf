#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

params.key

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

process TrainModel {

    input:
        tuple val(key), path('dlc')

    output:
        tuple val(key), path('dlc')

    script:
    """
    python '${workflow.projectDir}'/bin/train_dlc.py --data '$dlc'
    """

}

process UploadModel {

    input:
        tuple val(key), path('dlc')

    output:
        tuple val(key), path('dlc')

    script:
    """
    python '${workflow.projectDir}'/bin/upload_model.py --key '$key' --data '$dlc'
    """

}

workflow {


	DownloadData(params.key)

    TrainModel(DownloadData.out)

    UploadModel(TrainModel.out)

}
