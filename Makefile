# Reproducibility targets for the FedLearn artifact.
# Associated paper: "Who Saw It First: Zero-Day Propagation and Attribution
# Leakage in Federated Intrusion Detection" (IEEE Symposium on Security and Privacy).
#
# Default Python: `python3`. CPU execution is fully supported for all targets.

PY ?= python3

.PHONY: help setup verify verify-datasets verify-manifest verify-proofs verify-env \
        test traceability smoke proto \
        reproduce-attacks reproduce-defenses reproduce-robustness \
        reproduce-crossdataset reproduce-plots reproduce-all clean

help:
	@echo "FedLearn Artifact Reproducibility Targets:"
	@echo "  make help                     Display this help menu"
	@echo "  make setup                    Install dependencies in local virtualenv"
	@echo "  make verify                   Run dataset and checkpoint SHA-256 integrity checks"
	@echo "  make verify-datasets          Check SHA-256 hashes of 4 processed benchmark parquet files"
	@echo "  make verify-manifest          Check SHA-256 hashes of 30 archived tables/metrics/figures"
	@echo "  make verify-proofs            Machine-check all 9 Lean 4 formal proofs + math audit suite"
	@echo "  make verify-env               Validate Python runtime and dependency version pins"
	@echo "  make test                     Execute automated unit test suite (pytest)"
	@echo "  make traceability             Verify presence and validity of archived result records"
	@echo "  make smoke                    Run fast end-to-end sanity suite (< 1 minute)"
	@echo "  make reproduce-attacks        Reproduce Table 3 origin attribution & timing attacks"
	@echo "  make reproduce-defenses       Reproduce Table 4 & Figure 3 defense Pareto frontier"
	@echo "  make reproduce-robustness     Reproduce Table 5 operational friction stress tests"
	@echo "  make reproduce-crossdataset   Reproduce Table 6 & Figure 4 50-round FL sweeps"
	@echo "  make reproduce-plots          Render all publication figures (PDF & PNG)"
	@echo "  make reproduce-all            Execute the complete empirical reproduction suite"
	@echo "  make clean                    Remove temporary build and test caches"

setup:
	$(PY) -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e worker --no-deps

proto:
	$(PY) -m grpc_tools.protoc -I proto --python_out=worker/src/fedids_worker/gen proto/fedids/v1/experiment.proto proto/fedids/v1/metrics.proto

verify-datasets:
	$(PY) verification/verify_datasets.py

verify-manifest:
	$(PY) verification/verify_manifest.py

verify-proofs:
	cd leanproofs && lake build && .lake/build/bin/fedlearn_proofs && $(PY) verify_math.py && cd ..

verify-env:
	$(PY) scripts/verify_environment.py

test:
	$(PY) -m pytest worker/tests/ -q

traceability:
	$(PY) scripts/check_traceability.py

smoke: verify-env verify-datasets verify-manifest traceability test
	@echo ""
	@echo "================================================================="
	@echo "  FedLearn: SMOKE TEST PASS (All fast integrity checks OK)"
	@echo "================================================================="

reproduce-attacks:
	./scripts/run_table3_suite.sh

reproduce-defenses:
	./scripts/run_fig2_defenses.sh

reproduce-robustness:
	./scripts/run_sec5_5_robustness.sh

reproduce-crossdataset:
	$(PY) scripts/run_50fl_4datasets.py
	$(PY) scripts/calibrate_fl50_data.py

reproduce-plots:
	$(PY) plots/generate_paper_plots.py

reproduce-all: smoke verify-proofs reproduce-attacks reproduce-defenses reproduce-robustness reproduce-crossdataset reproduce-plots
	@echo ""
	@echo "================================================================="
	@echo "  FedLearn: FULL EMPIRICAL REPRODUCTION COMPLETED SUCCESSFULLY"
	@echo "================================================================="

clean:
	rm -rf .pytest_cache worker/.pytest_cache worker/src/fedids_worker.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	touch runs/.gitkeep
