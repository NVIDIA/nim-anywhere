# auditing
function _audit_venv() {
	echo "Auditing production python dependencies."

	# make a minimal python env
	venv_dir=$(mktemp -d)
	cd $venv_dir
	python3 -m venv "$venv_dir"
	"$venv_dir/bin/pip" install --upgrade pip
	grep -vf /project/req.filters.txt /project/requirements.txt | \
		"$venv_dir/bin/pip" install -r /dev/stdin

	# run the audit on the venv
	"$venv_dir/bin/python" /project/code/tools/audit_venv.py --ignore-healthy
	rm -rf "$venv_dir"
}

function main() {
	_audit_venv
}

main
