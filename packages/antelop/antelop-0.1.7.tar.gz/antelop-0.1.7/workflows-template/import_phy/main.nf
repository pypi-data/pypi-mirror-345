#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

params.key
params.phyDir

process DownloadData {

	input:
		val key

	output:
		tuple val(key), path('hashkey.txt'), path('recording'), path('equip.txt'), path('probe.json'), path('params.json')

	script:
	if (key != null)
		"""
		python '${workflow.projectDir}'/bin/download_data.py --key '$key'
		unzip -d recording recording/*.zip
		rm recording/*.zip
		"""

	else
		"""
		echo "No parameter specified"
		"""
}

process ConvertRec {

	input:
		tuple val(key), val(hash), path('recording'), path('equip.txt'), path('probe.json'), path('params.json')

	output:
		tuple val(key), val(hash), path('params.json'), path('split_recordings/*')

	script:
	"""
	python '${workflow.projectDir}'/bin/convert_rec.py
	"""

}

process PreProcess {

	input:
		tuple val(key), val(hash), path('params.json'), path('probe'), val(probenum)

	output:
		tuple val(key), val(hash), path('params.json'), val(probenum), path('preprocessed_*')

	script:
	"""
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/preprocess.py --probe '$probenum' --key '$key'
	"""

}

process ImportPhy {

	input:
		tuple val(key), val(hash), path(params), val(probenum), path(preprocessed)
		val(phyDir)

	output:
		tuple val(key), path(params), val(probenum), path(preprocessed), path('agreement_*')

	script:
	"""
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/import_phy.py --probe '$probenum' --phy '${phyDir}/${hash}'
	"""

}

process ExtractWaveforms {

	input:
		tuple val(key), val(probe_id), path(agreement), path(preprocessed), path(params)

	output:
		tuple val(key), val(probe_id), path('data_*')

	script:
	"""
	export NUMBA_CACHE_DIR='numba_cache'
	export MPLCONFIGDIR='matplotlib_cache'
	export FC_CACHE_DIR='fontconfig_cache'
	python '${workflow.projectDir}'/bin/extract_waveforms.py --sortkey '$key' --probeid '$probe_id'
	"""

}

process UploadData {

	input:
		tuple val(key), val(probe_ids), path(data)

	output:

	script:
	"""
	export MPLCONFIGDIR='matplotlib_cache'
	python '${workflow.projectDir}'/bin/send_db.py --sortkey '$key' --probe_ids '$probe_ids'
	"""

}

workflow {

    QuerySessions(params.key)

    Sessions = QuerySessions.out

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
        (sorters instanceof List ? sorters : [sorters]).splitJson().collect { item ->
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