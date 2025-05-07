-- # Class: "IdentifiableEntity" Description: "A generic grouping for any identifiable entity"
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
-- # Class: "Benchmark" Description: "A multi-stage workflow to evaluate processing stage for a specific task."
--     * Slot: version Description: The version of the benchmark.
--     * Slot: benchmarker Description: The name and contact details of the person responsible for this benchmark.
--     * Slot: software_backend Description: The software backend used to run the benchmark, e.g. whether apptainer, envmodules, or conda.
--     * Slot: storage Description: The place hosting all benchmark data.
--     * Slot: storage_api Description: The type of the storage API, i.e. S3.
--     * Slot: storage_bucket_name Description: The name of the bucket (i.e. for S3)
--     * Slot: benchmark_yaml_spec Description: Benchmark Specification version.
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
-- # Class: "Stage" Description: "A benchmark subtask with equivalent and independent modules."
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
--     * Slot: Benchmark_id Description: Autocreated FK slot
-- # Class: "Module" Description: "A single benchmark component assigned to a specific stage."
--     * Slot: software_environment Description: Reference to a software environment by key.
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
--     * Slot: Stage_id Description: Autocreated FK slot
--     * Slot: repository_id Description: The code repository hosting the module.
-- # Class: "IOFile" Description: "Represents an input / output file."
--     * Slot: path Description: The output path pattern for the IO file.
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
--     * Slot: Stage_id Description: Autocreated FK slot
-- # Class: "InputCollection" Description: "A holder for valid input combinations."
--     * Slot: id Description: 
--     * Slot: Stage_id Description: Autocreated FK slot
-- # Class: "Repository" Description: "A reference to code repository containing the module's executable code."
--     * Slot: id Description: 
--     * Slot: url Description: The git compatible url.
--     * Slot: commit Description: The commit hash.
-- # Class: "Parameter" Description: "A parameter and its scope."
--     * Slot: id Description: 
-- # Class: "SoftwareEnvironment" Description: "Contains snapshots of the software environment required for the modules to run."
--     * Slot: easyconfig Description: Easybuild configuration file.
--     * Slot: envmodule Description: Environment module name.
--     * Slot: conda Description: Conda environment file.
--     * Slot: apptainer Description: Apptainer image static ORAS url, including name:tag.
--     * Slot: id Description: A unique identifier for a thing
--     * Slot: name Description: A human-readable name for a thing
--     * Slot: description Description: A human-readable description for a thing
--     * Slot: Benchmark_id Description: Autocreated FK slot
-- # Class: "Module_exclude" Description: ""
--     * Slot: Module_id Description: Autocreated FK slot
--     * Slot: exclude_id Description: Ignore these module's outputs as input.
-- # Class: "Module_parameters" Description: ""
--     * Slot: Module_id Description: Autocreated FK slot
--     * Slot: parameters_id Description: 
-- # Class: "InputCollection_entries" Description: ""
--     * Slot: InputCollection_id Description: Autocreated FK slot
--     * Slot: entries_id Description: 
-- # Class: "Parameter_values" Description: ""
--     * Slot: Parameter_id Description: Autocreated FK slot
--     * Slot: values Description: 

CREATE TABLE "IdentifiableEntity" (
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE "Benchmark" (
	version TEXT NOT NULL, 
	benchmarker TEXT NOT NULL, 
	software_backend VARCHAR(10) NOT NULL, 
	storage TEXT NOT NULL, 
	storage_api VARCHAR(2) NOT NULL, 
	storage_bucket_name TEXT NOT NULL, 
	benchmark_yaml_spec TEXT, 
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE "Repository" (
	id INTEGER NOT NULL, 
	url TEXT NOT NULL, 
	"commit" TEXT NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE "Parameter" (
	id INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE "Stage" (
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	"Benchmark_id" TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY("Benchmark_id") REFERENCES "Benchmark" (id)
);
CREATE TABLE "SoftwareEnvironment" (
	easyconfig TEXT, 
	envmodule TEXT, 
	conda TEXT, 
	apptainer TEXT, 
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	"Benchmark_id" TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY("Benchmark_id") REFERENCES "Benchmark" (id)
);
CREATE TABLE "Parameter_values" (
	"Parameter_id" INTEGER, 
	"values" TEXT, 
	PRIMARY KEY ("Parameter_id", "values"), 
	FOREIGN KEY("Parameter_id") REFERENCES "Parameter" (id)
);
CREATE TABLE "Module" (
	software_environment TEXT NOT NULL, 
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	"Stage_id" TEXT, 
	repository_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(software_environment) REFERENCES "SoftwareEnvironment" (id), 
	FOREIGN KEY("Stage_id") REFERENCES "Stage" (id), 
	FOREIGN KEY(repository_id) REFERENCES "Repository" (id)
);
CREATE TABLE "IOFile" (
	path TEXT, 
	id TEXT NOT NULL, 
	name TEXT, 
	description TEXT, 
	"Stage_id" TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY("Stage_id") REFERENCES "Stage" (id)
);
CREATE TABLE "InputCollection" (
	id INTEGER NOT NULL, 
	"Stage_id" TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY("Stage_id") REFERENCES "Stage" (id)
);
CREATE TABLE "Module_exclude" (
	"Module_id" TEXT, 
	exclude_id TEXT, 
	PRIMARY KEY ("Module_id", exclude_id), 
	FOREIGN KEY("Module_id") REFERENCES "Module" (id), 
	FOREIGN KEY(exclude_id) REFERENCES "Module" (id)
);
CREATE TABLE "Module_parameters" (
	"Module_id" TEXT, 
	parameters_id INTEGER, 
	PRIMARY KEY ("Module_id", parameters_id), 
	FOREIGN KEY("Module_id") REFERENCES "Module" (id), 
	FOREIGN KEY(parameters_id) REFERENCES "Parameter" (id)
);
CREATE TABLE "InputCollection_entries" (
	"InputCollection_id" INTEGER, 
	entries_id TEXT, 
	PRIMARY KEY ("InputCollection_id", entries_id), 
	FOREIGN KEY("InputCollection_id") REFERENCES "InputCollection" (id), 
	FOREIGN KEY(entries_id) REFERENCES "IOFile" (id)
);