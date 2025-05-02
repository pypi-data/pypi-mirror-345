#!/usr/bin/env nextflow
nextflow.enable.dsl = 2
import java.security.MessageDigest

params.key

process QuerySessions {

	input:
		val key

	output:
		path 'sessions/*'

	script:
	if (key != null)
		"""
		python '${workflow.projectDir}'/bin/query_sessions.py --key '$key'
		"""

	else
		"""
		echo "No parameter specified"
		"""

	stub:
	"""
	echo "session_1" >> sessions.txt
	echo "session_2" >> sessions.txt
	"""
}

process DownloadData {

	input:
		path 'session.json'

	output:
		tuple path('session.json'), path('recording'), path('equip.txt'), path('probe.json'), path('params.txt')

	script:
	"""
	python '${workflow.projectDir}'/bin/download_data.py
	unzip -d recording recording/*.zip
	rm recording/*.zip
	"""

	stub:
	"""
	mkdir recording
	touch equip.txt
	touch probe.json
	touch params.txt
	"""

}

process ConvertRec {

	input:
		tuple val(trial), path('recording'), path('equip.txt'), path('probe.json'), path('params.txt')

	output:
		tuple val(trial), path('params.txt'), path('split_recordings/*')

	script:
	"""
	python '${workflow.projectDir}'/bin/convert_rec.py
	"""

	stub:
	"""
	mkdir split_recordings
	mkdir split_recordings/0
	mkdir split_recordings/1
	echo "1" >> params.txt
	echo "2" >> params.txt
	"""

}

process PreProcess {

	input:
		tuple val(trial), val(param), path('probe'), val(probenum)

	output:
		tuple path('probekey.json'), path('spikesorters.json'), path('preprocessed_*'), path('params.json'), path('probe')

	script:
	"""
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/preprocess.py --param '$param' --probe '$probenum' --trial '$trial'
	"""

	stub:
	"""
	echo '{"trial":"$trial","sortingparams_id":$param,"probe_id":$probenum}' >> probekey.json.bk
	tr -d '\n' < "probekey.json.bk" > "probekey.json"
	echo '{"pykilosort":{},"mountainsort5":{},"spykingcircus2":{}}' >> spikesorters.json
	mkdir preprocessed
	mkdir lfp
	touch params.json
	"""

}

process MountainSort5 {

	input:
		tuple val(probekey), val(sorter), path('spikesorters.json'), path('preprocessed')

	output:
		tuple val(probekey), path('mountainsort5')

	script:
	"""
	python '${workflow.projectDir}'/bin/spikesort.py --sorter '$sorter'
	"""

	stub:
	"""
	mkdir mountainsort5
	"""

}

process PyKiloSort {

	input:
		tuple val(probekey), val(sorter), path('spikesorters.json'), path('preprocessed')

	output:
		tuple val(probekey), path('pykilosort')

	script:
	"""
	export CUPY_CACHE_DIR='cupy_cache'
	python '${workflow.projectDir}'/bin/spikesort.py --sorter '$sorter'
	"""

	stub:
	"""
	mkdir pykilosort
	"""

}

process SpykingCircus2 {

	input:
		tuple val(probekey), val(sorter), path('spikesorters.json'), path('preprocessed')

	output:
		tuple val(probekey), path('spykingcircus2')

	script:
	"""
	export NUMBA_CACHE_DIR='numba_cache'
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/spikesort.py --sorter '$sorter'
	"""

	stub:
	"""
	mkdir spykingcircus2
	"""

}

process AgreementMatch {

	input:
		tuple val(probekey), path(sortinglist), path('preprocessed'), path('params.json'), path('raw')

	output:
		tuple path('sortkey.json'), path('probe_id.txt'), path('agreement_*'), path('preprocessed_*'), path('raw_*'), path('params.json')

	script:
	"""
	export NUMBA_CACHE_DIR='numba_cache'
	python '${workflow.projectDir}'/bin/agreement_match.py --probe '$probekey' --sortinglist '${sortinglist}'
	"""

	stub:
	"""
	probe=\$(echo '$probekey' | jq -r '.probe_id')
	echo -n \$probe > probe_id.txt
	sortkey=\$(echo '$probekey' | jq 'del(.probe_id)')
	echo -n \$sortkey > sortkey.json
	mkdir agreement
	"""

}

process ExtractWaveforms {

	input:
		tuple val(sortkey), val(probe_id), path(agreement), path(preprocessed), path(raw), path('params.json')

	output:
		tuple val(sortkey), val(probe_id), path('data_*'), path(agreement), path(preprocessed)

	script:
	"""
	export NUMBA_CACHE_DIR='numba_cache'
	export MPLCONFIGDIR='matplotlib_cache'
	export FC_CACHE_DIR='fontconfig_cache'
	python '${workflow.projectDir}'/bin/extract_waveforms.py --sortkey '$sortkey' --probeid '$probe_id'
	"""

	stub:
	"""
	"""

}

process ExportPhy {

	input:
		tuple val(sortkey), val(probe_ids), path(agreement), path(preprocessed), val(hash)

	output:
		tuple val(sortkey), path('phy')

	publishDir "${params.phyDir}/${hash}", mode: "copy", pattern: "phy"

	script:
	"""
	export NUMBA_CACHE_DIR='numba_cache'
	export MPLCONFIGDIR='matplotlib_cache'
	export FC_CACHE_DIR='fontconfig_cache'
	python '${workflow.projectDir}'/bin/export_phy.py --probe_ids '$probe_ids'
	"""

	stub:
	"""
	"""

}

process UploadData {

	input:
		tuple val(sortkey), val(probe_ids), path(data), val(hash)

	output:

	script:
	"""
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/send_db.py --sortkey '$sortkey' --probe_ids '$probe_ids' --hashkey '${hash}'
	"""

	stub:
	"""
	"""

}

workflow {

	QuerySessions(params.key)

	// Ensure the output of QuerySessions is always treated as a list
	Sessions = QuerySessions.out.flatMap { path ->
		(path instanceof List ? path : [path]).collect { file -> file }
	}

	DownloadData(Sessions)

	// read trial key
	ConvertRecChannel = DownloadData.out.map { tuple ->
		def trial = tuple[0].getText()
		def recording = tuple[1]
		def equip = tuple[2]
		def probe = tuple[3]
		def params = tuple[4]

		[ trial, recording, equip, probe, params ]
	}

	ConvertRec(ConvertRecChannel)

	// split channel by probe
	SplitProbe = ConvertRec.out.flatMap { trial, params, recording ->
		// Ensure that recording is always treated as a list
		(recording instanceof List ? recording : [recording]).collect { probe ->
			probenum = probe.getName()
			tuple(trial, params, probe, probenum)
		}
	}

	// split channel by parameter set
	SplitParam = SplitProbe.flatMap { trial, params, probe, probenum ->
		params.splitText().collect { param ->
			tuple(trial, param, probe, probenum)
		}
	}

	PreProcess(SplitParam)

	// split into individual spike sorters
	SplitSorters = PreProcess.out.flatMap { probe, sorters, preprocessed, params, raw ->
		def probekey = probe.getText()
		sorters.splitJson().collect { item ->
			tuple(probekey, item.key, sorters, preprocessed)
		}
	}

	// channel used later for agreement matching etc.
	OtherChannel = PreProcess.out.map { probe, sorters, preprocessed, params, raw ->
		def probekey = probe.getText()
		tuple(probekey, preprocessed, params, raw)
	}

	// make 3 different channels for the 3 spikesorters
	MountainSortChannel = SplitSorters.filter { it -> it[1] == 'mountainsort5'}
	KiloSortChannel = SplitSorters.filter { it -> it[1] == 'pykilosort'}
	SpykingCircusChannel = SplitSorters.filter { it -> it[1] == 'spykingcircus2'}

	MountainSort5(MountainSortChannel)
	PyKiloSort(KiloSortChannel)
	SpykingCircus2(SpykingCircusChannel)

	// match channels based on probe
	AgreementChannel = MountainSort5.out.join(PyKiloSort.out, by: 0, remainder: true).join(SpykingCircus2.out, by: 0, remainder: true).join(OtherChannel, by: 0)

	// get rid of nulls
	AgreementChannel = AgreementChannel.map { tuple ->
		def probekey = tuple[0]
		def sortinglist = tuple[1..3].findAll { it != null }
		def preprocessed = tuple[4]
		def params = tuple[5]
		def raw = tuple[6]

		[probekey, sortinglist, preprocessed, params, raw]

	}

	AgreementMatch(AgreementChannel)

	// read keys
	WaveChannel = AgreementMatch.out.map { tuple ->
		def sortkey = tuple[0].getText()
		def probe_id = tuple[1].getText()
		def agreement = tuple[2]
		def preprocessed = tuple[3]
		def raw = tuple[4]
		def params = tuple[5]

		[ sortkey, probe_id, agreement, preprocessed, raw, params ]
	}

	ExtractWaveforms(WaveChannel)

	// group data by probe and compute hashes
	WaveTmpChannel = ExtractWaveforms.out.groupTuple().map { tuple ->
		def sortkey = tuple[0]
		def probe_ids = tuple[1]
		def data = tuple[2]
		def agreement = tuple[3]
		def preprocessed = tuple[4]

		// Convert the string to bytes
		def inputBytes = sortkey.getBytes("UTF-8")

		// Create a MessageDigest object for SHA-256
		def sha256 = MessageDigest.getInstance("SHA-256")

		// Update the digest with the input bytes
		sha256.update(inputBytes)

		// Get the hash as a byte array
		def hashBytes = sha256.digest()

		// Convert the byte array to a hexadecimal string
		def hash = hashBytes.collect { String.format("%02X", it) }.join().toLowerCase().replaceAll("[\\s\\-]", "").toString()

		[ sortkey, probe_ids, data, agreement, preprocessed, hash ]
	}

	PhyChannel = WaveTmpChannel.map { tuple ->
		def sortkey = tuple[0]
		def probe_ids = tuple[1]
		def agreement = tuple[3]
		def preprocessed = tuple[4]
		def hash = tuple[5]

		[ sortkey, probe_ids, agreement, preprocessed, hash ]
	}

	ExportPhy(PhyChannel)

	UploadChannel = ExportPhy.out.join(WaveTmpChannel, by: 0).map { tuple ->
		def sortkey = tuple[0]
		def probe_ids = tuple[2]
		def data = tuple[3]
		def hash = tuple[6]

		[ sortkey, probe_ids, data, hash ]
	}

	UploadData(UploadChannel)

	// at the end: update table / param compute to not in compute if only one / zero in other table
	// easier if single job with keys concatenated - avoids collisions
}